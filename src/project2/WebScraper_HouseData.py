import requests
from bs4 import BeautifulSoup
import os
import time
import random
from datetime import datetime


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

        # 查找 class 为 tel_shop 的 <p> 元素
        tel_shop_paragraphs = soup.find_all('p', class_='tel_shop')
        # 查找 class 为 add_shop 的 <p> 元素
        add_shop_paragraphs = soup.find_all('p', class_='add_shop')
        # 查找 class 为 clearfix label 的 <p> 元素
        clearfix_paragraphs = soup.find_all('p', class_='clearfix label')
        # 查找 class 为 price_right 的 <dd> 元素
        price_right_dd = soup.find_all('dd', class_='price_right')

        # 提取每种元素的文本内容
        tel_numbers = [tel.get_text(strip=True) for tel in tel_shop_paragraphs]
        add_shops = [add.get_text(strip=True) for add in add_shop_paragraphs]
        clearfix_labels = [label.get_text(strip=True) for label in clearfix_paragraphs]
        prices = [price.get_text(strip=True) for price in price_right_dd]

        # 使用 zip 将数据按索引配对，保证每个电话、地址、描述、价格对应输出
        for tel, addr, label, price in zip(tel_numbers, add_shops, clearfix_labels, prices):
            print(f"电话: {tel}, 地址: {addr}, 描述: {label}, 价格: {price}")

    def save_data(self, data, filename):
        """
        保存爬取的数据到文件
        :param data: 要保存的数据
        :param filename: 文件名
        """
        if not os.path.exists('output'):
            os.makedirs('output')
        with open(os.path.join('output', filename), 'w', encoding='utf-8') as file:
            for item in data:
                file.write(f"{item}\n")

    def scrape(self):
        """
        开始爬取多个页面，并保存数据
        """
        for page_num in range(1, self.pages + 1):
            url = f"{self.base_url}?page={page_num}"
            print(f"正在爬取: {url}")

            html = self.get_html(url)
            if html:
                self.parse_html(html)  # 只输出筛选后的结果

            # 防止频繁请求被封禁，设置随机的延时
            time.sleep(random.uniform(1, 3))


if __name__ == "__main__":
    # 示例使用
    scraper = WebScraper_HouseData(base_url="https://sh.esf.fang.com/", pages=1)
    scraper.scrape()
