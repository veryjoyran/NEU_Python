# WebScraperGUI.py

import tkinter as tk
from tkinter import messagebox, ttk
from WebScraper_HouseData import WebScraper_HouseData
import sqlite3
import os
from DataLoader import DatabaseReader, DatabaseViewer
from DataPreprocessor import DataPreprocessor
from ModelTrainer import ModelTrainer
import pandas as pd
import joblib
import numpy as np
import re
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors

class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("二手房数据爬虫与预测系统")
        self.root.geometry("800x800")

        # 存储爬取到的数据
        self.scraped_data = []

        # 创建界面元素
        self.create_widgets()

    def get_db_connection(self, city_name):
        db_path = f"{city_name}_house_data.db"
        return sqlite3.connect(db_path)

    def create_table(self, db_connection):
        db_cursor = db_connection.cursor()
        db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS houses (
                room_type TEXT,
                area REAL,
                floor TEXT,
                orientation TEXT,
                build_year INTEGER,
                owner_name TEXT,
                address TEXT,
                description TEXT,
                price REAL
            )
        ''')
        db_connection.commit()

    def insert_into_db(self, db_connection, data):
        db_cursor = db_connection.cursor()
        for item in data:
            print(f"Inserting into DB: {item}")  # 调试信息
            db_cursor.execute('''
                INSERT INTO houses (room_type, area, floor, orientation, build_year, owner_name, address, description, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['room_type'],
                item['area'],
                item['floor'],
                item['orientation'],
                item['build_year'],
                item['owner_name'],
                item['address'],
                item['description'],
                item['price']
            ))
        db_connection.commit()

    def create_widgets(self):
        # 城市输入框的说明
        self.city_label = tk.Label(self.root, text="请输入城市首字母（例如：bj、sh、sy、hf）：", font=("Arial", 12))
        self.city_label.pack(pady=10)

        # 城市输入框
        self.city_entry = tk.Entry(self.root, font=("Arial", 14))
        self.city_entry.pack(pady=10)

        # 模型选择下拉菜单
        self.model_label = tk.Label(self.root, text="选择模型类型：", font=("Arial", 12))
        self.model_label.pack(pady=5)

        self.model_var = tk.StringVar()
        self.model_var.set("linear")  # 默认选择线性回归

        self.model_dropdown = ttk.Combobox(self.root, textvariable=self.model_var, state="readonly",
                                           values=["linear", "tree", "forest"], font=("Arial", 12))
        self.model_dropdown.pack(pady=5)

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

        # 训练模型按钮
        self.train_button = tk.Button(self.root, text="训练模型", font=("Arial", 14), command=self.train_model)
        self.train_button.pack(pady=10)

        # 预测价格按钮
        self.predict_button = tk.Button(self.root, text="预测价格", font=("Arial", 14), command=self.predict_price)
        self.predict_button.pack(pady=10)

        # 创建表格
        self.table = ttk.Treeview(self.root, columns=("房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"),
                                  show="headings", height=15)
        self.table.pack(pady=10)

        # 设置表头
        headers = ["房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"]
        for header in headers:
            self.table.heading(header, text=header)
            if header == "地址":
                self.table.column(header, width=200)
            elif header == "描述":
                self.table.column(header, width=300)
            elif header == "价格":
                self.table.column(header, width=100)
            else:
                self.table.column(header, width=80)

    def get_city_url(self, city_code):
        if city_code == "bj":
            return f"https://esf.fang.com/"
        else:
            return f"https://{city_code}.esf.fang.com/"

    def scrape_data(self):
        city_code = self.city_entry.get().strip().lower()

        if not city_code:
            messagebox.showwarning("输入错误", "城市首字母不能为空！")
            return

        city_url = self.get_city_url(city_code)
        scraper = WebScraper_HouseData(base_url=city_url, pages=100)

        for row in self.table.get_children():
            self.table.delete(row)

        data = scraper.scrape()
        self.scraped_data = data

        if data:
            for item in data:
                print(f"插入数据库的数据: {item}")  # 调试信息
                # 直接从字典中提取数据，按照表格列顺序填充
                self.table.insert("", tk.END, values=(item['room_type'], item['area'], item['floor'],
                                                      item['orientation'], item['build_year'], item['owner_name'],
                                                      item['address'], item['description'], item['price']))
        else:
            messagebox.showinfo("爬取完成", "没有获取到任何数据。")

    def save_to_db(self):
        if not self.scraped_data:
            messagebox.showwarning("没有数据", "请先爬取数据再保存到数据库！")
            return

        city_name = self.city_entry.get().strip().lower()
        db_connection = self.get_db_connection(city_name)
        self.create_table(db_connection)
        self.insert_into_db(db_connection, self.scraped_data)
        db_connection.close()

        messagebox.showinfo("保存成功", f"数据已成功保存到 {city_name} 的数据库！")

    def read_data_from_db(self):
        city_name = self.city_entry.get().strip().lower()
        if not city_name:
            messagebox.showwarning("输入错误", "城市名称不能为空！")
            return

        db_path = f"{city_name}_house_data.db"
        print(f"数据库路径：{db_path}")

        db_reader = DatabaseReader(db_path)
        db_reader.connect_to_db()
        db_reader.load_data()
        DatabaseViewer(self.root, db_reader)
        db_reader.close_connection()

    def train_model(self):
        city_name = self.city_entry.get().strip().lower()
        if not city_name:
            messagebox.showwarning("输入错误", "请先输入城市首字母！")
            return

        db_path = f"{city_name}_house_data.db"
        if not os.path.exists(db_path):
            messagebox.showwarning("数据库不存在", f"请先爬取并保存 {city_name} 的数据到数据库！")
            return

        # 从数据库中读取数据
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM houses", conn)
        conn.close()

        if df.empty:
            messagebox.showwarning("没有数据", "数据库中没有数据可以用于训练！")
            return

        # 数据预处理
        preprocessor = DataPreprocessor()

        # 获取选择的模型类型
        selected_model = self.model_var.get()

        # 创建Pipeline
        trainer = ModelTrainer(model_type=selected_model)
        pipeline = Pipeline([
            ('preprocessor', preprocessor.preprocessor),
            ('model', trainer.model)
        ])

        # 训练模型
        trained_pipeline = trainer.train(pipeline, df[['room_type', 'orientation', 'floor', 'area', 'build_year']],
                                         df['price'])

        # 保存Pipeline
        if not os.path.exists('models'):
            os.makedirs('models')
        pipeline_filename = f"models/{city_name}_pipeline.joblib"
        trainer.save_model(trained_pipeline, pipeline_filename)

        messagebox.showinfo("训练完成",
                            f"模型和预处理器已保存。\n模型文件: {pipeline_filename}")

    def predict_price(self):
        city_name = self.city_entry.get().strip().lower()
        if not city_name:
            messagebox.showwarning("输入错误", "请先输入城市首字母！")
            return

        selected_model = self.model_var.get()
        pipeline_filename = f"models/{city_name}_pipeline.joblib"
        if not os.path.exists(pipeline_filename):
            messagebox.showwarning("模型不存在", f"请先训练 {selected_model} 模型！")
            return

        try:
            pipeline = joblib.load(pipeline_filename)
            print(f"Loaded pipeline type: {type(pipeline)}")
            print(f"Pipeline steps: {pipeline.named_steps}")
        except Exception as e:
            print(f"加载模型失败: {e}")
            messagebox.showerror("加载错误", f"加载模型失败: {e}")
            return

        prediction_window = tk.Toplevel(self.root)
        prediction_window.title("预测价格")
        prediction_window.geometry("400x500")

        fields = ['房型', '朝向', '楼层', '面积', '建造年份']
        entries = {}
        for idx, field in enumerate(fields):
            label = tk.Label(prediction_window, text=f"请输入{field}：", font=("Arial", 12))
            label.pack(pady=5)
            entry = tk.Entry(prediction_window, font=("Arial", 12))
            entry.pack(pady=5)
            entries[field] = entry

        def submit_prediction():
            try:
                room_type = entries['房型'].get().strip()
                orientation = entries['朝向'].get().strip()
                floor = entries['楼层'].get().strip()
                area_input = entries['面积'].get().strip()
                build_year_input = entries['建造年份'].get().strip()

                # 使用正则表达式提取面积中的数字部分
                area_match = re.search(r'(\d+(\.\d+)?)', area_input)
                if area_match:
                    area = float(area_match.group(1))
                else:
                    raise ValueError("面积输入无效，请输入数字，如 118.17")

                # 验证建造年份是否为有效的四位数
                if re.match(r'^\d{4}$', build_year_input):
                    build_year = int(build_year_input)
                else:
                    raise ValueError("建造年份输入无效，请输入四位数字，如 1999")

                input_df = pd.DataFrame([{
                    'room_type': room_type,
                    'orientation': orientation,
                    'floor': floor,
                    'area': area,
                    'build_year': build_year
                }])
                # 打印输入数据
                print("Input DataFrame:")
                print(input_df)

                # 使用 pipeline 直接预测
                predicted_price = pipeline.predict(input_df)[0]

                # 打印预测结果
                print(f"Predicted Price: {predicted_price}")

                # 查找相似房源
                self.show_similar_houses(input_df, pipeline, city_name)

                messagebox.showinfo("预测结果", f"预测价格为: {predicted_price:.2f} 万元")
            except ValueError as ve:
                print(f"ValueError: {ve}")
                messagebox.showerror("输入错误", f"预测失败: {ve}")
            except Exception as e:
                print(f"Exception: {e}")
                messagebox.showerror("错误", f"预测失败: {e}")

        submit_btn = tk.Button(prediction_window, text="预测", font=("Arial", 12), command=submit_prediction)
        submit_btn.pack(pady=20)

    def show_similar_houses(self, input_df, pipeline, city_name):
        # 假设使用KNN查找相似房源
        from sklearn.neighbors import NearestNeighbors

        # 加载所有数据
        df = self.load_data(city_name)
        if df.empty:
            messagebox.showwarning("没有数据", "数据库中没有数据可以用于查找相似房源！")
            return

        # 预处理数据
        try:
            X = pipeline.named_steps['preprocessor'].transform(df[['room_type', 'orientation', 'floor', 'area', 'build_year']])
        except Exception as e:
            print(f"预处理数据失败: {e}")
            messagebox.showerror("预处理错误", f"预处理数据失败: {e}")
            return

        # 预处理输入
        try:
            input_processed = pipeline.named_steps['preprocessor'].transform(input_df)
        except Exception as e:
            print(f"预处理输入数据失败: {e}")
            messagebox.showerror("预处理错误", f"预处理输入数据失败: {e}")
            return

        # 使用KNN查找相似房源
        try:
            nbrs = NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(X)
            distances, indices = nbrs.kneighbors(input_processed)
            similar_houses = df.iloc[indices[0]]
        except Exception as e:
            print(f"KNN查找失败: {e}")
            messagebox.showerror("查找错误", f"KNN查找失败: {e}")
            return

        # 在新窗口中显示相似房源
        similar_window = tk.Toplevel(self.root)
        similar_window.title("相似房源推荐")
        similar_window.geometry("900x400")

        table = ttk.Treeview(similar_window,
                             columns=("房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"),
                             show="headings", height=15)
        table.pack(pady=10)

        headers = ["房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"]
        for header in headers:
            table.heading(header, text=header)
            if header == "地址":
                table.column(header, width=200)
            elif header == "描述":
                table.column(header, width=300)
            elif header == "价格":
                table.column(header, width=100)
            else:
                table.column(header, width=100)

        for _, row in similar_houses.iterrows():
            table.insert("", tk.END, values=(
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

    def load_data(self, city_name):
        db_path = f"{city_name}_house_data.db"
        if not os.path.exists(db_path):
            print(f"数据库文件不存在: {db_path}")
            return pd.DataFrame()
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM houses", conn)
        conn.close()
        return df

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()
