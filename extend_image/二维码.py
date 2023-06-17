# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : 二维码.py
# @Project : python-modules
# @Software: PyCharm
"""
pip install qrcode
"""
from PIL import Image
import qrcode


def asd(content):
    """
    version ：QR code 的版次，可以设置 1 ～ 40 的版次。
    error_correction ：容错率，可选 7%、15%、25%、30%，参数如下 ：
    qrcode.constants.ERROR_CORRECT_L ：7%
    qrcode.constants.ERROR_CORRECT_M ：15%（预设）
    qrcode.constants.ERROR_CORRECT_Q ：25%
    qrcode.constants.ERROR_CORRECT_H ：30%
    box_size ：每个模块的像素个数。
    border ：边框区的厚度，预设是 4。
    image_factory ：图片格式，默认是 PIL。
    mask_pattern ：mask_pattern 参数是 0 ～ 7，如果省略会自行使用最适当的方法。
    """
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10,
                       border=4)
    qr.add_data(content)
    # 设置二维码颜色为蓝色，背景色为黄色
    img = qr.make_image(fill_color='blue', back_color="yellow")
    img.show()


def Create_Qrcode(content, logoPath='1.1001.jpg'):
    """
    :param content: 二维码内容
    :param logoPath: logo图片路径 展示在二维码中间
    :return:
    """
    try:
        path = "qr_code.png"
        # 最小尺寸 1 会生成 21 * 21 的二维码，version 每增加 1，生成的二维码就会添加 4 尺寸
        # version ：QR code 的版次，可以设置 1 ～ 40 的版次。
        # 参数 error_correction 指定二维码的容错系数，分别有以下4个系数：
        # ERROR_CORRECT_L: 7%的字码可被容错
        # ERROR_CORRECT_M: 15%的字码可被容错
        # ERROR_CORRECT_Q: 25%的字码可被容错
        # ERROR_CORRECT_H: 30%的字码可被容错
        # 参数 box_size 表示二维码里每个格子的像素大小
        # 参数 border 表示边框的格子厚度是多少（默认是4）
        qr = qrcode.QRCode(version=3, box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_H)

        # 添加数据
        qr.add_data(content)
        # 填充数据
        qr.make(fit=True)
        # 生成图片
        # fill_color 二维码颜色
        # back_color 背景颜色
        img = qr.make_image(fill_color="green", back_color="white")
        img = img.convert('RGBA')
        img.show()
        # 二维码中间添加logo图片
        # 设置 logo 大小和位置
        icon = Image.open(logoPath)
        icon = icon.convert('RGBA')
        w, h = img.size
        # logo 大小参数
        factor = 4
        size_w = int(w / factor)
        size_h = int(h / factor)
        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        # 重置logo尺寸
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)

        # 居中显示坐标
        w = int((w - icon_w) / 2)
        h = int((h - icon_h) / 2)
        # 粘贴到二维码指定位置
        # im：源图像或像素值（整数或元组）。
        # box：一个可选的4元组，用于指定要粘贴到的区域。
        # 如果使用2元组，则将其视为左上角。
        # 如果忽略或无，则源将粘贴到左上角。
        # 如果给定图像作为第二个参数，而没有第三个参数，则框默认为（0，0），第二个自变量被解释为掩码图像。
        # mask：可选的掩码图像。
        img.paste(icon, (w, h), mask=None)
        img.show()
        # 保存
        # quality -- 图片保存质量 默认为 100 设置该参数可以对目标文件字节数进行调整
        img.save(path, quality=100)
        return {"status": 0, "result": 1, "msg": "二维码创建成功", "data": {"path": path}}
    except Exception as e:
        return {"status": 0, "result": 0, "msg": e.args, "data": {"path": ""}}


if __name__ == "__main__":
    asd('哈哈哈哈')
