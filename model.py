# 模型训练和预测模块
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from config import MODEL_CONFIG, DATA_CONFIG
import warnings
import os
import pickle
import time
warnings.filterwarnings('ignore')

class StockPredictor:
    def __init__(self, model_params=None):
        """
        初始化股票预测器
        
        Parameters:
            model_params: 模型参数
        """
        if model_params is None:
            model_params = MODEL_CONFIG
        self.model_params = model_params
        self.model = None
        self.feature_names = None
        
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'target') -> tuple:
        """
        准备训练数据
        
        Parameters:
            df: 包含特征和目标变量的数据
            target_col: 目标变量列名
        
        Returns:
            tuple: (X, y) 特征和目标变量
        """
        # 分离特征和目标变量
        feature_cols = [col for col in df.columns if col not in ['date', 'open', 'high', 'low', 'close', 'volume', target_col]]
        X = df[feature_cols]
        y = df[target_col]
        
        self.feature_names = feature_cols
        print(f"特征数量: {len(feature_cols)}")
        print(f"特征列: {feature_cols[:10]}...")  # 显示前10个特征
        
        return X, y
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        训练模型
        
        Parameters:
            X: 特征数据
            y: 目标变量
        """
        print("开始训练模型...")
        
        # 分割训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # 创建LightGBM数据集
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        # 训练模型
        self.model = lgb.train(
            self.model_params,
            train_data,
            valid_sets=[train_data, val_data],
            valid_names=['train', 'val'],
            num_boost_round=1000,
            callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(100)]
        )
        
        # 验证集预测
        y_pred = self.model.predict(X_val, num_iteration=self.model.best_iteration)
        
        # 计算评估指标
        mse = mean_squared_error(y_val, y_pred)
        mae = mean_absolute_error(y_val, y_pred)
        
        print(f"验证集 MSE: {mse:.6f}")
        print(f"验证集 MAE: {mae:.6f}")
        print(f"验证集 RMSE: {np.sqrt(mse):.6f}")
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        预测
        
        Parameters:
            X: 特征数据
        
        Returns:
            np.ndarray: 预测结果
        """
        if self.model is None:
            raise ValueError("模型尚未训练")
        
        predictions = self.model.predict(X, num_iteration=self.model.best_iteration)
        return predictions
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        获取特征重要性

        Returns:
            pd.DataFrame: 特征重要性排序
        """
        if self.model is None:
            raise ValueError("模型尚未训练")

        importance = self.model.feature_importance(importance_type='gain')
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        return feature_importance

    def save_model(self, filepath: str = "model/lgb_model.pkl") -> str:
        """
        保存模型到文件

        Parameters:
            filepath: 模型保存路径

        Returns:
            str: 保存的文件路径
        """
        if self.model is None:
            raise ValueError("模型尚未训练，无法保存")

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # 保存模型
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names,
                'model_params': self.model_params
            }, f)

        # 获取文件大小
        file_size = os.path.getsize(filepath)
        file_size_str = self._format_file_size(file_size)

        print(f"[OK] 模型已保存到: {filepath}")
        print(f"[PACK] 模型文件大小: {file_size_str}")

        return filepath

    def load_model(self, filepath: str = "model/lgb_model.pkl") -> None:
        """
        从文件加载模型

        Parameters:
            filepath: 模型文件路径
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"模型文件不存在: {filepath}")

        # 加载模型
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.feature_names = data.get('feature_names', [])
        self.model_params = data.get('model_params', {})

        # 获取文件大小
        file_size = os.path.getsize(filepath)
        file_size_str = self._format_file_size(file_size)

        print(f"[OK] 模型已从 {filepath} 加载")
        print(f"[PACK] 模型文件大小: {file_size_str}")
        print(f"[STATS] 特征数量: {len(self.feature_names)}")

    def get_model_size(self, filepath: str = "model/lgb_model.pkl") -> dict:
        """
        获取模型文件大小信息

        Parameters:
            filepath: 模型文件路径

        Returns:
            dict: 文件大小信息
        """
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            return {
                'path': filepath,
                'bytes': file_size,
                'formatted': self._format_file_size(file_size)
            }
        else:
            return {
                'path': filepath,
                'bytes': 0,
                'formatted': '文件不存在'
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小

        Parameters:
            size_bytes: 字节大小

        Returns:
            str: 格式化后的大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

def walk_forward_training(df: pd.DataFrame, train_period: int = 1000, test_period: int = 200) -> list:
    """
    Walk-forward训练
    
    Parameters:
        df: 训练数据
        train_period: 训练集大小
        test_period: 测试集大小
    
    Returns:
        list: 每个训练周期的模型和结果
    """
    results = []
    start_idx = 0
    
    print("开始Walk-forward训练...")
    predictor = StockPredictor()
    
    while start_idx + train_period + test_period <= len(df):
        # 确定训练和测试集
        train_end = start_idx + train_period
        test_end = train_end + test_period
        
        train_df = df.iloc[start_idx:train_end].copy()
        test_df = df.iloc[train_end:test_end].copy()
        
        print(f"训练集: {train_df['date'].iloc[0]} 到 {train_df['date'].iloc[-1]} ({len(train_df)}条记录)")
        print(f"测试集: {test_df['date'].iloc[0]} 到 {test_df['date'].iloc[-1]} ({len(test_df)}条记录)")
        
        # 准备数据
        X_train, y_train = predictor.prepare_data(train_df)
        X_test, y_test = predictor.prepare_data(test_df)
        
        # 训练模型
        predictor.train(X_train, y_train)

        # 保存模型（每个周期保存一个版本）
        timestamp = int(time.time())
        model_path = f"model/wf_model_period_{start_idx}_{timestamp}.pkl"
        predictor.save_model(model_path)
        
        # 预测
        y_pred = predictor.predict(X_test)
        
        # 计算评估指标
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # 保存结果
        result = {
            'train_period': (train_df['date'].iloc[0], train_df['date'].iloc[-1]),
            'test_period': (test_df['date'].iloc[0], test_df['date'].iloc[-1]),
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'predictor': predictor,
            'predictions': y_pred,
            'actual': y_test.values
        }
        results.append(result)
        
        print(f"测试集 MSE: {mse:.6f}, MAE: {mae:.6f}, RMSE: {rmse:.6f}")
        print("-" * 50)
        
        # 移动到下一个训练周期
        start_idx += test_period
    
    return results

if __name__ == "__main__":
    # 测试模型训练
    from data_loader import load_stock_data
    from feature_engineering import feature_engineering_pipeline
    
    # 加载并处理数据
    data = load_stock_data()
    processed_data = feature_engineering_pipeline(data)
    
    # 准备训练数据
    predictor = StockPredictor()
    X, y = predictor.prepare_data(processed_data)
    
    # 训练模型
    predictor.train(X, y)
    
    # 预测
    predictions = predictor.predict(X.tail(10))
    print("最后10个预测结果:")
    print(predictions)
    
    # 特征重要性
    importance = predictor.get_feature_importance()
    print("前10个重要特征:")
    print(importance.head(10))