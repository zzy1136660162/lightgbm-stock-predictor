# 模型评估模块
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils import calculate_ic, calculate_rank_ic, group_return_analysis

def evaluate_predictions(predictions, actual, dates=None):
    """
    评估预测结果
    
    Parameters:
        predictions: 预测值数组
        actual: 实际值数组
        dates: 日期数组（可选）
    
    Returns:
        dict: 评估结果
    """
    if len(predictions) != len(actual):
        raise ValueError("预测值和实际值长度不一致")
    
    # 计算基本统计指标
    mse = np.mean((predictions - actual) ** 2)
    mae = np.mean(np.abs(predictions - actual))
    rmse = np.sqrt(mse)
    
    # 计算IC和RankIC
    ic = calculate_ic(predictions, actual)
    rank_ic = calculate_rank_ic(predictions, actual)
    
    # 计算方向准确性
    pred_direction = np.sign(predictions)
    actual_direction = np.sign(actual)
    direction_accuracy = np.mean(pred_direction == actual_direction)
    
    results = {
        'MSE': mse,
        'MAE': mae,
        'RMSE': rmse,
        'IC': ic,
        'RankIC': rank_ic,
        'DirectionAccuracy': direction_accuracy
    }
    
    return results

def plot_predictions_vs_actual(predictions, actual, dates=None, title="Predictions vs Actual"):
    """
    绘制预测值vs实际值散点图
    
    Parameters:
        predictions: 预测值数组
        actual: 实际值数组
        dates: 日期数组（可选）
        title: 图表标题
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(actual, predictions, alpha=0.5)
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.title(title)
    
    # 添加拟合线
    z = np.polyfit(actual, predictions, 1)
    p = np.poly1d(z)
    plt.plot(actual, p(actual), "r--", alpha=0.8)
    
    # 添加相关系数
    correlation = np.corrcoef(actual, predictions)[0, 1]
    plt.text(0.05, 0.95, f'Correlation: {correlation:.4f}', 
             transform=plt.gca().transAxes, verticalalignment='top')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_ic_analysis(predictions, actual, dates=None):
    """
    绘制IC分析图
    
    Parameters:
        predictions: 预测值数组
        actual: 实际值数组
        dates: 日期数组（可选）
    """
    # 计算滚动IC
    window = min(20, len(predictions) // 10)  # 窗口大小
    rolling_ic = []
    
    for i in range(window, len(predictions)):
        ic = calculate_ic(predictions[i-window:i], actual[i-window:i])
        rolling_ic.append(ic)
    
    plt.figure(figsize=(12, 6))
    
    # 绘制滚动IC
    if dates is not None and len(dates) == len(rolling_ic):
        plt.plot(dates[window:], rolling_ic, label='Rolling IC')
    else:
        plt.plot(rolling_ic, label='Rolling IC')
    
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.7)
    plt.xlabel('Time')
    plt.ylabel('IC')
    plt.title('Rolling Information Coefficient (IC)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # 绘制IC分布直方图
    plt.figure(figsize=(10, 6))
    plt.hist(rolling_ic, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('IC')
    plt.ylabel('Frequency')
    plt.title('Distribution of Rolling IC')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_group_returns(predictions, actual, n_groups=10):
    """
    绘制分组收益图
    
    Parameters:
        predictions: 预测值数组
        actual: 实际值数组
        n_groups: 分组数量
    """
    # 分组收益分析
    group_returns = group_return_analysis(predictions, actual, n_groups)
    
    plt.figure(figsize=(10, 6))
    plt.bar(group_returns['group'], group_returns['avg_return'], 
            color='skyblue', edgecolor='navy', alpha=0.7)
    plt.xlabel('Group (Sorted by Prediction)')
    plt.ylabel('Average Actual Return')
    plt.title('Group Return Analysis')
    plt.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, v in enumerate(group_returns['avg_return']):
        plt.text(i+1, v + np.sign(v)*0.0001, f'{v:.4f}', 
                ha='center', va='bottom' if v >= 0 else 'top')
    
    plt.tight_layout()
    plt.show()
    
    return group_returns

def generate_evaluation_report(predictions, actual, dates=None):
    """
    生成完整的评估报告
    
    Parameters:
        predictions: 预测值数组
        actual: 实际值数组
        dates: 日期数组（可选）
    
    Returns:
        dict: 完整的评估报告
    """
    # 基本评估指标
    basic_metrics = evaluate_predictions(predictions, actual, dates)
    
    # 打印评估结果
    print("=== 模型评估报告 ===")
    print(f"MSE: {basic_metrics['MSE']:.6f}")
    print(f"MAE: {basic_metrics['MAE']:.6f}")
    print(f"RMSE: {basic_metrics['RMSE']:.6f}")
    print(f"IC: {basic_metrics['IC']:.4f}")
    print(f"RankIC: {basic_metrics['RankIC']:.4f}")
    print(f"Direction Accuracy: {basic_metrics['DirectionAccuracy']:.4f}")
    
    # 绘制图表
    plot_predictions_vs_actual(predictions, actual, dates)
    plot_ic_analysis(predictions, actual, dates)
    group_returns = plot_group_returns(predictions, actual)
    
    # 返回完整报告
    report = {
        'basic_metrics': basic_metrics,
        'group_returns': group_returns
    }
    
    return report

# 示例使用
if __name__ == "__main__":
    # 生成模拟数据进行测试
    np.random.seed(42)
    n_samples = 1000
    
    # 模拟预测值和实际值（具有一定相关性）
    true_signal = np.random.randn(n_samples)
    predictions = true_signal + np.random.randn(n_samples) * 0.5
    actual = true_signal * 0.3 + np.random.randn(n_samples) * 0.7
    
    # 生成日期
    dates = pd.date_range('2020-01-01', periods=n_samples, freq='D')
    
    # 生成评估报告
    report = generate_evaluation_report(predictions, actual, dates)
    
    print("\\n评估完成")