# Copyright (c) 836875692@qq.com
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from rembg import remove
import cv2
from PIL import Image


def svg_to_png(in_path, out_path, fmt="PNG", dpi=72, bg=0xffffff, scale=None, size=None, scale_x=1, size_x=None, scale_y=1, size_y=None):
    """
    svg 转 png
    :param in_path:
    :param out_path:
    :param fmt:
    :param dpi:
    :param bg:
    :param scale:
    :param size:
    :param scale_x:
    :param size_x:
    :param scale_y:
    :param size_y:
    :return:
    """
    # Convert SVG to ReportLab drawing.
    drawing = svg2rlg(in_path)
    # Work out scale factors
    # Scale over-rides scale_x|y, ditto size
    scale_x = scale if scale else scale_x
    scale_y = scale if scale else scale_y
    size_x = size if size else size_x
    size_y = size if size else size_y
    # Size over-rides scale
    scaling_x = size_x / drawing.width if size_x else scale_x
    scaling_y = size_y / drawing.height if size_y else scale_y
    # Scale the drawing
    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    # Render ReportLab drawing as a PNG
    renderPM.drawToFile(drawing, out_path, fmt=fmt, dpi=dpi, bg=bg)


def remove_back(input_path, output_path):
    """
    移除背景
    :param input_path:
    :param output_path:
    :return:
    """
    with open(input_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            in_put = i.read()
            output = remove(in_put)
            o.write(output)


def grayscale_image(input_path, output_path):
    """
    灰度处理
    :param input_path:
    :param output_path:
    :return:
    """
    img = cv2.imread(input_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # gray_img此时还是二维矩阵表示,所以要实现array到image的转换
    gray = Image.fromarray(gray_img)
    # 将图片保存到当前路径下，参数为保存的文件名
    gray.save(output_path)


def main():
    in_folder = r'E:\file\image\png_back'
    out_back_folder = os.path.join(in_folder, 'png_gray')
    os.makedirs(out_back_folder, exist_ok=True)
    out_gray_folder = os.path.join(in_folder, 'png_gray_back')
    os.makedirs(out_gray_folder, exist_ok=True)
    for file in os.listdir(in_folder):
        print(file)
        name, suffix = os.path.splitext(file)
        if suffix == '.png':
            in_path = os.path.join(in_folder, file)
            out_back_gray_path = os.path.join(out_back_folder, f'{name}_gray.png')
            out_back_gray = os.path.join(out_gray_folder, f'{name}_gray.png')
            # svg_to_png(in_path, out_path, scale=2, dpi=72)
            # remove_back(out_path, out_back_path)
            # grayscale_image(in_path, out_back_gray_path)
            remove_back(out_back_gray_path, out_back_gray)


if __name__ == '__main__':
    # breakpoint()
    main()
