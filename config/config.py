# -*- coding: utf-8 -*-
"""
配置文件
包含项目的各种配置参数
"""

import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# 爬虫配置
CRAWLER_CONFIG = {
    'max_comments': 1000,           # 最大评论数量
    'delay_min': 1,                 # 最小延迟时间（秒）
    'delay_max': 3,                 # 最大延迟时间（秒）
    'page_load_timeout': 30,        # 页面加载超时时间
    'implicit_wait': 10,            # 隐式等待时间
    'retry_times': 3,               # 重试次数
    'user_agents': [                # 用户代理列表
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
}

# 豆瓣网站配置
DOUBAN_CONFIG = {
    'movie_search_url': 'https://movie.douban.com/subject_search?search_text={}&cat=1002',
    'book_search_url': 'https://book.douban.com/subject_search?search_text={}',
    'movie_base_url': 'https://movie.douban.com',
    'book_base_url': 'https://book.douban.com',
    'movie_comments_url': 'https://movie.douban.com/subject/{}/comments',
    'book_comments_url': 'https://book.douban.com/subject/{}/comments'
}

# 文本分析配置
TEXT_ANALYSIS_CONFIG = {
    'min_word_length': 2,           # 最小词长度
    'max_word_length': 10,          # 最大词长度
    'top_words_count': 100,         # 高频词数量
    'stopwords_file': os.path.join(BASE_DIR, 'config', 'stopwords.txt'),
}

# 词云配置
WORDCLOUD_CONFIG = {
    'width': 1200,
    'height': 800,
    'background_color': 'white',
    'max_words': 100,
    'max_font_size': 100,
    'min_font_size': 10,
    'colormap': 'viridis',
    'font_path': None,  # 将在运行时自动检测中文字体
}

# 情感分析配置
SENTIMENT_CONFIG = {
    'positive_threshold': 0.6,      # 积极情感阈值
    'negative_threshold': 0.4,      # 消极情感阈值
    'neutral_range': (0.4, 0.6),    # 中性情感范围
}

# 知识图谱配置
KNOWLEDGE_GRAPH_CONFIG = {
    'min_cooccurrence': 3,          # 最小共现次数
    'max_nodes': 50,                # 最大节点数
    'layout': 'spring',             # 布局算法
    'node_size_multiplier': 100,    # 节点大小倍数
    'edge_width_multiplier': 2,     # 边宽度倍数
}

# 图表配置
CHART_CONFIG = {
    'style': 'seaborn-v0_8',          # 图表样式
    'figure_size': (12, 8),           # 图表大小
    'dpi': 300,                       # 分辨率
    'font_family': [
        'PingFang SC',                # 苹方字体
        'Heiti SC',                   # 黑体
        'Songti SC',                  # 宋体
        'Kaiti SC',                   # 楷体
        'STHeiti Light',              # 华文黑体
        'Microsoft YaHei',            # 微软雅黑
        'SimHei',                     # 中易黑体
        'Arial Unicode MS',           # Arial Unicode
        'DejaVu Sans'                 # 备用西文字体
    ],
    'font_size': {
        'title': 16,                  # 标题字号
        'label': 12,                  # 标签字号
        'tick': 10,                   # 刻度字号
        'legend': 10,                 # 图例字号
        'annotation': 9               # 注释字号
    },
    'colors': {
        'primary': '#2878B5',         # 主要颜色
        'secondary': '#9AC9DB',       # 次要颜色
        'highlight': '#C82423',       # 高亮颜色
        'background': '#FFFFFF'        # 背景颜色
    }
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(BASE_DIR, 'logs', 'app.log'),
} 