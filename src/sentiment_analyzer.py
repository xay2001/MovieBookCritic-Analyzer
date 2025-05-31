# -*- coding: utf-8 -*-
"""
情感分析模块
用于分析评论文本的情感倾向
"""

import os
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from snownlp import SnowNLP

from config.config import SENTIMENT_CONFIG, CHART_CONFIG


class SentimentAnalyzer:
    """情感分析器类"""
    
    def __init__(self):
        """初始化情感分析器"""
        self.comments_data = []
        self.sentiment_scores = []
        self.sentiment_labels = []
        self.time_sentiment = defaultdict(list)
        
        # 设置matplotlib样式
        plt.style.use(CHART_CONFIG['style'])
        plt.rcParams['font.sans-serif'] = CHART_CONFIG['font_family']
        plt.rcParams['axes.unicode_minus'] = False
    
    def load_data_from_file(self, filepath):
        """
        从文件加载评论数据
        
        Args:
            filepath (str): 文件路径
        """
        try:
            if filepath.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.comments_data = json.load(f)
            elif filepath.endswith('.txt'):
                self.comments_data = self._parse_txt_file(filepath)
            else:
                raise ValueError("不支持的文件格式，请使用.json或.txt文件")
            
            print(f"加载评论数据 {len(self.comments_data)} 条")
            
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.comments_data = []
    
    def _parse_txt_file(self, filepath):
        """解析txt格式的评论文件"""
        comments = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按分隔符分割评论
            comment_blocks = content.split('-' * 50)
            
            for block in comment_blocks:
                if not block.strip():
                    continue
                
                lines = block.strip().split('\n')
                comment_data = {}
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('评论时间:'):
                        comment_data['time'] = line.replace('评论时间:', '').strip()
                    elif line.startswith('用户:'):
                        comment_data['username'] = line.replace('用户:', '').strip()
                    elif line.startswith('评分:'):
                        try:
                            comment_data['rating'] = float(line.replace('评分:', '').strip())
                        except:
                            comment_data['rating'] = None
                    elif line.startswith('内容:'):
                        comment_data['content'] = line.replace('内容:', '').strip()
                
                if 'content' in comment_data and comment_data['content']:
                    if 'time' not in comment_data:
                        comment_data['time'] = datetime.now().strftime('%Y-%m-%d')
                    if 'username' not in comment_data:
                        comment_data['username'] = '匿名用户'
                    comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            print(f"解析txt文件失败: {e}")
            return []
    
    def analyze_sentiment(self):
        """分析情感倾向"""
        print("开始情感分析...")
        
        self.sentiment_scores = []
        self.sentiment_labels = []
        self.time_sentiment = defaultdict(list)
        
        for comment in self.comments_data:
            content = comment.get('content', '')
            if not content:
                continue
            
            # 使用SnowNLP进行情感分析
            try:
                s = SnowNLP(content)
                sentiment_score = s.sentiments
                
                # 根据阈值判断情感类别
                if sentiment_score >= SENTIMENT_CONFIG['positive_threshold']:
                    sentiment_label = 'positive'
                elif sentiment_score <= SENTIMENT_CONFIG['negative_threshold']:
                    sentiment_label = 'negative'
                else:
                    sentiment_label = 'neutral'
                
                self.sentiment_scores.append(sentiment_score)
                self.sentiment_labels.append(sentiment_label)
                
                # 按时间分组
                comment_time = comment.get('time', '')
                time_key = self._extract_time_key(comment_time)
                self.time_sentiment[time_key].append(sentiment_score)
                
            except Exception as e:
                print(f"分析评论情感时出错: {e}")
                continue
        
        print(f"情感分析完成，共分析 {len(self.sentiment_scores)} 条评论")
        self._print_sentiment_stats()
    
    def _extract_time_key(self, time_str):
        """从时间字符串提取时间键（年-月）"""
        try:
            # 尝试不同的时间格式
            time_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y年%m月%d日']
            
            for fmt in time_formats:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    return dt.strftime('%Y-%m')
                except ValueError:
                    continue
            
            # 如果无法解析，返回默认值
            return datetime.now().strftime('%Y-%m')
            
        except:
            return datetime.now().strftime('%Y-%m')
    
    def _print_sentiment_stats(self):
        """打印情感统计信息"""
        if not self.sentiment_scores:
            return
        
        positive_count = self.sentiment_labels.count('positive')
        negative_count = self.sentiment_labels.count('negative')
        neutral_count = self.sentiment_labels.count('neutral')
        total_count = len(self.sentiment_labels)
        
        avg_score = np.mean(self.sentiment_scores)
        
        print(f"\n=== 情感分析统计 ===")
        print(f"积极评论: {positive_count} ({positive_count/total_count*100:.1f}%)")
        print(f"消极评论: {negative_count} ({negative_count/total_count*100:.1f}%)")
        print(f"中性评论: {neutral_count} ({neutral_count/total_count*100:.1f}%)")
        print(f"平均情感得分: {avg_score:.3f}")
        
        if avg_score >= SENTIMENT_CONFIG['positive_threshold']:
            overall_sentiment = "积极"
        elif avg_score <= SENTIMENT_CONFIG['negative_threshold']:
            overall_sentiment = "消极"
        else:
            overall_sentiment = "中性"
        
        print(f"整体情感倾向: {overall_sentiment}")
    
    def plot_sentiment_distribution(self, save_path=None):
        """
        绘制情感分布图
        
        Args:
            save_path (str): 保存路径
        """
        if not self.sentiment_scores:
            print("请先进行情感分析")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 情感得分直方图
        ax1.hist(self.sentiment_scores, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(SENTIMENT_CONFIG['positive_threshold'], color='green', linestyle='--', 
                   label=f'积极阈值 ({SENTIMENT_CONFIG["positive_threshold"]})')
        ax1.axvline(SENTIMENT_CONFIG['negative_threshold'], color='red', linestyle='--', 
                   label=f'消极阈值 ({SENTIMENT_CONFIG["negative_threshold"]})')
        ax1.set_xlabel('情感得分')
        ax1.set_ylabel('频次')
        ax1.set_title('情感得分分布')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 情感类别饼图
        sentiment_counts = Counter(self.sentiment_labels)
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        labels = ['消极', '中性', '积极']
        sizes = [sentiment_counts.get('negative', 0), 
                sentiment_counts.get('neutral', 0), 
                sentiment_counts.get('positive', 0)]
        
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('情感类别分布')
        
        # 3. 情感得分箱线图
        sentiment_data = [
            [score for score, label in zip(self.sentiment_scores, self.sentiment_labels) if label == 'negative'],
            [score for score, label in zip(self.sentiment_scores, self.sentiment_labels) if label == 'neutral'],
            [score for score, label in zip(self.sentiment_scores, self.sentiment_labels) if label == 'positive']
        ]
        
        box_plot = ax3.boxplot(sentiment_data, labels=['消极', '中性', '积极'], patch_artist=True)
        box_colors = ['#ff9999', '#66b3ff', '#99ff99']
        for patch, color in zip(box_plot['boxes'], box_colors):
            patch.set_facecolor(color)
        
        ax3.set_ylabel('情感得分')
        ax3.set_title('各类别情感得分分布')
        ax3.grid(True, alpha=0.3)
        
        # 4. 情感得分散点图（时间序列）
        if len(self.sentiment_scores) == len(self.comments_data):
            colors_map = {'positive': 'green', 'neutral': 'blue', 'negative': 'red'}
            colors = [colors_map[label] for label in self.sentiment_labels]
            
            x_values = range(len(self.sentiment_scores))
            ax4.scatter(x_values, self.sentiment_scores, c=colors, alpha=0.6, s=30)
            ax4.axhline(SENTIMENT_CONFIG['positive_threshold'], color='green', linestyle='--', alpha=0.7)
            ax4.axhline(SENTIMENT_CONFIG['negative_threshold'], color='red', linestyle='--', alpha=0.7)
            ax4.set_xlabel('评论序号')
            ax4.set_ylabel('情感得分')
            ax4.set_title('情感得分时序分布')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
            print(f"情感分析图已保存到: {save_path}")
        
        plt.show()
    
    def plot_time_sentiment_trend(self, save_path=None):
        """
        绘制情感时间趋势图
        
        Args:
            save_path (str): 保存路径
        """
        if not self.time_sentiment:
            print("请先进行情感分析")
            return
        
        # 计算每个时间段的平均情感得分
        time_keys = sorted(self.time_sentiment.keys())
        avg_sentiments = []
        sentiment_stds = []
        positive_ratios = []
        negative_ratios = []
        
        for time_key in time_keys:
            scores = self.time_sentiment[time_key]
            avg_sentiments.append(np.mean(scores))
            sentiment_stds.append(np.std(scores))
            
            # 计算积极和消极比例
            positive_count = sum(1 for score in scores if score >= SENTIMENT_CONFIG['positive_threshold'])
            negative_count = sum(1 for score in scores if score <= SENTIMENT_CONFIG['negative_threshold'])
            total_count = len(scores)
            
            positive_ratios.append(positive_count / total_count * 100)
            negative_ratios.append(negative_count / total_count * 100)
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(CHART_CONFIG['figure_size'][0], 
                                                     CHART_CONFIG['figure_size'][1] * 1.2))
        
        # 1. 平均情感得分趋势
        ax1.plot(time_keys, avg_sentiments, marker='o', linewidth=2, markersize=6, 
                color='blue', label='平均情感得分')
        ax1.fill_between(time_keys, 
                        np.array(avg_sentiments) - np.array(sentiment_stds),
                        np.array(avg_sentiments) + np.array(sentiment_stds),
                        alpha=0.3, color='blue')
        
        ax1.axhline(SENTIMENT_CONFIG['positive_threshold'], color='green', linestyle='--', 
                   label=f'积极阈值 ({SENTIMENT_CONFIG["positive_threshold"]})')
        ax1.axhline(SENTIMENT_CONFIG['negative_threshold'], color='red', linestyle='--', 
                   label=f'消极阈值 ({SENTIMENT_CONFIG["negative_threshold"]})')
        
        ax1.set_ylabel('情感得分')
        ax1.set_title('情感得分时间趋势')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 积极/消极比例趋势
        ax2.plot(time_keys, positive_ratios, marker='o', linewidth=2, markersize=6, 
                color='green', label='积极评论比例')
        ax2.plot(time_keys, negative_ratios, marker='s', linewidth=2, markersize=6, 
                color='red', label='消极评论比例')
        
        ax2.set_xlabel('时间')
        ax2.set_ylabel('比例 (%)')
        ax2.set_title('积极/消极评论比例时间趋势')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
            print(f"情感趋势图已保存到: {save_path}")
        
        plt.show()
    
    def analyze_sentiment_by_rating(self):
        """按评分分析情感倾向"""
        if not self.sentiment_scores or not self.comments_data:
            print("请先进行情感分析")
            return
        
        # 收集有评分的评论数据
        rating_sentiment_data = []
        for i, comment in enumerate(self.comments_data):
            if i < len(self.sentiment_scores) and comment.get('rating') is not None:
                rating_sentiment_data.append({
                    'rating': comment['rating'],
                    'sentiment_score': self.sentiment_scores[i],
                    'sentiment_label': self.sentiment_labels[i]
                })
        
        if not rating_sentiment_data:
            print("没有找到带评分的评论数据")
            return
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(rating_sentiment_data)
        
        # 按评分分组统计
        rating_groups = df.groupby('rating').agg({
            'sentiment_score': ['mean', 'std', 'count'],
            'sentiment_label': lambda x: (x == 'positive').sum() / len(x) * 100
        }).round(3)
        
        print("\n=== 评分-情感倾向分析 ===")
        print("评分\t平均情感得分\t标准差\t评论数\t积极比例(%)")
        for rating in sorted(df['rating'].unique()):
            group_data = df[df['rating'] == rating]
            avg_sentiment = group_data['sentiment_score'].mean()
            std_sentiment = group_data['sentiment_score'].std()
            count = len(group_data)
            positive_ratio = (group_data['sentiment_label'] == 'positive').sum() / count * 100
            
            print(f"{rating}\t{avg_sentiment:.3f}\t\t{std_sentiment:.3f}\t{count}\t{positive_ratio:.1f}")
        
        return df
    
    def get_extreme_comments(self, n_positive=5, n_negative=5):
        """
        获取极端情感评论
        
        Args:
            n_positive (int): 最积极评论数量
            n_negative (int): 最消极评论数量
            
        Returns:
            dict: 极端评论数据
        """
        if not self.sentiment_scores:
            print("请先进行情感分析")
            return {}
        
        # 创建评论-情感得分对
        comment_sentiment_pairs = list(zip(self.comments_data, self.sentiment_scores))
        
        # 按情感得分排序
        sorted_pairs = sorted(comment_sentiment_pairs, key=lambda x: x[1])
        
        # 获取最消极和最积极的评论
        most_negative = sorted_pairs[:n_negative]
        most_positive = sorted_pairs[-n_positive:][::-1]  # 倒序，从最积极开始
        
        result = {
            'most_positive': [{'content': comment['content'], 'sentiment_score': score, 'time': comment.get('time', '')} 
                             for comment, score in most_positive],
            'most_negative': [{'content': comment['content'], 'sentiment_score': score, 'time': comment.get('time', '')} 
                             for comment, score in most_negative]
        }
        
        print(f"\n=== 最积极的{n_positive}条评论 ===")
        for i, item in enumerate(result['most_positive'], 1):
            print(f"{i}. 情感得分: {item['sentiment_score']:.3f}")
            print(f"   内容: {item['content'][:100]}...")
            print(f"   时间: {item['time']}")
            print()
        
        print(f"\n=== 最消极的{n_negative}条评论 ===")
        for i, item in enumerate(result['most_negative'], 1):
            print(f"{i}. 情感得分: {item['sentiment_score']:.3f}")
            print(f"   内容: {item['content'][:100]}...")
            print(f"   时间: {item['time']}")
            print()
        
        return result
    
    def save_sentiment_results(self, output_dir):
        """
        保存情感分析结果
        
        Args:
            output_dir (str): 输出目录
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存详细结果
            detailed_results = []
            for i, comment in enumerate(self.comments_data):
                if i < len(self.sentiment_scores):
                    detailed_results.append({
                        'content': comment.get('content', ''),
                        'time': comment.get('time', ''),
                        'username': comment.get('username', ''),
                        'rating': comment.get('rating'),
                        'sentiment_score': self.sentiment_scores[i],
                        'sentiment_label': self.sentiment_labels[i]
                    })
            
            # 保存为JSON
            results_file = os.path.join(output_dir, 'sentiment_analysis_detailed.json')
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_results, f, ensure_ascii=False, indent=2)
            
            # 保存统计摘要
            summary = self.get_sentiment_summary()
            summary_file = os.path.join(output_dir, 'sentiment_analysis_summary.json')
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            # 保存时间趋势数据
            time_trend_data = {}
            for time_key, scores in self.time_sentiment.items():
                time_trend_data[time_key] = {
                    'avg_sentiment': np.mean(scores),
                    'sentiment_std': np.std(scores),
                    'positive_ratio': sum(1 for s in scores if s >= SENTIMENT_CONFIG['positive_threshold']) / len(scores),
                    'negative_ratio': sum(1 for s in scores if s <= SENTIMENT_CONFIG['negative_threshold']) / len(scores),
                    'comment_count': len(scores)
                }
            
            time_trend_file = os.path.join(output_dir, 'sentiment_time_trend.json')
            with open(time_trend_file, 'w', encoding='utf-8') as f:
                json.dump(time_trend_data, f, ensure_ascii=False, indent=2)
            
            print(f"情感分析结果已保存到: {output_dir}")
            
        except Exception as e:
            print(f"保存情感分析结果失败: {e}")
    
    def get_sentiment_summary(self):
        """
        获取情感分析摘要
        
        Returns:
            dict: 摘要数据
        """
        if not self.sentiment_scores:
            return {}
        
        positive_count = self.sentiment_labels.count('positive')
        negative_count = self.sentiment_labels.count('negative')
        neutral_count = self.sentiment_labels.count('neutral')
        total_count = len(self.sentiment_labels)
        
        summary = {
            'total_comments': total_count,
            'avg_sentiment_score': np.mean(self.sentiment_scores),
            'sentiment_std': np.std(self.sentiment_scores),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': positive_count / total_count,
            'negative_ratio': negative_count / total_count,
            'neutral_ratio': neutral_count / total_count,
            'overall_sentiment': 'positive' if np.mean(self.sentiment_scores) >= SENTIMENT_CONFIG['positive_threshold']
                                else 'negative' if np.mean(self.sentiment_scores) <= SENTIMENT_CONFIG['negative_threshold']
                                else 'neutral'
        }
        
        return summary


def main():
    """测试函数"""
    analyzer = SentimentAnalyzer()
    
    # 假设已有数据文件
    data_file = 'data/肖申克的救赎.json'
    if os.path.exists(data_file):
        analyzer.load_data_from_file(data_file)
        analyzer.analyze_sentiment()
        
        # 生成图表
        analyzer.plot_sentiment_distribution(save_path='output/charts/sentiment_distribution.png')
        analyzer.plot_time_sentiment_trend(save_path='output/charts/sentiment_time_trend.png')
        
        # 分析评分与情感的关系
        analyzer.analyze_sentiment_by_rating()
        
        # 获取极端评论
        analyzer.get_extreme_comments()
        
        # 保存结果
        analyzer.save_sentiment_results('output')
        
        # 打印摘要
        summary = analyzer.get_sentiment_summary()
        print("\n=== 情感分析摘要 ===")
        for key, value in summary.items():
            print(f"{key}: {value}")


if __name__ == '__main__':
    main() 