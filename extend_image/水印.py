# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) Zhao
# Zhao-Jian-Wei, 836875692@qq.com
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def watermarkWeb(image_path, text, out_image, font_path=r'C:\Windows\Fonts\simkai.ttf'):
    """
    :param image_path: 原始图片路径
    :param text: 水印内容
    :param out_image 输出
    :param font_path: 字体路径
    windows 字体库  r'C:\Windows\Fonts\simkai.ttf'
    /usr/share/fonts/dejavu-lgc/DejaVuLGCSansCondensed-Bold.ttf  Linux
    :return:
    """
    # 打开原始图片 获取原始图片尺寸
    originalImg = Image.open(image_path)
    originalW, originalH = originalImg.size
    # 水印图片背景  mode类型为‘RGBA’ color 为none 为透明背景
    waterImageW = int(originalW * 1.5)
    waterImageH = int(originalH * 1.5)
    waterImagebackground = Image.new("RGBA", (waterImageW, waterImageH))
    waterImage = ImageDraw.Draw(waterImagebackground)  # 画出来
    fontsize = sizeScale(originalW)  # 水印字体大小
    waterfont = ImageFont.truetype(font_path, fontsize)  # 水印字体
    textW, textH = waterfont.getsize(text)
    waterImage.text([(waterImageW - textW) / 2, (waterImageH - textH) / 2], text, (255, 0, 0, 255), font=waterfont)  # 设置文字位置/内容/颜色/字体
    textRotate = waterImagebackground.rotate(30)  # 倾斜角度
    textRotate.thumbnail((originalW, originalH))  # 压缩到原图比例
    originalImg.paste(textRotate, None, mask=textRotate)  # 添加到原图上
    originalImg.save(out_image)


def sizeScale(imagew):
    """
    尺寸比例尺
    :param imagew: 原始图片宽度
    :return: 水印 字体 size
    """
    if imagew < 400:
        fontSize = 32
    elif imagew < 600:
        fontSize = 48
    elif imagew < 800:
        fontSize = 64
    elif imagew < 1000:
        fontSize = 80
    elif imagew < 1200:
        fontSize = 100
    elif imagew < 1400:
        fontSize = 128
    elif imagew < 1800:
        fontSize = 156
    elif imagew < 2200:
        fontSize = 192
    elif imagew < 2600:
        fontSize = 256
    elif imagew < 3100:
        fontSize = 300
    else:
        fontSize = 400
    return fontSize


def main():
    watermarkWeb('001.jpg', '佑仟百天照', '001水印.jpg')


if __name__ == '__main__':
    main()














