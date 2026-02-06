# 配置文件
import os

# 数据配置
DATA_CONFIG = {
    'start_date': '20200101',  # 数据开始日期
    'end_date': '20241231',    # 数据结束日期
    'target_stock': 'sh',      # 目标股票代码 ('sh' 为上证指数)
    'predict_days': 20,        # 预测天数 (约1个月)
    'feature_windows': [5, 10, 20, 30, 60]  # 特征计算窗口
}

# 模型配置
MODEL_CONFIG = {
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'min_data_in_leaf': 20,           # 增加最小叶子节点样本数，避免过拟合
    'min_gain_to_split': 0.0,          # 允许微小的增益分裂
    'verbose': -1,                     # 设置为-1来抑制日志输出
    'seed': 42
}

# 回测配置
BACKTEST_CONFIG = {
    'initial_cash': 100000,    # 初始资金
    'transaction_fee': 0.001,  # 交易费率
    'slippage': 0.001          # 滑点
}

# 可视化配置
VISUALIZATION_CONFIG = {
    'figure_size': (12, 8),
    'style': 'seaborn-v0_8-darkgrid'
}

# 输出路径
OUTPUT_PATH = 'output'
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)