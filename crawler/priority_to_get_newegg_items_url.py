# -*- coding: utf-8 -*-#
# Name: priority_to_get_newegg_items_url
# Description:  
# Date: 2019/10/16
"""
优先获取 newegg 自营的商品
"""
import json
import os
import sys
import re
from lxml import etree
import time, random

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from auxiliary.DbConnect import DbService
from settings import INIT_COLLECTIONS
from api.ApiRequest import ApiRequest
from auxiliary.LogRecord import Logger

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger

"""
1、将数据库中所有的品类URL提取出来,改为加入筛选条件为newegg后的URL
"""


class GetPid(ApiRequest):

    def __init__(self):
        super().__init__()

    def __get_p_id(self, url):
        response = self.answer_the_url(url)
        if response.status_code == 200:
            n_text = re.search(r'Biz\.SearchPanel2016\.NavigationListLimit\.Config={(.+)}', response.text)
            if n_text:
                n_number = re.search(r"N:(.+,)?", n_text.group(1))
                if n_number:
                    p_num = n_number.group(1).strip("'|,")
                    return p_num
                else:
                    return None
            else:
                return None
        else:
            return None

    def get_url_filter_newegg(self):
        for collection in INIT_COLLECTIONS:
            datas = dbservice.db[collection].find()
            for data in datas:
                category_link = data['category_link']
                if category_link.__contains__("Tid="):
                    tid = re.search(r'Tid=(.+)', category_link).group(1)
                    newegg_products_url = 'https://www.newegg.com/p/pl?N=100{}%208000&ActiveSearchResult=True'.format(
                        tid)
                elif category_link.__contains__("%208000"):
                    newegg_products_url = category_link
                elif category_link.__contains__('p/pl?'):
                    newegg_products_url = category_link + "%208000"
                else:
                    p_num = self.__get_p_id(category_link)
                    if p_num:
                        newegg_products_url = 'https://www.newegg.com/p/pl?N={}'.format(
                            p_num) + '%208000&ActiveSearchResult=True'
                    else:
                        continue
                # 加入到队列
                # print(newegg_products_url)
                dbservice.redis_conn.sadd("category_url_with_newegg", newegg_products_url)


# 获取带过滤条件为 newegg 自营后的品类URL
# GetPid().get_url_filter_newegg()


"""
2、获取每个带过滤条件后的品类下的page
"""


class GetItemUrlFilterNewegg(ApiRequest):

    def __init__(self):
        super().__init__()

    def __get_page(self, url):
        """
        :param category_url:
        :return: 获取该品类的页数
        """
        response = self.answer_the_url(url)
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
        elif str(category_url).__contains__('%208000&ActiveSearchResult=True'):
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
                        # 每个品类下的商品加入到每个品类下
                        category_name = html.xpath('//li[@class="is-current"]/text()')[0].strip().strip('\n').replace(" ",'_')
                        try:
                            # 加入到redis集合中，自动去除重复的数据
                            dbservice.redis_conn.sadd(category_name, item_url[0])
                            logger.info("商品URL：{}加入队列成功".format(str(item_url[0])))
                        except Exception as e:
                            logger.error("商品URL：{}加入队列失败,失败原因：{}".format(str(item_url[0]), str(e)))
                            # 出错重新加入到队列
                            dbservice.redis_conn.sadd(category_name, item_url[0])
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


"""
3、获取商品详情
调用获取商品详情接口
"""