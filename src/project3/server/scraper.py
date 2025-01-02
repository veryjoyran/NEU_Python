# server/scraper.py
import re
import requests
from bs4 import BeautifulSoup
import time
import random
from database import House, Session
import logging

logger = logging.getLogger(__name__)

class WebScraper_HouseData:
    def __init__(self, base_url, pages=5):
        self.base_url = base_url
        self.pages = pages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

    def get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException as e:
            logger.error(f"请求错误: {e}")
            return None

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'lxml')
        tel_shop_paragraphs = soup.find_all('p', class_='tel_shop')
        add_shop_paragraphs = soup.find_all('p', class_='add_shop')
        clearfix_paragraphs = soup.find_all('p', class_='clearfix label')
        price_right_dd = soup.find_all('dd', class_='price_right')

        tel_numbers = [tel.get_text(strip=True) for tel in tel_shop_paragraphs]
        add_shops = [add.get_text(strip=True) for add in add_shop_paragraphs]
        clearfix_labels = [label.get_text(strip=True) for label in clearfix_paragraphs]
        prices = [price.get_text(strip=True) for price in price_right_dd]

        data = []

        for tel, addr, label, price in zip(tel_numbers, add_shops, clearfix_labels, prices):
            phone_info = self.parse_phone_info(tel)
            if phone_info:
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
                data.append(house_data)
            else:
                logger.warning(f"电话信息解析失败: {tel}, 地址: {addr}, 描述: {label}, 价格: {price}")

        return data

    def parse_phone_info(self, tel):
        fields = tel.split('|')
        if len(fields) != 6:
            logger.warning(f"电话信息格式不匹配: {tel}")
            return None
        return {
            'room_type': fields[0],
            'area': fields[1],
            'floor': fields[2],
            'orientation': fields[3],
            'build_year': fields[4],
            'owner_name': fields[5]
        }

    def scrape(self, url=None):
        if url is None:
            url = self.base_url
        all_data = []
        for page_num in range(1, self.pages + 1):
            full_url = f"{url}?page={page_num}"
            logger.info(f"正在爬取: {full_url}")
            html = self.get_html(full_url)
            if html:
                page_data = self.parse_html(html)
                all_data.extend(page_data)
            time.sleep(random.uniform(1, 3))
        return all_data

    def save_to_db(self, data):
        session = Session()
        saved_count = 0
        try:
            for item in data:
                exists = session.query(House).filter_by(address=item['address'], price=item['price']).first()
                if not exists:
                    house = House(
                        room_type=item['room_type'],
                        area=item['area'],
                        floor=item['floor'],
                        orientation=item['orientation'],
                        build_year=item['build_year'],
                        owner_name=item['owner_name'],
                        address=item['address'],
                        description=item['description'],
                        price=item['price']
                    )
                    session.add(house)
                    saved_count += 1
            session.commit()
            logger.info(f"成功保存 {saved_count} 条新记录到数据库。")
        except Exception as e:
            session.rollback()
            logger.error(f"保存数据到数据库时出错: {e}")
        finally:
            session.close()

    def scrape_and_save(self, url=None):
        data = self.scrape(url)
        if data:
            self.save_to_db(data)
        return data

if __name__ == "__main__":
    # 示例使用
    scraper = WebScraper_HouseData(base_url="https://hf.esf.fang.com/", pages=1)
    data = scraper.scrape_and_save()
    print(f"爬取并保存了 {len(data)} 条数据。")
