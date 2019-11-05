# -*- coding: utf-8 -*-#
# Name: Category_init
# Description:  
# Date: 2019/10/11
"""
将mongodb数据库中的分类数据同步到redis队列中
"""
import os
import sys

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.DbConnect import DbService
from auxiliary.LogRecord import Logger

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger

from settings import INIT_COLLECTIONS

if __name__ == '__main__':
    for collection in INIT_COLLECTIONS:
        print(f"正在查询collection:{collection}")
        logger.info(f"正在查询collection:{collection}")
        datas = dbservice.db[collection].find()
        for data in datas:
            category_link = data['category_link']
            dbservice.redis_conn.sadd("category_urls", category_link)
        print(f"当前collection:{collection} 初始化完毕")
        logger.info(f"当前collection:{collection} 初始化完毕")
    logger.info(f"全部collection初始化完毕")
    print(f"全部collection初始化完毕")
