# -*- coding: utf-8 -*-#
# Name: items_count
# Description:  
# Date: 2019/10/17

import os
import sys


current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.DbConnect import DbService

# 实例化数据库类
dbservice = DbService()


keys = dbservice.redis_conn.keys('*')
print(len(keys))
count = 0
for key in keys:
    if key == "category_url_with_newegg" or key == 'items_url':
        pass
    else:
        num = dbservice.redis_conn.scard(key)
        count += num
        print(f"{key}:{num}")
print(f"总计已获得商品数量：{count}")


product_collections = dbservice.db.collection_names()
newegg_total_count = 0
for collection in product_collections:
    if collection in ['first_categories_url', 'second_categories_url', 'third_categories_url', 'fourth_categories_url',
                      'products_info']:
        pass
    else:
        every_category_count = dbservice.db[collection].find().count()
        print(f"品类:{collection},数据量:{every_category_count}")
        newegg_total_count += every_category_count

print("总计：",newegg_total_count)
