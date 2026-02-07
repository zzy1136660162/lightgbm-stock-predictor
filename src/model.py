# -*- coding: utf-8 -*-
"""
LightGBM 模型模块 - 训练和预测
"""

import lightgbm as lgb
import numpy as np
import pandas as pd

from config.settings import MODEL_PARAMS


class StockModel:
    """LightGBM 股票预测模型"""
    
    def __init__(self, params: dict = None):
        """
        初始化模型
        
        Args:
            params: 模型参数（默认从 config 读取）
        """
        self.params = params or MODEL_PARAMS
        self.model = None
        self.feature_cols = None
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'StockModel':
        """
        训练模型
        
        Args:
            X_train: 训练特征
            y_train: 训练目标
        
        Returns:
            self
        """
        self.feature_cols = X_train.columns.tolist()
        
        self.model = lgb.LGBMRegressor(**self.params)
        self.model.fit(X_train, y_train)
        
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        预测
        
        Args:
            X: 特征数据
        
        Returns:
            预测值数组
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用 train()")
        
        return self.model.predict(X)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        获取特征重要性
        
        Returns:
            特征重要性 DataFrame
        """
        if self.model is None:
            return None
        
        importance = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> StockModel:
    """快速训练模型"""
    model = StockModel()
    model.train(X_train, y_train)
    return model


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    评估预测效果
    
    Args:
        y_true: 真实值
        y_pred: 预测值
    
    Returns:
        评估指标字典
    """
    # 准确率：预测方向是否正确
    direction_true = y_true > 0
    direction_pred = y_pred > 0
    accuracy = (direction_true == direction_pred).mean()
    
    # 收益对比
    bh_return = y_true.sum() * 100  # 买入持有收益
    strat_return = (direction_pred * y_true).sum() * 100  # 策略收益
    
    return {
        'accuracy': accuracy,
        'buyhold_return': bh_return,
        'strategy_return': strat_return
    }


if __name__ == "__main__":
    # 测试
    from src.data_manager import get_data_manager
    from src.feature import prepare_data
    
    dm = get_data_manager()
    df = dm.get_stock_data('600808')
    
    if df is not None:
        result = prepare_data(df)
        if result:
            X_train, X_test, y_train, y_test, df_test = result
            
            model = train_model(X_train, y_train)
            preds = model.predict(X_test)
            
            # 评估
            metrics = evaluate_predictions(y_test.values, preds)
            
            print(f"准确率: {metrics['accuracy']:.1%}")
            print(f"买入持有收益: {metrics['buyhold_return']:.1f}%")
            print(f"策略收益: {metrics['strategy_return']:.1f}%")
            
            # 特征重要性
            print("\n特征重要性:")
            print(model.get_feature_importance())
