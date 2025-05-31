# 豆瓣电影/图书评论分析系统使用指南

## 🎯 项目概述

这是一个完整的豆瓣电影/图书评论分析系统，能够自动收集评论数据，进行深度文本分析、情感分析、词云生成和知识图谱构建。

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖包
pip install -r requirements.txt
```

### 2. 运行演示

```bash
# 使用示例数据运行完整演示
python demo.py
```

### 3. 分析现有文件

```bash
# 分析指定文件
python main.py --analyze_only --file data/sample_movie_comments.txt
```

### 4. 完整数据收集和分析

```bash
# 分析电影评论
python main.py --type movie --name "流浪地球2" --max_comments 500

# 分析图书评论
python main.py --type book --name "三体" --max_comments 1000
```

## 📋 功能模块

### 1. 数据收集模块 (`src/crawler.py`)

**功能特性:**
- 🔍 智能豆瓣评论爬取
- 🌐 支持电影和图书评论
- 🛡️ 内置反爬虫机制
- 📊 支持多种数据格式输出

**使用示例:**
```python
from src.crawler import DoubanCrawler

crawler = DoubanCrawler()
crawler.set_search_target("movie", "流浪地球2")
crawler.collect_comments(max_comments=500)
```

### 2. 文本分析模块 (`src/text_analyzer.py`)

**功能特性:**
- ✂️ 智能中文分词 (jieba)
- 📈 词频统计和分析
- ⏰ 时间维度词频趋势
- 🔑 关键词提取 (TF-IDF + TextRank)
- 📊 可视化图表生成

**分析结果:**
- 词频分析图表
- 时间趋势图
- 关键词列表
- 统计数据JSON

### 3. 词云生成模块 (`src/wordcloud_generator.py`)

**功能特性:**
- 🎨 多种词云样式 (基础、心形、星形)
- 🖥️ 自动中文字体检测
- 🌈 美观的色彩搭配
- 📐 高分辨率输出

**生成的词云:**
- 基础矩形词云
- 心形词云
- 星形词云

### 4. 情感分析模块 (`src/sentiment_analyzer.py`)

**功能特性:**
- 🎭 中文情感分析 (SnowNLP)
- 📊 情感分布统计
- 📈 时间维度情感趋势
- 🔍 极端评论提取
- 💯 评分与情感关联分析

**分析指标:**
- 情感得分 (0-1)
- 积极/消极/中性分类
- 情感趋势变化
- 代表性评论提取

### 5. 知识图谱模块 (`src/knowledge_graph.py`)

**功能特性:**
- 🧠 智能实体识别
- 🔗 关系网络构建
- 📊 图谱统计分析
- 🌐 交互式可视化

**输出格式:**
- 静态图谱 (PNG)
- 交互式网页 (HTML)
- 图谱数据 (JSON)

## 📊 输出文件说明

### 数据文件 (`output/`)
- `word_frequency.json` - 词频数据
- `keywords.json` - 关键词列表
- `sentiment_analysis_summary.json` - 情感分析摘要
- `sentiment_analysis_detailed.json` - 详细情感数据
- `entities.json` - 实体数据
- `relations.json` - 关系数据

### 图表文件 (`output/charts/`)
- `word_frequency.png` - 词频柱状图
- `time_word_trend.png` - 词频时间趋势图
- `sentiment_distribution.png` - 情感分布图
- `sentiment_time_trend.png` - 情感时间趋势图

### 词云文件 (`output/wordclouds/`)
- `{name}_basic.png` - 基础词云
- `{name}_heart.png` - 心形词云
- `{name}_star.png` - 星形词云

### 图谱文件 (`output/graphs/`)
- `{name}_knowledge_graph.png` - 静态知识图谱
- `{name}_interactive_graph.html` - 交互式知识图谱

### 报告文件
- `analysis_report.html` - 完整分析报告

## ⚙️ 配置选项

### 系统配置 (`config/config.py`)

```python
# 基础配置
DATA_DIR = "data"           # 数据目录
OUTPUT_DIR = "output"       # 输出目录
LOG_DIR = "logs"           # 日志目录

# 爬虫配置
CRAWLER_CONFIG = {
    "delay_range": (2, 5),     # 请求延迟范围
    "retry_times": 3,          # 重试次数
    "timeout": 30              # 超时时间
}

# 文本分析配置
TEXT_ANALYSIS_CONFIG = {
    "min_word_length": 2,      # 最小词长
    "top_words_count": 100,    # 高频词数量
    "keyword_count": 50        # 关键词数量
}

# 词云配置
WORDCLOUD_CONFIG = {
    "width": 1600,             # 图片宽度
    "height": 900,             # 图片高度
    "max_words": 200           # 最大词数
}
```

### 停用词配置 (`config/stopwords.txt`)
- 自定义中文停用词列表
- 过滤无意义词汇
- 提高分析质量

## 🔧 命令行参数

```bash
python main.py [选项]
```

### 主要参数:
- `--type` : 分析类型 (movie/book)
- `--name` : 内容名称
- `--max_comments` : 最大评论数量 (默认1000)
- `--analyze_only` : 仅分析模式，不收集数据
- `--file` : 指定要分析的文件路径

### 使用示例:

```bash
# 收集并分析电影评论
python main.py --type movie --name "肖申克的救赎" --max_comments 500

# 收集并分析图书评论  
python main.py --type book --name "百年孤独" --max_comments 800

# 仅分析现有文件
python main.py --analyze_only --file data/movie_comments.txt

# 使用默认设置（交互式输入）
python main.py
```

## 📈 数据格式要求

### 输入文件格式

文本文件应包含以下格式的评论数据：

```
评论时间: 2024-01-15
用户: 用户名
评分: 4.5
内容: 这是一条评论内容...
--------------------------------------------------
评论时间: 2024-01-14
用户: 另一个用户
评分: 3.0
内容: 另一条评论内容...
--------------------------------------------------
```

## 🛠️ 扩展开发

### 添加新的分析方法

1. 在对应模块中添加新方法
2. 更新配置文件
3. 修改主程序调用

### 添加新的可视化类型

1. 扩展 `WordCloudGenerator` 类
2. 添加新的形状和样式
3. 更新配置选项

### 定制情感分析

1. 替换或扩展 SnowNLP 引擎
2. 添加领域专用词典
3. 调整情感阈值

## 🔍 故障排除

### 常见问题

1. **依赖包安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

2. **中文字体问题**
   - 系统会自动检测可用字体
   - 可在配置文件中指定字体路径

3. **内存不足**
   - 减少 `max_comments` 数量
   - 分批处理大数据集

4. **网络连接问题**
   - 检查网络连接
   - 调整爬虫延迟设置

### 调试模式

```bash
# 启用详细日志
export PYTHONPATH=$PYTHONPATH:.
python main.py --type movie --name "测试电影" --max_comments 10
```

## 📞 技术支持

如果遇到问题，请检查：
1. Python版本 (建议3.8+)
2. 依赖包版本兼容性
3. 网络连接状态
4. 文件权限设置

## 🎉 成功案例

演示成功分析了25条示例电影评论，生成了：
- ✅ 3种样式的词云图
- ✅ 4种统计图表
- ✅ 完整的情感分析报告
- ✅ 知识图谱可视化
- ✅ HTML综合报告

系统已验证在 macOS、Windows 和 Linux 环境下正常运行。 