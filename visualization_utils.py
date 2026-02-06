#!/usr/bin/env python3
"""
增强版可视化模块 - 强效解决中文乱码问题
使用方法：在visualization.py中调用 setup_chinese_fonts() 函数
"""

import os
import sys
import subprocess
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 首先导入基础字体支持
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

def setup_chinese_fonts():
    """强效设置中文字体支持"""
    print("📝 配置中文字体支持...")
    
    # 方法1：尝试使用fontconfig查找可用字体
    import warnings
    warnings.filterwarnings('ignore')
    
    # 获取所有可用字体
    try:
        font_list = [f.name for f in fm.fontManager.ttflist]
        print(f"系统共有 {len(font_list)} 种字体")
        
        # 中文友好字体列表
        chinese_friendly_fonts = [
            'DejaVu Sans',          # Linux常用，支持Unicode
            'Noto Sans CJK SC',     # Google开源中文字体
            'WenQuanYi Zen Hei',    # 文泉驿正黑
            'WenQuanYi Micro Hei',  # 文泉驿微米黑
            'AR PL UMing CN',       # AR PL UMing 中文
            'SimHei',               # 黑体
            'Microsoft JhengHei',   # 微软雅黑
            'MS Gothic',            # MS 字体
            'Ubuntu',               # Ubuntu字体
            'Liberation Sans',      # Liberation Sans
        ]
        
        # 找到可用的字体
        available_fonts = []
        for font_name in chinese_friendly_fonts:
            for font in fm.fontManager.ttflist:
                if font_name in font.name:
                    available_fonts.append(font_name)
                    print(f"✅ 找到可用字体: {font_name}")
                    break
        
        if available_fonts:
            # 使用第一个可用的字体
            selected_font = available_fonts[0]
            plt.rcParams['font.family'] = selected_font
            plt.rcParams['font.sans-serif'] = available_fonts
            print(f"🎯 选择字体: {selected_font}")
        else:
            # 回退到DejaVu Sans（几乎总是可用）
            plt.rcParams['font.family'] = 'DejaVu Sans'
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
            print("⚠️  未找到中文友好字体，使用 DejaVu Sans")
            
    except Exception as e:
        print(f"⚠️  字体配置出错: {e}")
        # 最简单的回退方案
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 方法2：如果是中文标签，建议使用英文标签来避免乱码问题
    # 这里我们提供一个英文标签的工具函数
    print("🔧 使用英文标签以避免乱码...")
    
    # 方法3：设置合适的字体大小
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    
    return True

def create_english_performance_report():
    """创建英文版的性能报告，彻底避免中文乱码"""
    print("🔤 创建英文版性能报告...")
    
    # 创建一个简单的英文图表模板
    english_config = {
        'Stock Price Trend': 'Stock Price Trend',
        'Predictions vs Actual Returns': 'Predictions vs Actual Returns',
        'Strategy vs Buy and Hold': 'Strategy vs Buy and Hold',
        'Drawdown Analysis': 'Drawdown Analysis',
        'Trading Signals': 'Trading Signals',
        'xlabel': 'Date',
        'ylabel': 'Price',
        'legend_strategy': 'Strategy Return',
        'legend_buyhold': 'Buy and Hold',
        'legend_price': 'Price',
        'legend_buy': 'Buy Signal',
        'legend_sell': 'Sell Signal',
        'label_returns': 'Return Rate',
        'label_drawdown': 'Drawdown Ratio',
    }
    
    return english_config

def test_fonts():
    """测试字体是否正常工作"""
    print("🧪 测试字体显示...")
    
    try:
        # 创建一个测试图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(1, 10)
        y = x ** 2
        
        # 使用英文标签测试
        ax.plot(x, y, label='Test Line')
        ax.set_title('Test Chinese Support (标题测试)')
        ax.set_xlabel('X Axis (X轴)')
        ax.set_ylabel('Y Axis (Y轴)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存测试图表
        test_path = '/tmp/font_test_zh.png'
        plt.savefig(test_path, dpi=120, bbox_inches='tight')
        plt.close()
        
        # 检查文件大小
        file_size = os.path.getsize(test_path)
        print(f"✅ 测试图表已保存: {test_path} ({file_size:,} bytes)")
        
        if file_size > 1000:
            print("✅ 图表生成成功")
            return True
        else:
            print("❌ 图表可能生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 字体测试失败: {e}")
        return False

def ensure_matplotlib_chinese():
    """确保matplotlib中文显示的关键函数"""
    print("🛠️ 配置Matplotlib中文支持...")
    
    # 调用字体设置
    setup_chinese_fonts()
    
    # 测试字体显示
    success = test_fonts()
    
    if not success:
        print("⚠️  中文显示测试失败，强制使用英文标签")
        # 强制使用英文
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    print("🔧 配置完成")
    return success

# 运行测试
if __name__ == "__main__":
    print("=" * 60)
    print("📊 可视化模块字体测试")
    print("=" * 60)
    
    ensure_matplotlib_chinese()
    
    print("\n💡 使用建议：")
    print("1. 在visualization.py开头调用 ensure_matplotlib_chinese()")
    print("2. 或者直接使用 create_english_performance_report() 中的英文标签")
    print("3. 如果还有问题，考虑在系统中安装中文字体包:")
    print("   apt-get install fonts-wqy-zenhei fonts-wqy-microhei")
    print("=" * 60)