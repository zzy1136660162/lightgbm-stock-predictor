# -*- coding: utf-8 -*-
"""
特征工程模块 - 计算技术指标特征
"""

import pandas as pd
import numpy as np

from config.settings import FEATURE_COLS


class FeatureEngineer:
    """特征工程处理器"""
    
    def __init__(self, close_col: str = '收盘'):
        """
        初始化
        
        Args:
            close_col: 收盘价列名
        """
        self.close_col = close_col
        self.feature_cols = FEATURE_COLS
    
    def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有特征
        
        Args:
            df: 原始数据 DataFrame
        
        Returns:
            添加特征后的 DataFrame
        """
        df = df.copy()
        
        # ========== 1. 移动平均比 ==========
        for w in [5, 10, 20, 40]:
            ma = df[self.close_col].rolling(w).mean()
            df[f'ma{w}'] = ma
            df[f'ma{w}_ratio'] = df[self.close_col] / ma
        
        # ========== 2. RSI (相对强弱指数) ==========
        delta = df[self.close_col].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ========== 3. MACD (移动平均收敛散度) ==========
        ema12 = df[self.close_col].ewm(span=12).mean()
        ema26 = df[self.close_col].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # ========== 4. 价格变化率 ==========
        df['change_5'] = df[self.close_col].pct_change(5)
        df['change_10'] = df[self.close_col].pct_change(10)
        
        # ========== 5. 波动率 ==========
        df['volatility'] = df[self.close_col].pct_change().rolling(10).std()
        
        return df
    
    def add_target(self, df: pd.DataFrame, predict_days: int = 20) -> pd.DataFrame:
        """
        添加预测目标（未来N天收益率）
        
        Args:
            df: 数据 DataFrame
            predict_days: 预测未来天数
        
        Returns:
            添加目标后的 DataFrame
        """
        df = df.copy()
        df['target'] = df[self.close_col].shift(-predict_days) / df[self.close_col] - 1
        return df
    
    def clean_data(self, df: pd.DataFrame, min_rows: int = 400) -> pd.DataFrame:
        """
        清洗数据，去除NaN
        
        Args:
            df: 特征数据 DataFrame
            min_rows: 最小行数要求
        
        Returns:
            清洗后的 DataFrame
        """
        df_clean = df.dropna(subset=self.feature_cols + ['target'])
        
        if len(df_clean) < min_rows:
            return None
        
        return df_clean
    
    def split_data(self, df: pd.DataFrame, test_size: int = 100):
        """
        分割训练集和测试集
        
        Args:
            df: 清洗后的数据
            test_size: 测试集大小
        
        Returns:
            (X_train, X_test, y_train, y_test)
        """
        train_size = len(df) - test_size
        
        X = df[self.feature_cols]
        y = df['target']
        
        return X[:train_size], X[train_size:], y[:train_size], y[train_size:]


# ============ 便捷函数 ============
def create_features(df: pd.DataFrame, close_col: str = '收盘') -> pd.DataFrame:
    """快速创建特征"""
    fe = FeatureEngineer(close_col)
    df = fe.calculate_features(df)
    df = fe.add_target(df)
    return df


def prepare_data(df: pd.DataFrame, close_col: str = '收盘') -> tuple:
    """
    准备训练数据
    
    Returns:
        (X_train, X_test, y_train, y_test, df_test)
    """
    fe = FeatureEngineer(close_col)
    
    # 特征 + 目标
    df = fe.calculate_features(df)
    df = fe.add_target(df)
    
    # 清洗
    df_clean = fe.clean_data(df)
    if df_clean is None:
        return None
    
    # 分割
    X_train, X_test, y_train, y_test = fe.split_data(df_clean)
    
    # 测试集数据（保留完整信息用于回测）
    test_start = len(df_clean) - 100
    df_test = df_clean.iloc[test_start:].copy()
    
    return X_train, X_test, y_train, y_test, df_test


if __name__ == "__main__":
    # 测试
    import pandas as pd
    from src.data_manager import get_data_manager
    
    dm = get_data_manager()
    df = dm.get_stock_data('600808')
    
    if df is not None:
        fe = FeatureEngineer()
        df_features = fe.calculate_features(df)
        df_features = fe.add_target(df_features)
        df_clean = fe.clean_data(df_features)
        
        print(f"原始数据: {len(df)}")
        print(f"特征数据: {len(df_features)}")
        print(f"清洗后: {len(df_clean)}")
        print(f"特征列: {fe.feature_cols}")
