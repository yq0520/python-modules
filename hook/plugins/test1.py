# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : test1.py
# @Project : python-modules
# @Software: PyCharm
def registerCallbacks(reg):
    matchEvents_change = {'event_name': ['vendor_dailies_oss_download']}
    reg.registerCallback(main, matchEvents_change)


def main(log, event):
    log.info('我也执行')
