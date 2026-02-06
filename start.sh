#!/bin/bash

# 项目启动脚本
echo "🚀 LightGBM 股票预测项目启动脚本"
echo "================================="

# 检查GPU
echo "🎮 检查GPU状态..."
nvidia-smi

# 设置代理（如果需要）
if [ ! -z "$HTTP_PROXY" ]; then
    echo "🌐 使用代理: $HTTP_PROXY"
fi

# 安装必要依赖
echo "📦 安装必要依赖..."
pip install --upgrade pip

# 尝试安装核心依赖
echo "📥 安装核心依赖..."
pip install numpy pandas

# 尝试安装scikit-learn
echo "📥 安装scikit-learn..."
pip install scikit-learn

# 尝试安装LightGBM
echo "📥 安装LightGBM..."
pip install lightgbm

# 检查安装结果
echo "🔍 检查安装结果..."
python3 -c "import numpy; print('✅ numpy:', numpy.__version__)"
python3 -c "import pandas; print('✅ pandas:', pandas.__version__)"
python3 -c "import sklearn; print('✅ scikit-learn:', sklearn.__version__)"
python3 -c "import lightgbm as lgb; print('✅ LightGBM:', lgb.__version__)"

# 运行项目测试
echo "🚀 运行项目测试..."
python3 run_project.py

echo "🏁 启动脚本执行完成"