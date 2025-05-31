# -*- coding: utf-8 -*-
"""
文本分析模块
用于对评论文本进行分词、词频分析和关键词提取
"""

import os
import re
import json
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd
import numpy as np
import jieba
import jieba.analyse
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm

from config.config import TEXT_ANALYSIS_CONFIG, CHART_CONFIG


class TextAnalyzer:
    """文本分析器类"""
    
    def __init__(self):
        """初始化文本分析器"""
        self.stopwords = self._load_stopwords()
        self.comments_data = []
        self.word_freq = Counter()
        self.time_word_freq = defaultdict(Counter)
        self.keywords = []
        
        # 设置matplotlib中文字体
        self._setup_matplotlib_font()
        
        # 添加自定义词典
        self._add_custom_words()
    
    def _setup_matplotlib_font(self):
        """设置matplotlib中文字体"""
        import matplotlib.font_manager as fm
        
        # 设置图表样式
        plt.style.use(CHART_CONFIG['style'])
        
        # 尝试设置中文字体
        font_found = False
        chinese_font_path = None
        
        # 首先尝试使用STHeiti Light字体
        heiti_path = '/System/Library/Fonts/STHeiti Light.ttc'
        if os.path.exists(heiti_path):
            chinese_font_path = heiti_path
            font_found = True
        else:
            # 如果找不到STHeiti Light，尝试其他中文字体
            for font_family in CHART_CONFIG['font_family']:
                try:
                    for f in fm.findSystemFonts():
                        if font_family.lower() in f.lower():
                            chinese_font_path = f
                            font_found = True
                            break
                    if font_found:
                        break
                except Exception as e:
                    print(f"尝试设置字体 {font_family} 失败: {str(e)}")
                    continue
        
        if font_found and chinese_font_path:
            # 创建字体属性对象
            chinese_font_prop = fm.FontProperties(fname=chinese_font_path)
            
            # 全局设置
            plt.rcParams['font.family'] = ['sans-serif']
            plt.rcParams['font.sans-serif'] = [chinese_font_prop.get_name()]
            plt.rcParams['axes.unicode_minus'] = False
            
            # 保存字体属性以供后续使用
            self.font_prop = chinese_font_prop
            
            print(f"成功设置中文字体: {chinese_font_prop.get_name()}")
        else:
            print("警告: 未找到合适的中文字体，将使用系统默认字体")
            plt.rcParams['font.family'] = ['sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            self.font_prop = None
        
        # 设置其他图表参数
        plt.rcParams['figure.figsize'] = CHART_CONFIG['figure_size']
        plt.rcParams['figure.dpi'] = CHART_CONFIG['dpi']
        plt.rcParams['axes.titlesize'] = CHART_CONFIG['font_size']['title']
        plt.rcParams['axes.labelsize'] = CHART_CONFIG['font_size']['label']
        plt.rcParams['xtick.labelsize'] = CHART_CONFIG['font_size']['tick']
        plt.rcParams['ytick.labelsize'] = CHART_CONFIG['font_size']['tick']
        plt.rcParams['legend.fontsize'] = CHART_CONFIG['font_size']['legend']
    
    def _load_stopwords(self):
        """加载停用词"""
        stopwords = set()
        try:
            if os.path.exists(TEXT_ANALYSIS_CONFIG['stopwords_file']):
                with open(TEXT_ANALYSIS_CONFIG['stopwords_file'], 'r', encoding='utf-8') as f:
                    stopwords = set(line.strip() for line in f if line.strip())
            print(f"加载停用词 {len(stopwords)} 个")
        except Exception as e:
            print(f"加载停用词失败: {e}")
        
        # 添加额外的停用词
        extra_stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '上', 
            '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '还',
            '这', '来', '电影', '影片', '片子', '图书', '书', '小说', '作品', '故事',
            '觉得', '感觉', '真的', '确实', '应该', '可能', '比较', '非常', '特别', '挺',
            '太', '最', '更', '还是', '但是', '不过', '虽然', '如果', '因为', '所以',
            '然后', '而且', '或者', '以及', '对于', '关于', '。', '，', '！', '？', '；',
            '：', '"', '"', ''', ''', '（', '）', '【', '】', '《', '》', '、', '…',
        }
        stopwords.update(extra_stopwords)
        
        return stopwords
    
    def _add_custom_words(self):
        """添加自定义词典"""
        # 添加一些常见的电影/图书相关词汇
        custom_words = [
            '剧情', '演技', '特效', '配音', '配乐', '摄影', '导演', '编剧', '主演',
            '男主', '女主', '反派', '配角', '剧本', '台词', 'bgm', '背景音乐',
            '情节', '人物', '角色', '性格', '形象', '塑造', '刻画', '描写',
            '文笔', '写作', '叙述', '描述', '情感', '感情', '爱情', '友情',
            '亲情', '悬疑', '推理', '科幻', '奇幻', '恐怖', '喜剧', '悲剧',
            '动作', '冒险', '历史', '传记', '纪录', '动画', '漫画', '小说',
        ]
        
        for word in custom_words:
            jieba.add_word(word)
    
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
    
    def segment_text(self, text):
        """
        文本分词
        
        Args:
            text (str): 待分词文本
            
        Returns:
            list: 分词结果列表
        """
        # 清理文本
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        
        # 分词
        words = jieba.lcut(text)
        
        # 过滤停用词和长度不符合要求的词
        filtered_words = []
        for word in words:
            word = word.strip()
            if (word and 
                word not in self.stopwords and 
                TEXT_ANALYSIS_CONFIG['min_word_length'] <= len(word) <= TEXT_ANALYSIS_CONFIG['max_word_length'] and
                not word.isdigit()):
                filtered_words.append(word)
        
        return filtered_words
    
    def analyze_word_frequency(self):
        """分析词频"""
        print("开始词频分析...")
        
        all_words = []
        
        for comment in self.comments_data:
            content = comment.get('content', '')
            words = self.segment_text(content)
            all_words.extend(words)
            
            # 按时间分组统计词频
            comment_time = comment.get('time', '')
            time_key = self._extract_time_key(comment_time)
            self.time_word_freq[time_key].update(words)
        
        # 统计总体词频
        self.word_freq = Counter(all_words)
        
        print(f"总词数: {len(all_words)}")
        print(f"不重复词数: {len(self.word_freq)}")
        print(f"时间段数: {len(self.time_word_freq)}")
    
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
    
    def extract_keywords(self, top_n=None):
        """
        提取关键词
        
        Args:
            top_n (int): 提取的关键词数量
            
        Returns:
            list: 关键词列表
        """
        if top_n is None:
            top_n = TEXT_ANALYSIS_CONFIG['top_words_count']
        
        # 合并所有评论文本
        all_text = ' '.join([comment.get('content', '') for comment in self.comments_data])
        
        # 使用TF-IDF提取关键词
        keywords_tfidf = jieba.analyse.extract_tags(all_text, topK=top_n, withWeight=True)
        
        # 使用TextRank提取关键词
        keywords_textrank = jieba.analyse.textrank(all_text, topK=top_n, withWeight=True)
        
        # 合并两种方法的结果
        keyword_scores = {}
        for word, score in keywords_tfidf:
            keyword_scores[word] = keyword_scores.get(word, 0) + score
        
        for word, score in keywords_textrank:
            keyword_scores[word] = keyword_scores.get(word, 0) + score * 0.5  # TextRank权重稍低
        
        # 按分数排序
        self.keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        print(f"提取关键词 {len(self.keywords)} 个")
        return self.keywords
    
    def plot_word_frequency(self, top_n=20, save_path=None):
        """
        绘制词频图
        
        Args:
            top_n (int): 显示的高频词数量
            save_path (str): 保存路径
        """
        if not self.word_freq:
            print("请先进行词频分析")
            return
        
        # 获取高频词
        top_words = self.word_freq.most_common(top_n)
        words, freqs = zip(*top_words)
        
        # 创建图表
        plt.figure(figsize=CHART_CONFIG['figure_size'])
        
        # 创建条形图
        bars = plt.bar(range(len(words)), freqs, color=plt.cm.viridis(np.linspace(0, 1, len(words))))
        
        # 设置标签和标题
        plt.xlabel('词汇', fontsize=CHART_CONFIG['font_size']['label'], fontproperties=self.font_prop)
        plt.ylabel('频次', fontsize=CHART_CONFIG['font_size']['label'], fontproperties=self.font_prop)
        plt.title(f'词频分析 (Top {top_n})', fontsize=CHART_CONFIG['font_size']['title'], 
                 fontproperties=self.font_prop, pad=20)
        
        # 设置x轴标签
        plt.xticks(range(len(words)), words, rotation=45, ha='right', 
                  fontsize=CHART_CONFIG['font_size']['tick'], fontproperties=self.font_prop)
        
        # 在条形图上添加数值标签
        for i, (bar, freq) in enumerate(zip(bars, freqs)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + freq*0.01,
                    str(freq), ha='center', va='bottom', 
                    fontsize=CHART_CONFIG['font_size']['annotation'], fontproperties=self.font_prop)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight', facecolor='white')
            print(f"词频图已保存到: {save_path}")
        
        plt.show()
    
    def plot_time_word_trend(self, top_n=10, save_path=None):
        """
        绘制词频随时间的变化趋势
        
        Args:
            top_n (int): 显示的高频词数量
            save_path (str): 保存路径
        """
        if not self.time_word_freq:
            print("请先进行时间维度的词频分析")
            return
        
        # 获取所有时间点
        time_points = sorted(self.time_word_freq.keys())
        
        # 获取总体高频词
        total_freq = Counter()
        for time_freq in self.time_word_freq.values():
            total_freq.update(time_freq)
        top_words = [word for word, _ in total_freq.most_common(top_n)]
        
        # 创建数据矩阵
        data = []
        for word in top_words:
            word_trend = []
            for time in time_points:
                freq = self.time_word_freq[time].get(word, 0)
                word_trend.append(freq)
            data.append(word_trend)
        
        # 创建图表
        plt.figure(figsize=CHART_CONFIG['figure_size'])
        
        # 绘制趋势线
        for i, word_data in enumerate(data):
            plt.plot(range(len(time_points)), word_data, 
                    marker='o', linewidth=2, label=top_words[i])
        
        # 设置标签和标题
        plt.xlabel('时间', fontsize=CHART_CONFIG['font_size']['label'], 
                  fontproperties=self.font_prop)
        plt.ylabel('词频', fontsize=CHART_CONFIG['font_size']['label'], 
                  fontproperties=self.font_prop)
        plt.title('词频时间趋势分析', fontsize=CHART_CONFIG['font_size']['title'], 
                 fontproperties=self.font_prop, pad=20)
        
        # 设置x轴标签
        plt.xticks(range(len(time_points)), time_points, 
                  rotation=45, ha='right', 
                  fontsize=CHART_CONFIG['font_size']['tick'])
        
        # 设置图例
        plt.legend(prop=self.font_prop, 
                  fontsize=CHART_CONFIG['font_size']['legend'], 
                  loc='upper right', 
                  bbox_to_anchor=(1.15, 1))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
            print(f"词频趋势图已保存到: {save_path}")
        
        plt.show()
    
    def get_analysis_report(self):
        """
        生成分析报告
        
        Returns:
            dict: 分析报告数据
        """
        report = {
            'basic_stats': {
                'total_comments': len(self.comments_data),
                'total_words': sum(self.word_freq.values()),
                'unique_words': len(self.word_freq),
                'avg_words_per_comment': sum(self.word_freq.values()) / len(self.comments_data) if self.comments_data else 0,
            },
            'top_words': self.word_freq.most_common(20),
            'keywords': self.keywords[:20] if self.keywords else [],
            'time_periods': len(self.time_word_freq),
        }
        
        return report
    
    def save_analysis_results(self, output_dir):
        """
        保存分析结果
        
        Args:
            output_dir (str): 输出目录
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存词频数据
            word_freq_file = os.path.join(output_dir, 'word_frequency.json')
            with open(word_freq_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.word_freq.most_common(100)), f, ensure_ascii=False, indent=2)
            
            # 保存关键词
            keywords_file = os.path.join(output_dir, 'keywords.json')
            with open(keywords_file, 'w', encoding='utf-8') as f:
                json.dump(self.keywords, f, ensure_ascii=False, indent=2)
            
            # 保存时间趋势数据
            time_trend_file = os.path.join(output_dir, 'time_word_frequency.json')
            time_trend_data = {}
            for time_key, word_counter in self.time_word_freq.items():
                time_trend_data[time_key] = dict(word_counter.most_common(50))
            
            with open(time_trend_file, 'w', encoding='utf-8') as f:
                json.dump(time_trend_data, f, ensure_ascii=False, indent=2)
            
            # 保存分析报告
            report = self.get_analysis_report()
            report_file = os.path.join(output_dir, 'analysis_report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"分析结果已保存到: {output_dir}")
            
        except Exception as e:
            print(f"保存分析结果失败: {e}")


def main():
    """测试函数"""
    analyzer = TextAnalyzer()
    
    # 假设已有数据文件
    data_file = 'data/肖申克的救赎.json'
    if os.path.exists(data_file):
        analyzer.load_data_from_file(data_file)
        analyzer.analyze_word_frequency()
        analyzer.extract_keywords()
        
        # 生成图表
        analyzer.plot_word_frequency(save_path='output/charts/word_frequency.png')
        analyzer.plot_time_word_trend(save_path='output/charts/time_word_trend.png')
        
        # 保存分析结果
        analyzer.save_analysis_results('output')
        
        # 打印报告
        report = analyzer.get_analysis_report()
        print("\n=== 分析报告 ===")
        print(f"总评论数: {report['basic_stats']['total_comments']}")
        print(f"总词数: {report['basic_stats']['total_words']}")
        print(f"不重复词数: {report['basic_stats']['unique_words']}")
        print(f"平均每条评论词数: {report['basic_stats']['avg_words_per_comment']:.2f}")
        
        print("\n高频词Top10:")
        for word, freq in report['top_words'][:10]:
            print(f"{word}: {freq}")


if __name__ == '__main__':
    main() 