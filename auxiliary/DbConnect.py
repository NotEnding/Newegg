#! /usr/bin/python
# -*- coding: utf-8 -*-
# @Time  : 2019/6/12 下午7:31
import os
import sys
import pymongo
import redis
import yaml

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from settings import CONF_DIR


class DbService:

    def __init__(self):
        with open(CONF_DIR + '/conf.yaml', 'r') as f:
            config_dict = yaml.load(f, Loader=yaml.FullLoader)
        mongo_dict = config_dict["mongo"]
        redis_dict = config_dict["redis"]
        # mongo配置
        mongo_info = {
            'host': mongo_dict['host'],
            'port': mongo_dict['port'],
            'username': mongo_dict['username'],
            'password': mongo_dict['password'],
            'connect': False
        }
        self.client = pymongo.MongoClient(**mongo_info)  #
        self.db = self.client[mongo_dict['db']]  # 指定数据库
        # redis配置
        redis_config = {
            "host": redis_dict["host"],
            "port": redis_dict["port"],
            "password": redis_dict["password"],
            "db": redis_dict["db"],
            "decode_responses": True,
            "max_connections": 100,
            "encoding": 'utf-8',
        }
        # 创建redis连接池
        redis_pool = redis.ConnectionPool(**redis_config)
        self.redis_conn = redis.Redis(connection_pool=redis_pool)
