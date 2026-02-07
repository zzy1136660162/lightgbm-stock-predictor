# -*- coding: utf-8 -*-
"""
单股票测试脚本

使用:
    python main.py --stock 600808
    python main.py --stock 600519 --show-chart
"""

import argparse
import os
import sys
import pandas as pd

# 添加项目根目录
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from config.settings import DEFAULT_STOCKS
from src.data_manager import DataManager
from src.feature import FeatureEngineer
from src.model import StockModel
from src.backtest import Backtester


def find_stock_name(code: str) -> str:
    """查找股票名称"""
    for c, name in DEFAULT_STOCKS:
        if c == code:
            return name
    return '未知'


def run_single_stock(code: str, show_chart: bool = False) -> dict:
    """
    运行单只股票测试
    
    Args:
        code: 股票代码
        show_chart: 是否显示图表
    
    Returns:
        回测结果
    """
    name = find_stock_name(code)
    
    print("=" * 60)
    print(f"股票回测: {code} {name}")
    print("=" * 60)
    
    # 1. 获取数据
    dm = DataManager()
    df = dm.get_stock_data(code)
    
    if df is None:
        print(f"❌ 无法获取 {code} 的数据")
        return None
    
    print(f"✅ 数据加载: {len(df)} 条")
    print(f"   时间范围: {df['日期'].min()} ~ {df['日期'].max()}")
    
    # 2. 特征工程
    fe = FeatureEngineer()
    df = fe.calculate_features(df)
    df = fe.add_target(df)
    df_clean = fe.clean_data(df)
    
    if df_clean is None:
        print("❌ 特征计算失败")
        return None
    
    print(f"✅ 特征计算: {len(df_clean)} 条有效数据")
    print(f"   特征数: {len(fe.feature_cols)}")
    
    # 3. 分割数据
    X_train, X_test, y_train, y_test = fe.split_data(df_clean)
    print(f"✅ 数据分割: 训练集 {len(X_train)} / 测试集 {len(X_test)}")
    
    # 4. 训练模型
    model = StockModel()
    model.train(X_train, y_train)
    print("✅ 模型训练完成")
    
    # 5. 预测
    preds = model.predict(X_test)
    print(f"✅ 预测完成: {len(preds)} 个")
    
    # 6. 回测
    test_start = len(df_clean) - 100
    df_test = df_clean.iloc[test_start:].copy()
    df_test['pred'] = preds
    
    bt = Backtester()
    result = bt.run_backtest(df_test)
    
    # 7. 输出结果
    print("\n" + "=" * 60)
    print("回测结果")
    print("=" * 60)
    print(f"买入持有收益: {result['buyhold_return']:+.2f}%")
    print(f"策略收益:      {result['strategy_return']:+.2f}%")
    print(f"策略收益(净):  {result['strategy_return_net']:+.2f}%")
    print(f"准确率:        {result['accuracy']:.1%}")
    print(f"交易次数:      {result['trades']}")
    
    # 特征重要性
    print("\n【特征重要性 Top 5】")
    importance = model.get_feature_importance()
    print(importance.head(5).to_string(index=False))
    
    return result


def main():
    parser = argparse.ArgumentParser(description='股票预测回测')
    parser.add_argument('--stock', type=str, default='600808',
                       help='股票代码 (默认: 600808)')
    parser.add_argument('--chart', action='store_true',
                       help='显示图表')
    
    args = parser.parse_args()
    
    run_single_stock(args.stock, args.chart)


if __name__ == "__main__":
    main()
