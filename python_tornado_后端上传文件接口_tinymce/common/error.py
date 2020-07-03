#!/usr/bin/env python
# -*- coding:utf-8 -*-


CODEMSG = {
    2000: u"True",
    4000: u"客户上传的文件格式不正确",
    4010: u"客户上传的文件格式是要求格式以外的文件",
    4001: u"客户上传的文件列超过1024",
    4002: u"客户端未传值或值传递错误!",
    4021: u"客户端有未传值参数或为None!",
    4022: u"客户端传递值错误!",
    4003: u"文件数据格式不对",
    4004: u"已经存在",
    4005: u"用户未认证或认证不成功",
    4006: u"无法进行数据分析",
    4007: u"用户分析条件不正确",
    4008: u"用户无权限",
    4999: u"Unknown Error!!!",
    5000: u"服务器错误",
    5001: u"数据表已经存在",
    5002: u"sql语句错误",
    5003: u"索引文件未创建"
}


class MyCustomError(Exception):
    """
    Error class for the IBM SPSS Statistics Input Output Module
    Use Method:

    def example():
    try:
        raise ValueError # ['']
        raise SPSSError(retcode="6001") or  raise SPSSError(retcode=6001)
    except Exception as e:
        e = FormatErrorCode(e)
        print(e) # ['4999', 'Unknown Error!!!']

    example()

    #>>> (5001, '数据表已经存在')

    """

    def __init__(self, msg=None, retcode=4999):
        self.retcode = int(retcode)
        try:
            if not msg:
                msg = CODEMSG[int(self.retcode)]
        except:
            msg = "Unknown Error!!!"
        Exception.__init__(self, self.retcode, msg)


def FormatErrorCode(arg):
    data = str(arg).replace("(", "").replace(")", "").replace("'", '').split(",")
    if all(data):
        Error_Infor = [i.strip() for i in data if i]
        if len(Error_Infor) == 2:
            return [i.strip() for i in data if i]
        else:
            try:
                raise MyCustomError(msg=Error_Infor[0])
            except Exception as e:
                return FormatErrorCode(e)
    else:
        try:
            raise MyCustomError()
        except Exception as e:
            return FormatErrorCode(e)


class SPSSError(MyCustomError):
    def __init__(self, retcode=None):
        super(SPSSError, self).__init__(retcode=retcode)


class GetParametersError(MyCustomError):
    def __init__(self, retcode=4002):
        super(GetParametersError, self).__init__(retcode=retcode)

if __name__ == '__main__':
    def example():
        try:
            raise ValueError # ['']
            # raise SPSSError(retcode="6001") #or  raise SPSSError(retcode=6001)
        except Exception as e:
            status, msg = FormatErrorCode(e)
            print(status) # ['4999', 'Unknown Error!!!']
            print(msg) # ['4999', 'Unknown Error!!!']

    example()