# -*- coding: utf-8 -*-#
# Name: EmailNotice
# Description:  
# Date: 2019/10/14
"""
邮件通知脚本
"""
import os
import sys
import time

current_path = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.split(current_path)[0]
sys.path.append(BASE_DIR)  #

from auxiliary.DbConnect import DbService

# 实例化数据库类
dbservice = DbService()

################################### 商品详情 ###################################

# 统计商品详情入库成功数
success_command = 'grep -o "商品详情信息入库成功" ' + BASE_DIR + '/log/syslog|wc -l'
with os.popen(success_command, "r") as p:
    success_detail_count = p.read().strip('\n')

# 统计商品详情入库失败数
fail_command = 'grep -o "商品详情信息入库失败" ' + BASE_DIR + '/log/syslog|wc -l'
with os.popen(fail_command, "r") as p:
    fail_detail_count = p.read().strip('\n')

# 统计未获取到商品详情信息数据条数
noget_detail = 'grep -o "未解析到商品详情信息,url:" ' + BASE_DIR + '/log/syslog|wc -l'
with os.popen(noget_detail, "r") as p:
    noget_detail_count = p.read().strip('\n')

# 统计解析商品详情信息出错的数据条数
noparse_detail = 'grep -o "商品详情信息解析出错,url:" ' + BASE_DIR + '/log/syslog|wc -l'
with os.popen(noparse_detail, "r") as p:
    noparse_detail_count = p.read().strip('\n')

# 已入库总数
success_count = dbservice.db['products_info'].find().count()

# newegg自营类产品
product_collections = dbservice.db.collection_names()
newegg_total_count = 0
for collection in product_collections:
    if collection in ['first_categories_url', 'second_categories_url', 'third_categories_url', 'fourth_categories_url',
                      'products_info']:
        pass
    else:
        every_category_count = dbservice.db[collection].find().count()
        newegg_total_count += every_category_count

####################################### 邮件发送 ######################################
email_content = BASE_DIR + '/email.txt'
with open(email_content, 'w', encoding='utf-8') as f:
    # 商品详情信息
    f.write('今日截止到当前时间 {} 商品详情数据入库成功数：{} 条\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                     success_detail_count))
    f.write('今日截止到当前时间 {} 商品详情数据入库失败数：{} 条\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                     fail_detail_count))
    f.write('今日截止到当前时间 {} 未解析到商品详情数据数：{} 条\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                     noget_detail_count))
    f.write('今日截止到当前时间 {} 商品详情信息解析出错数：{} 条\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                     noparse_detail_count))
    f.write('截止到当前时间 {} Newegg 数据总入库：{} 条\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                    str(success_count)))

    f.write('截止到当前时间 {} Newegg 抓取数据量整体进度完成：{:.2%}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                          (success_count / 1872509)))
    f.write('截止到当前时间 {} Newegg 自营类产品数据已抓取总数：{}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                       str(newegg_total_count)))
