# -*- coding: utf-8 -*-#
# Name: get_item_detail
# Description:  
# Date: 2019/10/11
"""
获取商品详情信息
产品ID：product_id
所属品类：product_subcategory_id，product_subcategory_name
品牌：只需要品牌名
标题：product_title
描述：ul class=itemColumn【短描】 + overview 【长描】
产品父子关系及属性：properties
图片：div class=objImages
库存：product_instock（没有具体数量，有库存为1）
价格：product_sale_price
运费：product_default_shipping_cost
销量：没有
卖家评级：没有
上架时间：没有

"""
import datetime
import os
import sys
from lxml import etree
import re

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


class GetItemDetail(ApiRequest):

    def __init__(self):
        super().__init__()

    def __parse_item_info(self, resp):
        """

        :param resp: 页面相应内容
        :return: 返回product info
        """
        product_info_dict = dict()
        html = resp.text
        html_element = etree.HTML(html)
        # product info
        product_info_text = re.search(r'utag_data =(.+)(var description =)', html, re.DOTALL)
        if product_info_text:
            product_info_str = product_info_text.group(1).strip('\n')
            # 产品ID
            product_id_str = re.search(r'product_id:(.+)?', product_info_str)
            if product_id_str:
                product_id = product_id_str.group(1).strip('[,|,]').strip("'")
            else:
                product_id = ''
            # 页面上显示的商品ID
            product_web_id_str = re.search(r'product_web_id:(.+)?', product_info_str)
            if product_web_id_str:
                product_web_id = product_web_id_str.group(1).strip('[,|,]').strip("'")
            else:
                product_web_id = ''
            product_info_dict['product_web_id'] = product_web_id
            product_info_dict['product_id'] = product_id if product_id else product_web_id
            # category,sub_category name
            product_category_name_str = re.search(r"product_category_name:(.+)?", product_info_str)  # 父类
            product_subcategory_name_str = re.search(r"product_subcategory_name:(.+)?", product_info_str)  # 子类
            if product_subcategory_name_str:
                product_subcategory_name = product_subcategory_name_str.group(1).strip('[,|,]').strip("'").replace(
                    'amp;', '')
            else:
                product_subcategory_name = ''
            if product_category_name_str:
                product_category_name = product_category_name_str.group(1).strip('[,|,]').strip("'").replace('amp;', '')
            else:
                product_category_name = ''
            # category,sub_category id
            product_category_id_str = re.search(r"product_category_id:(.+)?", product_info_str)
            product_subcategory_id_str = re.search(r"product_subcategory_id:(.+)?", product_info_str)
            if product_subcategory_id_str:
                product_subcategory_id = product_subcategory_id_str.group(1).strip('[,|,]').strip("'")
            else:
                product_subcategory_id = ''
            if product_category_id_str:
                product_category_id = product_category_id_str.group(1).strip('[,|,]').strip("'")
            else:
                product_category_id = ''
            # 分类信息
            product_info_dict['product_category_info'] = {
                "category_id": product_category_id,
                "category_name": product_category_name,
                "subcategory_id": product_subcategory_id,
                "subcategory_name": product_subcategory_name
            }
            # 品牌
            brand_str = re.search(r"product_manufacture:(.+)?", product_info_str)
            if brand_str:
                brand = brand_str.group(1).strip('[,|,]').strip("'")
            else:
                brand = ''
            product_info_dict['brand'] = brand
            # 标题
            title_str = re.search(r"product_title:(.+)?", product_info_str)
            if title_str:
                title = title_str.group(1).strip('[,|,]').strip("'")
            else:
                title_xpath = html_element.xpath('//span[@id="grpDescrip_"]/text()')
                if title_xpath:
                    title = title_xpath[0].strip('\n').strip()
                else:
                    title = ''
            product_info_dict['title'] = title
            # 库存（没有具体数量，有库存为1）
            product_instock_str = re.search(r"product_instock:(.+)?", product_info_str)
            if product_instock_str:
                instock = product_instock_str.group(1).strip('[,|,]').strip("'")
            else:
                instock = '0'  # 无库存
            product_info_dict['instock'] = instock
            # 价格：product_sale_price
            product_sale_price_str = re.search(r"product_sale_price:(.+)?", product_info_str)
            if product_sale_price_str:
                product_sale_price = product_sale_price_str.group(1).strip('[,|,]').strip("'")
            else:
                product_sale_price = ''
            product_info_dict['sale_price'] = product_sale_price
            # 默认运费
            product_shipping_cost_str = re.search(r"product_default_shipping_cost:(.+)?", product_info_str)
            if product_shipping_cost_str:
                product_default_shipping_cost = product_shipping_cost_str.group(1).strip('[,|,]').strip("'")
            else:
                product_default_shipping_cost = ''
            product_info_dict['default_shipping_cost'] = product_default_shipping_cost
            # product 属性信息
            product_properties_text = re.search(r"var ProductProperty =(.+?)</script>", html, re.DOTALL)
            if product_properties_text:
                product_properties_str = product_properties_text.group(1).strip().strip('\n')
                # properties
                properties_str = re.search(r"properties:(.+)?", product_properties_str)
                if properties_str:
                    product_properties = properties_str.group(1).strip(',').strip()
                else:
                    product_properties = ''
                # availableMap
                availableMap_str = re.search(r"availableMap:(.+)?", product_properties_str)
                if availableMap_str:
                    product_availableMap = availableMap_str.group(1).strip(',').strip()
                else:
                    product_availableMap = ''
                # selectedProperties
                selectedProperties_str = re.search(r"selectedProperties:(.+)?", product_properties_str)
                if selectedProperties_str:
                    product_selectedProperties = selectedProperties_str.group(1).strip()
                else:
                    product_selectedProperties = ''
                product_info_dict['ProductProperty'] = {
                    "properties": product_properties,
                    "availableMap": product_availableMap,
                    "selectedProperties": product_selectedProperties
                }
            else:
                product_info_dict['ProductProperty'] = ''
            # description 描述信息
            short_description_li_element = html_element.xpath('//div[@class="grpBullet"]/ul[@class="itemColumn"]/li')
            short_description = []
            if short_description_li_element:
                for li in short_description_li_element:
                    description_text = li.xpath('./text()')[0].strip().strip('\n').strip('\r')
                    short_description.append(description_text)
            else:
                short_description = ''
            # 长文字描述
            long_description = []
            long_description_element = html_element.xpath('//div[@id="arimemodetail"]/*')
            if long_description_element:
                for long in long_description_element:
                    long_description_text = long.xpath('.')[0].xpath("string(.)")
                    description_info = long_description_text.replace("\r", "").replace("\n", "").replace("\t",
                                                                                                         "").replace(
                        "\xa0", "").strip()
                    if len(description_info) != 0:
                        long_description.append(description_info)
            else:
                long_description = ''
            product_info_dict['description'] = {
                "short_description": short_description,
                "long_description": long_description
            }
            # 主图
            primary_image_info = html_element.xpath('//div[@class="objImages"]//span[@class="mainSlide"]/@imgzoompic')
            if primary_image_info:
                primary_image = "https:" + primary_image_info[0]
            else:
                img_src = html_element.xpath('//div[@class="objImages"]//span[@class="mainSlide"]/img/@src')
                if img_src:
                    primary_image = "https:" + img_src[0]
                else:
                    primary_image = ''
            # 从图
            secondary_image_list = []
            secondary_image_li_element = html_element.xpath('//ul[@class="navThumbs"]/li')
            if secondary_image_li_element:
                for secondary_image_li in secondary_image_li_element:
                    img = secondary_image_li.xpath('./a/img/@src')
                    if img:
                        secondary_image_list.append(("https:" + img[0]))
                    else:
                        image_text_list = secondary_image_li.xpath('./a/@onfocus')
                        if image_text_list:
                            url_re = re.search(r"Biz.Product.DetailPage.swapProductImageWithLoadding2011\((.+)?",
                                               image_text_list[0])
                            if url_re:
                                url = url_re.group(1).split(',')[0]
                                secondary_image_list.append(("https:" + url.strip()))
                            else:
                                secondary_image_list.append('')
                        else:
                            secondary_image_list.append('')
            else:
                secondary_image_list = ''
            # 商品图片
            product_info_dict['product_image'] = {
                "primary_image": primary_image,
                "secondary_image_list": secondary_image_list
            }
            # Specifications
            sectionTitle_ = html_element.xpath('//div[@id="detailSpecContent"]/h2')
            if sectionTitle_:
                sectionTitle = sectionTitle_[0].xpath("string(.)").strip()
            else:
                sectionTitle = ''
            spec_fieldset_elements = html_element.xpath('//div[@id="Specs"]/fieldset')
            if spec_fieldset_elements:
                section_info = []
                for spec_fieldset in spec_fieldset_elements:
                    spec_title = spec_fieldset.xpath('./h3[@class="specTitle"]/text()')[0]
                    dl_element = spec_fieldset.xpath('./dl')
                    spec_info = []
                    for dl in dl_element:
                        spec_name = dl.xpath('./dt')[0].xpath("string(.)").strip().replace('.',"_")
                        spec_value = dl.xpath('./dd/text()')
                        spec_info.append({str(spec_name): str(spec_value)})
                    section_info.append({
                        "specTitle": spec_title,
                        "spec": spec_info
                    })
                Specifications = {
                    "sectionTitle": sectionTitle,
                    "sectionSpecs": section_info
                }
            else:
                Specifications = ''
            product_info_dict['Specifications'] = Specifications
            # item tab name 所属大类
            product_page_tab_str = re.search(r'page_tab_name:(.+)?', product_info_str)
            if product_page_tab_str:
                product_page_tab_name = product_page_tab_str.group(1).strip('[,|,]').strip("'").replace('amp;', '')
            else:
                product_page_tab_name = ''
            product_info_dict['page_tab_name'] = product_page_tab_name
            # site region
            product_site_region_str = re.search(r'site_region:(.+)?', product_info_str)
            if product_site_region_str:
                product_site_region = product_site_region_str.group(1).strip('[,|,]').strip("'")
            else:
                product_site_region = ''
            product_info_dict['site_region'] = product_site_region
            # site_currency
            product_site_currency_str = re.search(r'site_currency:(.+)?', product_info_str)
            if product_site_currency_str:
                product_site_currency = product_site_currency_str.group(1).strip('[,|,]').strip("'")
            else:
                product_site_currency = ''
            product_info_dict['site_currency'] = product_site_currency
            # product_model
            product_model_str = re.search(r'product_model:(.+)?', product_info_str)
            if product_model_str:
                product_model = product_model_str.group(1).strip('[,|,]').strip("'")
            else:
                product_model = ''
            product_info_dict['product_model'] = product_model
            # product_group_id
            product_group_id_str = re.search(r'product_group_id:(.+)?', product_info_str)
            if product_group_id_str:
                product_group_id = product_group_id_str.group(1).strip('[,|,]').strip("'")
            else:
                product_group_id = ''
            product_info_dict['product_group_id'] = product_group_id
        else:
            product_info_dict = ''
        return product_info_dict

    def get_item_detail(self, item_url):
        response = self.answer_the_url(item_url)
        try:
            product_info_dict = self.__parse_item_info(response)
            if product_info_dict:
                # 创建时间
                create_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                product_info_dict['create_time'] = create_time
                # product_url
                product_info_dict['product_url'] = item_url
                # 对应的大品类
                collection = product_info_dict['page_tab_name'] if product_info_dict[
                    'page_tab_name'] else 'products_info'
                try:
                    # 入库 先去重
                    # print(product_info_dict)
                    dbservice.db[collection].find_one_and_delete({"product_id": product_info_dict["product_id"]})
                    dbservice.db[collection].insert_one(product_info_dict)
                    logger.info("商品详情信息入库成功,商品id:{}".format(product_info_dict['product_id']))
                except Exception as e:
                    logger.error("商品详情信息入库失败,商品id:{},错误原因:{}".format(product_info_dict['product_id'], str(e)))
                    # 入库失败的重新加入到对应的品类集合中去
                    dbservice.redis_conn.sadd(str(collection), item_url)
            else:
                logger.info("未解析到商品详情信息,url:{}".format(item_url))
        except Exception as e:
            logger.error("商品详情信息解析出错,url:{},错误原因:{}".format(item_url, str(e)))
            # 解析商品详情出错的重新加入到队列中，后续处理
            dbservice.redis_conn.sadd('parse_error_url', item_url)
