# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : test.py
# @Project : python-modules
# @Software: PyCharm
import time


def registerCallbacks(reg):
    matchEvents_change = {'transfer_mode': ['vendor_dailies_oss_download']}
    reg.registerCallback(main, matchEvents_change)


def main(log, event):
    log.info('我执行')
    time.sleep(3)
