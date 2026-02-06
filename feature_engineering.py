# 特征工程模块
import pandas as pd
import numpy as np
from config import DATA_CONFIG
import warnings
warnings.filterwarnings('ignore')

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算技术指标特征
    
    Parameters:
        df: 股票数据
    
    Returns:
        pd.DataFrame: 添加了技术指标的股票数据
    """
    df = df.copy()
    
    # 移动平均线
    for window in DATA_CONFIG['feature_windows']:
        df[f'MA_{window}'] = df['close'].rolling(window=window).mean()
        df[f'MA_{window}_ratio'] = df['close'] / df[f'MA_{window}']
    
    # 指数移动平均线
    for window in DATA_CONFIG['feature_windows']:
        df[f'EMA_{window}'] = df['close'].ewm(span=window).mean()
        df[f'EMA_{window}_ratio'] = df['close'] / df[f'EMA_{window}']
    
    # 布林带
    window = 20
    df['BB_middle'] = df['close'].rolling(window=window).mean()
    bb_std = df['close'].rolling(window=window).std()
    df['BB_upper'] = df['BB_middle'] + 2 * bb_std
    df['BB_lower'] = df['BB_middle'] - 2 * bb_std
    df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
    df['BB_position'] = (df['close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
    
    # RSI
    df['RSI'] = calculate_rsi(df['close'], 14)
    
    # MACD
    df['MACD'], df['MACD_signal'] = calculate_macd(df['close'])
    df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
    
    # 成交量相关特征
    for window in [5, 10, 20]:
        df[f'volume_MA_{window}'] = df['volume'].rolling(window=window).mean()
        df[f'volume_ratio_{window}'] = df['volume'] / df[f'volume_MA_{window}']
    
    # 价格变化率
    for window in DATA_CONFIG['feature_windows']:
        df[f'price_change_{window}'] = df['close'].pct_change(window)
    
    # 波动率
    for window in DATA_CONFIG['feature_windows']:
        df[f'volatility_{window}'] = df['close'].pct_change().rolling(window=window).std()
    
    # 最高/最低价差
    for window in DATA_CONFIG['feature_windows']:
        df[f'high_low_spread_{window}'] = (df['high'].rolling(window=window).max() - 
                                          df['low'].rolling(window=window).min()) / df['close']
    
    # 开盘-收盘价差
    df['open_close_diff'] = (df['close'] - df['open']) / df['open']
    
    # 高低价差
    df['high_low_diff'] = (df['high'] - df['low']) / df['low']
    
    return df

def calculate_rsi(close_prices: pd.Series, window: int = 14) -> pd.Series:
    """
    计算RSI指标
    
    Parameters:
        close_prices: 收盘价序列
        window: 计算窗口
    
    Returns:
        pd.Series: RSI值
    """
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(close_prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    计算MACD指标
    
    Parameters:
        close_prices: 收盘价序列
        fast: 快速EMA周期
        slow: 慢速EMA周期
        signal: 信号线周期
    
    Returns:
        tuple: (MACD线, 信号线)
    """
    ema_fast = close_prices.ewm(span=fast).mean()
    ema_slow = close_prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal).mean()
    return macd, macd_signal

def create_target_variable(df: pd.DataFrame, predict_days: int = None) -> pd.DataFrame:
    """
    创建目标变量（未来n天的收益率）
    
    Parameters:
        df: 股票数据
        predict_days: 预测天数
    
    Returns:
        pd.DataFrame: 添加了目标变量的数据
    """
    if predict_days is None:
        predict_days = DATA_CONFIG['predict_days']
    
    df = df.copy()
    # 未来n天的收益
    df['target'] = df['close'].shift(-predict_days) / df['close'] - 1
    return df

def add_lag_features(df: pd.DataFrame, columns: list = None, lags: list = None) -> pd.DataFrame:
    """
    添加滞后特征
    
    Parameters:
        df: 股票数据
        columns: 需要添加滞后特征的列名列表
        lags: 滞后天数列表
    
    Returns:
        pd.DataFrame: 添加了滞后特征的数据
    """
    if columns is None:
        columns = ['close', 'volume', 'open_close_diff', 'high_low_diff']
    if lags is None:
        lags = [1, 2, 3, 5, 10]
    
    df = df.copy()
    for col in columns:
        for lag in lags:
            df[f'{col}_lag_{lag}'] = df[col].shift(lag)
    
    return df

def feature_engineering_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    特征工程完整流程
    
    Parameters:
        df: 原始股票数据
    
    Returns:
        pd.DataFrame: 完成特征工程的数据
    """
    print("开始特征工程...")
    
    # 1. 计算技术指标
    df = calculate_technical_indicators(df)
    print(f"技术指标计算完成，当前特征数: {len(df.columns)}")
    
    # 2. 添加滞后特征
    df = add_lag_features(df)
    print(f"滞后特征添加完成，当前特征数: {len(df.columns)}")
    
    # 3. 创建目标变量
    df = create_target_variable(df)
    print(f"目标变量创建完成，当前特征数: {len(df.columns)}")
    
    # 4. 删除包含NaN的行
    initial_rows = len(df)
    df = df.dropna().reset_index(drop=True)
    final_rows = len(df)
    print(f"删除缺失值: 从 {initial_rows} 行到 {final_rows} 行")
    
    print("特征工程流程完成")
    return df

if __name__ == "__main__":
    # 测试特征工程
    from data_loader import load_stock_data
    
    # 加载数据
    data = load_stock_data()
    print("原始数据形状:", data.shape)
    
    # 执行特征工程
    processed_data = feature_engineering_pipeline(data)
    print("处理后数据形状:", processed_data.shape)
    print("特征列预览:")
    print(processed_data.columns.tolist()[-20:])  # 显示最后20个列名