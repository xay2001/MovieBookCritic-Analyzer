# -*- coding: utf-8 -*-
"""
知识图谱模块
用于构建评论知识图谱
"""

import os
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import jieba
import jieba.posseg as pseg

from config.config import KNOWLEDGE_GRAPH_CONFIG, CHART_CONFIG


class KnowledgeGraphBuilder:
    """知识图谱构建器类"""
    
    def __init__(self):
        """初始化知识图谱构建器"""
        self.comments_data = []
        self.entities = {}  # 实体字典 {entity: {type, frequency, ...}}
        self.relations = defaultdict(int)  # 关系字典 {(entity1, entity2): weight}
        self.graph = nx.Graph()
        
        # 设置matplotlib样式
        plt.style.use(CHART_CONFIG['style'])
        plt.rcParams['font.sans-serif'] = CHART_CONFIG['font_family']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 初始化实体类型规则
        self._init_entity_rules()
    
    def _init_entity_rules(self):
        """初始化实体识别规则"""
        # 定义不同类型的实体关键词
        self.entity_types = {
            'person': ['导演', '演员', '主演', '编剧', '制片人', '配音', '作者', '作家'],
            'movie': ['电影', '影片', '片子', '剧', '纪录片', '动画', '电视剧'],
            'book': ['小说', '书', '作品', '图书', '文学', '散文', '诗歌'],
            'genre': ['喜剧', '悲剧', '动作', '科幻', '爱情', '恐怖', '悬疑', '推理', '历史', '传记'],
            'emotion': ['感动', '震撼', '温暖', '感人', '搞笑', '紧张', '刺激', '浪漫', '忧伤'],
            'quality': ['经典', '优秀', '出色', '完美', '精彩', '深刻', '有趣', '无聊', '糟糕'],
            'element': ['剧情', '情节', '演技', '特效', '音乐', '配乐', '摄影', '台词', '节奏', '结局']
        }
        
        # 扩展词典
        jieba.add_word('剧情')
        jieba.add_word('演技')
        jieba.add_word('特效')
        jieba.add_word('配乐')
        jieba.add_word('摄影')
        jieba.add_word('台词')
    
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
                    if line.startswith('内容:'):
                        comment_data['content'] = line.replace('内容:', '').strip()
                
                if 'content' in comment_data and comment_data['content']:
                    comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            print(f"解析txt文件失败: {e}")
            return []
    
    def extract_entities(self):
        """提取实体"""
        print("开始提取实体...")
        
        self.entities = {}
        entity_contexts = defaultdict(list)  # 记录实体上下文
        
        for comment in self.comments_data:
            content = comment.get('content', '')
            if not content:
                continue
            
            # 使用jieba进行词性标注
            words = pseg.cut(content)
            
            # 清理和标准化文本
            cleaned_content = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', content)
            
            for word, flag in words:
                word = word.strip()
                
                # 过滤条件
                if (len(word) < 2 or len(word) > 8 or 
                    word.isdigit() or 
                    word in ['电影', '影片', '片子', '小说', '书', '作品']):
                    continue
                
                # 实体类型识别
                entity_type = self._classify_entity(word, flag)
                
                if entity_type:
                    if word not in self.entities:
                        self.entities[word] = {
                            'type': entity_type,
                            'frequency': 0,
                            'contexts': []
                        }
                    
                    self.entities[word]['frequency'] += 1
                    
                    # 记录上下文（前后各3个字符）
                    start_idx = max(0, content.find(word) - 10)
                    end_idx = min(len(content), content.find(word) + len(word) + 10)
                    context = content[start_idx:end_idx]
                    
                    if len(self.entities[word]['contexts']) < 5:  # 最多保存5个上下文
                        self.entities[word]['contexts'].append(context)
        
        # 过滤低频实体
        min_freq = 2
        self.entities = {k: v for k, v in self.entities.items() if v['frequency'] >= min_freq}
        
        print(f"提取到 {len(self.entities)} 个实体")
        
        # 打印实体类型统计
        type_counts = Counter([entity['type'] for entity in self.entities.values()])
        print("实体类型分布:")
        for entity_type, count in type_counts.most_common():
            print(f"  {entity_type}: {count}")
    
    def _classify_entity(self, word, pos_flag):
        """
        分类实体类型
        
        Args:
            word (str): 词汇
            pos_flag (str): 词性标记
            
        Returns:
            str: 实体类型，如果不是实体则返回None
        """
        # 基于词性的初步分类
        if pos_flag in ['nr', 'nrf']:  # 人名
            return 'person'
        elif pos_flag in ['ns', 'nt']:  # 地名、机构名
            return 'place'
        elif pos_flag in ['n', 'ng', 'nz']:  # 名词
            # 进一步基于关键词分类
            for entity_type, keywords in self.entity_types.items():
                if any(keyword in word for keyword in keywords):
                    return entity_type
            
            # 如果是有意义的名词，分类为概念
            if len(word) >= 2 and not word.isdigit():
                return 'concept'
        elif pos_flag in ['a', 'ad']:  # 形容词
            return 'attribute'
        elif pos_flag in ['v', 'vn']:  # 动词
            return 'action'
        
        return None
    
    def build_relations(self):
        """构建实体关系"""
        print("开始构建实体关系...")
        
        self.relations = defaultdict(int)
        entity_names = list(self.entities.keys())
        
        # 基于共现关系构建
        for comment in self.comments_data:
            content = comment.get('content', '')
            if not content:
                continue
            
            # 找出在该评论中出现的实体
            comment_entities = []
            for entity in entity_names:
                if entity in content:
                    comment_entities.append(entity)
            
            # 为共现的实体对创建关系
            for entity1, entity2 in combinations(comment_entities, 2):
                if entity1 != entity2:
                    # 确保关系的一致性（按字典序排序）
                    rel_key = tuple(sorted([entity1, entity2]))
                    self.relations[rel_key] += 1
        
        # 过滤低频关系
        min_cooccurrence = KNOWLEDGE_GRAPH_CONFIG['min_cooccurrence']
        self.relations = {k: v for k, v in self.relations.items() 
                         if v >= min_cooccurrence}
        
        print(f"构建了 {len(self.relations)} 个关系")
    
    def create_graph(self):
        """创建NetworkX图"""
        print("开始创建知识图谱...")
        
        self.graph = nx.Graph()
        
        # 添加节点
        for entity, info in self.entities.items():
            self.graph.add_node(entity, 
                               type=info['type'],
                               frequency=info['frequency'],
                               size=min(info['frequency'] * KNOWLEDGE_GRAPH_CONFIG['node_size_multiplier'], 1000))
        
        # 添加边
        for (entity1, entity2), weight in self.relations.items():
            if entity1 in self.graph.nodes and entity2 in self.graph.nodes:
                self.graph.add_edge(entity1, entity2, 
                                  weight=weight,
                                  width=min(weight * KNOWLEDGE_GRAPH_CONFIG['edge_width_multiplier'], 10))
        
        print(f"图谱包含 {self.graph.number_of_nodes()} 个节点和 {self.graph.number_of_edges()} 条边")
        
        # 计算图谱指标
        self._calculate_graph_metrics()
    
    def _calculate_graph_metrics(self):
        """计算图谱指标"""
        if self.graph.number_of_nodes() == 0:
            return
        
        print("\n=== 图谱分析指标 ===")
        
        # 基本指标
        print(f"节点数: {self.graph.number_of_nodes()}")
        print(f"边数: {self.graph.number_of_edges()}")
        print(f"密度: {nx.density(self.graph):.4f}")
        
        # 连通性
        if nx.is_connected(self.graph):
            print("图是连通的")
            print(f"平均路径长度: {nx.average_shortest_path_length(self.graph):.4f}")
        else:
            components = list(nx.connected_components(self.graph))
            print(f"图不连通，包含 {len(components)} 个连通分量")
            largest_component = max(components, key=len)
            print(f"最大连通分量大小: {len(largest_component)}")
        
        # 中心性分析
        centrality = nx.degree_centrality(self.graph)
        top_central_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("\n度中心性最高的节点:")
        for node, cent in top_central_nodes:
            print(f"  {node}: {cent:.4f}")
        
        # 聚类系数
        clustering = nx.average_clustering(self.graph)
        print(f"\n平均聚类系数: {clustering:.4f}")
    
    def visualize_graph(self, save_path=None, layout='spring', node_limit=None):
        """
        可视化图谱（静态图）
        
        Args:
            save_path (str): 保存路径
            layout (str): 布局算法
            node_limit (int): 节点数量限制
        """
        if self.graph.number_of_nodes() == 0:
            print("图谱为空，无法可视化")
            return
        
        # 限制节点数量以提高可视化效果
        if node_limit and self.graph.number_of_nodes() > node_limit:
            # 按度中心性选择最重要的节点
            centrality = nx.degree_centrality(self.graph)
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:node_limit]
            subgraph_nodes = [node for node, _ in top_nodes]
            graph_to_plot = self.graph.subgraph(subgraph_nodes)
        else:
            graph_to_plot = self.graph
        
        # 设置布局
        if layout == 'spring':
            pos = nx.spring_layout(graph_to_plot, k=1, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(graph_to_plot)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(graph_to_plot)
        else:
            pos = nx.spring_layout(graph_to_plot)
        
        # 创建图表
        plt.figure(figsize=(16, 12))
        
        # 根据实体类型设置颜色
        type_colors = {
            'person': '#ff9999', 'movie': '#66b3ff', 'book': '#99ff99',
            'genre': '#ffcc99', 'emotion': '#ff99cc', 'quality': '#c2c2f0',
            'element': '#ffb3e6', 'concept': '#c4e17f', 'attribute': '#ffd1dc',
            'action': '#87ceeb', 'place': '#dda0dd'
        }
        
        node_colors = []
        node_sizes = []
        
        for node in graph_to_plot.nodes():
            node_type = self.entities[node]['type']
            node_colors.append(type_colors.get(node_type, '#cccccc'))
            
            # 节点大小根据频次决定
            frequency = self.entities[node]['frequency']
            node_sizes.append(min(frequency * 100, 1000))
        
        # 绘制边
        edges = graph_to_plot.edges()
        edge_weights = [graph_to_plot[u][v]['weight'] for u, v in edges]
        max_weight = max(edge_weights) if edge_weights else 1
        edge_widths = [w / max_weight * 3 for w in edge_weights]
        
        nx.draw_networkx_edges(graph_to_plot, pos, 
                              width=edge_widths,
                              alpha=0.5, edge_color='gray')
        
        # 绘制节点
        nx.draw_networkx_nodes(graph_to_plot, pos,
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8)
        
        # 绘制标签
        nx.draw_networkx_labels(graph_to_plot, pos,
                               font_size=8,
                               font_family='sans-serif')
        
        plt.title('评论知识图谱', fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # 添加图例
        legend_elements = []
        for entity_type, color in type_colors.items():
            if any(self.entities[node]['type'] == entity_type for node in graph_to_plot.nodes()):
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                 markerfacecolor=color, markersize=10, 
                                                 label=entity_type))
        
        if legend_elements:
            plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        plt.tight_layout()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
            print(f"知识图谱已保存到: {save_path}")
        
        plt.show()
    
    def create_interactive_graph(self, save_path=None, node_limit=50):
        """
        创建交互式图谱
        
        Args:
            save_path (str): 保存路径
            node_limit (int): 节点数量限制
        """
        if self.graph.number_of_nodes() == 0:
            print("图谱为空，无法创建交互式图谱")
            return
        
        # 限制节点数量
        if node_limit and self.graph.number_of_nodes() > node_limit:
            centrality = nx.degree_centrality(self.graph)
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:node_limit]
            subgraph_nodes = [node for node, _ in top_nodes]
            graph_to_use = self.graph.subgraph(subgraph_nodes)
        else:
            graph_to_use = self.graph
        
        # 创建pyvis网络
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
        
        # 设置物理引擎参数
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "stabilization": {"iterations": 100}
          }
        }
        """)
        
        # 添加节点
        type_colors = {
            'person': '#ff9999', 'movie': '#66b3ff', 'book': '#99ff99',
            'genre': '#ffcc99', 'emotion': '#ff99cc', 'quality': '#c2c2f0',
            'element': '#ffb3e6', 'concept': '#c4e17f', 'attribute': '#ffd1dc',
            'action': '#87ceeb', 'place': '#dda0dd'
        }
        
        for node in graph_to_use.nodes():
            entity_info = self.entities[node]
            node_type = entity_info['type']
            frequency = entity_info['frequency']
            
            # 创建节点标题（悬停显示的信息）
            title = f"实体: {node}\n类型: {node_type}\n频次: {frequency}"
            
            # 上下文信息
            if 'contexts' in entity_info and entity_info['contexts']:
                title += f"\n上下文示例: {entity_info['contexts'][0][:30]}..."
            
            net.add_node(node,
                        label=node,
                        title=title,
                        color=type_colors.get(node_type, '#cccccc'),
                        size=min(frequency * 5, 50))
        
        # 添加边
        for edge in graph_to_use.edges(data=True):
            source, target, data = edge
            weight = data['weight']
            
            # 边的标题
            title = f"共现次数: {weight}"
            
            net.add_edge(source, target,
                        title=title,
                        width=min(weight * 2, 10),
                        color='#848484')
        
        # 保存交互式图谱
        if save_path:
            net.save_graph(save_path)
            print(f"交互式知识图谱已保存到: {save_path}")
        else:
            # 保存到默认位置
            default_path = os.path.join('output', 'graphs', 'interactive_knowledge_graph.html')
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
            net.save_graph(default_path)
            print(f"交互式知识图谱已保存到: {default_path}")
        
        return net
    
    def analyze_entity_clusters(self):
        """分析实体聚类"""
        if self.graph.number_of_nodes() == 0:
            return
        
        print("\n=== 实体聚类分析 ===")
        
        # 使用社区检测算法
        try:
            communities = nx.community.greedy_modularity_communities(self.graph)
            
            print(f"检测到 {len(communities)} 个社区")
            
            for i, community in enumerate(communities):
                if len(community) >= 3:  # 只显示有3个以上节点的社区
                    print(f"\n社区 {i+1} ({len(community)} 个实体):")
                    
                    # 按频次排序显示
                    community_entities = [(entity, self.entities[entity]['frequency']) 
                                        for entity in community]
                    community_entities.sort(key=lambda x: x[1], reverse=True)
                    
                    for entity, freq in community_entities[:10]:  # 显示前10个
                        print(f"  {entity} (类型: {self.entities[entity]['type']}, 频次: {freq})")
        
        except Exception as e:
            print(f"社区检测失败: {e}")
    
    def get_entity_recommendations(self, entity, top_n=5):
        """
        获取实体推荐（基于图结构）
        
        Args:
            entity (str): 目标实体
            top_n (int): 推荐数量
            
        Returns:
            list: 推荐实体列表
        """
        if entity not in self.graph.nodes:
            print(f"实体 '{entity}' 不在图谱中")
            return []
        
        # 获取邻居节点
        neighbors = list(self.graph.neighbors(entity))
        
        # 按边权重排序
        neighbor_weights = []
        for neighbor in neighbors:
            weight = self.graph[entity][neighbor]['weight']
            neighbor_weights.append((neighbor, weight))
        
        neighbor_weights.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = neighbor_weights[:top_n]
        
        print(f"\n与 '{entity}' 相关的实体推荐:")
        for neighbor, weight in recommendations:
            neighbor_type = self.entities[neighbor]['type']
            print(f"  {neighbor} (类型: {neighbor_type}, 关联强度: {weight})")
        
        return [item[0] for item in recommendations]
    
    def save_graph_data(self, output_dir):
        """
        保存图谱数据
        
        Args:
            output_dir (str): 输出目录
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存实体数据
            entities_file = os.path.join(output_dir, 'entities.json')
            with open(entities_file, 'w', encoding='utf-8') as f:
                json.dump(self.entities, f, ensure_ascii=False, indent=2)
            
            # 保存关系数据
            relations_data = {f"{k[0]}-{k[1]}": v for k, v in self.relations.items()}
            relations_file = os.path.join(output_dir, 'relations.json')
            with open(relations_file, 'w', encoding='utf-8') as f:
                json.dump(relations_data, f, ensure_ascii=False, indent=2)
            
            # 保存图谱统计
            stats = {
                'total_entities': len(self.entities),
                'total_relations': len(self.relations),
                'graph_nodes': self.graph.number_of_nodes(),
                'graph_edges': self.graph.number_of_edges(),
                'graph_density': nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0,
                'entity_types': Counter([entity['type'] for entity in self.entities.values()])
            }
            
            stats_file = os.path.join(output_dir, 'graph_statistics.json')
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"知识图谱数据已保存到: {output_dir}")
            
        except Exception as e:
            print(f"保存图谱数据失败: {e}")


def main():
    """测试函数"""
    kg_builder = KnowledgeGraphBuilder()
    
    # 假设已有数据文件
    data_file = 'data/肖申克的救赎.json'
    if os.path.exists(data_file):
        kg_builder.load_data_from_file(data_file)
        kg_builder.extract_entities()
        kg_builder.build_relations()
        kg_builder.create_graph()
        
        # 可视化图谱
        kg_builder.visualize_graph(save_path='output/graphs/knowledge_graph.png', 
                                 node_limit=30)
        
        # 创建交互式图谱
        kg_builder.create_interactive_graph(save_path='output/graphs/interactive_knowledge_graph.html')
        
        # 分析聚类
        kg_builder.analyze_entity_clusters()
        
        # 实体推荐示例
        if '剧情' in kg_builder.entities:
            kg_builder.get_entity_recommendations('剧情')
        
        # 保存数据
        kg_builder.save_graph_data('output/graphs')
        
        print("知识图谱构建完成！")


if __name__ == '__main__':
    main() 