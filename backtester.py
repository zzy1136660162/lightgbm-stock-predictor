# 回测模块
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import BACKTEST_CONFIG
import warnings
warnings.filterwarnings('ignore')

class Backtester:
    def __init__(self, initial_cash: float = None, transaction_fee: float = None, slippage: float = None):
        """
        初始化回测器
        
        Parameters:
            initial_cash: 初始资金
            transaction_fee: 交易费率
            slippage: 滑点
        """
        config = BACKTEST_CONFIG
        self.initial_cash = initial_cash or config['initial_cash']
        self.transaction_fee = transaction_fee or config['transaction_fee']
        self.slippage = slippage or config['slippage']
        
        # 回测结果
        self.cash = self.initial_cash
        self.position = 0  # 持仓数量
        self.position_value = 0  # 持仓价值
        self.total_value = self.initial_cash  # 总资产价值
        self.trade_log = []  # 交易日志
        self.portfolio_history = []  # 投资组合历史
    
    def execute_trade(self, date, signal, price, confidence=1.0, position_size=0.1):
        """
        执行交易
        
        Parameters:
            date: 交易日期
            signal: 交易信号 (-1: 卖出, 0: 持有, 1: 买入)
            price: 交易价格
            confidence: 信号置信度
            position_size: 头寸大小
        """
        # 计算可交易的头寸大小
        available_cash = self.cash * position_size * confidence
        available_position = self.position * position_size * confidence
        
        # 考虑滑点后的实际价格
        buy_price = price * (1 + self.slippage)
        sell_price = price * (1 - self.slippage)
        
        if signal == 1 and available_cash > 0:  # 买入信号
            # 计算可以买入的数量
            quantity = available_cash // buy_price
            if quantity > 0:
                cost = quantity * buy_price
                fee = cost * self.transaction_fee
                total_cost = cost + fee
                
                if total_cost <= self.cash:
                    self.cash -= total_cost
                    self.position += quantity
                    self.position_value = self.position * price
                    
                    # 记录交易
                    self.trade_log.append({
                        'date': date,
                        'action': 'BUY',
                        'price': buy_price,
                        'quantity': quantity,
                        'cost': cost,
                        'fee': fee,
                        'total_cost': total_cost,
                        'cash_after': self.cash,
                        'position_after': self.position
                    })
        
        elif signal == -1 and self.position > 0:  # 卖出信号
            # 计算可以卖出的数量
            quantity = min(int(available_position), self.position)
            if quantity > 0:
                revenue = quantity * sell_price
                fee = revenue * self.transaction_fee
                total_revenue = revenue - fee
                
                self.cash += total_revenue
                self.position -= quantity
                self.position_value = self.position * price
                
                # 记录交易
                self.trade_log.append({
                    'date': date,
                    'action': 'SELL',
                    'price': sell_price,
                    'quantity': quantity,
                    'revenue': revenue,
                    'fee': fee,
                    'total_revenue': total_revenue,
                    'cash_after': self.cash,
                    'position_after': self.position
                })
    
    def update_portfolio_value(self, date, price):
        """
        更新投资组合价值
        
        Parameters:
            date: 日期
            price: 当前价格
        """
        self.position_value = self.position * price
        self.total_value = self.cash + self.position_value
        
        # 记录投资组合历史
        self.portfolio_history.append({
            'date': date,
            'cash': self.cash,
            'position': self.position,
            'position_value': self.position_value,
            'total_value': self.total_value,
            'price': price
        })
    
    def run_backtest(self, df: pd.DataFrame) -> dict:
        """
        运行回测
        
        Parameters:
            df: 包含信号和价格的数据
            
        Returns:
            dict: 回测结果
        """
        print("开始回测...")
        
        # 初始化
        self.cash = self.initial_cash
        self.position = 0
        self.position_value = 0
        self.total_value = self.initial_cash
        self.trade_log = []
        self.portfolio_history = []
        
        # 遍历数据进行回测
        for i, row in df.iterrows():
            # 获取信号
            signal = row.get('signal', 0)
            confidence = row.get('confidence', 1.0)
            position_size = row.get('position_size', 0.1)
            
            # 执行交易
            if signal != 0 and not np.isnan(signal):
                self.execute_trade(
                    row['date'], 
                    int(signal), 
                    row['close'], 
                    confidence, 
                    position_size
                )
            
            # 更新投资组合价值
            self.update_portfolio_value(row['date'], row['close'])
        
        # 计算回测结果
        results = self.calculate_performance()
        print("回测完成")
        
        return results
    
    def calculate_performance(self) -> dict:
        """
        计算回测绩效指标
        
        Returns:
            dict: 绩效指标
        """
        if not self.portfolio_history:
            return {}
        
        # 转换为DataFrame便于计算
        portfolio_df = pd.DataFrame(self.portfolio_history)
        portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
        portfolio_df = portfolio_df.set_index('date')
        
        # 计算收益率
        portfolio_df['returns'] = portfolio_df['total_value'].pct_change()
        portfolio_df['cumulative_returns'] = (1 + portfolio_df['returns']).cumprod() - 1
        portfolio_df['strategy_cumulative_returns'] = portfolio_df['cumulative_returns']
        
        # 基准收益率（买入并持有）
        initial_price = portfolio_df['price'].iloc[0]
        final_price = portfolio_df['price'].iloc[-1]
        buy_hold_return = final_price / initial_price - 1
        
        # 绩效指标
        total_return = self.total_value / self.initial_cash - 1
        annual_return = (1 + total_return) ** (252 / len(portfolio_df)) - 1
        
        volatility = portfolio_df['returns'].std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        peak = portfolio_df['total_value'].expanding(min_periods=1).max()
        drawdown = (portfolio_df['total_value'] - peak) / peak
        max_drawdown = drawdown.min()
        
        # 胜率
        winning_trades = sum(1 for trade in self.trade_log if trade.get('total_revenue', 0) > 0 or trade.get('total_cost', 0) < 0)
        total_trades = len([t for t in self.trade_log if t['action'] in ['BUY', 'SELL']])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        results = {
            'initial_cash': self.initial_cash,
            'final_value': self.total_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'buy_hold_return': buy_hold_return,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'portfolio_history': portfolio_df,
            'trade_log': self.trade_log
        }
        
        return results

