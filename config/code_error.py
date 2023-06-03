# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : code_error.py
# @Project : python-modules
# @Software: PyCharm
"""
返回指定状态码 以及对应语言提示 并记录错误日志
"""
from config.conf import response_message
from config.log import com_log


class Author(object):
    def __init__(self, response, language):
        self.response = response
        self.language = language


def response_200(author, data):
    author.response.status_code = 200
    message = response_message(author.language, 10200)
    return {'code': 0, 'msg': message, 'data': data}


def response_500(author, error):
    """服务器内部错误:服务器遇到错误，无法完成请求"""
    code = 500
    language_code = 10500
    message = response_message(author.language, str(error))
    com_log.record(com_log.ERROR, f'{code}[{language_code}]: {str(error)}')
    author.response.status_code = code
    return {'code': language_code, 'msg': message, 'data': str(error)}


class CodeException(Exception):
    def __init__(self, e, *args, **kwargs):
        super().__init__(args)
        self.e = e
        self.language = kwargs.get('language')
        self.args = args

    def __str__(self):
        return self.get_message()

    def get_message(self):
        message = response_message(self.language, self.e)
        if self.args:
            count = message.count('{}')
            if len(self.args) >= count:
                message = message.format(*self.args)
        return message

    def response(self):
        return {'code': self.e, 'msg': self.get_message()}


def main():
    try:
        # a = 0
        # c = 10/a
        raise CodeException('40008')
    except CodeException as ce:
        print(ce.e)
        print(ce)
        print(ce.response())
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
