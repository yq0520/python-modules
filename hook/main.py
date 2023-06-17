# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : main.py
# @Project : python-modules
# @Software: PyCharm

"""
钩子hook，顾名思义，可以理解是一个挂钩，作用是有需要的时候挂一个东西上去。
具体的解释是：钩子函数是把我们自己实现的hook函数在某一时刻挂接到目标挂载点上。

hook函数是程序中预定义好的函数，这个函数处于原有程序流程当中（暴露一个钩子出来）
我们需要再在有流程中钩子定义的函数块中实现某个具体的细节，需要把我们的实现，挂接或者注册（register）到钩子里，使得hook函数对目标可用
hook 是一种编程机制，和具体的语言没有直接的关系
如果从设计模式上看，hook模式是模板方法的扩展
钩子只有注册的时候，才会使用，所以原有程序的流程中，没有注册或挂载时，执行的是空（即没有执行任何操作）
"""

import importlib
import logging
import os
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from threading import Thread


class Registrar(object):
    """
    See public API docs in docs folder.
    """

    def __init__(self, plugin):
        """
        Wrap a plugin so it can be passed to a user.
        """
        self._plugin = plugin
        self._allowed = ['logger', 'setEmails', 'registerCallback']

    def getLogger(self):
        """
        Get the logger for this plugin.

        @return: The logger configured for this plugin.
        @rtype: L{logging.Logger}
        """
        # TODO: Fix this ugly protected member access
        return self.logger

    def __getattr__(self, name):
        if name in self._allowed:
            return getattr(self._plugin, name)
        raise AttributeError("type object '%s' has no attribute '%s'" % (type(self).__name__, name))


class Callback(object):
    def __init__(self, callback, match_events, plugin):
        self._name = None
        self._callback = callback
        self._matchEvents = match_events
        self._plugin = plugin
        if hasattr(callback, '__name__'):
            self._name = callback.__name__
        elif hasattr(callback, '__class__') and hasattr(callback, '__call__'):
            self._name = '%s_%s' % (callback.__class__.__name__, hex(id(callback)))
        else:
            raise ValueError('registerCallback argument.')

    def canProcess(self, event):
        """
        验证 event 注册信息
        :param event:
        :return:
        """
        if not self._matchEvents:
            return False
        attributes = self._matchEvents['event_name']

        if event['event_name'] and event['event_name'] in attributes:
            return True
        return False

    def process(self, log, event):
        if self.canProcess(event):
            self._callback(log, event)


class Plugin(object):
    def __init__(self, name):
        print(os.path.splitext(os.path.basename(name)))
        self.name = os.path.splitext(os.path.basename(name))[0]
        self.suffix = os.path.splitext(os.path.basename(name))[1]
        self.log = self._log()
        self._callbacks = []

    def log_handler(self, fmt):
        """
        # filename：日志文件名
        # when：日志文件按什么维度切分。'S'-秒；'M'-分钟；'H'-小时；'D'-天；'W'-周
        #       这里需要注意，如果选择 D-天，那么这个不是严格意义上的'天'，而是从你
        #       项目启动开始，过了24小时，才会从新创建一个新的日志文件，
        #       如果项目重启，这个时间就会重置。所以这里选择'MIDNIGHT'-是指过了午夜
        #       12点，就会创建新的日志。
        # interval：是指等待多少个单位 when 的时间后，Logger会自动重建文件。
        # backupCount：是保留日志个数。默认的0是不会自动删除掉日志
        :param fmt:
        :return:
        """
        logs = 'logs'
        exists = os.path.exists(logs)
        if not exists:
            os.makedirs(logs)
        handler = TimedRotatingFileHandler(filename=f'{logs}/{self.name}.log', when="D", interval=1, backupCount=7, encoding="utf-8")
        formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')  # 设置格式
        handler.setFormatter(formatter)
        # handler.setLevel(level)
        return handler

    def _log(self):
        """
        critical > error > warning > info > debug
        :return:
        """
        logger = None
        if self.name not in Logger.manager.loggerDict:
            logger = logging.getLogger(self.name)  # 设置日志名称
            logger.setLevel(logging.INFO)

            handler = self.log_handler('[%(levelname)s][%(asctime)s]:%(message)s.')
            debug = self.log_handler('[%(levelname)s][%(asctime)s][%(lineno)d]:%(message)s.')
            info = self.log_handler('[%(levelname)s][%(asctime)s][info]:%(message)s.')
            # warning = self.log_handler('warning', logging.WARNING)
            # error = self.log_handler('error', logging.ERROR)

            # 添加刚设置的handler
            logger.addHandler(handler)
            logger.addHandler(debug)
            logger.addHandler(info)
            # logger.addHandler(warning)
            # logger.addHandler(error)

        return logger

    def load(self):
        self._callbacks = []
        if self.suffix == ".py":
            spec2 = importlib.import_module(f'plugins.{self.name}')

            regFunc = getattr(spec2, 'registerCallbacks', None)
            if callable(regFunc):
                regFunc(Registrar(self))
            else:
                print('registerCallbacks')

    def registerCallback(self, callback, match_events):
        self._callbacks.append(Callback(callback, match_events, self))

    def process(self, event):
        for callback in self._callbacks:
            callback.process(self.log, event)


class PluginCollection(object):
    def __init__(self):
        self._plugins = {}

    def load(self):
        plugins_dict = {}
        for basename in os.listdir('plugins'):
            if not basename.endswith('.py'):
                continue
            if basename in self._plugins.keys():
                plugins_dict[basename] = self._plugins[basename]
            else:
                plugins_dict[basename] = Plugin(basename)
            plugins_dict[basename].load()
        self._plugins = plugins_dict

    def __iter__(self):
        for basename in sorted(self._plugins.keys()):
            yield self._plugins[basename]

    def process(self, event):
        for key, plugin in self._plugins.items():
            # plugin.process(event)
            th = Thread(target=plugin.process, args=(event,))
            # 设置守护线程
            # th.setDaemon(True)
            th.start()


def main():
    pl = PluginCollection()
    pl.load()
    data = {'transfer_mode': 'vendor_dailies_oss_download'}
    pl.process(data)


if __name__ == '__main__':
    main()
