# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : obs_api.py
# @Project : python-modules
# @Software: PyCharm
"""
 pip install esdk-obs-python --trusted-host pypi.org
"""
import re
import traceback

from obs import ObsClient


class ObsAPi(object):
    def __init__(self):
        self.client = ObsClient(
            access_key_id='',
            secret_access_key='',
            server='https://outsourced.obs.cn-north-1.myhuaweicloud.com'
        )
        self.bucket = 'outsourced'

    def close_client(self):
        if self.client:
            self.client.close()

    @staticmethod
    def key_rule(key):
        """
        对象键 规范处理
        :param key:
        :return:
        """
        # 反斜线转换
        key = key.replace('\\', '/')
        # 首个字符
        key = re.sub('^/', '', key)
        return key

    @staticmethod
    def progress_callback(transferredAmount, totalAmount, totalSeconds):
        # 获取上传平均速率(KB/S)
        print(transferredAmount * 1.0 / totalSeconds / 1024)
        # 获取上传进度百分比
        print(transferredAmount * 100.0 / totalAmount)

    def upload_file(self, uploadFile, objectKey, partSize, taskNum, enableCheckpoint=False):
        """
        :param uploadFile:待上传的本地文件，如aa/bb.txt。
        :param objectKey:对象名，即上传后的文件名。
        :param partSize:分段大小，单位字节，取值范围是100KB~5GB，默认为9MB。
        :param taskNum:分段上传时的最大并发数，默认为1。
        :param enableCheckpoint:是否开启断点续传模式，默认为False，表示不开启。
        :return:
        """
        try:
            resp = self.client.uploadFile(self.bucket, objectKey, uploadFile, partSize, taskNum, enableCheckpoint, progressCallback=self.progress_callback)
            if resp.status < 300:
                print('requestId:', resp.requestId)
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
        except:
            print(traceback.format_exc())

    def download_file(self, downloadFile, objectKey, partSize, taskNum, enableCheckpoint):
        try:
            resp = self.client.downloadFile(self.bucket, objectKey, downloadFile, partSize, taskNum, enableCheckpoint, progressCallback=self.progress_callback)
            if resp.status < 300:
                print('requestId:', resp.requestId)
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
        except:
            print(traceback.format_exc())

    def create_folder(self, folder):
        try:
            folder = self.key_rule(folder)
            if folder[-1] != '/':
                folder = f'{folder}/'
            resp = self.client.putContent(self.bucket, folder, content=None)
            if resp.status < 300:
                print('requestId:', resp.requestId)
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
        except:
            print(traceback.format_exc())

    def get_list_objects(self, prefix, delimiter, max_keys=1000):
        """
        :param prefix:限定返回的对象名必须带有prefix前缀。
        :param delimiter:
        :param max_keys:列举对象的最大数目，取值范围为1~1000，当超出范围时，按照默认的1000进行处理。
        :return:
        """
        prefix = self.key_rule(prefix)
        if prefix[-1] != '/':
            prefix = f'{prefix}/'
        try:
            max_num = 1000
            mark = None
            while True:
                resp = self.client.listObjects(self.bucket, prefix=prefix, marker=mark, max_keys=max_num)
                if resp.status < 300:
                    print('requestId:', resp.requestId)
                    print('name:', resp.body.name)
                    print('prefix:', resp.body.prefix)
                    print('max_keys:', resp.body.max_keys)
                    print('is_truncated:', resp.body.is_truncated)
                    index = 1
                    for content in resp.body.contents:
                        print('object [' + str(index) + ']')
                        print('key:', content.key)
                        print('lastModified:', content.lastModified)
                        print('etag:', content.etag)
                        print('size:', content.size)
                        print('storageClass:', content.storageClass)
                        print('owner_id:', content.owner.owner_id)
                        print('owner_name:', content.owner.owner_name)
                        index += 1
                    if resp.body.is_truncated is True:
                        mark = resp.body.next_marker
                    else:
                        break
                else:
                    print('errorCode:', resp.errorCode)
                    print('errorMessage:', resp.errorMessage)
        except:
            import traceback
            print(traceback.format_exc())
