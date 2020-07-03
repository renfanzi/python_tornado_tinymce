#!/usr/bin/env python
# -*- coding:utf-8 -*-


import re
import tornado.web
from app import static_path
from controllers.HomeHandlers import BaseController
import os
import stat
from datetime import datetime
import random
import json
import base64
import tornado.ioloop
from controllers.HomeHandlers import BaseHandler


class Upload(object):
    ''' upload image or file    '''

    def __init__(self):
        self.config = {}

        self.oriName = ''  # 原始文件名
        self.fileName = ''  # 新文件名
        self.fullName = ''  # 完整文件名,即从当前配置目录开始的URL
        self.filePath = ''  # 完整文件名,即从当前配置目录开始的URL
        self.fileSize = 0  # 文件大小
        self.fileType = ''  # 文件类型
        self.stateMap = {
            "SUCCESS": "SUCCESS",  # 上传成功标记，在UEditor中内不可改变，否则flash判断会出错
            "ERROR_FILE_MAXSIZE": "文件大小超出 upload_max_filesize 限制",
            "ERROR_FILE_LIMITSIZE": "文件大小超出 MAX_FILE_SIZE 限制",
            "ERROR_FILE_UPLOAD_FAILED": "文件未被完整上传",
            "ERROR_FILE_NOT_UPLOAD": "没有文件被上传",
            "ERROR_FILE_NULL": "上传文件为空",
            "ERROR_SIZE_EXCEED": "文件大小超出网站限制",
            "ERROR_TYPE_NOT_ALLOWED": "文件类型不允许",
            "ERROR_CREATE_DIR": "目录创建失败",
            "ERROR_DIR_NOT_WRITEABLE": "目录没有写权限",
            "ERROR_FILE_SAVE": "文件保存时出错",
            "ERROR_FILE_NOT_FOUND": "找不到上传文件",
            "ERROR_WRITE_CONTENT": "写入文件内容错误"
        }

    def getItem(self, key):
        fp = open("static/ueditor/config.json", 'r')
        config = json.loads(fp.read())
        fp.close()
        for k, v in config.items():
            if k == key:
                return v

    def getStateInfo(self, stateinfo):
        for k, v in self.stateMap.items():
            if k == stateinfo:
                return v

    def checkSize(self):
        if self.fileSize > self.config['maxSize']:
            return False
        else:
            return True

    def checkType(self):
        if self.fileType in self.config['allowFiles']:
            return True
        else:
            return False

    def getFullName(self):
        now = datetime.now()
        randint = random.randint(100000, 999999)
        format = self.config['pathFormat']
        format = format.replace("{yyyy}", now.strftime("%Y"))
        format = format.replace("{mm}", now.strftime("%m"))
        format = format.replace("{dd}", now.strftime("%d"))
        format = format.replace("{time}", now.strftime("%H%M%S"))
        format = format.replace("{rand:6}", str(randint))

        ext = self.oriName[self.oriName.rfind("."):]
        self.fileName = "%s%s%s" % (now.strftime("%H%M%S"), randint, ext)
        return format + ext

    def getFilePath(self):

        fullpath = os.path.join(os.getcwd(), self.fullName)
        return fullpath

    def uploadFile(self, upfile):
        result = {'state': '', 'url': '', 'title': '', 'original': ''}

        if not upfile or len(upfile) == 0:
            result['state'] = self.getStateInfo('ERROR_FILE_NOT_UPLOAD')
            return result

        self.oriName = upfile[0]['filename']
        self.fileType = self.oriName[self.oriName.rfind('.'):]
        data = upfile[0]['body']
        self.fileSize = len(data)

        if self.fileSize == 0:
            result['state'] = self.getStateInfo('ERROR_FILE_NULL')
            return result

        if not self.checkSize():
            result['state'] = self.getStateInfo('ERROR_SIZE_EXCEED')
            return result

        if not self.checkType():
            result['state'] = self.getStateInfo('ERROR_TYPE_NOT_ALLOWED')
            return result

        self.fullName = self.getFullName()
        self.filePath = self.getFilePath()

        dirname = os.path.dirname(self.filePath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except Exception as e:
                result['state'] = self.getStateInfo('ERROR_CREATE_DIR')
                return result

        if not os.access(dirname, os.R_OK | os.W_OK):
            try:
                os.chmod(dirname, stat.S_IREAD | stat.S_IWRITE)
            except Exception as e:
                result['state'] = self.getStateInfo('ERROR_DIR_NOT_WRITEABLE')
                return result

        try:
            fp = open(self.filePath, 'wb')
            fp.write(data)
            fp.close()
        except Exception as e:
            result['state'] = self.getStateInfo('ERROR_FILE_SAVE')
            return result

        result['state'] = self.stateMap['SUCCESS']
        result['url'] = self.fullName
        result['title'] = self.fileName
        result['original'] = self.oriName
        return result

    def getFileList(self, start, size):
        result = {'state': '', 'list': [], 'start': 0, 'total': 0}
        path = self.config['path']
        listSize = self.config['listSize']

        listfiles = []
        for root, dirs, files in os.walk(path):
            for file in files:
                self.fileType = file[file.rfind('.'):]
                if self.checkType():
                    url = root + '/' + file
                    listfiles.append({'url': '%s' % url})

        if size > listSize:
            num = listSize
        else:
            num = size

        listfiles.sort()
        lists = listfiles[start:(start + num)]

        result['state'] = self.stateMap['SUCCESS']
        result['list'] = lists
        result['start'] = start
        result['total'] = len(listfiles)
        return result


class UploadImageHandler(BaseHandler):

    def post(self):

        upload = Upload()
        fieldName = upload.getItem('imageFieldName')
        upload.config['pathFormat'] = upload.getItem('imagePathFormat')
        upload.config['maxSize'] = upload.getItem('imageMaxSize')
        upload.config['allowFiles'] = upload.getItem('imageAllowFiles')

        upfile = self.request.files[fieldName]
        result = upload.uploadFile(upfile)
        # tinymce 规定返回格式如此
        result = {'location': "http://127.0.0.1:5000/" + result["url"]}

        self.write(result)

class UploadVideoHandler(BaseHandler):

    def post(self):

        upload = Upload()
        fieldName = upload.getItem('videoFieldName')
        upload.config['pathFormat'] = upload.getItem('videoPathFormat')
        upload.config['maxSize'] = upload.getItem('videoMaxSize')
        upload.config['allowFiles'] = upload.getItem('videoAllowFiles')

        upfile = self.request.files[fieldName]
        result = upload.uploadFile(upfile)
        result = {'location': "http://127.0.0.1:5000/" + result["url"]}
        self.write(result)

class UploadFileHandler(BaseHandler):

    def post(self):

        upload = Upload()
        fieldName = upload.getItem('fileFieldName')
        upload.config['pathFormat'] = upload.getItem('filePathFormat')
        upload.config['maxSize'] = upload.getItem('fileMaxSize')
        upload.config['allowFiles'] = upload.getItem('fileAllowFiles')

        upfile = self.request.files[fieldName]
        result = upload.uploadFile(upfile)
        # tinymce 规定返回格式如此
        result = {'location': "http://127.0.0.1:5000/" + result["url"]}

        self.write(result)
