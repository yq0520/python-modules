# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) Zhao
# Zhao-Jian-Wei, 836875692@qq.com

# 图片对比

# pip install opencv-python

import datetime
from threading import Thread

import cv2
import numpy as np

MAX_FEATURES = 10000
GOOD_MATCH_PERCENT = 0.08


class MyThread(Thread):
    def __init__(self, func, args, name=''):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as ex:
            print(ex)
            return None


def ThreadFun(p):
    ak_aze = p[0]
    img = p[1]
    key_points1, descriptors1 = ak_aze.detectAndCompute(img, mask=None)
    return key_points1, descriptors1


def alignImages(im1, im2):
    im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    # ak_aze = cv2.ORB_create(MAX_FEATURES)
    ak_aze = cv2.AKAZE_create(descriptor_type=2, threshold=0.002, nOctaves=4, nOctaveLayers=4, diffusivity=3)
    # ak_aze = cv2.AKAZE_create()
    t1 = MyThread(ak_aze.detectAndCompute, (im1Gray, None,), "")
    t2 = MyThread(ak_aze.detectAndCompute, (im2Gray, None,), "")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    key_points1, descriptors1 = t1.get_result()
    key_points2, descriptors2 = t2.get_result()

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE)
    matches = list(matcher.match(descriptors1, descriptors2, None))

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)
    imMatches = cv2.drawMatches(im1, key_points1, im2, key_points2, matches, None)
    cv2.imwrite('matches1.jpg', imMatches)

    # Remove not so good matches 值越低 精度越高
    numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
    matches = matches[:numGoodMatches]

    imMatches = cv2.drawMatches(im1, key_points1, im2, key_points2, matches, None)
    cv2.imwrite('matches2.jpg', imMatches)
    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for num_I, match in enumerate(matches):
        points1[num_I, :] = key_points1[match.queryIdx].pt
        points2[num_I, :] = key_points2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    # Use homography
    height, width, channels = im2.shape
    color = im2[int(width / 2)][int(height / 2)]
    border_value = (int(color[0]), int(color[1]), int(color[2]))
    im1Reg = cv2.warpPerspective(im1, h, (width, height), borderValue=border_value)

    return im1Reg


start_time = datetime.datetime.now()
path_img = 'src.jpg'
path_empty = 'standard.jpg'
path_save = 'save.jpg'

image = cv2.imread(path_empty, cv2.IMREAD_COLOR)
back = cv2.imread(path_img, cv2.IMREAD_COLOR)

back_align = alignImages(back, image)

cv2.imwrite(path_save, back_align)
end_time = datetime.datetime.now()
str_msg = 'Done: '
