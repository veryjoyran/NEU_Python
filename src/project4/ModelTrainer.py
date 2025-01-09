# ModelTrainer.py

import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

class ModelTrainer:
    def __init__(self, model_type='linear'):
        """
        初始化模型训练器
        :param model_type: 模型类型，支持 'linear', 'tree', 'forest'
        """
        if model_type == 'linear':
            model = LinearRegression()
        elif model_type == 'tree':
            model = DecisionTreeRegressor(random_state=42)
        elif model_type == 'forest':
            model = RandomForestRegressor(random_state=42)
        else:
            raise ValueError("Unsupported model type")
        self.model = model
        self.model_type = model_type

    def train(self, pipeline, X, y):
        """
        训练模型
        :param pipeline: 包含预处理和模型的Pipeline
        :param X: 特征数据
        :param y: 目标变量
        :return: 训练好的Pipeline
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"{self.model_type} 模型的均方误差: {mse}")
        return pipeline

    def save_model(self, pipeline, filename):
        """
        保存训练好的Pipeline
        :param pipeline: 训练好的Pipeline
        :param filename: 保存的文件名
        """
        joblib.dump(pipeline, filename)
        print(f"模型已保存到 {filename}")
