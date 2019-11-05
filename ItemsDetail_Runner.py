# -*- coding: utf-8 -*-#
# Name: ItemsDetail_Runner
# Description:  
# Date: 2019/10/14
"""
获取商品详情启动文件
"""
import os
import random
import sys
import time
from multiprocessing.pool import Pool

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.DbConnect import DbService
from auxiliary.LogRecord import Logger
from crawler.get_item_detail import GetItemDetail

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


# 任务处理函数
def script_task(item_url):
    GetItemDetail().get_item_detail(item_url)


if __name__ == '__main__':
    keys = dbservice.redis_conn.keys('*')
    for key in keys:
        if key == "category_url_with_newegg" or key == 'items_url':
            continue
        else:
            # 优先爬取 newegg 自营
            while True:
                queue_length = dbservice.redis_conn.scard(key)
                if queue_length != 0:
                    po = Pool(2)
                    for i in range(2):
                        category_url = dbservice.redis_conn.spop(key)
                        if category_url:
                            po.apply_async(script_task, args=(category_url,))
                        else:
                            continue
                    time.sleep(random.random() * 2)
                    po.close()
                    po.join()
                else:
                    logger.info("{} 类下全部商品详情信息获取完成".format(str(key)))
                    break
    logger.info("Newegg 网站下全部的自营商品详情获取完成")
