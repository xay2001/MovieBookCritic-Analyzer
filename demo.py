#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆瓣评论分析系统演示脚本
使用示例数据演示系统功能
"""

import os
import sys
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_demo():
    """运行演示"""
    print("🎬 豆瓣电影/图书评论分析系统演示")
    print("=" * 60)
    
    # 检查示例数据文件
    sample_file = "data/sample_movie_comments.txt"
    if not os.path.exists(sample_file):
        print(f"错误: 示例数据文件不存在 {sample_file}")
        return
    
    print(f"使用示例数据文件: {sample_file}")
    print("开始运行分析...")
    
    try:
        # 运行主程序进行分析
        cmd = [
            sys.executable, "main.py",
            "--analyze_only",
            "--file", sample_file
        ]
        
        print("执行命令:", " ".join(cmd))
        print("-" * 60)
        
        # 运行分析
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 分析完成！")
            print("\n📊 程序输出:")
            print(result.stdout)
            
            # 列出生成的文件
            print("\n📁 生成的文件:")
            output_dir = "output"
            if os.path.exists(output_dir):
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        print(f"  ✓ {filepath}")
            
        else:
            print("❌ 分析失败！")
            print("错误输出:")
            print(result.stderr)
            
    except Exception as e:
        print(f"运行演示时出现错误: {e}")

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'jieba', 'snownlp', 'wordcloud', 'matplotlib', 
        'pandas', 'numpy', 'networkx', 'selenium'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

if __name__ == '__main__':
    # 检查依赖
    if not check_dependencies():
        print("请先安装缺少的依赖包")
        sys.exit(1)
    
    # 运行演示
    run_demo() 