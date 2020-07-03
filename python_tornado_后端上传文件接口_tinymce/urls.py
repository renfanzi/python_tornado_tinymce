#!/usr/bin/env python
# -*- coding:utf-8 -*-


from controllers.UeditHandlers import *

urls = list()

# -----<富文本编辑器操作-添加文章>----- #
editorUrls = [


    # -----> 富文本编辑器上传文件和图片接口 <----- #
    (r'/uploadimage/', UploadImageHandler),

    (r'/uploadvideo/', UploadVideoHandler),

    (r'/uploadfile/', UploadFileHandler),

]

urls += editorUrls