def evaluate_strategy(results: dict) -> None:
    """
    评估策略表现
    
    Parameters:
        results: 回测结果
    """
    print("\n=== 策略表现评估 ===")
    print(f"初始资金: {results['initial_cash']:,.2f}")
    print(f"最终价值: {results['final_value']:,.2f}")
    print(f"总收益率: {results['total_return']:.2%}")
    print(f"年化收益率: {results['annual_return']:.2%}")
    print(f"波动率: {results['volatility']:.2%}")
    print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    print(f"最大回撤: {results['max_drawdown']:.2%}")
    print(f"买入持有收益率: {results['buy_hold_return']:.2%}")
    print(f"总交易次数: {results['total_trades']}")
    print(f"胜率: {results['win_rate']:.2%}")
    
    # 超额收益
    excess_return = results['total_return'] - results['buy_hold_return']
    print(f"超额收益: {excess_return:.2%}")

if __name__ == "__main__":
    # 测试回测
    from data_loader import load_stock_data
    from feature_engineering import feature_engineering_pipeline
    from signal_generator import generate_trading_strategy
    
    # 加载数据
    data = load_stock_data()
    processed_data = feature_engineering_pipeline(data)
    
    # 生成模拟预测和策略
    np.random.seed(42)
    predictions = np.random.randn(100) * 0.02
    strategy_data = generate_trading_strategy(processed_data, predictions)
    
    # 运行回测
    backtester = Backtester()
    results = backtester.run_backtest(strategy_data)
    
    # 评估策略
    evaluate_strategy(results)