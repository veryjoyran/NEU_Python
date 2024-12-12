import tkinter as tk
from tkinter import messagebox, ttk
from WebScraper_HouseData import WebScraper_HouseData


class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("房产数据爬虫")
        self.root.geometry("800x600")

        # 创建界面元素
        self.create_widgets()

    def create_widgets(self):
        # 城市输入框的说明
        self.city_label = tk.Label(self.root, text="请输入城市首字母（例如：sh、nj、hf）：", font=("Arial", 12))
        self.city_label.pack(pady=10)

        # 城市输入框
        self.city_entry = tk.Entry(self.root, font=("Arial", 14))
        self.city_entry.pack(pady=10)

        # 开始爬取按钮
        self.scrape_button = tk.Button(self.root, text="开始爬取", font=("Arial", 14), command=self.scrape_data)
        self.scrape_button.pack(pady=10)

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
        self.table.column("楼层", width=80)
        self.table.column("朝向", width=80)
        self.table.column("建造年份", width=80)
        self.table.column("业主", width=80)
        self.table.column("地址", width=120)
        self.table.column("描述", width=180)
        self.table.column("价格", width=100)

    def get_city_url(self, city_code):
        """
        根据城市首字母生成对应的爬取网址
        :param city_code: 城市首字母
        :return: 对应城市的 URL
        """
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

        if data:
            for item in data:
                # 直接从字典中提取数据，按照表格列顺序填充
                self.table.insert("", tk.END, values=(item['room_type'], item['area'], item['floor'],
                                                      item['orientation'], item['build_year'], item['owner_name'],
                                                      item['address'], item['description'], item['price']))
        else:
            messagebox.showinfo("爬取完成", "没有获取到任何数据。")

def main():
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
