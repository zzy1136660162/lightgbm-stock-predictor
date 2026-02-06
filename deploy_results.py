#!/usr/bin/env python3
"""
LightGBM 结果部署脚本
自动将项目结果部署到nginx公开目录
"""

import os
import shutil
import time
from datetime import datetime

# 配置路径
SOURCE_DIR = "/root/.openclaw/workspace/lightgbm_stock_predictor/output"
TARGET_DIR = "/var/www/openclaw/workspace/public"
DOMAIN_URL = "http://openclaw-public.yuntuoengine.com"
RESULT_PAGE = "lightgbm-results.html"

def deploy_results():
    """部署项目结果到nginx目录"""
    print("=== LightGBM 结果部署工具 ===")
    print(f"部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查源目录
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 源目录不存在: {SOURCE_DIR}")
        return False
    
    # 检查目标目录
    if not os.path.exists(TARGET_DIR):
        print(f"❌ 目标目录不存在: {TARGET_DIR}")
        return False
    
    # 获取源文件列表
    source_files = []
    for filename in os.listdir(SOURCE_DIR):
        source_path = os.path.join(SOURCE_DIR, filename)
        if os.path.isfile(source_path):
            source_files.append(filename)
    
    if not source_files:
        print("❌ 源目录中没有文件")
        return False
    
    print(f"📁 发现文件: {len(source_files)} 个")
    for filename in source_files:
        file_path = os.path.join(SOURCE_DIR, filename)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"   - {filename} ({file_size:.2f} MB)")
    
    print()
    
    # 复制文件
    print("🚀 开始部署...")
    success_count = 0
    
    for filename in source_files:
        source_path = os.path.join(SOURCE_DIR, filename)
        target_path = os.path.join(TARGET_DIR, filename)
        
        try:
            shutil.copy2(source_path, target_path)
            success_count += 1
            print(f"   ✅ {filename}")
        except Exception as e:
            print(f"   ❌ {filename} - {e}")
    
    print()
    print(f"📊 部署完成: {success_count}/{len(source_files)} 个文件成功")
    
    # 显示访问信息
    print()
    print("=== 访问信息 ===")
    print(f"🌐 外网域名: {DOMAIN_URL}")
    print(f"📈 结果页面: {DOMAIN_URL}/{RESULT_PAGE}")
    print()
    
    # 检查nginx状态
    try:
        import subprocess
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout.strip() == 'active':
            print("✅ Nginx 服务运行正常")
        else:
            print("⚠️  Nginx 服务状态异常")
    except:
        print("⚠️  无法检查Nginx服务状态")
    
    return True

def show_deployment_info():
    """显示部署信息"""
    print()
    print("=== 部署信息 ===")
    print(f"源目录: {SOURCE_DIR}")
    print(f"目标目录: {TARGET_DIR}")
    print(f"外网域名: {DOMAIN_URL}")
    print(f"结果页面: {DOMAIN_URL}/{RESULT_PAGE}")
    print()

def check_nginx():
    """检查nginx服务"""
    try:
        result = subprocess.run(['systemctl', 'status', 'nginx'], 
                              capture_output=True, text=True, timeout=5)
        if "active (running)" in result.stdout:
            return True
        return False
    except:
        return False

def update_html_page():
    """更新HTML页面"""
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LightGBM 股票预测项目 - 实时更新</title>
    <meta http-equiv="refresh" content="300"> <!-- 5分钟自动刷新 -->
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 30px; }
        .status { color: #28a745; font-weight: bold; }
        .file-list { margin: 20px 0; }
        .file-item { padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; }
        .update-time { text-align: center; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 LightGBM 股票预测项目</h1>
            <p class="status">✅ 系统正常运行 - 自动更新中</p>
        </div>
        
        <div class="file-list">
            <h2>📁 最新结果文件</h2>
            <div class="file-item">📊 strategy_data.csv - 策略数据</div>
            <div class="file-item">💰 portfolio_history.csv - 投资组合历史</div>
            <div class="file-item">🔮 predictions.csv - 预测结果</div>
            <div class="file-item">📝 trade_log.csv - 交易日志</div>
            <div class="file-item">📈 performance_report.png - 性能报告图</div>
        </div>
        
        <div class="update-time">
            最后更新: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''
        </div>
    </div>
</body>
</html>'''
    
    html_path = os.path.join(TARGET_DIR, "index.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML页面已更新: {html_path}")

if __name__ == "__main__":
    # 显示部署信息
    show_deployment_info()
    
    # 执行部署
    if deploy_results():
        print("🎉 部署成功！")
        
        # 可选：更新简化的HTML页面
        print("\n📝 更新HTML页面...")
        update_html_page()
        
        print(f"\n🔗 访问链接: {DOMAIN_URL}/{RESULT_PAGE}")
        print(f"🔗 根目录: {DOMAIN_URL}/")
    else:
        print("❌ 部署失败！")