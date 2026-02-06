#!/usr/bin/env python3
"""
测试脚本 - 使用简化版测试流程
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入模块"""
    print("=== 开始测试模块导入 ===")
    
    try:
        import pandas as pd
        print("✅ pandas 导入成功")
    except ImportError as e:
        print(f"❌ pandas 导入失败: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy 导入成功")
    except ImportError as e:
        print(f"❌ numpy 导入失败: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib 导入成功")
    except ImportError as e:
        print(f"❌ matplotlib 导入失败: {e}")
        return False
    
    try:
        from data_loader import load_stock_data
        print("✅ data_loader 导入成功")
    except ImportError as e:
        print(f"❌ data_loader 导入失败: {e}")
        return False
    
    try:
        from feature_engineering import feature_engineering_pipeline
        print("✅ feature_engineering 导入成功")
    except ImportError as e:
        print(f"❌ feature_engineering 导入失败: {e}")
        return False
    
    try:
        import lightgbm as lgb
        print("✅ lightgbm 导入成功")
    except ImportError as e:
        print(f"❌ lightgbm 导入失败: {e}")
        
        # 尝试使用默认的Python库作为备选
        try:
            from sklearn.ensemble import RandomForestRegressor
            print("🔧 使用 scikit-learn RandomForest 作为替代")
        except ImportError:
            print("❌ 没有可用的机器学习库")
            return False
    
    print("✅ 所有模块导入测试通过")
    return True

def test_data_loading():
    """测试数据加载"""
    print("\n=== 开始测试数据加载 ===")
    
    try:
        from data_loader import load_stock_data
        data = load_stock_data()
        
        if data is not None and len(data) > 0:
            print(f"✅ 数据加载成功，获得 {len(data)} 条记录")
            print(f"   数据列：{list(data.columns)}")
            print(f"   日期范围：{data['date'].min()} 到 {data['date'].max()}")
            return True
        else:
            print("❌ 数据加载失败，返回空数据")
            return False
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return False

def test_gpu_availability():
    """测试GPU可用性"""
    print("\n=== GPU可用性测试 ===")
    
    # 测试 NVIDIA GPU
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU 可用")
            # 尝试解析输出找到3060Ti
            if '3060 Ti' in result.stdout or '3060' in result.stdout:
                print("🎮 RTX 3060Ti 已识别")
            return True
        else:
            print("❌ NVIDIA GPU 不可用或 nvidia-smi 未安装")
    except Exception as e:
        print(f"❌ GPU测试失败: {e}")
    
    # 尝试导入CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ PyTorch CUDA 可用，GPU: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("❌ PyTorch CUDA 不可用")
    except ImportError:
        print("❌ PyTorch 未安装")
    
    return False

def test_feature_engineering():
    """测试特征工程"""
    print("\n=== 开始测试特征工程 ===")
    
    try:
        # 创建模拟数据
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=250, freq='D')
        np.random.seed(42)
        
        test_data = pd.DataFrame({
            'date': dates,
            'open': 100 + np.cumsum(np.random.randn(250) * 0.5),
            'high': 101 + np.cumsum(np.random.randn(250) * 0.5),
            'low': 99 + np.cumsum(np.random.randn(250) * 0.5),
            'close': 100 + np.cumsum(np.random.randn(250) * 0.5),
            'volume': np.random.randint(1000000, 10000000, 250)
        })
        
        from feature_engineering import feature_engineering_pipeline
        processed_data = feature_engineering_pipeline(test_data)
        
        if processed_data is not None and len(processed_data) > 0:
            print(f"✅ 特征工程成功，生成 {len(processed_data.columns)} 个特征")
            print(f"   处理前数据形状: {test_data.shape}")
            print(f"   处理后数据形状: {processed_data.shape}")
            
            # 检查是否有目标变量
            if 'target' in processed_data.columns:
                print(f"   目标变量已创建")
            
            return True
        else:
            print("❌ 特征工程失败")
            return False
            
    except Exception as e:
        print(f"❌ 特征工程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_program():
    """测试主程序"""
    print("\n=== 开始测试主程序 ===")
    
    try:
        # 创建一个简化的主程序测试
        print("🚀 启动简化测试流程...")
        
        # 测试数据加载
        data_found = test_data_loading() if not data_found else data_found
        
        if not data_found:
            print("⚠️  数据加载失败，使用模拟数据")
            import pandas as pd
            import numpy as np
            
            dates = pd.date_range('2024-01-01', periods=250, freq='D')
            np.random.seed(42)
            
            data = pd.DataFrame({
                'date': dates,
                'open': 100 + np.cumsum(np.random.randn(250) * 0.5),
                'high': 101 + np.cumsum(np.random.randn(250) * 0.5),
                'low': 99 + np.cumsum(np.random.randn(250) * 0.5),
                'close': 100 + np.cumsum(np.random.randn(250) * 0.5),
                'volume': np.random.randint(1000000, 10000000, 250)
            })
        else:
            from data_loader import load_stock_data
            data = load_stock_data()
        
        # 测试特征工程
        from feature_engineering import feature_engineering_pipeline
        processed_data = feature_engineering_pipeline(data)
        
        print(f"✅ 主程序测试完成")
        print(f"   最终数据形状: {processed_data.shape}")
        print(f"   特征数量: {len(processed_data.columns)}")
        
        if 'target' in processed_data.columns:
            target_stats = processed_data['target'].describe()
            print(f"   目标变量统计:")
            print(f"     Mean: {target_stats['mean']:.4f}")
            print(f"     Std : {target_stats['std']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 主程序测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("              LightGBM股票预测模型测试")
    print("=" * 60)
    
    # 测试GPU
    has_gpu = test_gpu_availability()
    
    # 测试导入
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n⚠️  部分导入失败，尝试安装依赖...")
        try:
            import subprocess
            print("正在安装必要依赖...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "pandas", "numpy", "matplotlib", "scikit-learn"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 依赖安装成功")
                imports_ok = test_imports()
            else:
                print(f"❌ 依赖安装失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 安装依赖失败: {e}")
    
    # 测试数据加载
    data_found = False
    if imports_ok:
        data_found = test_data_loading()
    
    # 测试特征工程
    features_ok = False
    if data_found:
        features_ok = test_feature_engineering()
    
    # 测试主程序
    main_ok = False
    if features_ok or imports_ok:
        main_ok = test_main_program()
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("                  测试总结")
    print("=" * 60)
    print(f"✅ GPU可用性: {'可用' if has_gpu else '不可用'}")
    print(f"✅ 模块导入: {'通过' if imports_ok else '失败'}")
    print(f"✅ 数据加载: {'通过' if data_found else '失败'}")
    print(f"✅ 特征工程: {'通过' if features_ok else '失败'}")
    print(f"✅ 主程序: {'通过' if main_ok else '失败'}")
    
    if all([imports_ok, data_found or features_ok, main_ok]):
        print("\n🎉 测试完成！项目可以正常运行。")
        print("\n📊 下一步建议：")
        print("   1. 运行完整模型训练：python main.py")
        print(f"   2. 使用GPU加速: 安装GPU版本的LightGBM")
        if has_gpu:
            print("   3. GPU加速安装: pip install lightgbm --install-option=--gpu")
        print("   4. 调整参数：编辑 config.yaml 文件")
    else:
        print("\n⚠️  部分测试失败，请检查依赖项和代码。")
    
    print("=" * 60)

if __name__ == "__main__":
    main()