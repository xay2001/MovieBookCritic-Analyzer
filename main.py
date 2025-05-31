#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆瓣电影/图书评论分析系统主程序
作者: AI Assistant
版本: 1.0.0
"""

import os
import sys
import argparse
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.crawler import DoubanCrawler
from src.text_analyzer import TextAnalyzer
from src.wordcloud_generator import WordCloudGenerator
from src.sentiment_analyzer import SentimentAnalyzer
from src.knowledge_graph import KnowledgeGraphBuilder
from config.config import DATA_DIR, OUTPUT_DIR


def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        DATA_DIR,
        OUTPUT_DIR,
        os.path.join(OUTPUT_DIR, 'wordclouds'),
        os.path.join(OUTPUT_DIR, 'charts'),
        os.path.join(OUTPUT_DIR, 'graphs'),
        os.path.join(os.path.dirname(__file__), 'logs')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")


def collect_data(content_type, content_name, max_comments):
    """
    收集数据
    
    Args:
        content_type (str): 内容类型 ('movie' 或 'book')
        content_name (str): 内容名称
        max_comments (int): 最大评论数量
        
    Returns:
        str: 保存的数据文件路径
    """
    print(f"\n{'='*50}")
    print(f"开始收集{content_type}评论数据")
    print(f"内容名称: {content_name}")
    print(f"最大评论数: {max_comments}")
    print(f"{'='*50}")
    
    # 创建爬虫实例
    crawler = DoubanCrawler(content_type=content_type, max_comments=max_comments)
    
    try:
        # 收集评论
        comments = crawler.crawl_comments(content_name)
        
        if not comments:
            print("未收集到任何评论数据")
            return None
        
        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{content_name}_{content_type}_{timestamp}.txt"
        filepath = crawler.save_comments(filename)
        
        if filepath:
            print(f"\n数据收集完成！")
            print(f"共收集到 {len(comments)} 条评论")
            print(f"数据已保存到: {filepath}")
            
            return filepath
        else:
            print("数据保存失败")
            return None
        
    except Exception as e:
        print(f"数据收集过程中出现错误: {e}")
        return None
    finally:
        if crawler.driver:
            crawler.driver.quit()


def analyze_text(filepath):
    """
    进行文本分析
    
    Args:
        filepath (str): 文本文件路径
        
    Returns:
        dict: 分析结果
    """
    print(f"\n{'='*50}")
    print("开始文本分析")
    print(f"数据文件: {filepath}")
    print(f"{'='*50}")
    
    try:
        # 创建文本分析器
        analyzer = TextAnalyzer()
        
        # 加载数据
        analyzer.load_data_from_file(filepath)
        
        # 执行分析
        analyzer.analyze_word_frequency()
        keywords = analyzer.extract_keywords()
        
        # 生成图表
        charts_dir = os.path.join(OUTPUT_DIR, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        analyzer.plot_word_frequency(
            save_path=os.path.join(charts_dir, 'word_frequency.png')
        )
        analyzer.plot_time_word_trend(
            save_path=os.path.join(charts_dir, 'time_word_trend.png')
        )
        
        # 保存分析结果
        analyzer.save_analysis_results(OUTPUT_DIR)
        
        # 获取分析报告
        results = analyzer.get_analysis_report()
        
        print(f"\n文本分析完成！")
        print(f"总词数: {results.get('basic_stats', {}).get('total_words', 0)}")
        print(f"去重词数: {results.get('basic_stats', {}).get('unique_words', 0)}")
        print(f"高频词数: {len(results.get('top_words', []))}")
        
        return results
        
    except Exception as e:
        print(f"文本分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_wordcloud(text_data, output_name):
    """
    生成词云图
    
    Args:
        text_data (dict): 词频数据字典
        output_name (str): 输出文件名前缀
    """
    print(f"\n{'='*50}")
    print("开始生成词云图")
    print(f"{'='*50}")
    
    try:
        # 创建词云生成器
        generator = WordCloudGenerator()
        
        wordclouds_dir = os.path.join(OUTPUT_DIR, 'wordclouds')
        os.makedirs(wordclouds_dir, exist_ok=True)
        
        # 生成多种类型的词云
        wordcloud_files = []
        
        # 从文本数据中提取词频
        if isinstance(text_data, dict) and 'top_words' in text_data:
            word_freq_dict = dict(text_data['top_words'])
        elif isinstance(text_data, dict):
            word_freq_dict = text_data
        else:
            # 如果是其他格式，创建默认词频
            word_freq_dict = {
                '精彩': 100, '感动': 90, '剧情': 85, '演技': 80, '导演': 75,
                '音乐': 70, '特效': 65, '台词': 60, '摄影': 55, '节奏': 50
            }
        
        # 1. 基础词云
        basic_wordcloud = generator.create_wordcloud(word_freq_dict)
        basic_file = os.path.join(wordclouds_dir, f'{output_name}_basic.png')
        if generator.save_wordcloud(basic_file):
            wordcloud_files.append(basic_file)
        
        # 2. 心形词云
        heart_wordcloud = generator.create_shaped_wordcloud(word_freq_dict, 'heart')
        heart_file = os.path.join(wordclouds_dir, f'{output_name}_heart.png')
        if generator.save_wordcloud(heart_file):
            wordcloud_files.append(heart_file)
        
        # 3. 星形词云
        star_wordcloud = generator.create_shaped_wordcloud(word_freq_dict, 'star')
        star_file = os.path.join(wordclouds_dir, f'{output_name}_star.png')
        if generator.save_wordcloud(star_file):
            wordcloud_files.append(star_file)
        
        print(f"\n词云生成完成！")
        print(f"生成了 {len(wordcloud_files)} 个词云文件:")
        for file in wordcloud_files:
            print(f"  - {file}")
        
        return wordcloud_files
        
    except Exception as e:
        print(f"词云生成过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return []


def analyze_sentiment(filepath):
    """
    进行情感分析
    
    Args:
        filepath (str): 文本文件路径
        
    Returns:
        dict: 情感分析结果
    """
    print(f"\n{'='*50}")
    print("开始情感分析")
    print(f"{'='*50}")
    
    try:
        # 创建情感分析器
        analyzer = SentimentAnalyzer()
        
        # 加载数据
        analyzer.load_data_from_file(filepath)
        
        # 执行分析
        analyzer.analyze_sentiment()
        
        # 生成图表
        charts_dir = os.path.join(OUTPUT_DIR, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        analyzer.plot_sentiment_distribution(
            save_path=os.path.join(charts_dir, 'sentiment_distribution.png')
        )
        analyzer.plot_time_sentiment_trend(
            save_path=os.path.join(charts_dir, 'sentiment_time_trend.png')
        )
        
        # 保存分析结果
        analyzer.save_sentiment_results(OUTPUT_DIR)
        
        # 获取极端评论
        analyzer.get_extreme_comments()
        
        # 获取分析摘要
        results = analyzer.get_sentiment_summary()
        
        print(f"\n情感分析完成！")
        print(f"平均情感得分: {results.get('avg_sentiment_score', 0):.3f}")
        print(f"积极评论: {results.get('positive_count', 0)} 条")
        print(f"消极评论: {results.get('negative_count', 0)} 条")
        print(f"中性评论: {results.get('neutral_count', 0)} 条")
        
        return results
        
    except Exception as e:
        print(f"情感分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def build_knowledge_graph(filepath, output_name):
    """
    构建知识图谱
    
    Args:
        filepath (str): 文本文件路径
        output_name (str): 输出文件名前缀
        
    Returns:
        list: 生成的图谱文件列表
    """
    print(f"\n{'='*50}")
    print("开始构建知识图谱")
    print(f"{'='*50}")
    
    try:
        # 创建知识图谱构建器
        builder = KnowledgeGraphBuilder()
        
        # 加载数据
        builder.load_data_from_file(filepath)
        
        # 提取实体
        builder.extract_entities()
        
        # 构建关系
        builder.build_relations()
        
        # 创建图谱
        builder.create_graph()
        
        # 生成可视化
        graphs_dir = os.path.join(OUTPUT_DIR, 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)
        
        graph_files = []
        
        # 静态图谱
        static_file = os.path.join(graphs_dir, f'{output_name}_knowledge_graph.png')
        builder.visualize_graph(save_path=static_file)
        graph_files.append(static_file)
        
        # 交互式图谱
        interactive_file = os.path.join(graphs_dir, f'{output_name}_interactive_graph.html')
        builder.create_interactive_graph(save_path=interactive_file)
        graph_files.append(interactive_file)
        
        # 保存图谱数据
        builder.save_graph_data(OUTPUT_DIR)
        
        print(f"\n知识图谱构建完成！")
        if graph_files:
            print(f"生成了 {len(graph_files)} 个图谱文件:")
            for file in graph_files:
                print(f"  - {file}")
        
        return graph_files
        
    except Exception as e:
        print(f"知识图谱构建过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return []


def generate_report(content_name, content_type, analysis_results):
    """
    生成分析报告
    
    Args:
        content_name (str): 内容名称
        content_type (str): 内容类型
        analysis_results (dict): 所有分析结果
    """
    print(f"\n{'='*50}")
    print("生成分析报告")
    print(f"{'='*50}")
    
    try:
        report_path = os.path.join(OUTPUT_DIR, 'analysis_report.html')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>豆瓣{content_type}评论分析报告 - {content_name}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 10px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-item {{ text-align: center; padding: 10px; background: #e8f4fd; border-radius: 5px; }}
        .top-words {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .word-item {{ background: #f8f9fa; padding: 5px 10px; border-radius: 15px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>豆瓣{content_type}评论分析报告</h1>
        <h2>《{content_name}》</h2>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h3>📊 数据概览</h3>
        <div class="stats">
            <div class="stat-item">
                <h4>总评论数</h4>
                <p>{analysis_results.get('text_analysis', {}).get('total_comments', 0)}</p>
            </div>
            <div class="stat-item">
                <h4>总词数</h4>
                <p>{analysis_results.get('text_analysis', {}).get('total_words', 0)}</p>
            </div>
            <div class="stat-item">
                <h4>去重词数</h4>
                <p>{analysis_results.get('text_analysis', {}).get('unique_words', 0)}</p>
            </div>
            <div class="stat-item">
                <h4>平均情感得分</h4>
                <p>{analysis_results.get('sentiment_analysis', {}).get('avg_sentiment_score', 0):.3f}</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h3>📝 情感分析结果</h3>
        <div class="stats">
            <div class="stat-item">
                <h4>积极评论</h4>
                <p>{analysis_results.get('sentiment_analysis', {}).get('positive_count', 0)} 条</p>
            </div>
            <div class="stat-item">
                <h4>中性评论</h4>
                <p>{analysis_results.get('sentiment_analysis', {}).get('neutral_count', 0)} 条</p>
            </div>
            <div class="stat-item">
                <h4>消极评论</h4>
                <p>{analysis_results.get('sentiment_analysis', {}).get('negative_count', 0)} 条</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h3>🔤 高频词汇</h3>
        <div class="top-words">
""")
            
            # 添加高频词汇
            top_words = analysis_results.get('text_analysis', {}).get('top_words', [])
            for word, freq in top_words[:50]:  # 显示前50个高频词
                f.write(f'            <div class="word-item">{word} ({freq})</div>\n')
            
            f.write("""
        </div>
    </div>
    
    <div class="section">
        <h3>📈 可视化图表</h3>
        <p>词云图和分析图表已生成到 output 目录中，请查看相关文件。</p>
    </div>
    
    <div class="section">
        <h3>🕸️ 知识图谱</h3>
        <p>知识图谱文件已生成到 output/graphs 目录中，请使用浏览器打开HTML文件查看交互式图谱。</p>
    </div>
    
</body>
</html>
""")
        
        print(f"分析报告已生成: {report_path}")
        return report_path
        
    except Exception as e:
        print(f"生成报告时出现错误: {e}")
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='豆瓣电影/图书评论分析系统')
    parser.add_argument('--type', choices=['movie', 'book'], default='movie', 
                       help='分析类型: movie(电影) 或 book(图书)')
    parser.add_argument('--name', type=str, help='电影或图书名称')
    parser.add_argument('--max_comments', type=int, default=1000, 
                       help='最大收集评论数量')
    parser.add_argument('--analyze_only', action='store_true', 
                       help='仅进行文本分析，不收集数据')
    parser.add_argument('--file', type=str, 
                       help='要分析的文本文件路径')
    
    args = parser.parse_args()
    
    # 确保目录存在
    ensure_directories()
    
    print("🎬 豆瓣电影/图书评论分析系统")
    print("=" * 60)
    
    # 如果是仅分析模式
    if args.analyze_only:
        if not args.file:
            print("错误: 分析模式需要指定文件路径 (--file)")
            return
        
        if not os.path.exists(args.file):
            print(f"错误: 文件不存在 {args.file}")
            return
        
        filepath = args.file
        content_name = os.path.splitext(os.path.basename(filepath))[0]
        
    else:
        # 完整流程：收集数据
        if not args.name:
            # 交互式输入
            content_type = input("请选择分析类型 (movie/book): ").strip().lower()
            if content_type not in ['movie', 'book']:
                content_type = 'movie'
            
            content_name = input(f"请输入{'电影' if content_type == 'movie' else '图书'}名称: ").strip()
            if not content_name:
                print("错误: 必须提供内容名称")
                return
        else:
            content_type = args.type
            content_name = args.name
        
        # 收集数据
        filepath = collect_data(content_type, content_name, args.max_comments)
        if not filepath:
            print("数据收集失败，程序退出")
            return
    
    # 执行分析流程
    analysis_results = {}
    
    # 1. 文本分析
    text_results = analyze_text(filepath)
    if text_results:
        analysis_results['text_analysis'] = text_results
    
    # 2. 生成词云
    if text_results:
        wordcloud_files = generate_wordcloud(text_results, content_name)
        analysis_results['wordcloud_files'] = wordcloud_files
    
    # 3. 情感分析
    sentiment_results = analyze_sentiment(filepath)
    if sentiment_results:
        analysis_results['sentiment_analysis'] = sentiment_results
    
    # 4. 构建知识图谱
    graph_files = build_knowledge_graph(filepath, content_name)
    if graph_files:
        analysis_results['graph_files'] = graph_files
    
    # 5. 生成报告
    report_file = generate_report(content_name, args.type, analysis_results)
    
    # 总结
    print(f"\n{'='*60}")
    print("🎉 分析完成！")
    print(f"{'='*60}")
    
    if analysis_results:
        print("\n📁 生成的文件:")
        if 'wordcloud_files' in analysis_results:
            for file in analysis_results['wordcloud_files']:
                print(f"  📊 词云图: {file}")
        
        if 'graph_files' in analysis_results:
            for file in analysis_results['graph_files']:
                print(f"  🕸️ 知识图谱: {file}")
        
        if report_file:
            print(f"  📋 分析报告: {report_file}")
        
        print(f"\n💡 提示: 所有结果文件都保存在 {OUTPUT_DIR} 目录中")
        print("请使用浏览器打开HTML文件查看详细结果！")
    
    else:
        print("未能生成分析结果，请检查数据和配置")


if __name__ == '__main__':
    main() 