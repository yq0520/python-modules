# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) Zhao
# Zhao-Jian-Wei, 836875692@qq.com
import os
import time

import cv2
import numpy as np
from PIL import Image


def get_outfile(infile, outfile):
    if outfile:
        return outfile
    name, suffix = os.path.splitext(infile)
    outfile = '{}-out{}'.format(name, suffix)
    return outfile


def cut_image(file):
    """
    剪裁图片
    右上角为 原点
    img.crop((x坐标起点，y坐标起点，宽度，高度))
    :param file:
    :param outfile:
    :return:
    """
    img = Image.open(file)
    region_left = img.crop((0, 0, img.width * 2 / 3, img.height))
    region_left.save('left.jpg')

    region = img.crop((img.width / 2, 0, img.width, img.height))
    region.save('right.jpg')


def splicing(img_left, img_right):
    # img1gray=cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    # img2gray=cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    surf = cv2.SIFT_create()
    kp_left, desc_left = surf.detectAndCompute(img_left, None)
    kp_right, desc_right = surf.detectAndCompute(img_right, None)

    bf = cv2.BFMatcher()

    matchers = bf.knnMatch(desc_left, desc_right, k=2)

    verify_matchers = []
    for m1, m2 in matchers:
        if m1.distance < 0.8 * m2.distance:
            verify_matchers.append(m1)

    if len(verify_matchers) > 10:
        img_left_pts, img_right_pts = [], []
        for m in verify_matchers:
            img_left_pts.append(kp_left[m.queryIdx].pt)
            img_right_pts.append(kp_right[m.queryIdx].pt)

        img_left_pts = np.float32(img_left_pts).reshape(-1, 1, 2)
        img_right_pts = np.float32(img_right_pts).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(img_left_pts, img_right_pts, cv2.RANSAC, 5.0)
        return H

    else:
        print("not enough matches!")


def stitch_image():
    start_time = time.time()
    img_left = cv2.imread("left.jpg")  # query
    img_right = cv2.imread("right.jpg")  # train
    H = splicing(img_left, img_right)
    h_left, w_left = img_left.shape[:2]
    h_right, w_right = img_right.shape[:2]
    img_left_dims = np.float32([[0, 0], [0, h_left], [h_left, w_left], [w_left, 0]]).reshape(-1, 1, 2)
    img_right_dims = np.float32([[0, 0], [0, h_right], [h_right, w_right], [w_right, 0]]).reshape(-1, 1, 2)

    img_left_transform = cv2.perspectiveTransform(img_left_dims, H)
    result_dims = np.concatenate((img_right_dims, img_left_transform), axis=0)
    [x_min, y_min] = np.int32(result_dims.min(axis=0).ravel() - 0.5)
    [x_max, y_max] = np.int32(result_dims.max(axis=0).ravel() + 0.5)
    transform_dist = [-x_min, y_min]

    transform_array = np.array([
        [1, 0, transform_dist[0]],
        [0, 1, transform_dist[1]],
        [0, 0, 1],
    ])

    out_w = x_max - x_min
    out_h = y_max - y_min
    result_img = cv2.warpPerspective(img_left, transform_array.dot(H), (out_w, out_h))
    result_img[transform_dist[1]:transform_dist[1] + h_right, transform_dist[0]:transform_dist[0] + w_right] = img_right
    cv2.imwrite('out.jpg', result_img)


def join_horizontal(img_left_name, img_right_name):
    """
    水平拼接图片
    :param img_left_name: 左半边图片路径
    :param img_right_name: 右半边图片路径
    :return:
    """
    img_left = cv2.imread(img_left_name)
    img_right = cv2.imread(img_right_name)

    # 检测必要的关键点，并提取特征
    surf = cv2.SIFT_create()
    left_kp, left_desc = surf.detectAndCompute(img_left, None)
    right_kp, right_desc = surf.detectAndCompute(img_right, None)

    # FLANN匹配器接收两个参数：indexParams对象和searchParams对象
    # 这些参数以Python中字典（和C++中结构体）的形式传递
    # trees=5 的核密度树索引算法，FLANN可以并行处理此算法。
    indexParams = dict(algorithm=1, trees=5)
    # 每个 tree 执行50次检查或者遍历，检查次数越多，可以提供的精度也越高，但是，计算成本也就更高。
    searchParams = dict(checks=50)

    flann = cv2.FlannBasedMatcher(indexParams, searchParams)
    match = flann.knnMatch(left_desc, right_desc, k=2)

    # 检测特征并计算SIFT描述符 组建一个通过了劳氏比率检验的匹配列表
    good = []
    for i, (m, n) in enumerate(match):
        if m.distance < 0.75 * n.distance:
            good.append(m)

    # 从技术上讲，我们最少可以用4个匹配项来计算单应性。
    # 但是，如果这4个匹配项中的任意一个有缺陷，都将会破坏结果的准确性。
    # 实际中最少用到10个匹配项。对于额外的匹配项，单应性查找算法可以丢弃一些异常值，
    # 以便产生与大部分匹配项子集紧密匹配的结果。因此，我们继续检查是否至少有10个好的匹配项

    if len(good) > 10:
        # 查找匹配的关键点的二维坐标，并把这些坐标放入浮点坐标对的两个列表中。
        # 一个列表包含查询图像中的关键点坐标，另一个列表包含场景中匹配的关键点坐标
        src_pts = np.float32([left_kp[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        ano_pts = np.float32([right_kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # 寻找单应性
        M, mask = cv2.findHomography(src_pts, ano_pts, cv2.RANSAC, 5.0)
        # 投影转换
        warpImg = cv2.warpPerspective(img_right, np.linalg.inv(M), (img_left.shape[1] + img_right.shape[1], img_right.shape[0]))
        direct = warpImg.copy()

        direct[0:img_left.shape[0], 0:img_left.shape[1]] = img_left

        # 计算重叠部分
        rows, cols = img_left.shape[:2]
        # 开始重叠的最左端
        for col in range(0, cols):
            if img_left[:, col].any() and warpImg[:, col].any():
                left = col
                break
        # 重叠的最右一列
        for col in range(cols - 1, 0, -1):
            if img_left[:, col].any() and warpImg[:, col].any():
                right = col
                break
        # direct宽度 减去重叠的宽度
        width = img_left.shape[1] + img_right.shape[1] - (right - left + 1)
        region = direct[0:rows, 0:width]
        cv2.imwrite('region.png', region)
    else:
        print('匹配值不够')


def main():
    # cut_image('001.jpg')
    join_horizontal('left.jpg', 'right.jpg')


if __name__ == '__main__':
    main()
