#!/usr/bin/env python3
"""
中文字体配置模块
用于解决matplotlib图表中文乱码问题
"""

import os
import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def check_and_install_chinese_fonts():
    """检查和安装中文字体"""
    print("=== 检查中文字体支持 ===")
    
    # 检查系统是否安装了中文字体
    installed_fonts = []
    try:
        result = subprocess.run(['fc-list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if 'chinese' in result.output.lower() or 'chinese' in result.output:
                print("✅ 系统已安装中文字体")
                return True
            elif 'zh-cn' in result.output.lower():
                print("✅ 系统已安装中文简体字体")
                return True
    except Exception as e:
        print(f"检查字体时出错: {e}")
    
    print("⚠️  系统中文字体未安装，尝试安装...")
    
    # Ubuntu/Debian系统安装中文字体
    try:
        print("安装中文字体包...")
        subprocess.run(['apt-get', 'update'], check=True, timeout=120)
        subprocess.run(['apt-get', 'install', '-y', 'fonts-wqy-zenhei', 'fonts-wqy-microhei'], 
                       check=True, timeout=300)
        print("✅ 中文字体安装完成")
        return True
    except Exception as e:
        print(f"❌ 安装中文字体失败: {e}")
        return False

def setup_matplotlib_chinese():
    """配置matplotlib中文字体支持"""
    print("\n=== 配置Matplotlib中文字体 ===")
    
    # 尝试查找可用的中文字体
    chinese_font_candidates = [
        'SimHei',                    # Windows 黑体
        'Microsoft YaHei',           # Windows 微软雅黑
        'PingFang SC',               # macOS 苹方
        'WenQuanYi Zen Hei',         # Linux 文泉驿正黑
        'WenQuanYi Micro Hei',       # Linux 文泉驿微米黑
        'Noto Sans CJK SC',          # Google Noto字体
        'FangSong',                  # 仿宋
        'KaiTi',                     # 楷体
        'STHeiti',                   # 华文黑体
        'STSong',                    # 华文宋体
        'YaHei Consolas Hybrid',     # 雅黑混合字体
    ]
    
    # 获取当前系统中所有可用字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    print(f"系统可用字体数量: {len(available_fonts)}")
    
    # 查找可用的中文字体
    usable_chinese_fonts = []
    for font in chinese_font_candidates:
        if font in available_fonts:
            usable_chinese_fonts.append(font)
            print(f"✅ 找到中文字体: {font}")
    
    if not usable_chinese_fonts:
        print("❌ 未找到可用的中文字体")
        
        # 尝试重新扫描字体缓存
        try:
            print("重新扫描字体缓存...")
            fm._rebuild()
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            for font in chinese_font_candidates:
                if font in available_fonts:
                    usable_chinese_fonts.append(font)
                    print(f"✅ 扫描后找到中文字体: {font}")
        except Exception as e:
            print(f"重新扫描字体缓存失败: {e}")
    
    if usable_chinese_fonts:
        # 设置第一个可用的中文字体
        selected_font = usable_chinese_fonts[0]
        print(f"📝 使用字体: {selected_font}")
        
        # 配置matplotlib
        plt.rcParams['font.family'] = selected_font
        plt.rcParams['font.sans-serif'] = usable_chinese_fonts
        
        # 确保字体设置生效
        matplotlib.rcParams.update({'font.family': selected_font})
        
        # 测试字体设置
        test_config = matplotlib.rcParams['font.family']
        print(f"✅ 字体设置完成，当前字体族: {test_config}")
        return True
    else:
        print("⚠️  未找到中文字体，将使用英文字体")
        # 使用默认英文字体
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        return False

def add_chinese_font_to_matplotlib():
    """手动添加中文字体到matplotlib"""
    print("\n=== 手动添加中文字体到Matplotlib ===")
    
    # 指定可能的中文字体路径
    possible_font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',    # 文泉驿正黑
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', # 文泉驿微米黑
        '/usr/share/fonts/truetype/arphic/uming.ttc',     # AR PL UMing
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc', # Noto Sans
        '/usr/share/fonts/chinese/TrueType/simsun.ttc',   # 宋体
        '/usr/share/fonts/chinese/TrueType/simhei.ttf',   # 黑体
    ]
    
    added_fonts = []
    for font_path in possible_font_paths:
        if os.path.exists(font_path):
            try:
                # 添加字体到matplotlib
                fm.fontManager.addfont(font_path)
                font_name = fm.FontProperties(fname=font_path).get_name()
                added_fonts.append(font_name)
                print(f"✅ 添加字体: {font_name} ({font_path})")
            except Exception as e:
                print(f"❌ 添加字体失败 {font_path}: {e}")
    
    if added_fonts:
        # 使用添加的字体
        plt.rcParams['font.family'] = added_fonts[0]
        plt.rcParams['font.sans-serif'] = added_fonts
        print(f"✅ 使用添加的字体: {added_fonts[0]}")
        return True
    
    return False

def ensure_chinese_display():
    """确保中文显示正常"""
    print("\n=== 确保中文显示正常 ===")
    
    # 方法1：检查并安装字体
    if check_and_install_chinese_fonts():
        print("✅ 中文字体检查通过")
    else:
        print("⚠️  中文字体安装失败")
    
    # 方法2：使用系统字体
    success = setup_matplotlib_chinese()
    if not success:
        # 方法3：手动添加字体
        print("\n尝试手动添加中文字体...")
        success = add_chinese_font_to_matplotlib()
    
    if success:
        print("✅ 中文字体配置成功")
    else:
        print("⚠️  中文字体配置失败，将使用英文字体")
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 其他配置
    plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    plt.rcParams['font.size'] = 10
    
    # 测试配置
    print("\n=== 字体配置测试 ===")
    print(f"字体族: {matplotlib.rcParams['font.family']}")
    print(f"字体列表: {matplotlib.rcParams['font.sans-serif']}")
    
    return success

def test_chinese_plot():
    """测试中文绘图"""
    try:
        print("\n=== 测试中文图表生成 ===")
        
        # 创建测试图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 使用中文标签
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        
        ax.plot(x, y, label='测试线')
        ax.set_title('中文标题测试')
        ax.set_xlabel('X轴标签')
        ax.set_ylabel('Y轴标签')
        ax.legend(title='图例')
        ax.grid(True)
        
        # 保存测试图表
        test_image_path = '/tmp/chinese_test.png'
        plt.savefig(test_image_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print(f"✅ 测试图表已保存到: {test_image_path}")
        print(f"✅ 图表尺寸: {os.path.getsize(test_image_path)} 字节")
        
        return True
    except Exception as e:
        print(f"❌ 中文图表测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("中文字体配置工具")
    print("=" * 60)
    
    # 确保中文显示
    success = ensure_chinese_display()
    
    # 测试中文图表
    if success:
        test_chinese_plot()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ 中文字体配置成功完成")
    else:
        print("⚠️  中文字体配置部分失败，将使用英文字体")
        print("   可能需要在系统中安装中文字体包")
        print("   建议运行: apt-get install fonts-wqy-zenhei fonts-wqy-microhei")
    
    print("=" * 60)

if __name__ == "__main__":
    main()