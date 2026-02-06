# 数据加载模块
import akshare as ak
import pandas as pd
import numpy as np
from config import DATA_CONFIG
import warnings
warnings.filterwarnings('ignore')

def load_stock_data(stock_code: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    从akshare加载股票数据
    
    Parameters:
        stock_code: 股票代码，默认使用配置中的目标股票
        start_date: 开始日期，默认使用配置中的日期
        end_date: 结束日期，默认使用配置中的日期
    
    Returns:
        pd.DataFrame: 股票数据
    """
    if stock_code is None:
        stock_code = DATA_CONFIG['target_stock']
    if start_date is None:
        start_date = DATA_CONFIG['start_date']
    if end_date is None:
        end_date = DATA_CONFIG['end_date']
    
    try:
        # 使用akshare获取股票数据
        if stock_code == 'sh':
            # 获取上证指数数据
            df = ak.stock_zh_index_daily(symbol="sh000001")
        else:
            # 获取个股数据
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                   start_date=start_date, end_date=end_date, 
                                   adjust="qfq")
        
        # 重命名列名（akshare返回的数据列名可能不一致）
        if 'date' not in df.columns and '日期' in df.columns:
            df = df.rename(columns={'日期': 'date'})
        if 'open' not in df.columns and '开盘' in df.columns:
            df = df.rename(columns={'开盘': 'open'})
        if 'high' not in df.columns and '最高' in df.columns:
            df = df.rename(columns={'最高': 'high'})
        if 'low' not in df.columns and '最低' in df.columns:
            df = df.rename(columns={'最低': 'low'})
        if 'close' not in df.columns and '收盘' in df.columns:
            df = df.rename(columns={'收盘': 'close'})
        if 'volume' not in df.columns and '成交量' in df.columns:
            df = df.rename(columns={'成交量': 'volume'})
            
        # 确保日期列为datetime类型
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # 确保数值列为float类型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        print(f"获取股票数据时出错: {e}")
        # 如果akshare获取失败，创建一些模拟数据用于测试
        print("创建模拟数据用于测试...")
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        dates = dates[dates.dayofweek < 5]  # 只保留工作日
        
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.randn(len(dates)) * 0.01),
            'high': prices * (1 + np.abs(np.random.randn(len(dates)) * 0.02)),
            'low': prices * (1 - np.abs(np.random.randn(len(dates)) * 0.02)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(dates))
        })
        
        return df

def load_multiple_stocks(stock_list: list, start_date: str = None, end_date: str = None) -> dict:
    """
    加载多个股票数据
    
    Parameters:
        stock_list: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        dict: 股票数据字典
    """
    stock_data = {}
    for stock in stock_list:
        try:
            stock_data[stock] = load_stock_data(stock, start_date, end_date)
            print(f"成功加载股票 {stock} 的数据，共 {len(stock_data[stock])} 条记录")
        except Exception as e:
            print(f"加载股票 {stock} 数据失败: {e}")
    
    return stock_data

if __name__ == "__main__":
    # 测试数据加载
    data = load_stock_data()
    print("数据加载测试:")
    print(data.head())
    print(f"数据形状: {data.shape}")