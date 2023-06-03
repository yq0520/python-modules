# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : log.py
# @Project : python-modules
# @Software: PyCharm
"""
自定义日志 每一级别对应一个文件 分开存放
"""
import inspect
import logging
# from logging.handlers import RotatingFileHandler
import os
from logging import Logger
from logging.handlers import TimedRotatingFileHandler


class Log(object):
    """
    自定义日志
    CRITICAL(50) > ERROR(40) > WARNING(30) > INFO(20) > DEBUG(10)
    """
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10

    def __init__(self, name=None, log_path='logs', level=ERROR):
        """
        :param name:
        :param log_path:
        :param level:
        """
        com_log_parent_path = os.path.dirname(os.path.abspath(__file__))
        com_log_path = os.path.dirname(com_log_parent_path)
        self.__name = name
        self.__path = "{0}/{1}".format(com_log_path, log_path)
        self.__error = None
        self.__warning = None
        self.__info = None
        self.__debug = None
        exists = os.path.exists(self.__path)
        if not exists:
            os.makedirs(self.__path)
        if logging.ERROR <= level:
            _path = "{0}/{1}.log".format(self.__path, 'ERROR')
            self.__error = self.__base_log(log_path + 'ERROR', logging.ERROR, _path, 5)
        if logging.WARNING <= level:
            _path = "{0}/{1}.log".format(self.__path, 'WARNING')
            self.__warning = self.__base_log(log_path + 'WARNING', logging.WARNING, _path, 5)
        if logging.INFO <= level:
            _path = "{0}/{1}.log".format(self.__path, 'INFO')
            self.__info = self.__base_log(log_path + 'INFO', logging.INFO, _path, 5)
        if logging.DEBUG <= level:
            _path = "{0}/{1}.log".format(self.__path, 'DEBUG')
            self.__debug = self.__base_log(log_path + 'DEBUG', logging.DEBUG, _path, 5)

    def record(self, level, text):
        if logging.ERROR == level:
            if self.__error:
                text_list = ['******** start ********', text]
                count = 1
                for info in inspect.trace():
                    context_list = []
                    for value in info.code_context:
                        context_list.append(value.lstrip())
                    text_list.append(f"*****{count}***** \nfilename={info.filename};\nfunction={info.function};")
                    text_list.append(f"line={info.lineno};\ncontext={''.join(context_list)}")
                    count += 1
                message = "\n".join(text_list)
                message += "******** end ********"
                self.__error.error(message)
        if logging.WARNING == level:
            if self.__warning:
                self.__warning.warning(text)
        if logging.INFO == level:
            if self.__info:
                self.__info.info(text)
        if logging.DEBUG == level:
            if self.__debug:
                self.__debug.debug(text)
        logging.shutdown()

    @staticmethod
    def __base_log(logger_name, level, path, size):
        """
        日志管理类型
        :param logger_name: 日志名字 *** 用来给日志分类，不同类日志 分别记录 每一个类型值需初始化一次
        :param level: 日志级别 *** 记录日志的等级
        :param path: 文件存储路径
        :param size: 日志文件分割大小 单位 Mb 天数
        :return:
        """
        logger = None
        if logger_name not in Logger.manager.loggerDict:
            # logging.basicConfig()
            handler = logging.handlers.TimedRotatingFileHandler(path, when="D", interval=1, backupCount=size, encoding="utf-8")
            fmt = '[%(asctime)s]:%(message)s.'  # 日志输出的格式
            formatter = logging.Formatter(fmt)  # 设置格式
            handler.setFormatter(formatter)
            logger = logging.getLogger(logger_name)  # 设置日志名称
            logger.addHandler(handler)  # 添加刚设置的handler
            logger.setLevel(level)  # 设置级别为info以上记录到日志
        return logger


com_log = Log()
