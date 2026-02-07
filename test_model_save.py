# 测试模型保存和加载功能
import sys
sys.path.insert(0, '.')

from data_loader import load_stock_data
from feature_engineering import feature_engineering_pipeline
from model import StockPredictor

print("=== 测试模型保存和加载功能 ===\n")

# 1. 加载数据
print("1. 加载股票数据...")
data = load_stock_data()
print(f"   数据加载完成，共{len(data)}条记录\n")

# 2. 特征工程
print("2. 执行特征工程...")
processed_data = feature_engineering_pipeline(data)
print(f"   特征工程完成\n")

# 3. 训练模型
print("3. 训练模型...")
predictor = StockPredictor()
X, y = predictor.prepare_data(processed_data)
predictor.train(X, y)
print(f"   模型训练完成\n")

# 4. 保存模型
print("4. 保存模型...")
model_path = predictor.save_model("model/lgb_model.pkl")
print(f"   模型保存路径: {model_path}\n")

# 5. 获取模型大小
print("5. 模型文件信息:")
model_info = predictor.get_model_size("model/lgb_model.pkl")
print(f"   路径: {model_info['path']}")
print(f"   大小: {model_info['formatted']}\n")

# 6. 加载模型
print("6. 测试加载模型...")
predictor2 = StockPredictor()
predictor2.load_model("model/lgb_model.pkl")
print(f"   模型加载成功!\n")

# 7. 使用加载的模型进行预测
print("7. 使用加载的模型预测...")
predictions = predictor2.predict(X.head(5))
print(f"   预测结果: {predictions}\n")

print("=== 所有功能测试通过! ===")

