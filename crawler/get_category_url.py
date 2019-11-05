# -*- coding: utf-8 -*-#
# Name: get_category_url
# Description:  
# Date: 2019/10/10

"""
获取网站的分类信息
"""
import os
import sys
from lxml import etree

current_path = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_path)[0]
sys.path.append(rootPath)

from api.ApiRequest import ApiRequest
from auxiliary.DbConnect import DbService
from auxiliary.LogRecord import Logger

from settings import BASE_URL

# 实例化数据库类
dbservice = DbService()
# 实例化日志类
logger = Logger().logger


class GetCategory(ApiRequest):
    def __init__(self):
        super().__init__()

    def get_first_categories_url(self):
        """
        :return: 返回home页面12个大分类的URL
        """
        response = self.answer_the_url(BASE_URL)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            li_element = html.xpath('//ul[@class="main-nav-categories page-section-gray"]/li')
            if li_element:
                for li in li_element:
                    category_name = li.xpath('./a/@title')[0]
                    category_url = li.xpath('./a/@href')[0]
                    insert_data = {
                        "category_name": category_name,
                        "category_link": category_url
                    }
                    dbservice.db['first_categories_url'].insert_one(insert_data)
            else:
                pass
        else:
            logger.info("请求{}失败，未获取到信息".format(BASE_URL))

    def get_second_categories_url(self, first_category_url):
        """
        :param first_category_url: 传入获取到的第一级品类URL
        :return: 返回下一级的品类URL
        """
        response = self.answer_the_url(first_category_url)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            dl_element = html.xpath('//div[@class="left-nav"]/dl')
            if dl_element:
                for dl in dl_element:
                    li_element = dl.xpath('./dd/ul[@class="filter-box-list"]/li')
                    if li_element:
                        for li in li_element:
                            category_name = li.xpath('./a/@title')[0]
                            category_url = li.xpath('./a/@href')[0]
                            if category_url.startswith("https") or category_url.startswith('http'):
                                category_link = category_url
                            else:
                                category_link = "https:" + category_url
                            insert_data = {
                                "category_name": category_name,
                                "category_link": category_link
                            }
                            print(insert_data)
                            dbservice.db['second_categories_url'].insert_one(insert_data)
                    else:
                        pass
            else:
                pass
        else:
            logger.info("请求{}失败，未获取到信息".format(first_category_url))

    def get_third_categories_url(self, second_category_url):
        """
        :param second_category_url: 传入上一级的URL
        :return: 获取下一级的URL
        """
        response = self.answer_the_url(second_category_url)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            dl_element = html.xpath('//div[@class="left-nav"]/dl[@class="filter-box is-category is-active"]')
            if dl_element:
                for dl in dl_element:
                    li_element = dl.xpath('./dd/ul[@class="filter-box-list"]/li')
                    if li_element:
                        for li in li_element:
                            category_name = li.xpath('./a/@title')[0]
                            category_url = li.xpath('./a/@href')[0]
                            if category_url.startswith("https") or category_url.startswith('http'):
                                category_link = category_url
                            else:
                                category_link = "https:" + category_url
                            insert_data = {
                                "category_name": category_name,
                                "category_link": category_link
                            }
                            print(insert_data)
                            dbservice.db['third_categories_url'].insert_one(insert_data)
                    else:
                        pass
            else:
                pass
        else:
            logger.info("请求{}失败，未获取到信息".format(second_category_url))

    def get_fourth_categories_url(self, third_category_url):
        """
        :param third_category_url: 传入上一级url
        :return: 获取下一级URL
        """
        response = self.answer_the_url(third_category_url)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            dl_element = html.xpath('//div[@class="left-nav"]/dl[@class="filter-box is-category is-active"]')
            if dl_element:
                for dl in dl_element:
                    li_element = dl.xpath('./dd[@class="filter-box-body"]/ul[@class="filter-box-list"]/li')
                    if li_element:
                        for li in li_element:
                            category_name = li.xpath('./a/@title')
                            if category_name:
                                category_name = category_name[0]
                            else:
                                text_name = li.xpath('./a/text')
                                if text_name:
                                    category_name = text_name[0].strip('\n')
                                else:
                                    # 拿不到category_name则跳出本次循环
                                    continue
                            category_url = li.xpath('./a/@href')[0]
                            if category_url.startswith("https") or category_url.startswith('http'):
                                category_link = category_url
                            else:
                                category_link = "https:" + category_url
                            insert_data = {
                                "category_name": category_name,
                                "category_link": category_link
                            }
                            print(insert_data)
                            dbservice.db['fourth_categories_url'].insert_one(insert_data)
                    else:
                        pass
            else:
                pass
        else:
            logger.info("请求{}失败，未获取到信息".format(third_category_url))


if __name__ == '__main__':
    datas = dbservice.db['third_categories_url'].find()
    for data in datas:
        third_category_url = data['category_link']
        print(third_category_url)
        GetCategory().get_fourth_categories_url(third_category_url)
