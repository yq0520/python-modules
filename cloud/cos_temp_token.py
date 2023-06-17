# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : cos_temp_token.py
# @Project : python-modules
# @Software: PyCharm
"""
pip install -U qcloud-python-sts
"""
import json
from sts.sts import Sts


class CosTempToken(object):
    def __init__(self):
        self.secret_id = '用户的 SecretId'
        self.secret_key = '用户的 SecretKey'
        self.region = '用户的 region'
        self.bucket = '存储桶'

    def get_credential_demo(self) -> dict:
        config = {
            # 请求URL，域名部分必须和domain保持一致
            # 使用外网域名时：https://sts.tencentcloudapi.com/
            # 使用内网域名时：https://sts.internal.tencentcloudapi.com/
            'url': 'https://sts.tencentcloudapi.com/',
            # 域名，非必须，默认为 sts.tencentcloudapi.com
            # 内网域名：sts.internal.tencentcloudapi.com
            'domain': 'sts.tencentcloudapi.com',

            # 临时密钥有效时长，单位是秒
            # 要申请的临时密钥最长有效时间，单位秒，默认 1800，最大可设置 7200
            'duration_seconds': 1800,

            'secret_id': self.secret_id,
            # 固定密钥
            'secret_key': self.secret_key,
            # 设置网络代理
            # 'proxy': {
            #     'http': 'xx',
            #     'https': 'xx'
            # },
            # 换成你的 bucket
            'bucket': self.bucket,
            # 换成 bucket 所在地区
            'region': self.region,
            # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
            # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
            'allow_prefix': ['BBE/zhaojianwei/', 'doc/'],
            # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
            'allow_actions': [
                # 简单上传
                'name/cos:PutObject',
                'name/cos:PostObject',
                # 分片上传
                'name/cos:InitiateMultipartUpload',
                'name/cos:ListMultipartUploads',
                'name/cos:ListParts',
                'name/cos:UploadPart',
                'name/cos:CompleteMultipartUpload',
                # 查询对象列表
                'name/cos:GetBucket'
            ],
            # 临时密钥生效条件，关于condition的详细设置规则和COS支持的condition类型可以参考 https://cloud.tencent.com/document/product/436/71306
            "condition": {
                # "ip_equal": {
                #     "qcs:ip": [
                #         "10.217.182.3/24",
                #         "111.21.33.72/24",
                #     ]
                # }
            }
        }

        try:
            sts = Sts(config)
            response = sts.get_credential()

            print('get data : ' + json.dumps(dict(response), indent=4))
            return dict(response).get('credentials')
        except Exception as e:
            print(e)


def main():
    ctt = CosTempToken()
    ctt.get_credential_demo()


if __name__ == '__main__':
    main()
