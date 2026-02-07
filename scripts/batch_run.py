# -*- coding: utf-8 -*-
"""
批量回测脚本 - 并行处理多只股票

功能:
1. 下载/读取股票数据
2. 特征工程
3. 模型训练
4. 回测评估
5. 生成汇总报告

使用:
    python scripts/batch_run.py [--workers N] [--force-update]
"""

import os
import sys
import argparse
import time
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

# 添加项目根目录到路径
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from config.settings import DEFAULT_STOCKS, RESULTS_DIR
from src.data_manager import DataManager
from src.feature import FeatureEngineer
from src.model import StockModel
from src.backtest import Backtester


class BatchRunner:
    """批量回测运行器"""
    
    def __init__(self, workers: int = None, force_update: bool = False):
        """
        初始化
        
        Args:
            workers: 并行线程数（默认CPU核心数）
            force_update: 是否强制更新数据
        """
        self.workers = workers or multiprocessing.cpu_count()
        self.force_update = force_update
        self.data_manager = DataManager()
        self.results = []
    
    def process_single_stock(self, stock_info: tuple) -> dict:
        """
        处理单只股票（核心流程）
        
        Args:
            stock_info: (code, name)
        
        Returns:
            回测结果字典
        """
        code, name = stock_info
        
        try:
            # 1. 获取数据
            df = self.data_manager.get_stock_data(code, self.force_update)
            if df is None or len(df) < 400:
                return {
                    'code': code, 'name': name,
                    'status': 'failed',
                    'reason': '数据不足'
                }
            
            # 2. 特征工程
            fe = FeatureEngineer()
            df = fe.calculate_features(df)
            df = fe.add_target(df)
            df_clean = fe.clean_data(df)
            
            if df_clean is None:
                return {
                    'code': code, 'name': name,
                    'status': 'failed',
                    'reason': '特征计算失败'
                }
            
            # 3. 分割数据
            X_train, X_test, y_train, y_test = fe.split_data(df_clean)
            
            # 4. 训练模型
            model = StockModel()
            model.train(X_train, y_train)
            
            # 5. 预测
            preds = model.predict(X_test)
            
            # 6. 回测
            test_start = len(df_clean) - 100
            df_test = df_clean.iloc[test_start:].copy()
            df_test['pred'] = preds
            
            bt = Backtester()
            backtest_result = bt.run_backtest(df_test)
            
            return {
                'code': code,
                'name': name,
                'status': 'success',
                'data_count': len(df),
                'buyhold_return': round(backtest_result['buyhold_return'], 1),
                'strategy_return': round(backtest_result['strategy_return'], 1),
                'accuracy': round(backtest_result['accuracy'], 2),
                'trades': backtest_result['trades']
            }
            
        except Exception as e:
            return {
                'code': code,
                'name': name,
                'status': 'error',
                'reason': str(e)[:100]
            }
    
    def run(self, stock_list: list = None) -> pd.DataFrame:
        """
        运行批量回测
        
        Args:
            stock_list: 股票列表
        
        Returns:
            结果 DataFrame
        """
        stocks = stock_list or DEFAULT_STOCKS
        total = len(stocks)
        
        print("=" * 60)
        print(f"A股批量回测 (并行: {self.workers}线程)")
        print(f"股票数量: {total}")
        print("=" * 60)
        
        self.results = []
        completed = 0
        
        # 并行处理
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self.process_single_stock, s): s for s in stocks}
            
            for future in as_completed(futures):
                stock = futures[future]
                code, name = stock
                completed += 1
                
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    if result['status'] == 'success':
                        status = '✅'
                        metrics = f"BH:{result['buyhold_return']:+.1f}% Strat:{result['strategy_return']:+.1f}% Acc:{result['accuracy']:.0%}"
                    elif result['status'] == 'failed':
                        status = '❌'
                        metrics = result.get('reason', '未知')
                    else:
                        status = '⚠️'
                        metrics = result.get('reason', '未知')
                    
                    print(f"[{completed:2d}/{total}] {code} {name} {status} {metrics}")
                    
                except Exception as e:
                    print(f"[{completed:2d}/{total}] {code} {name} ❌ 错误: {e}")
        
        # 生成汇总
        self.print_summary()
        
        return pd.DataFrame([r for r in self.results if r['status'] == 'success'])
    
    def print_summary(self):
        """打印汇总报告"""
        success_results = [r for r in self.results if r['status'] == 'success']
        total = len(self.results)
        success = len(success_results)
        
        print("\n" + "=" * 60)
        print("回测汇总")
        print("=" * 60)
        print(f"分析股票: {total} 只")
        print(f"成功: {success} 只")
        print(f"失败: {total - success} 只")
        
        if success == 0:
            print("\n没有成功的回测结果!")
            return
        
        df = pd.DataFrame(success_results)
        
        # 统计
        positive_strat = len(df[df['strategy_return'] > 0])
        print(f"正收益策略: {positive_strat} 只 ({positive_strat/success:.0%})")
        print(f"平均买入持有: {df['buyhold_return'].mean():.1f}%")
        print(f"平均策略收益: {df['strategy_return'].mean():.1f}%")
        print(f"平均准确率: {df['accuracy'].mean():.1%}")
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(RESULTS_DIR, f'backtest_results_{timestamp}.csv')
        df.to_csv(output_file, index=False)
        print(f"\n详细结果已保存到: {output_file}")
        
        # Top10 / Bottom10
        df_sorted = df.sort_values('strategy_return', ascending=False)
        
        print("\n【收益Top 10】")
        print(df_sorted.head(10)[['code', 'name', 'buyhold_return', 'strategy_return', 'accuracy']].to_string(index=False))
        
        print("\n【收益Bottom 10】")
        print(df_sorted.tail(10)[['code', 'name', 'buyhold_return', 'strategy_return', 'accuracy']].to_string(index=False))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量股票回测')
    parser.add_argument('--workers', type=int, default=None,
                       help='并行线程数 (默认: CPU核心数)')
    parser.add_argument('--force-update', action='store_true',
                       help='强制更新数据')
    parser.add_argument('--stock-list', type=str, default=None,
                       help='股票列表文件路径')
    
    args = parser.parse_args()
    
    # 加载股票列表
    stock_list = None
    if args.stock_list and os.path.exists(args.stock_list):
        df = pd.read_csv(args.stock_list)
        stock_list = list(zip(df['代码'].astype(str).str.zfill(6), df['名称']))
    
    # 运行
    runner = BatchRunner(workers=args.workers, force_update=args.force_update)
    runner.run(stock_list)


if __name__ == "__main__":
    main()
