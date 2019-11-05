# -*- coding: utf-8 -*-#
# Name: ItemsUrl_Runner
# Description:  
# Date: 2019/10/11
"""
获取商品URL处理函数
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
from crawler.get_item_url import GetItemUrl
from crawler.priority_to_get_newegg_items_url import GetItemUrlFilterNewegg

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


# 任务处理函数
def run_task(category_url):
    # 全部获取
    # GetItemUrl().get_all_page_item_url(category_url)
    # 优先获取newegg 自营
    GetItemUrlFilterNewegg().get_all_page_item_url(category_url)


if __name__ == '__main__':
    while True:
        # 优先获取 newegg 自营商品
        category_urls_length = dbservice.redis_conn.scard("category_url_with_newegg")
        if category_urls_length != 0:
            po = Pool(2)
            for i in range(2):
                category_url = dbservice.redis_conn.spop("category_url_with_newegg")
                if category_url:
                    po.apply_async(run_task, args=(category_url,))
                else:
                    continue
            time.sleep(random.random() * 2)
            po.close()
            po.join()
        else:
            logger.info("全部品类获取完成")
            break
    logger.info('任务执行完毕，全部商品item url获取完成')
