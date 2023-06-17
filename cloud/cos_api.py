# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : cos_api.py
# @Project : python-modules
# @Software: PyCharm

"""
腾讯云 存储 cos 文件上传下载
pip install cos-python-sdk-v5
"""
import logging
import os
import re
import sys

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from qcloud_cos.cos_threadpool import SimpleThreadPool
from cloud.cos_temp_token import CosTempToken

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def cos_client():
    """
    通过 COS 默认域名访问时，SDK 会以 {bucket-appid}.cos.{region}.myqcloud.com 的域名形式访问 COS。
    通过 COS 全球加速域名访问时，SDK 会以 {bucket-appid}.cos.accelerate.myqcloud.com 的域名形式访问 COS，region 不会出现在访问域名中。


    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
    secret_id = os.environ['COS_SECRET_ID']     # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
    secret_key = os.environ['COS_SECRET_KEY']   # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
    region = None              # 通过 Endpoint 初始化不需要配置 region
    token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
    scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

    endpoint = 'cos.accelerate.myqcloud.com' # 替换为用户的 endpoint 或者 cos全局加速域名，如果使用桶的全球加速域名，需要先开启桶的全球加速功能，请参见 https://cloud.tencent.com/document/product/436/38864
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Endpoint=endpoint, Scheme=scheme)
    client = CosS3Client(config)
    :return:
    """
    secret_id = '用户的 SecretId'
    secret_key = '用户的 SecretKey'
    region = '用户的 region'
    # 全球加速域名 {bucket-appid}.cos.{region}.myqcloud.com
    # endpoint = ''
    endpoint = 'cos.accelerate.myqcloud.com'
    config = CosConfig(
        Region=region,
        SecretId=secret_id,
        SecretKey=secret_key,
        Endpoint=endpoint,
    )
    client = CosS3Client(config)
    return client


def cos_token_client():
    ctt = CosTempToken()
    data = ctt.get_credential_demo()
    if data:
        # 1. 设置用户属性, 包括 secret_id, secret_key, region 等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
        tmp_secret_id = data.get('tmpSecretId')  # 临时密钥的 SecretId，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
        tmp_secret_key = data.get('tmpSecretKey')  # 临时密钥的 SecretKey，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
        token = data.get('sessionToken')  # 临时密钥的 Token，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
        region = '用户的 region'  # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket

        config = CosConfig(Region=region, SecretId=tmp_secret_id, SecretKey=tmp_secret_key, Token=token)
        client = CosS3Client(config)
        return client


