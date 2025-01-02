# client/main.py
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("二手房数据客户端")
        self.root.geometry("800x700")

        self.scraped_data = []  # 存储爬取到的数据

        self.create_widgets()

    def create_widgets(self):
        # 城市输入框
        self.city_label = tk.Label(self.root, text="请输入城市首字母（例如：bj、sh、sy、hf）：", font=("Arial", 12))
        self.city_label.pack(pady=10)

        self.city_entry = tk.Entry(self.root, font=("Arial", 14))
        self.city_entry.pack(pady=10)

        # 页数输入框
        self.pages_label = tk.Label(self.root, text="请输入爬取页数（默认5）：", font=("Arial", 12))
        self.pages_label.pack(pady=10)

        self.pages_entry = tk.Entry(self.root, font=("Arial", 14))
        self.pages_entry.pack(pady=10)

        # 开始爬取按钮
        self.scrape_button = tk.Button(self.root, text="开始爬取", font=("Arial", 14), command=self.scrape_data)
        self.scrape_button.pack(pady=10)

        # 显示数据按钮
        self.show_button = tk.Button(self.root, text="显示数据", font=("Arial", 14), command=self.show_data)
        self.show_button.pack(pady=10)

        # 统计按钮
        self.stats_button = tk.Button(self.root, text="显示统计图", font=("Arial", 14), command=self.show_statistics)
        self.stats_button.pack(pady=10)

        # 创建表格
        self.table = ttk.Treeview(self.root, columns=("房型", "面积", "楼层", "朝向", "建造年份", "业主", "地址", "描述", "价格"),
                                  show="headings", height=15)
        self.table.pack(pady=10)

        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)

    def scrape_data(self):
        city_code = self.city_entry.get().strip().lower()
        pages = self.pages_entry.get().strip()
        pages = int(pages) if pages.isdigit() else 5

        if not city_code:
            messagebox.showwarning("输入错误", "城市首字母不能为空！")
            return

        payload = {"city_code": city_code, "pages": pages}
        try:
            response = requests.post("http://localhost:5000/api/scrape", json=payload)
            if response.status_code == 200:
                message = response.json().get("message", f"爬取完成，获取到 {len(self.scraped_data)} 条数据。")
                self.scraped_data = response.json().get("data", [])
                data_count = len(self.scraped_data)
                messagebox.showinfo("成功", f"{message} 新增 {data_count} 条记录已保存到数据库。")
                # 显示在表格中
                for row in self.table.get_children():
                    self.table.delete(row)
                for item in self.scraped_data:
                    self.table.insert("", tk.END, values=(
                        item['room_type'], item['area'], item['floor'],
                        item['orientation'], item['build_year'], item['owner_name'],
                        item['address'], item['description'], item['price']
                    ))
            else:
                messagebox.showerror("错误", f"爬取失败: {response.text}")
        except Exception as e:
            messagebox.showerror("错误", f"无法连接到服务器: {e}")

    def show_data(self):
        try:
            response = requests.get("http://localhost:5000/api/houses")
            if response.status_code == 200:
                data = response.json()
                for row in self.table.get_children():
                    self.table.delete(row)
                for item in data:
                    self.table.insert("", tk.END, values=(
                        item['room_type'], item['area'], item['floor'],
                        item['orientation'], item['build_year'], item['owner_name'],
                        item['address'], item['description'], item['price']
                    ))
            else:
                messagebox.showerror("错误", f"获取数据失败: {response.text}")
        except Exception as e:
            messagebox.showerror("错误", f"无法连接到服务器: {e}")

    def show_statistics(self):
        try:
            response = requests.get("http://localhost:5000/api/statistics")
            if response.status_code == 200:
                stats = response.json().get("statistics", {})
                if not stats:
                    messagebox.showinfo("信息", "没有统计数据可显示。")
                    return
                room_types = list(stats.keys())
                counts = list(stats.values())

                fig, ax = plt.subplots(figsize=(10, 6))

                # 设置中文字体
                plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
                plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

                bars = ax.bar(room_types, counts, color='skyblue')
                ax.set_xlabel('房型')
                ax.set_ylabel('数量')
                ax.set_title('二手房房型统计')

                # 旋转x轴标签以防止重叠
                plt.xticks(rotation=45, ha='right')

                # 在每个柱子上方添加数量标签
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=10, color='black')

                # 创建一个新的窗口来显示图表
                stats_window = tk.Toplevel(self.root)
                stats_window.title("统计图")
                canvas = FigureCanvasTkAgg(fig, master=stats_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                messagebox.showerror("错误", f"获取统计数据失败: {response.text}")
        except Exception as e:
            messagebox.showerror("错误", f"无法连接到服务器: {e}")

def main():
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
