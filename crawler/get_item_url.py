# -*- coding: utf-8 -*-#
# Name: get_item_url
# Description:  
# Date: 2019/10/11

"""
获取商品的URL
"""
import os
import sys
from lxml import etree
import time
import random

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from api.ApiRequest import ApiRequest
from auxiliary.DbConnect import DbService
from auxiliary.LogRecord import Logger

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


class GetItemUrl(ApiRequest):

    def __init__(self):
        super().__init__()

    def __get_page(self, category_url):
        """
        :param category_url:
        :return: 获取该品类的页数
        """
        response = self.answer_the_url(category_url)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            # 获取page
            page_info = html.xpath(
                '//div[@class="list-tool-pagination"]/span[@class="list-tool-pagination-text"]/strong/text()')
            if page_info:
                page = page_info[0].split('/')[-1]
            else:
                page = ''
            return page
        else:
            return None

    def __judge_page(self, category_url, page):
        """
        :param category_url: request url
        :param page: 页数
        :return: 根据不同的URL，加入不同参数样式的page形式
        """
        if str(category_url).__contains__('SubCategory') and str(category_url).__contains__('Tid='):
            link = str(category_url).split('?')[0] + '/Page-' + str(page) + '?' + str(category_url).split('?')[-1]
        elif str(category_url).__contains__('SubCategory') and not str(category_url).__contains__('Tid='):
            link = str(category_url) + '/Page-' + str(page)
        elif str(category_url).__contains__('Submit='):
            link = str(category_url) + "&Page=" + str(page)
        else:
            link = str(category_url) + "&Page=" + str(page)
        return link

    def __get_single_page_item_url(self, category_url):
        """
        :param category_url:
        :return: 解析单个页面上的item URL
        """
        response = self.answer_the_url(category_url)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            div_element = html.xpath('//div[@class="items-view is-grid"]/div')
            if div_element:
                for div in div_element:
                    item_url = div.xpath('./div[@class="item-info"]/a[@class="item-title"]/@href')
                    if item_url:
                        try:
                            # 加入到redis集合中，自动去除重复的数据
                            dbservice.redis_conn.sadd('items_url', item_url[0])
                            logger.info("商品URL：{}加入队列成功".format(str(item_url[0])))
                        except Exception as e:
                            logger.error("商品URL：{}加入队列失败,失败原因：{}".format(str(item_url[0]), str(e)))
                            # 出错重新加入到队列
                            dbservice.redis_conn.sadd('items_url', item_url[0])
                    else:
                        logger.info("{}链接未获取到商品URL信息".format(category_url))
            else:
                logger.info("{}链接未获取到商品URL信息".format(category_url))
        else:
            logger.info("{} 请求失败".format(category_url))

    def get_all_page_item_url(self, category_url):
        """
        :param category_url: 解析全部页面下的商品URL
        :return:
        """
        page = self.__get_page(category_url)
        if page:
            for pg in range(1, int(page) + 1):
                # 不同的category URL 翻页参数不同
                link = self.__judge_page(category_url, str(pg))
                logger.info("开始请求 {},当前第{} 页".format(link, str(pg)))
                self.__get_single_page_item_url(link)
                # 单个获取完成后，延时
                time.sleep(random.random() * 2)
            logger.info("{} 全部页数获取完成，总计{} 页".format(category_url, str(page)))
        else:
            logger.info('{} 链接页面没有商品信息'.format(category_url))
