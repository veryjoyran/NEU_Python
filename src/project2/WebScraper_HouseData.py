import re
import requests
from bs4 import BeautifulSoup
import os
import time
import random


class WebScraper_HouseData:
    def __init__(self, base_url, pages=5):
        """
        初始化爬虫类
        :param base_url: 要爬取的网站首页URL
        :param pages: 要爬取的页面数
        """
        self.base_url = base_url
        self.pages = pages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }

    def get_html(self, url):
        """
        获取网页HTML内容
        :param url: 要获取的网页URL
        :return: 网页HTML内容
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # 如果返回状态码不是200，抛出异常
            response.encoding = response.apparent_encoding  # 自动检测编码
            return response.text
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return None

    def parse_html(self, html):
        """
        获取页面中 class="shop_list shop_list_4" 的 div 中的指定元素数据
        :param html: 网页HTML内容
        :return: 返回经过筛选后的数据并按一一对应方式输出
        """
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'lxml')

        # 根据网页内容提取所需要的数据
        tel_shop_paragraphs = soup.find_all('p', class_='tel_shop')
        add_shop_paragraphs = soup.find_all('p', class_='add_shop')
        clearfix_paragraphs = soup.find_all('p', class_='clearfix label')
        price_right_dd = soup.find_all('dd', class_='price_right')

        # 提取每种元素的文本内容
        tel_numbers = [tel.get_text(strip=True) for tel in tel_shop_paragraphs]
        add_shops = [add.get_text(strip=True) for add in add_shop_paragraphs]
        clearfix_labels = [label.get_text(strip=True) for label in clearfix_paragraphs]
        prices = [price.get_text(strip=True) for price in price_right_dd]

        data = []

        # 使用 zip 将数据按索引配对，保证每个电话、地址、描述、价格对应输出
        for tel, addr, label, price in zip(tel_numbers, add_shops, clearfix_labels, prices):
            # 解析电话信息
            phone_info = self.parse_phone_info(tel)

            if phone_info:  # 只有当phone_info字典有数据时才进行输出
                print(f"房型: {phone_info.get('room_type', 'N/A')}, 面积: {phone_info.get('area', 'N/A')}, "
                      f"楼层: {phone_info.get('floor', 'N/A')}, 朝向: {phone_info.get('orientation', 'N/A')}, "
                      f"建造年份: {phone_info.get('build_year', 'N/A')}, 业主: {phone_info.get('owner_name', 'N/A')}, "
                      f"地址: {addr}, 描述: {label}, 价格: {price}")
                house_data = {
                    'room_type': phone_info.get('room_type', 'N/A'),
                    'area': phone_info.get('area', 'N/A'),
                    'floor': phone_info.get('floor', 'N/A'),
                    'orientation': phone_info.get('orientation', 'N/A'),
                    'build_year': phone_info.get('build_year', 'N/A'),
                    'owner_name': phone_info.get('owner_name', 'N/A'),
                    'address': addr,
                    'description': label,
                    'price': price
                }
                # print(house_data)
                data.append(house_data)
            else:
                print(f"电话信息解析失败: {tel}, 地址: {addr}, 描述: {label}, 价格: {price}")

        return data

    def parse_phone_info(self, tel):
        """
        解析电话部分的信息，包括房间配置、面积、楼层、朝向、建造年份和业主姓名
        :param tel: 电话信息字符串
        :return: 返回划分后的信息
        """
        # 使用split进行分割
        fields = tel.split('|')

        if len(fields) != 6:
            print(f"电话信息格式不匹配: {tel}")
            return None

        room_type = fields[0]  # 房间配置
        area = fields[1]  # 面积
        floor = fields[2]  # 楼层
        orientation = fields[3]  # 朝向
        build_year = fields[4]  # 建造年份
        owner_name = fields[5]  # 业主姓名

        # 返回字典格式的信息
        return {
            'room_type': room_type,
            'area': area,
            'floor': floor,
            'orientation': orientation,
            'build_year': build_year,
            'owner_name': owner_name
        }

    def save_data(self, data, filename):
        if not os.path.exists('output'):
            os.makedirs('output')
        with open(os.path.join('output', filename), 'w', encoding='utf-8') as file:
            for item in data:
                file.write(f"{item}\n")

    def scrape(self, url=None):
        # 如果没有传入url，则默认使用self.base_url
        if url is None:
            url = self.base_url

        all_data = []

        for page_num in range(1, self.pages + 1):
            full_url = f"{url}?page={page_num}"
            print(f"正在爬取: {full_url}")

            html = self.get_html(full_url)
            if html:
                page_data=self.parse_html(html)
                all_data.extend(page_data)

            # 防止频繁请求被封禁，设置随机的延时
            time.sleep(random.uniform(1, 3))

        return all_data

if __name__ == "__main__":
    # 示例使用
    scraper = WebScraper_HouseData(base_url="https://hf.esf.fang.com/", pages=1)
    data=scraper.scrape()  # 没有传入url时，默认使用base_url
    print()
    print(data)