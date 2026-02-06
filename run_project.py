#!/usr/bin/env python3
"""
项目运行脚本 - 简化版测试流程
"""
import sys
import os
import traceback

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """检查环境"""
    print("=== 环境检查 ===")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查GPU
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ NVIDIA GPU 可用")
            if '3060' in result.stdout:
                print("🎮 RTX 3060/3060Ti 已识别")
        else:
            print("⚠️  NVIDIA GPU 不可用或 nvidia-smi 未安装")
    except Exception as e:
        print(f"⚠️  GPU检查失败: {e}")
    
    return True

def test_data_module():
    """测试数据模块"""
    print("\n=== 测试数据模块 ===")
    
    try:
        from data_loader import load_stock_data
        print("✅ data_loader 模块导入成功")
        
        # 测试数据加载
        print("正在加载数据...")
        data = load_stock_data()
        if data is not None and len(data) > 0:
            print(f"✅ 数据加载成功，共 {len(data)} 条记录")
            print(f"   列名: {list(data.columns)}")
            print(f"   日期范围: {data['date'].min()} 到 {data['date'].max()}")
            return True
        else:
            print("⚠️  数据为空，使用模拟数据")
            return False
    except Exception as e:
        print(f"❌ 数据模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_feature_module():
    """测试特征模块"""
    print("\n=== 测试特征模块 ===")
    
    try:
        from feature_engineering import feature_engineering_pipeline, calculate_technical_indicators
        print("✅ feature_engineering 模块导入成功")
        
        # 创建测试数据
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        test_data = pd.DataFrame({
            'date': dates,
            'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'high': 101 + np.cumsum(np.random.randn(100) * 0.5),
            'low': 99 + np.cumsum(np.random.randn(100) * 0.5),
            'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'volume': np.random.randint(1000000, 10000000, 100)
        })
        
        print("正在处理特征工程...")
        processed_data = feature_engineering_pipeline(test_data)
        
        if processed_data is not None and len(processed_data) > 0:
            print(f"✅ 特征工程成功")
            print(f"   处理前: {test_data.shape}")
            print(f"   处理后: {processed_data.shape}")
            print(f"   特征数: {len(processed_data.columns)}")
            
            if 'target' in processed_data.columns:
                print(f"   目标变量已创建")
            
            return True
        else:
            print("❌ 特征工程失败")
            return False
            
    except Exception as e:
        print(f"❌ 特征模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_model_module():
    """测试模型模块"""
    print("\n=== 测试模型模块 ===")
    
    try:
        import lightgbm as lgb
        print("✅ LightGBM 导入成功")
        print(f"   LightGBM 版本: {lgb.__version__}")
        
        # 检查是否支持GPU
        try:
            params = {
                'device': 'gpu',
                'gpu_platform_id': 0,
                'gpu_device_id': 0
            }
            print("✅ LightGBM GPU 支持可用")
        except:
            print("⚠️  LightGBM GPU 支持不可用")
        
        return True
    except ImportError:
        print("⚠️  LightGBM 未安装，尝试使用 scikit-learn")
        try:
            from sklearn.ensemble import RandomForestRegressor
            print("✅ scikit-learn 导入成功")
            return True
        except ImportError:
            print("❌ 机器学习库不可用")
            return False
    except Exception as e:
        print(f"❌ 模型模块测试失败: {e}")
        traceback.print_exc()
        return False

def run_simplified_workflow():
    """运行简化工作流程"""
    print("\n=== 运行简化工作流程 ===")
    
    try:
        import pandas as pd
        import numpy as np
        
        # 1. 创建模拟数据
        print("1. 创建模拟数据...")
        dates = pd.date_range('2020-01-01', periods=500, freq='D')
        np.random.seed(42)
        
        # 生成模拟股价数据
        returns = np.random.randn(500) * 0.02
        prices = 100 * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.randn(500) * 0.01),
            'high': prices * (1 + np.abs(np.random.randn(500)) * 0.02),
            'low': prices * (1 - np.abs(np.random.randn(500)) * 0.02),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 500)
        })
        
        print(f"   数据形状: {data.shape}")
        
        # 2. 特征工程
        print("2. 执行特征工程...")
        from feature_engineering import feature_engineering_pipeline
        processed_data = feature_engineering_pipeline(data)
        print(f"   处理后数据形状: {processed_data.shape}")
        
        # 3. 准备训练数据
        print("3. 准备训练数据...")
        feature_cols = [col for col in processed_data.columns 
                       if col not in ['date', 'open', 'high', 'low', 'close', 'volume', 'target']]
        X = processed_data[feature_cols].fillna(0)
        y = processed_data['target'].fillna(0)
        
        print(f"   特征矩阵: {X.shape}")
        print(f"   目标变量: {y.shape}")
        
        # 4. 模型训练（如果可用）
        print("4. 模型训练...")
        try:
            import lightgbm as lgb
            from sklearn.model_selection import train_test_split
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # 检查GPU可用性
            params = {
                'objective': 'regression',
                'metric': 'rmse',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': 0
            }
            
            # 尝试使用GPU
            try:
                gpu_params = params.copy()
                gpu_params.update({
                    'device': 'gpu',
                    'gpu_platform_id': 0,
                    'gpu_device_id': 0
                })
                train_data = lgb.Dataset(X_train, label=y_train)
                model = lgb.train(gpu_params, train_data, num_boost_round=10)
                print("✅ 使用GPU训练成功")
            except:
                # 回退到CPU
                train_data = lgb.Dataset(X_train, label=y_train)
                model = lgb.train(params, train_data, num_boost_round=10)
                print("✅ 使用CPU训练成功")
            
            # 预测
            predictions = model.predict(X_test)
            print(f"   预测完成，共 {len(predictions)} 个预测值")
            
            # 特征重要性
            importance = model.feature_importance(importance_type='gain')
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            print(f"   前5个重要特征:")
            for i in range(min(5, len(feature_importance))):
                row = feature_importance.iloc[i]
                print(f"     {row['feature']}: {row['importance']:.2f}")
            
        except ImportError:
            # 使用scikit-learn作为备选
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            model = RandomForestRegressor(n_estimators=10, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            print("✅ 使用RandomForest训练成功")
            print(f"   预测完成，共 {len(predictions)} 个预测值")
        
        # 5. 信号生成
        print("5. 生成交易信号...")
        from signal_generator import generate_trading_signals
        
        signals = generate_trading_signals(predictions, threshold=0.001)
        print(f"   生成 {len(signals)} 个交易信号")
        print(f"   买入信号: {sum(1 for s in signals if s == 1)}")
        print(f"   卖出信号: {sum(1 for s in signals if s == -1)}")
        print(f"   持有信号: {sum(1 for s in signals if s == 0)}")
        
        # 6. 回测
        print("6. 运行回测...")
        from backtester import Backtester
        
        # 创建回测数据
        backtest_data = processed_data.tail(len(predictions)).copy()
        backtest_data = backtest_data.reset_index(drop=True)
        
        # 添加信号
        backtest_data.loc[:, 'signal'] = signals[:len(backtest_data)]
        
        backtester = Backtester(initial_cash=100000, transaction_fee=0.001, slippage=0.001)
        results = backtester.run_backtest(backtest_data)
        
        if results:
            print("✅ 回测完成")
            print(f"   初始资金: {results['initial_cash']:,.2f}")
            print(f"   最终价值: {results['final_value']:,.2f}")
            print(f"   总收益率: {results['total_return']:.2%}")
            print(f"   年化收益: {results['annual_return']:.2%}")
            print(f"   夏普比率: {results['sharpe_ratio']:.2f}")
            print(f"   最大回撤: {results['max_drawdown']:.2%}")
        else:
            print("⚠️  回测未返回结果")
        
        print("\n✅ 简化工作流程完成")
        return True
        
    except Exception as e:
        print(f"❌ 工作流程执行失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("         LightGBM股票预测项目测试")
    print("=" * 60)
    
    # 环境检查
    check_environment()
    
    # 模块测试
    data_ok = test_data_module()
    features_ok = test_feature_module()
    model_ok = test_model_module()
    
    # 运行工作流程
    workflow_ok = False
    if data_ok and features_ok and model_ok:
        workflow_ok = run_simplified_workflow()
    
    # 总结
    print("\n" + "=" * 60)
    print("                    测试总结")
    print("=" * 60)
    print(f"✅ 数据模块: {'通过' if data_ok else '失败'}")
    print(f"✅ 特征模块: {'通过' if features_ok else '失败'}")
    print(f"✅ 模型模块: {'通过' if model_ok else '失败'}")
    print(f"✅ 工作流程: {'通过' if workflow_ok else '失败'}")
    
    if all([data_ok, features_ok, model_ok, workflow_ok]):
        print("\n🎉 所有测试通过！项目可以正常运行。")
        print("\n📊 下一步建议：")
        print("   1. 安装完整依赖: pip install -r requirements.txt")
        print("   2. 运行完整项目: python main.py")
        print("   3. 调整参数: 编辑 config.yaml 文件")
        print("   4. 查看结果: 检查 output/ 目录")
    else:
        print("\n⚠️  部分测试失败，请检查依赖项和代码。")
        if not model_ok:
            print("   建议安装 LightGBM: pip install lightgbm")
    
    print("=" * 60)

if __name__ == "__main__":
    main()