"""
可视化模块 - 支持中文字体显示
使用 chinese_font_fix.py 进行字体配置
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

# 导入并应用中文字体修复
try:
    from chinese_font_fix import apply_chinese_font_fix
    apply_chinese_font_fix()
    print("✅ 中文字体配置已应用")
except Exception as e:
    print(f"⚠️  中文字体配置失败: {e}")
    # 使用默认配置
    plt.rcParams['font.family'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

def plot_stock_price(df: pd.DataFrame, title: str = "股票价格走势") -> plt.Figure:
    """绘制股票价格走势图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['date'], df['close'], linewidth=1, label='收盘价')
    ax.set_title(title)
    ax.set_xlabel('日期')
    ax.set_ylabel('价格')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 格式化日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def plot_predictions_vs_actual(df: pd.DataFrame, predictions: np.ndarray, 
                              title: str = "预测值与实际值对比") -> plt.Figure:
    """绘制预测值与实际值对比"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 只绘制有预测值的部分
    actual_values = df['target'].tail(len(predictions)).values
    
    x = range(len(predictions))
    ax.plot(x, actual_values, label='实际收益率', alpha=0.7)
    ax.plot(x, predictions, label='预测收益率', alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel('时间点')
    ax.set_ylabel('收益率')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_feature_importance(importance_df: pd.DataFrame, top_n: int = 20) -> plt.Figure:
    """绘制特征重要性"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    top_features = importance_df.head(top_n)
    bars = ax.barh(range(len(top_features)), top_features['importance'])
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'])
    ax.set_xlabel('重要性')
    ax.set_title(f'前{top_n}个重要特征')
    ax.invert_yaxis()
    
    # 添加数值标签
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}', ha='left', va='center', fontsize=8)
    
    plt.tight_layout()
    return fig

