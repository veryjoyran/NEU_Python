# DataPreprocessor.py

import pandas as pd
import re
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


class DataPreprocessor:
    def __init__(self):
        # 定义需要进行独热编码的类别特征
        self.categorical_features = ['room_type', 'orientation', 'floor']
        # 定义需要进行标准化的数值特征
        self.numeric_features = ['area', 'build_year']

        # 定义预处理管道
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), self.categorical_features)
            ]
        )

    def preprocess(self, df):
        """
        对数据进行预处理
        :param df: 原始数据的DataFrame
        :return: 预处理后的特征和目标变量
        """
        # 处理缺失值（简单删除包含缺失值的行）
        df = df.dropna()

        # 特征和目标变量
        X = df[['room_type', 'orientation', 'floor', 'area', 'build_year']]
        y = df['price']

        # 应用预处理管道
        X_processed = self.preprocessor.fit_transform(X)

        return X_processed, y

    def transform(self, df):
        """
        使用已拟合的预处理管道对新数据进行转换
        :param df: 新数据的DataFrame
        :return: 预处理后的特征
        """
        # 仅选择特征列
        X = df[['room_type', 'orientation', 'floor', 'area', 'build_year']]

        # 应用预处理管道
        X_processed = self.preprocessor.transform(X)

        return X_processed

    def _clean_area(self, area_str):
        """
        清洗面积字段，移除单位并转换为浮点数
        :param area_str: 面积字符串，例如 "67.4㎡"
        :return: 浮点数面积
        """
        try:
            # 使用正则表达式提取数字部分
            match = re.search(r'(\d+(\.\d+)?)', str(area_str))
            if match:
                return float(match.group(1))
            else:
                print(f"面积格式不匹配: {area_str}")
                return None
        except (ValueError, AttributeError) as e:
            print(f"面积转换错误: {area_str} -> {e}")
            return None

    def _clean_price(self, price_str):
        """
        清洗价格字段，只提取总价部分并转换为浮点数（单位：万）
        :param price_str: 价格字符串，例如 "360万53412元/㎡"
        :return: 浮点数总价（万）
        """
        try:
            # 提取“万”前的数字部分
            match = re.search(r'(\d+\.?\d*)万', price_str)
            if match:
                price = float(match.group(1))
                return price
            else:
                # 如果没有“万”，提取“元”并转换为“万”
                match = re.search(r'(\d+\.?\d*)元', price_str)
                if match:
                    price = float(match.group(1)) / 10000  # 转换为万
                    return price
                else:
                    print(f"价格格式不匹配: {price_str}")
                    return None
        except (ValueError, AttributeError) as e:
            print(f"价格转换错误: {price_str} -> {e}")
            return None

    def _clean_build_year(self, build_year_str):
        """
        清洗建造年份字段，提取年份并转换为整数
        :param build_year_str: 建造年份字符串，例如 "1996年建"
        :return: 整数年份
        """
        try:
            match = re.search(r'(\d{4})年建', build_year_str)
            if match:
                return int(match.group(1))
            else:
                print(f"建造年份格式不匹配: {build_year_str}")
                return None
        except (ValueError, AttributeError) as e:
            print(f"建造年份转换错误: {build_year_str} -> {e}")
            return None
