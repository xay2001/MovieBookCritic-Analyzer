# 豆瓣电影/图书评论分析系统

## 项目简介

这是一个基于Python的豆瓣电影/图书评论分析系统，能够自动收集豆瓣上的评论数据，并进行多维度的文本分析，包括：

1. **数据收集**：从豆瓣网站收集最多1000条电影/图书评论
2. **词频分析**：对评论文本进行分词和词频统计（按时间维度）
3. **词云生成**：提取关键词并生成可视化词云图
4. **情感分析**：计算情感得分并判断情感倾向
5. **知识图谱**：构建评论知识图谱

## 项目结构

```
douban/
├── README.md                 # 项目说明文档
├── requirements.txt          # 依赖包列表
├── main.py                  # 主程序入口
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── crawler.py           # 数据爬取模块
│   ├── text_analyzer.py     # 文本分析模块
│   ├── sentiment_analyzer.py # 情感分析模块
│   ├── wordcloud_generator.py # 词云生成模块
│   └── knowledge_graph.py   # 知识图谱构建模块
├── data/                    # 数据存储目录
├── output/                  # 输出结果目录
│   ├── wordclouds/         # 词云图片
│   ├── charts/             # 分析图表
│   └── graphs/             # 知识图谱
└── config/                  # 配置文件目录
    └── config.py           # 配置参数
```

## 环境要求

- Python 3.8+
- Chrome浏览器（用于网页爬取）

## 安装步骤

1. **克隆项目**（如果是从git仓库）或直接下载项目文件

2. **安装依赖包**：
   ```bash
   pip install -r requirements.txt
   ```

3. **下载Chrome驱动**：
   系统会自动下载匹配的ChromeDriver，如果遇到问题，请手动下载并放置在系统PATH中。

## 使用方法

### 1. 基本使用

```bash
python main.py
```

程序将会：
1. 提示您选择分析类型（电影或图书）
2. 输入要分析的内容名称
3. 自动收集评论数据
4. 进行各种文本分析
5. 生成分析报告和可视化图表

### 2. 命令行参数

```bash
# 分析电影
python main.py --type movie --name "肖申克的救赎" --max_comments 500

# 分析图书
python main.py --type book --name "三体" --max_comments 1000

# 只进行文本分析（使用已有的txt文件）
python main.py --analyze_only --file "data/某电影.txt"
```

### 3. 参数说明

- `--type`: 分析类型，可选 `movie` 或 `book`
- `--name`: 电影或图书名称
- `--max_comments`: 最大收集评论数量（默认1000）
- `--analyze_only`: 仅进行文本分析，不进行数据收集
- `--file`: 指定要分析的文本文件路径

## 输出结果

运行完成后，会在相应目录生成以下文件：

1. **数据文件**：
   - `data/某电影.txt` 或 `data/某图书.txt` - 原始评论数据

2. **分析报告**：
   - `output/analysis_report.html` - 完整的分析报告

3. **可视化图表**：
   - `output/wordclouds/wordcloud.png` - 词云图
   - `output/charts/word_frequency.png` - 词频分析图
   - `output/charts/sentiment_analysis.png` - 情感分析图
   - `output/charts/time_sentiment.png` - 时间维度情感变化图

4. **知识图谱**：
   - `output/graphs/knowledge_graph.html` - 交互式知识图谱
   - `output/graphs/knowledge_graph.png` - 知识图谱静态图

## 功能特性

### 1. 数据收集
- 使用Selenium模拟浏览器访问豆瓣网站
- 自动翻页收集评论
- 处理反爬虫机制
- 保存评论内容、时间、评分等信息

### 2. 文本分析
- 使用jieba进行中文分词
- 去除停用词和无意义词汇
- 按时间维度进行词频统计
- 生成词频分析图表

### 3. 词云生成
- 提取高频关键词
- 生成美观的中文词云图
- 支持自定义样式和颜色

### 4. 情感分析
- 使用SnowNLP进行中文情感分析
- 计算情感得分（0-1，越接近1越积极）
- 统计情感倾向分布
- 分析情感随时间的变化趋势

### 5. 知识图谱
- 提取实体和关系
- 构建评论主题网络
- 生成交互式可视化图谱

## 技术栈

- **数据收集**：Selenium, BeautifulSoup
- **文本处理**：jieba, re
- **情感分析**：SnowNLP
- **数据分析**：pandas, numpy
- **可视化**：matplotlib, wordcloud, pyecharts
- **知识图谱**：networkx, pyvis

## 注意事项

1. **合规使用**：请遵守豆瓣网站的使用条款，不要过于频繁地访问
2. **网络连接**：确保网络连接稳定，爬取过程可能需要较长时间
3. **反爬机制**：如遇到验证码或访问限制，请适当调整爬取间隔
4. **数据质量**：系统会自动过滤明显的垃圾评论，但仍建议人工检查

## 常见问题

### Q: 爬取速度很慢怎么办？
A: 可以调整配置文件中的延迟时间，但不建议设置得过短以免触发反爬机制。

### Q: 无法访问豆瓣网站？
A: 检查网络连接，或尝试使用代理服务器。

### Q: 词云图显示乱码？
A: 确保系统安装了中文字体，程序会自动寻找合适的字体文件。

### Q: 分析结果不准确？
A: 可以调整停用词列表，或增加训练数据来提高分析准确性。

## 扩展功能

项目预留了扩展接口，可以轻松添加：
- 更多网站的数据源
- 不同的情感分析模型
- 更复杂的知识图谱构建算法
- 实时数据分析功能

## 许可证

本项目仅用于学习和研究目的，请勿用于商业用途。 