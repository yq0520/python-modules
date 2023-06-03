# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : conf.py
# @Project : python-modules
# @Software: PyCharm

import yaml
import os


def system_folder(file, parent_number=0):
    """
    从当前文件 算起 向上级查找目录层级
    :param file:对应文件
    :param parent_number:层级
    :return: 对应文件父级目录 或当前目录
    """
    self_path = os.path.abspath(file)
    for i in range(parent_number):
        self_path = os.path.dirname(self_path)
    return self_path


class DB(object):
    def __init__(self, host, username, password, database, port):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port


class RedisDB(object):
    def __init__(self, password, host, port, database):
        self.password = password
        self.host = host
        self.port = port
        self.database = database


class Settings(object):
    """
    读取配置文件
    """

    def __init__(self):
        """
        _config: 统一配置信息
        _envConfig: 环境区分配置信息
        """
        with open(os.path.join(system_folder(__file__, 1), 'setting.yaml'), encoding='utf-8') as s:
            _config = yaml.load(s, Loader=yaml.FullLoader)
        self._config = _config
        self._env_config = _config.get(_config.get('env'))

    def debug(self):
        return self._config.get('env')

    def server_name(self):
        return self._config.get('name')

    def token_key(self):
        return self._config.get('token_key')

    def token_expire(self):
        """
        token 过期时间 0 为永不过期 单位 秒
        :return:
        """
        return self._config.get('token_expire', 0)

    def min_password_length(self):
        """
        密码最小长度
        :return:
        """
        return self._config.get('password_min_length', 8)

    def default_language(self):
        return self._config.get('language')

    def server_db(self):
        _db = self._env_config.get('db')
        return DB(_db.get('user'), _db.get('password'), _db.get('host'), _db.get('port'), _db.get('db'))

    def redis_db(self):
        _db = self._env_config.get('redis')
        return RedisDB(_db.get('password'), _db.get('host'), _db.get('port'), _db.get('db'))


cf = Settings()

with open(os.path.join(system_folder(__file__, 1), 'language.yaml'), 'r', encoding='utf-8') as f:
    LANGUAGE = yaml.load(f, Loader=yaml.FullLoader)


def response_message(language, code=10200):
    """
    根据语言标识 代码返回对应的 语言提示新
    :param language: 语言标识
    :param code: 提示代码
    :return:
    """
    if language is None:
        language = cf.default_language()
    message = LANGUAGE.get(language, None)
    if message is None:
        message = LANGUAGE[cf.default_language()]
    if code in message.keys():
        msg_info = message[code]
    else:
        msg_info = code
    return msg_info
