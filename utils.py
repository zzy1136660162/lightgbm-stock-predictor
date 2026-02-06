# 工具函数模块
import pandas as pd
import numpy as np
import yaml
import os

def load_config(config_path='config.yaml'):
    """
    加载配置文件
    
    Parameters:
        config_path: 配置文件路径
    
    Returns:
        dict: 配置参数
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

def save_results(results, filename):
    """
    保存结果到文件
    
    Parameters:
        results: 结果数据
        filename: 保存的文件名
    """
    if isinstance(results, pd.DataFrame):
        if filename.endswith('.csv'):
            results.to_csv(filename, index=False)
        elif filename.endswith('.parquet'):
            results.to_parquet(filename, index=False)
        else:
            results.to_csv(filename, index=False)
    else:
        # 保存为JSON格式
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

def calculate_ic(predicted, actual):
    """
    计算信息系数(IC)
    
    Parameters:
        predicted: 预测值
        actual: 实际值
    
    Returns:
        float: IC值
    """
    if len(predicted) != len(actual):
        raise ValueError("预测值和实际值长度不一致")
    
    # 计算秩相关系数
    ic = pd.Series(predicted).corr(pd.Series(actual), method='spearman')
    return ic

def calculate_rank_ic(predicted, actual):
    """
    计算秩信息系数(RankIC)
    
    Parameters:
        predicted: 预测值
        actual: 实际值
    
    Returns:
        float: RankIC值
    """
    if len(predicted) != len(actual):
        raise ValueError("预测值和实际值长度不一致")
    
    # 计算秩相关系数
    rank_pred = pd.Series(predicted).rank()
    rank_actual = pd.Series(actual).rank()
    rank_ic = rank_pred.corr(rank_actual, method='spearman')
    return rank_ic

def group_return_analysis(predictions, actual, n_groups=10):
    """
    分组收益分析
    
    Parameters:
        predictions: 预测值
        actual: 实际值
        n_groups: 分组数量
    
    Returns:
        pd.DataFrame: 分组收益分析结果
    """
    if len(predictions) != len(actual):
        raise ValueError("预测值和实际值长度不一致")
    
    # 创建DataFrame
    df = pd.DataFrame({
        'predicted': predictions,
        'actual': actual
    })
    
    # 按预测值分组
    df['group'] = pd.qcut(df['predicted'], n_groups, labels=False, duplicates='drop')
    
    # 计算每组的平均实际收益
    group_returns = df.groupby('group')['actual'].mean().reset_index()
    group_returns.columns = ['group', 'avg_return']
    group_returns['group'] = group_returns['group'] + 1  # 分组从1开始
    
    return group_returns

# 示例使用
if __name__ == "__main__":
    # 测试工具函数
    import numpy as np
    
    # 测试IC计算
    np.random.seed(42)
    pred = np.random.randn(100)
    actual = pred + np.random.randn(100) * 0.3
    
    ic = calculate_ic(pred, actual)
    rank_ic = calculate_rank_ic(pred, actual)
    
    print(f"IC: {ic:.4f}")
    print(f"RankIC: {rank_ic:.4f}")
    
    # 测试分组收益分析
    group_returns = group_return_analysis(pred, actual, n_groups=5)
    print("\\n分组收益分析:")
    print(group_returns)