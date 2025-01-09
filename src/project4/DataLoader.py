# DataLoader.py

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pandas as pd
import os


class DatabaseReader:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.data = None

    def connect_to_db(self):
        """连接到数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)  # 连接到SQLite数据库
            print("成功连接到数据库")
        except sqlite3.Error as e:
            print(f"连接数据库失败: {e}")

    def load_data(self):
        """从数据库中加载数据"""
        if self.connection:
            query = "SELECT * FROM houses"  # 查询所有房源数据
            self.data = pd.read_sql_query(query, self.connection)
            print(f"成功加载 {len(self.data)} 条数据")
        else:
            print("未能连接到数据库，无法加载数据")

    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("数据库连接已关闭")

    def preprocess_price(self):
        """处理价格字段，提取出“万”字前的数字部分"""
        # 使用正则表达式提取数字部分，并转化为浮动型数值
        self.data['price_numeric'] = self.data['price'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
        print(f"价格字段处理完成，共处理 {len(self.data)} 条数据")

    def sort_data(self, sort_option):
        """按处理后的价格排序"""
        if self.data is not None:
            if sort_option == '1':  # 按价格升序
                return self.data.sort_values(by='price_numeric', ascending=True)
            elif sort_option == '2':  # 按价格降序
                return self.data.sort_values(by='price_numeric', ascending=False)
            else:
                print("无效的排序选项")
                return self.data  # 默认不排序
        else:
            print("没有数据可排序")
            return None


# 新窗口类：显示数据库中的房源数据
class DatabaseViewer:
    def __init__(self, root, db_reader):
        self.root = root
        self.db_reader = db_reader
        self.window = tk.Toplevel(root)  # 新窗口
        self.window.title("房源数据")
        self.window.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        """创建显示表格的UI"""
        # 创建表格
        self.table = ttk.Treeview(self.window, columns=("房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"),
                                  show="headings", height=15)
        self.table.pack(pady=10)

        # 设置表头
        headers = ["房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"]
        for header in headers:
            self.table.heading(header, text=header)
            if header == "地址":
                self.table.column(header, width=180)
            elif header == "描述":
                self.table.column(header, width=250)
            elif header == "价格":
                self.table.column(header, width=130)
            else:
                self.table.column(header, width=100)

        # 加载并显示数据
        self.load_and_display_data()

        # 创建排序按钮
        self.create_sort_buttons()

    def create_sort_buttons(self):
        """创建排序按钮"""
        # 按价格升序排序按钮
        self.sort_asc_button = tk.Button(self.window, text="按价格升序排序", command=self.sort_asc)
        self.sort_asc_button.pack(side=tk.LEFT, padx=10, pady=10)

        # 按价格降序排序按钮
        self.sort_desc_button = tk.Button(self.window, text="按价格降序排序", command=self.sort_desc)
        self.sort_desc_button.pack(side=tk.LEFT, padx=10, pady=10)

    def load_and_display_data(self):
        """从数据库加载并显示数据"""
        # 加载数据
        self.db_reader.load_data()

        # 处理价格字段
        self.db_reader.preprocess_price()

        # 默认加载数据并显示
        self.display_data(self.db_reader.data)

    def sort_asc(self):
        """按升序排序并显示数据"""
        sorted_data = self.db_reader.sort_data('1')
        self.display_data(sorted_data)

    def sort_desc(self):
        """按降序排序并显示数据"""
        sorted_data = self.db_reader.sort_data('2')
        self.display_data(sorted_data)

    def display_data(self, data):
        """将数据展示到表格"""
        if data is None:
            return

        # 清空表格内容
        for row in self.table.get_children():
            self.table.delete(row)

        # 将排序后的数据填充到表格
        for _, row in data.iterrows():
            self.table.insert("", tk.END, values=(
                row['room_type'],
                row['area'],
                row['floor'],
                row['orientation'],
                row['build_year'],
                row['owner_name'],
                row['address'],
                row['description'],
                row['price']
            ))


def run_test(city):
    # 创建主窗口
    root = tk.Tk()
    root.title("数据库查看器")
    root.geometry("400x200")

    # 测试数据库路径
    db_path = city + '_house_data.db'  # 假设数据库文件位于当前路径下
    if not os.path.exists(db_path):
        messagebox.showerror("错误", "数据库文件不存在，请检查路径！")
        return

    # 实例化数据库读取器
    db_reader = DatabaseReader(db_path)

    # 连接数据库
    db_reader.connect_to_db()

    # 实例化数据库查看器
    db_viewer = DatabaseViewer(root, db_reader)

    # 启动Tkinter的事件循环
    root.mainloop()


if __name__ == "__main__":
    run_test('sh')  # 'sh' 为城市代码，可以修改为其他城市
