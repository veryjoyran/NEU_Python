import tkinter as tk
from tkinter import messagebox, ttk
from WebScraper_HouseData import WebScraper_HouseData
import sqlite3
import os
from DataLoader import DatabaseReader,DatabaseViewer

class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("二手房数据爬虫")
        self.root.geometry("800x600")

        # 存储爬取到的数据
        self.scraped_data = []

        # 创建界面元素
        self.create_widgets()


    def get_db_connection(self, city_name):
        """
        根据城市名称生成对应的数据库连接。
        :param city_name: 城市名称
        :return: 对应的数据库连接
        """
        db_path = f"{city_name}_house_data.db"
        return sqlite3.connect(db_path)

    def create_table(self, db_connection):
        """
        创建数据库表（如果表不存在的话）
        :param db_connection: 数据库连接
        """
        db_cursor = db_connection.cursor()
        db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS houses (
                room_type TEXT,
                area TEXT,
                floor TEXT,
                orientation TEXT,
                build_year TEXT,
                owner_name TEXT,
                address TEXT,
                description TEXT,
                price TEXT
            )
        ''')
        db_connection.commit()

    def insert_into_db(self, db_connection, data):
        """
        将爬取的数据插入到数据库
        :param db_connection: 数据库连接
        :param data: 爬取到的房屋数据
        """
        db_cursor = db_connection.cursor()
        for item in data:
            db_cursor.execute('''
                INSERT INTO houses (room_type, area, floor, orientation, build_year, owner_name, address, description, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item['room_type'], item['area'], item['floor'], item['orientation'], item['build_year'],
                  item['owner_name'], item['address'], item['description'], item['price']))
        db_connection.commit()

    def create_widgets(self):
        # 城市输入框的说明
        self.city_label = tk.Label(self.root, text="请输入城市首字母（例如：bj、sh、sy、hf）：", font=("Arial", 12))
        self.city_label.pack(pady=10)

        # 城市输入框
        self.city_entry = tk.Entry(self.root, font=("Arial", 14))
        self.city_entry.pack(pady=10)

        # 开始爬取按钮
        self.scrape_button = tk.Button(self.root, text="开始爬取", font=("Arial", 14), command=self.scrape_data)
        self.scrape_button.pack(pady=10)

        # 保存到数据库按钮
        self.save_button = tk.Button(self.root, text="保存到数据库", font=("Arial", 14), command=self.save_to_db)
        self.save_button.pack(pady=10)

        # 读取数据库按钮
        self.read_db_button = tk.Button(self.root, text="读取数据库", font=("Arial", 14),
                                        command=self.read_data_from_db)
        self.read_db_button.pack(pady=10)

        # 创建表格
        self.table = ttk.Treeview(self.root, columns=("房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"),
                                  show="headings", height=15)
        self.table.pack(pady=10)

        # 设置表头
        self.table.heading("房型", text="房型")
        self.table.heading("面积", text="面积")
        self.table.heading("楼层", text="楼层")
        self.table.heading("朝向", text="朝向")
        self.table.heading("建造年份", text="建造年份")
        self.table.heading("业主", text="业主")
        self.table.heading("地址", text="地址")
        self.table.heading("描述", text="描述")
        self.table.heading("价格", text="价格")

        # 设置列宽
        self.table.column("房型", width=80)
        self.table.column("面积", width=80)
        self.table.column("楼层", width=100)
        self.table.column("朝向", width=80)
        self.table.column("建造年份", width=80)
        self.table.column("业主", width=80)
        self.table.column("地址", width=180)
        self.table.column("描述", width=250)
        self.table.column("价格", width=130)

    def get_city_url(self, city_code):
        """
        根据城市首字母生成对应的爬取网址
        :param city_code: 城市首字母
        :return: 对应城市的 URL
        """
        if city_code == "bj":
            return f"https://esf.fang.com/"
        else:
            return f"https://{city_code}.esf.fang.com/"

    def scrape_data(self):
        # 获取用户输入的城市首字母
        city_code = self.city_entry.get().strip().lower()

        if not city_code:
            messagebox.showwarning("输入错误", "城市首字母不能为空！")
            return

        # 生成对应城市的URL
        city_url = self.get_city_url(city_code)

        # 创建爬虫对象并进行爬取
        scraper = WebScraper_HouseData(base_url=city_url, pages=1)  # 默认爬取1页，可以修改

        # 清空之前的表格内容
        for row in self.table.get_children():
            self.table.delete(row)

        # 开始爬取并显示数据
        data = scraper.scrape()  # 获取所有数据
        self.scraped_data = data  # 保存爬取的数据

        if data:
            for item in data:
                # 直接从字典中提取数据，按照表格列顺序填充
                self.table.insert("", tk.END, values=(item['room_type'], item['area'], item['floor'],
                                                      item['orientation'], item['build_year'], item['owner_name'],
                                                      item['address'], item['description'], item['price']))
        else:
            messagebox.showinfo("爬取完成", "没有获取到任何数据。")

    def save_to_db(self):
        """
        将爬取的数据保存到对应城市的数据库
        """
        if not self.scraped_data:
            messagebox.showwarning("没有数据", "请先爬取数据再保存到数据库！")
            return

        # 获取城市名称（可以从用户输入的城市代码中推断出）
        city_name = self.city_entry.get().strip().lower()

        # 获取对应城市的数据库连接
        db_connection = self.get_db_connection(city_name)

        # 创建表格（如果表格不存在）
        self.create_table(db_connection)

        # 保存数据到对应城市的数据库
        self.insert_into_db(db_connection, self.scraped_data)

        # 关闭数据库连接
        db_connection.close()

        messagebox.showinfo("保存成功", f"数据已成功保存到 {city_name} 的数据库！")

    def read_data_from_db(self):
        """读取数据库数据并在新窗口中显示"""
        city_name = self.city_entry.get().strip().lower()  # 获取用户输入的城市名称
        if not city_name:
            messagebox.showwarning("输入错误", "城市名称不能为空！")
            return

        db_path = f"{city_name}_house_data.db"  # 动态生成数据库路径
        print(f"数据库路径：{db_path}")

        # 初始化 DatabaseReader 类
        db_reader = DatabaseReader(db_path)

        # 尝试连接并加载数据
        db_reader.connect_to_db()
        db_reader.load_data()

        # 在新窗口中显示数据库内容
        DatabaseViewer(self.root, db_reader)

        # 关闭数据库连接
        db_reader.close_connection()

def main():
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