def plot_backtest_results(results: dict) -> plt.Figure:
    """绘制回测结果"""
    if 'portfolio_history' not in results:
        print("没有投资组合历史数据用于绘图")
        return None
    
    portfolio_df = results['portfolio_history']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制总资产价值
    ax.plot(portfolio_df.index, portfolio_df['total_value'], 
            label='策略收益', linewidth=2)
    
    # 绘制买入持有策略作为基准
    initial_price = portfolio_df['price'].iloc[0]
    buy_hold_value = results['initial_cash'] * (portfolio_df['price'] / initial_price)
    ax.plot(portfolio_df.index, buy_hold_value, 
            label='买入持有', linewidth=2, linestyle='--')
    
    ax.set_title('回测结果对比')
    ax.set_xlabel('日期')
    ax.set_ylabel('资产价值')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 格式化日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def plot_drawdown(results: dict) -> plt.Figure:
    """绘制回撤图"""
    if 'portfolio_history' not in results:
        print("没有投资组合历史数据用于绘图")
        return None
    
    portfolio_df = results['portfolio_history']
    
    # 计算回撤
    peak = portfolio_df['total_value'].expanding(min_periods=1).max()
    drawdown = (portfolio_df['total_value'] - peak) / peak
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.fill_between(portfolio_df.index, drawdown, 0, alpha=0.3, color='red')
    ax.plot(portfolio_df.index, drawdown, color='red', linewidth=1)
    ax.set_title('策略回撤分析')
    ax.set_xlabel('日期')
    ax.set_ylabel('回撤比例')
    ax.grid(True, alpha=0.3)
    
    # 格式化日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def plot_trading_signals(df: pd.DataFrame) -> plt.Figure:
    """绘制交易信号"""
    # 只绘制有信号的部分
    signal_df = df[df['signal'].notna()].copy()
    
    if signal_df.empty:
        print("没有交易信号数据用于绘图")
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(signal_df['date'], signal_df['close'], linewidth=1, label='价格')
    
    # 标记买入信号
    buy_signals = signal_df[signal_df['signal'] == 1]
    ax.scatter(buy_signals['date'], buy_signals['close'], 
              color='green', marker='^', s=100, label='买入信号', alpha=0.7)
    
    # 标记卖出信号
    sell_signals = signal_df[signal_df['signal'] == -1]
    ax.scatter(sell_signals['date'], sell_signals['close'], 
              color='red', marker='v', s=100, label='卖出信号', alpha=0.7)
    
    ax.set_title('交易信号分布')
    ax.set_xlabel('日期')
    ax.set_ylabel('价格')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 格式化日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def create_performance_report(results: Dict[str, Any], backtest_results: Dict[str, Any]) -> plt.Figure:
    """创建综合性能报告图表"""
    try:
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('股票预测策略综合性能报告', fontsize=16, fontweight='bold')
        
        # 1. 股价走势
        ax1 = plt.subplot(2, 3, 1)
        if 'raw_data' in results:
            data = results['raw_data']
            ax1.plot(data['date'], data['close'], linewidth=1)
            ax1.set_title('股价走势')
            ax1.set_xlabel('日期')
            ax1.set_ylabel('价格')
            ax1.grid(True, alpha=0.3)
            
            # 格式化日期
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. 预测vs实际
        ax2 = plt.subplot(2, 3, 2)
        if 'predictions' in results and 'processed_data' in results:
            predictions = results['predictions']
            df = results['processed_data']
            actual_values = df['target'].tail(len(predictions)).values
            
            x = range(len(predictions))
            ax2.plot(x, actual_values, label='实际', alpha=0.7)
            ax2.plot(x, predictions, label='预测', alpha=0.7)
            ax2.set_title('预测vs实际收益率')
            ax2.set_xlabel('时间点')
            ax2.set_ylabel('收益率')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # 3. 策略vs基准
        ax3 = plt.subplot(2, 3, 3)
        if backtest_results and 'portfolio_history' in backtest_results:
            portfolio_df = backtest_results['portfolio_history']
            ax3.plot(portfolio_df.index, portfolio_df['total_value'], 
                    label='策略', linewidth=2)
            
            initial_price = portfolio_df['price'].iloc[0]
            buy_hold_value = backtest_results['initial_cash'] * (portfolio_df['price'] / initial_price)
            ax3.plot(portfolio_df.index, buy_hold_value, 
                    label='买入持有', linewidth=2, linestyle='--')
            
            ax3.set_title('策略vs买入持有')
            ax3.set_xlabel('日期')
            ax3.set_ylabel('资产价值')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 格式化日期
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax3.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # 4. 回撤分析
        ax4 = plt.subplot(2, 3, 4)
        if backtest_results and 'portfolio_history' in backtest_results:
            portfolio_df = backtest_results['portfolio_history']
            peak = portfolio_df['total_value'].expanding(min_periods=1).max()
            drawdown = (portfolio_df['total_value'] - peak) / peak
            
            ax4.fill_between(portfolio_df.index, drawdown, 0, alpha=0.3, color='red')
            ax4.plot(portfolio_df.index, drawdown, color='red', linewidth=1)
            ax4.set_title('回撤分析')
            ax4.set_xlabel('日期')
            ax4.set_ylabel('回撤比例')
            ax4.grid(True, alpha=0.3)
            
            # 格式化日期
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax4.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        
        # 5. 交易信号
        ax5 = plt.subplot(2, 3, 5)
        if 'strategy_data' in results:
            signal_df = results['strategy_data']
            signal_df = signal_df[signal_df['signal'].notna()].copy()
            
            if not signal_df.empty:
                ax5.plot(signal_df['date'], signal_df['close'], linewidth=1, label='价格')
                
                buy_signals = signal_df[signal_df['signal'] == 1]
                ax5.scatter(buy_signals['date'], buy_signals['close'], 
                           color='green', marker='^', s=50, label='买入', alpha=0.7)
                
                sell_signals = signal_df[signal_df['signal'] == -1]
                ax5.scatter(sell_signals['date'], sell_signals['close'], 
                           color='red', marker='v', s=50, label='卖出', alpha=0.7)
                
                ax5.set_title('交易信号')
                ax5.set_xlabel('日期')
                ax5.set_ylabel('价格')
                ax5.legend()
                ax5.grid(True, alpha=0.3)
                
                # 格式化日期
                ax5.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                ax5.xaxis.set_major_locator(mdates.MonthLocator())
                plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
        
        # 6. 性能指标文本
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        if backtest_results:
            performance_text = [
                "策略性能指标:",
                f"初始资金: {backtest_results.get('initial_cash', 0):,.0f}",
                f"最终价值: {backtest_results.get('final_value', 0):,.0f}",
                f"总收益率: {backtest_results.get('total_return', 0):.2%}",
                f"年化收益: {backtest_results.get('annual_return', 0):.2%}",
                f"波动率: {backtest_results.get('volatility', 0):.2%}",
                f"夏普比率: {backtest_results.get('sharpe_ratio', 0):.2f}",
                f"最大回撤: {backtest_results.get('max_drawdown', 0):.2%}",
                f"交易次数: {backtest_results.get('total_trades', 0)}",
                f"胜率: {backtest_results.get('win_rate', 0):.2%}"
            ]
            
            for i, line in enumerate(performance_text):
                ax6.text(0.1, 0.9 - i*0.08, line, transform=ax6.transAxes, 
                        fontsize=10, verticalalignment='top')
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        print(f"创建性能报告时出错: {e}")
        return None

def save_figure(fig: plt.Figure, filename: str, output_dir: str = "output") -> None:
    """保存图表"""
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    
    # 使用更高的DPI和PNG格式确保最好质量
    fig.savefig(filepath, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none', format='png')
    print(f"图表已保存到: {filepath}")

# 测试函数
if __name__ == "__main__":
    print("📊 可视化模块测试")
    
    # 首先测试字体配置
    try:
        # 测试图表生成
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        sample_data = pd.DataFrame({
            'date': dates,
            'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'signal': np.random.choice([0, 1, -1], 100, p=[0.7, 0.15, 0.15])
        })
        
        # 测试中文图表
        fig = plot_stock_price(sample_data, "股价走势图测试")
        save_figure(fig, "/tmp/visualization_test_chinese.png")
        plt.close(fig)
        print("✅ 中文图表测试完成")
        
    except Exception as e:
        print(f"❌ 图表测试失败: {e}")