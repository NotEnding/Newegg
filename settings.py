# -*- coding: utf-8 -*-#
# Name: settings
# Description:  
# Date: 2019/10/10

import os

# base dir
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 获取项目所在目录

# conf dir
CONF_DIR = os.path.join(BASE_DIR, "conf")  # 存储配置信息
if not os.path.exists(CONF_DIR):
    os.mkdir(CONF_DIR)

# log dir
LOG_DIR = os.path.join(BASE_DIR, "log")  # 日志存放目录
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)


# BASE_URL
BASE_URL = 'https://www.newegg.com/'

# init collections
INIT_COLLECTIONS = ['second_categories_url', 'third_categories_url', 'fourth_categories_url']


# 优先抓取newegg自营的
'https://www.newegg.com/All-in-One-Computers/SubCategory/ID-3309?Tid=167567'
'https://www.newegg.com/p/pl?N=100167567%208000&ActiveSearchResult=True'


'https://www.newegg.com/p/pl?N=100007583%20600545970%204802'
'https://www.newegg.com/p/pl?N=100007583%20600545970%204802%208000'
