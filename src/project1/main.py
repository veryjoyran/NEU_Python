import pandas as pd
from tqdm import tqdm
from openpyxl import load_workbook


file_path = 'house_data_20240430.xlsx'


def load_data_with_progress(file_path):

    workbook = load_workbook(filename=file_path, read_only=True)
    sheet = workbook.active

    # 获取总行数，减去标题行
    total_rows = sheet.max_row - 1

    #显示进度条
    data = []
    header = None
    for i, row in enumerate(tqdm(sheet.iter_rows(values_only=True), total=total_rows + 1)):
        # 第一行作为标题
        if i == 0:
            header = row
        else:
            data.append(row)

    df = pd.DataFrame(data, columns=header)
    return df

house_data = load_data_with_progress(file_path)

pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)     # 显示所有行
pd.set_option('display.width', 1000)        # 设置显示宽度，避免换行
pd.set_option('display.colheader_justify', 'left')  # 左对齐列标题

query_address = input("请输入查询地址关键词: ")

# 进行模糊查询，过滤包含查询条件的地址
filtered_data = house_data[house_data['f地址'].str.contains(query_address, na=False)]

# 获取用户选择的排序方式
print("请选择排序方式：")
print("1. 按收藏数量降序排序")
print("2. 按价格升序排序")
print("3. 按价格降序排序")
sort_option = input("请输入排序方式的编号（1/2/3）：")

# 根据用户选择的排序方式排序数据
if sort_option == '1':
    sorted_data = filtered_data.sort_values(by='favCount', ascending=False)
elif sort_option == '2':
    sorted_data = filtered_data.sort_values(by='unitPrice', ascending=True)
elif sort_option == '3':
    sorted_data = filtered_data.sort_values(by='unitPrice', ascending=False)
else:
    print("无效的输入，默认按收藏数量降序排序")
    sorted_data = filtered_data.sort_values(by='favCount', ascending=False)

# 指定要输出的列，包括收藏数量
output_columns = [
    'unitPrice', 'favCount', 'f地址', '商圈', 'shopDistance', 'waterType', 'electricType',
    'buildingCount', 'greenRate', 'property', 'resblockId', '链接'
]

result = sorted_data[output_columns]
print(result)
result.to_excel("filtered_results.xlsx", index=False)  # 保存为 Excel 文件

