# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) Zhao
# Zhao-Jian-Wei, 836875692@qq.com

import base64


# 图片转base64
def img_to_base64(img_path):
    with open(img_path, 'rb') as f:
        image = f.read()
    image_base64 = str(base64.b64encode(image), encoding='utf-8')
    return image_base64
