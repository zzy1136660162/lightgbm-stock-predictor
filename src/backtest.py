# -*- coding: utf-8 -*-
"""
回测模块 - 模拟交易策略表现
"""

import pandas as pd
import numpy as np

from config.settings import BACKTEST_PARAMS


class Backtester:
    """
    股票回测器
    
    策略逻辑:
    - 预测 > 0: 买入 (signal = 1)
    - 预测 < 0: 卖出 (signal = -1)
    - 预测 = 0: 持有 (signal = 0)
    """
    
    def __init__(self, 
                 initial_cash: float = None,
                 transaction_fee: float = None,
                 slippage: float = None):
        """
        初始化回测器
        
        Args:
            initial_cash: 初始资金
            transaction_fee: 交易费率
            slippage: 滑点
        """
        self.initial_cash = initial_cash or BACKTEST_PARAMS['initial_cash']
        self.transaction_fee = transaction_fee or BACKTEST_PARAMS['transaction_fee']
        self.slippage = slippage or BACKTEST_PARAMS['slippage']
    
    def generate_signals(self, df: pd.DataFrame, pred_col: str = 'pred') -> pd.DataFrame:
        """
        根据预测生成交易信号
        
        Args:
            df: 包含预测值的 DataFrame
            pred_col: 预测列名
        
        Returns:
            添加信号后的 DataFrame
        """
        df = df.copy()
        
        df['signal'] = 0
        df.loc[df[pred_col] > 0, 'signal'] = 1   # 买入
        df.loc[df[pred_col] < 0, 'signal'] = -1  # 卖出
        
        return df
    
    def calculate_returns(self, df: pd.DataFrame, 
                          price_col: str = '收盘',
                          signal_col: str = 'signal') -> pd.DataFrame:
        """
        计算收益率
        
        Args:
            df: 包含信号的 DataFrame
            price_col: 价格列名
            signal_col: 信号列名
        
        Returns:
            添加收益率的 DataFrame
        """
        df = df.copy()
        
        # 日收益率
        df['daily_ret'] = df[price_col].pct_change()
        
        # 策略收益率（信号滞后一期，避免未来函数）
        df['strat_ret'] = df[signal_col].shift(1) * df['daily_ret']
        
        # 考虑交易成本
        # 当信号变化时收取交易费
        signal_change = df[signal_col].diff().fillna(0)
        df['strat_ret_net'] = df['strat_ret'] - abs(signal_change) * self.transaction_fee
        
        return df
    
    def run_backtest(self, df: pd.DataFrame, 
                     pred_col: str = 'pred',
                     price_col: str = '收盘') -> dict:
        """
        运行回测
        
        Args:
            df: 包含预测值的数据
            pred_col: 预测列名
            price_col: 价格列名
        
        Returns:
            回测结果字典
        """
        # 1. 生成信号
        df = self.generate_signals(df, pred_col)
        
        # 2. 计算收益
        df = self.calculate_returns(df, price_col)
        
        # 3. 计算指标
        bh_cumret = df['daily_ret'].sum() * 100
        strat_cumret = df['strat_ret'].sum() * 100
        strat_cumret_net = df['strat_ret_net'].sum() * 100
        
        # 准确率
        y_true = df['target'].iloc[100:].values
        preds = df[pred_col].iloc[100:].values
        direction_true = y_true > 0
        direction_pred = preds > 0
        accuracy = (direction_true == direction_pred).mean() if len(direction_true) > 0 else 0
        
        # 交易次数
        trades = (df['signal'].diff() != 0).sum()
        
        return {
            'buyhold_return': bh_cumret,
            'strategy_return': strat_cumret,
            'strategy_return_net': strat_cumret_net,
            'accuracy': accuracy,
            'trades': trades,
            'data': df
        }
    
    def summary(self, result: dict) -> str:
        """
        生成回测摘要
        
        Args:
            result: run_backtest 返回的结果
        
        Returns:
            摘要字符串
        """
        df = result['data']
        return f"""
========== 回测结果 ==========
买入持有收益: {result['buyhold_return']:+.2f}%
策略收益:     {result['strategy_return']:+.2f}%
策略收益(净): {result['strategy_return_net']:+.2f}%
准确率:       {result['accuracy']:.1%}
交易次数:     {result['trades']}
数据点数:     {len(df)}
"""


def quick_backtest(df: pd.DataFrame, pred_col: str = 'pred') -> dict:
    """
    快速回测
    
    Args:
        df: 包含 pred 和 target 列的 DataFrame
    
    Returns:
        回测结果
    """
    bt = Backtester()
    result = bt.run_backtest(df, pred_col)
    return result


if __name__ == "__main__":
    # 测试
    from src.data_manager import get_data_manager
    from src.feature import prepare_data
    from src.model import train_model
    
    dm = get_data_manager()
    df = dm.get_stock_data('600808')
    
    if df is not None:
        # 准备数据
        data = prepare_data(df)
        if data:
            X_train, X_test, y_train, y_test, df_test = data
            
            # 训练模型
            model = train_model(X_train, y_train)
            preds = model.predict(X_test)
            
            # 添加预测到测试集
            df_test['pred'] = preds
            
            # 回测
            bt = Backtester()
            result = bt.run_backtest(df_test)
            
            print(bt.summary(result))