class CosApi(object):
    def __init__(self, client):
        self.client = client
        self.bucket = '存储桶'

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
    def error(e):
        e.get_trace_id()  # 获取请求的 trace_id
        e.get_request_id()  #
        e.get_resource_location()  # 获取 URL 地址
        return {
            # 获取原始错误信息，格式为XML
            'origin_msg': e.get_origin_msg(),
            # 获取处理过的错误信息，格式为dict
            'digest_msg': e.get_digest_msg(),
            # 获取 http 错误码（如4XX，5XX)  https://cloud.tencent.com/document/product/436/7730
            'status_code': e.get_status_code(),
            # 获取 COS 定义的错误码 https://cloud.tencent.com/document/product/436/7730
            'error_code': e.get_error_code(),
            # 获取 COS 错误码的具体描述 https://cloud.tencent.com/document/product/436/7730
            'error_msg': e.get_error_msg(),
            # 获取请求的 trace_id
            'trace_id': e.get_trace_id(),
            # 获取请求的 request_id
            'request_id': e.get_request_id(),
            # 获取 URL 地址
            'resource_location': e.get_resource_location(),
        }

    @staticmethod
    def upload_percentage(consumed_bytes, total_bytes):
        """进度条回调函数，计算当前上传的百分比

        :param consumed_bytes: 已经上传的数据量
        :param total_bytes: 总数据量
        """
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            print('\r{0}% '.format(rate))
            sys.stdout.flush()

    def upload_file(self, local_file, key):
        """

        :param local_file: 本地文件
        :param key: 云端文件
        :return:
        """
        for i in range(0, 10):
            try:
                self.client.upload_file(
                    Bucket=self.bucket,
                    Key=key,
                    LocalFilePath=local_file)
                break
            except CosClientError or CosServiceError as e:
                print(e)

    def upload_dir(self, upload_dir, cos_dir):
        """
        文件夹上传
        :param upload_dir:
        :param cos_dir:
        :return:
        """
        g = os.walk(upload_dir)
        # 创建上传的线程池
        pool = SimpleThreadPool()
        cos_dir = self.key_rule(cos_dir)
        for path, dir_list, file_list in g:
            for file_name in file_list:
                srcKey = os.path.join(path, file_name)
                cos_key = self.key_rule(srcKey.replace(upload_dir, ''))
                cosObjectKey = self.key_rule(os.path.join(cos_dir, cos_key))
                print(cosObjectKey)
                # 判断 COS 上文件是否存在
                exists = False
                try:
                    self.client.head_object(Bucket=self.bucket, Key=cosObjectKey)
                    exists = True
                except CosServiceError as e:
                    if e.get_status_code() == 404:
                        exists = False
                    else:
                        print("Error happened, re_upload it.")
                if not exists:
                    print("File %s not exists in cos, upload it", srcKey)
                    pool.add_task(self.client.upload_file, self.bucket, cosObjectKey, srcKey)
        pool.wait_completion()
        result = pool.get_result()
        if not result['success_all']:
            print("Not all files upload success. you should retry")

    def download_file(self, key, dest_file):
        """
        使用高级接口断点续传，失败重试时不会下载已成功的分块(这里重试10次)

        :param key: 云端文件
        :param dest_file: 本地文件
        :return:
        """
        for i in range(0, 10):
            try:
                self.client.download_file(
                    Bucket=self.bucket,
                    Key=key,
                    DestFilePath=dest_file)
                break
            except CosClientError or CosServiceError as e:
                print(e)

    def list_current_dir(self, prefix, delimiter=''):
        """
        列出当前目录子节点，返回所有子节点信息
        :param prefix: 目录节点 'doc/'
        :param delimiter: 如果 delimiter 设置为 "/"，则需要在程序里递归处理子目录
        :return:
        """
        file_info = []
        sub_dirs = []
        marker = ""
        count = 1
        while True:
            response = self.client.list_objects(self.bucket, prefix, delimiter, marker)
            count += 1

            if "CommonPrefixes" in response:
                common_prefixes = response.get("CommonPrefixes")
                sub_dirs.extend(common_prefixes)

            if "Contents" in response:
                contents = response.get("Contents")
                file_info.extend(contents)

            if "NextMarker" in response.keys():
                marker = response["NextMarker"]
            else:
                break
        sorted(file_info, key=lambda info: info["Key"])
        return file_info

    def download_files(self, local_dir, file_info):
        """
        下载文件到本地目录，如果本地目录已经有同名文件则会被覆盖；
        如果目录结构不存在，则会创建和对象存储一样的目录结构
        :param local_dir: 目标目录
        :param file_info: 文件列表
        :return:
        """
        pool = SimpleThreadPool()
        for file in file_info:
            # 文件下载 获取文件到本地
            file_cos_key = file["Key"]
            localName = os.path.join(local_dir, file_cos_key)

            # 如果本地目录结构不存在，递归创建
            if not os.path.exists(os.path.dirname(localName)):
                os.makedirs(os.path.dirname(localName))

            # skip dir, no need to download it
            if str(localName).endswith("/"):
                continue

            # 实际下载文件
            # 使用线程池方式
            pool.add_task(self.client.download_file, self.bucket, file_cos_key, localName)
        pool.wait_completion()
        return None

    def download_dir_from_cos(self, local_dir, prefix):
        """
        功能封装，下载对象存储上面的一个目录到本地磁盘
        :param local_dir: 目标目录
        :param prefix: 云端目录
        :return:
        """
        file_info = []
        try:
            file_info = self.list_current_dir(prefix)

        except CosServiceError as e:
            print(e.get_origin_msg())
            print(e.get_digest_msg())
            print(e.get_status_code())
            print(e.get_error_code())
            print(e.get_error_msg())
            print(e.get_resource_location())
            print(e.get_trace_id())
            print(e.get_request_id())

        self.download_files(local_dir, file_info)
        return None

    def list_objects_page(self, prefix, marker='', max_keys=10):
        """
        分页列举桶内对象，每个分页10个对象
        :param prefix: 默认为空，对对象的对象键进行筛选，匹配 prefix 为前缀的对象
        :param marker: 默认以 UTF-8 二进制顺序列出条目，标记返回对象的 list 的起点位置
        :param max_keys: 最多返回的对象数量，默认为最大的1000
        :return:
        """
        while True:
            response = self.client.list_objects(
                Bucket=self.bucket, Prefix=prefix, Marker=marker, MaxKeys=max_keys)
            if 'Contents' in response:
                for content in response['Contents']:
                    print(content['Key'])

            if response['IsTruncated'] == 'false':
                break
            marker = response["NextMarker"]
        return marker

    def list_objects_dir(self, prefix, delimiter=''):
        file_info = []
        sub_dirs = []
        marker = ""
        count = 1
        while True:
            response = self.client.list_objects(self.bucket, prefix, delimiter, marker)
            count += 1

            if "CommonPrefixes" in response:
                common_prefixes = response.get("CommonPrefixes")
                sub_dirs.extend(common_prefixes)

            if "Contents" in response:
                contents = response.get("Contents")
                file_info.extend(contents)

            if "NextMarker" in response.keys():
                marker = response["NextMarker"]
            else:
                break
        return sub_dirs, file_info

    def object_exists(self, key):
        """
        检查存储桶中是否存在某个对象。
        :param key:
        :return: True 表示对象存在，False 表示对象不存在。
        """
        return self.client.object_exists(self.bucket, key)

    def create_dir(self, cos_dir):
        cos_dir = self.key_rule(cos_dir)
        if cos_dir[-1] != '/':
            cos_dir = f'{cos_dir}/'
        self.client.put_object(Bucket=self.bucket, Key=cos_dir, Body=b'')


def main():
    try:
        client = cos_token_client()
        if client is None:
            raise Exception('client is None')
        cos = CosApi(client)
        # 上传对象
        # local_file = r"D:\file\img\1.1001.jpg"
        # cos.upload_file(local_file, 'doc/2.jpg')

        # 批量上传
        # upload_dir = r'D:\file\element'
        # cos.upload_folder(upload_dir, 'doc')

        # 下载对象
        # dest_file = r'D:\file\img\download_cos.ico'
        # cos.download_file('doc/bbb/m10.ico', dest_file)

        # 批量下载
        # cos.download_dir_from_cos(r'D:\file\img\cos', 'doc/')

        dirs, files = cos.list_objects_dir('doc/', '/')
        print(dirs)
        print(len(dirs))
        print(files)
        print(len(files))

        # cos.create_dir('BBE/zhaojianwei/from_MORE/')

        print('success')
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
