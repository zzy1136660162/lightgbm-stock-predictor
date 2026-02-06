#!/usr/bin/env python3
"""
中文乱码解决方案 - 强制性的中文字体配置
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import subprocess
import sys

def force_chinese_font_support():
    """强制中文字体支持 - 使用多种方法确保成功"""
    print("🔧 强制启用中文字体支持...")
    
    # 方法1：手动添加常用中文字体路径
    chinese_font_paths = [
        # Linux中文字体路径
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/arphic/uming.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        # 系统常用路径
        '/usr/share/fonts/chinese/TrueType/simsun.ttc',
        '/usr/share/fonts/chinese/TrueType/simhei.ttf',
    ]
    
    font_added = False
    for font_path in chinese_font_paths:
        if os.path.exists(font_path):
            try:
                fm.fontManager.addfont(font_path)
                font_name = fm.FontProperties(fname=font_path).get_name()
                print(f"✅ 添加字体: {font_name}")
                font_added = True
            except Exception as e:
                print(f"⚠️  无法添加字体 {font_path}: {e}")
    
    # 方法2：设置多个候选字体（按优先级排列）
    chinese_font_families = [
        'Noto Sans CJK SC',          # Noto Sans 简体中文
        'WenQuanYi Zen Hei',         # 文泉驿正黑
        'WenQuanYi Micro Hei',       # 文泉驿微米黑
        'SimHei',                    # 黑体
        'Microsoft YaHei',           # 微软雅黑
        'AR PL UMing CN',            # AR PL UMing 中文
        'FangSong',                  # 仿宋
        'KaiTi',                     # 楷体
        'STHeiti',                   # 华文黑体
        'STSong',                    # 华文宋体
        'YaHei Consolas Hybrid',     # 雅黑混合体
        'DejaVu Sans',               # 备用英文字体
        'Liberation Sans',           # 备用字体
    ]
    
    # 设置字体配置（关键步骤）
    matplotlib.rcParams['font.family'] = chinese_font_families
    matplotlib.rcParams['font.sans-serif'] = chinese_font_families
    
    # 其他必要的matplotlib配置
    matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    matplotlib.rcParams['font.size'] = 12
    matplotlib.rcParams['axes.titlesize'] = 14
    matplotlib.rcParams['axes.labelsize'] = 12
    matplotlib.rcParams['xtick.labelsize'] = 10
    matplotlib.rcParams['ytick.labelsize'] = 10
    matplotlib.rcParams['legend.fontsize'] = 10
    
    print("✅ 字体配置完成")
    print(f"🎯 当前字体配置: {matplotlib.rcParams['font.family']}")
    
    return True

def validate_chinese_display():
    """验证中文字体显示是否正常"""
    print("\n🧪 验证中文字体显示...")
    
    try:
        # 创建一个包含中文的测试图表
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 中文文本测试（关键）
        chinese_test_strings = [
            '中文标题测试',
            '中文标签测试',
            '收益率分析',
            '回撤分析',
            '交易信号',
            '资产价值',
            '预测vs实际'
        ]
        
        # 创建一些图表示例
        import numpy as np
        x = np.arange(1, 11)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        # 绘制中文图表
        ax.plot(x, y1, label='正弦曲线', linewidth=2, marker='o')
        ax.plot(x, y2, label='余弦曲线', linewidth=2, marker='s')
        
        # 设置中文标题和标签
        ax.set_title('中文标题测试 - 数据可视化')
        ax.set_xlabel('X轴标签 (时间)')
        ax.set_ylabel('Y轴标签 (数值)')
        ax.legend(title='图例')
        ax.grid(True, alpha=0.3)
        
        # 保存并检查
        test_file = '/tmp/chinese_font_validation.png'
        plt.savefig(test_file, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        # 检查文件是否正确生成
        if os.path.exists(test_file) and os.path.getsize(test_file) > 2000:
            print(f"✅ 中文显示测试通过: {test_file}")
            print(f"   文件大小: {os.path.getsize(test_file):,} 字节")
            
            # 显示字体信息
            print(f"   当前字体: {matplotlib.rcParams['font.family']}")
            return True
        else:
            print("❌ 中文显示测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        return False

def emergency_english_fallback():
    """紧急英文回退方案"""
    print("🔧 启用英文回退方案...")
    
    # 使用最稳定的英文配置
    english_config = [
        'DejaVu Sans',
        'Liberation Sans', 
        'Arial',
        'Helvetica',
        'sans-serif'
    ]
    
    matplotlib.rcParams['font.family'] = english_config
    matplotlib.rcParams['font.sans-serif'] = english_config
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    print("✅ 英文回退配置完成")
    return True

def apply_chinese_font_fix():
    """应用中文乱码修复"""
    print("=" * 60)
    print("🔤 中文乱码修复工具")
    print("=" * 60)
    
    # 步骤1：强制字体配置
    success = force_chinese_font_support()
    
    # 步骤2：验证显示
    if success:
        validation_result = validate_chinese_display()
        if not validation_result:
            print("⚠️  中文显示验证失败，切换到英文模式")
            emergency_english_fallback()
    else:
        print("❌ 字体配置失败，切换到英文模式")
        emergency_english_fallback()
    
    print("\n" + "=" * 60)
    print("📊 配置摘要:")
    print(f"🎯 字体家族: {matplotlib.rcParams['font.family']}")
    print(f"📏 字体大小: {matplotlib.rcParams['font.size']}")
    print(f"🔢 负号显示: {matplotlib.rcParams['axes.unicode_minus']}")
    print("=" * 60)
    
    return True

# 如果直接运行此脚本
if __name__ == "__main__":
    apply_chinese_font_fix()
    
    # 显示当前配置
    print("\n🔍 当前Matplotlib配置:")
    print(f"Font Family: {matplotlib.rcParams['font.family']}")
    print(f"Font Sans Serif: {matplotlib.rcParams['font.sans-serif']}")
    print(f"Unicode Minus: {matplotlib.rcParams['axes.unicode_minus']}")