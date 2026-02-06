# 信号生成模块
import pandas as pd
import numpy as np
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

def generate_trading_signals(predictions: np.ndarray, threshold: float = 0.0) -> List[int]:
    """
    根据预测结果生成交易信号
    
    Parameters:
        predictions: 预测结果（未来收益）
        threshold: 生成信号的阈值
    
    Returns:
        List[int]: 交易信号列表 (-1: 卖出, 0: 持有, 1: 买入)
    """
    signals = []
    for pred in predictions:
        if pred > threshold:
            signals.append(1)   # 买入信号
        elif pred < -threshold:
            signals.append(-1)  # 卖出信号
        else:
            signals.append(0)   # 持有信号
    
    return signals

def generate_signals_with_confidence(predictions: np.ndarray, 
                                   buy_threshold: float = 0.02, 
                                   sell_threshold: float = -0.02) -> List[Tuple[int, float]]:
    """
    根据预测结果生成带置信度的交易信号
    
    Parameters:
        predictions: 预测结果（未来收益）
        buy_threshold: 买入阈值
        sell_threshold: 卖出阈值
    
    Returns:
        List[Tuple[int, float]]: (信号, 置信度) 列表
    """
    signals = []
    for pred in predictions:
        if pred > buy_threshold:
            # 买入信号，置信度为正收益率
            confidence = min(pred / (buy_threshold * 2), 1.0)  # 标准化置信度到0-1
            signals.append((1, confidence))
        elif pred < sell_threshold:
            # 卖出信号，置信度为负收益率的绝对值
            confidence = min(abs(pred) / (abs(sell_threshold) * 2), 1.0)  # 标准化置信度到0-1
            signals.append((-1, confidence))
        else:
            # 持有信号，置信度为0
            signals.append((0, 0.0))
    
    return signals

def apply_signal_rules(df: pd.DataFrame, signals: List[int]) -> pd.DataFrame:
    """
    将交易信号应用到数据中
    
    Parameters:
        df: 股票数据
        signals: 交易信号列表
    
    Returns:
        pd.DataFrame: 添加了交易信号的数据
    """
    df = df.copy()
    # 只对有预测结果的部分添加信号
    df.loc[df.index[-len(signals):], 'signal'] = signals
    return df

def position_sizing(confidence: float, max_position: float = 0.2) -> float:
    """
    根据信号置信度确定头寸大小
    
    Parameters:
        confidence: 信号置信度 (0-1)
        max_position: 最大头寸比例
    
    Returns:
        float: 建议头寸比例
    """
    return confidence * max_position

def risk_management(df: pd.DataFrame, 
                   stop_loss: float = 0.05, 
                   take_profit: float = 0.1) -> pd.DataFrame:
    """
    风险管理规则
    
    Parameters:
        df: 包含信号的数据
        stop_loss: 止损比例
        take_profit: 止盈比例
    
    Returns:
        pd.DataFrame: 添加了风险管理信号的数据
    """
    df = df.copy()
    
    # 这里可以添加更复杂的风控逻辑
    df['stop_loss_level'] = df['close'] * (1 - stop_loss)
    df['take_profit_level'] = df['close'] * (1 + take_profit)
    
    return df

def generate_trading_strategy(df: pd.DataFrame, predictions: np.ndarray) -> pd.DataFrame:
    """
    生成完整的交易策略
    
    Parameters:
        df: 股票数据
        predictions: 预测结果
    
    Returns:
        pd.DataFrame: 包含完整交易策略的数据
    """
    print("开始生成交易策略...")
    
    # 生成带置信度的信号
    signals_with_confidence = generate_signals_with_confidence(predictions)
    
    # 提取信号和置信度
    signals = [signal for signal, _ in signals_with_confidence]
    confidences = [confidence for _, confidence in signals_with_confidence]
    
    # 应用信号到数据
    df_with_signals = apply_signal_rules(df, signals)
    
    # 添加置信度
    df_with_signals.loc[df_with_signals.index[-len(confidences):], 'confidence'] = confidences
    
    # 计算头寸大小
    position_sizes = [position_sizing(conf) for conf in confidences]
    df_with_signals.loc[df_with_signals.index[-len(position_sizes):], 'position_size'] = position_sizes
    
    # 风险管理
    df_with_strategy = risk_management(df_with_signals)
    
    print(f"生成交易信号数量: {len(signals)}")
    print(f"买入信号: {sum(1 for s in signals if s == 1)}")
    print(f"卖出信号: {sum(1 for s in signals if s == -1)}")
    print(f"持有信号: {sum(1 for s in signals if s == 0)}")
    
    return df_with_strategy

if __name__ == "__main__":
    # 测试信号生成
    import numpy as np
    
    # 模拟预测结果
    np.random.seed(42)
    predictions = np.random.randn(100) * 0.03  # 模拟收益率预测
    
    # 生成交易信号
    signals = generate_trading_signals(predictions, threshold=0.01)
    print("交易信号示例 (前20个):", signals[:20])
    
    # 生成带置信度的信号
    signals_with_confidence = generate_signals_with_confidence(predictions)
    print("带置信度的信号示例 (前5个):", signals_with_confidence[:5])
    
    # 测试完整策略生成
    from data_loader import load_stock_data
    from feature_engineering import feature_engineering_pipeline
    
    data = load_stock_data()
    processed_data = feature_engineering_pipeline(data)
    
    # 使用最后100个预测
    test_predictions = np.random.randn(100) * 0.02
    strategy_data = generate_trading_strategy(processed_data, test_predictions)
    
    print("策略数据列:", strategy_data.columns.tolist())
    print("最后几行策略数据:")
    print(strategy_data[['date', 'close', 'signal', 'confidence', 'position_size']].tail())