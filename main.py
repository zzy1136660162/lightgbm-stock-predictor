import pandas as pd
import numpy as np
import warnings
import os
import argparse
from datetime import datetime
warnings.filterwarnings('ignore')

# 导入项目模块
from config import DATA_CONFIG, MODEL_CONFIG, BACKTEST_CONFIG
from data_loader import load_stock_data
from feature_engineering import feature_engineering_pipeline
from model import StockPredictor, walk_forward_training
from signal_generator import generate_trading_strategy
from backtester import Backtester, evaluate_strategy
from visualization import create_performance_report

def save_results(results, output_dir="output"):
    """保存结果到文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存策略数据
    if 'strategy_data' in results:
        results['strategy_data'].to_csv(f"{output_dir}/strategy_data.csv", index=False)
    
    # 保存预测结果
    if 'predictions' in results:
        pred_df = pd.DataFrame({'predictions': results['predictions']})
        pred_df.to_csv(f"{output_dir}/predictions.csv", index=False)
    
    # 保存回测结果
    if 'backtest_results' in results and results['backtest_results']:
        bt_results = results['backtest_results']
        if 'portfolio_history' in bt_results:
            bt_results['portfolio_history'].to_csv(f"{output_dir}/portfolio_history.csv")
        if 'trade_log' in bt_results:
            pd.DataFrame(bt_results['trade_log']).to_csv(f"{output_dir}/trade_log.csv", index=False)

def run_pipeline(stock_code=None, use_walk_forward=True, save_output=True):
    """运行完整的预测流水线"""
    print("=== LightGBM 股票1个月预测基线模型 ===")
    start_time = datetime.now()
    print(f"开始时间: {start_time}")
    
    results = {}
    
    try:
        # 1. 数据加载
        print("\n1. 加载股票数据...")
        data = load_stock_data(stock_code)
        print(f"数据加载完成，共{len(data)}条记录")
        print(f"数据时间范围: {data['date'].min()} 到 {data['date'].max()}")
        results['raw_data'] = data
        
        # 2. 特征工程
        print("\n2. 执行特征工程...")
        processed_data = feature_engineering_pipeline(data)
        print(f"特征工程完成，共{len(processed_data)}条记录，{len(processed_data.columns)}个特征")
        results['processed_data'] = processed_data
        
        # 3. 模型训练
        print("\n3. 模型训练...")
        if use_walk_forward:
            print("使用Walk-forward训练方法...")
            wf_results = walk_forward_training(processed_data, train_period=1000, test_period=200)
            print(f"训练完成，共{len(wf_results)}个训练周期")
            
            # 保存walk-forward结果摘要
            wf_summary = []
            for i, result in enumerate(wf_results):
                wf_summary.append({
                    'period': i+1,
                    'train_start': result['train_period'][0],
                    'train_end': result['train_period'][1],
                    'test_start': result['test_period'][0],
                    'test_end': result['test_period'][1],
                    'rmse': result['rmse'],
                    'mae': result['mae']
                })
            
            wf_summary_df = pd.DataFrame(wf_summary)
            results['wf_summary'] = wf_summary_df
            
            # 使用最后一个模型的结果
            last_result = wf_results[-1]
            predictions = last_result['predictions']
            predictor = last_result['predictor']
        else:
            print("使用标准训练方法...")
            predictor = StockPredictor(MODEL_CONFIG)
            X, y = predictor.prepare_data(processed_data)
            predictor.train(X, y)
            predictions = predictor.predict(X)
            
            # 保存特征重要性
            importance = predictor.get_feature_importance()
            results['feature_importance'] = importance
        
        results['predictor'] = predictor
        results['predictions'] = predictions
        print(f"预测完成，共生成{len(predictions)}个预测结果")
        
        # 4. 信号生成
        print("\n4. 生成交易策略...")
        strategy_data = generate_trading_strategy(processed_data, predictions)
        results['strategy_data'] = strategy_data
        print("策略生成完成")
        
        # 5. 回测
        print("\n5. 运行回测...")
        backtester = Backtester(
            initial_cash=BACKTEST_CONFIG['initial_cash'],
            transaction_fee=BACKTEST_CONFIG['transaction_fee'],
            slippage=BACKTEST_CONFIG['slippage']
        )
        backtest_results = backtester.run_backtest(strategy_data)
        results['backtest_results'] = backtest_results
        print("回测完成")
        
        # 6. 评估策略
        print("\n6. 评估策略表现...")
        evaluate_strategy(backtest_results)
        
        # 7. 生成可视化报告
        print("\n7. 生成可视化报告...")
        fig = create_performance_report(results, backtest_results)
        if fig:
            fig.savefig("output/performance_report.png", dpi=300, bbox_inches='tight')
            print("可视化报告已保存到 output/performance_report.png")
        
        # 8. 保存结果
        if save_output:
            print("\n8. 保存结果...")
            save_results(results)
            print("结果已保存到 output 目录")
        
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        print(f"\n=== 项目运行完成 ===")
        print(f"结束时间: {end_time}")
        print(f"运行时长: {elapsed_time}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ 运行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    parser = argparse.ArgumentParser(description='LightGBM 股票1个月预测基线模型')
    parser.add_argument('--stock', type=str, default=None, 
                       help='股票代码 (默认: 上证指数)')
    parser.add_argument('--no-walk-forward', action='store_true',
                       help='不使用walk-forward训练')
    parser.add_argument('--no-save', action='store_true',
                       help='不保存结果到文件')
    
    args = parser.parse_args()
    
    # 运行流水线
    results = run_pipeline(
        stock_code=args.stock,
        use_walk_forward=not args.no_walk_forward,
        save_output=not args.no_save
    )
    
    if results:
        print("\n✅ 项目成功完成!")
        return 0
    else:
        print("\n❌ 项目执行失败!")
        return 1

if __name__ == "__main__":
    exit(main())