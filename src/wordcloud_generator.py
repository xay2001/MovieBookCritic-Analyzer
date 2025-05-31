# -*- coding: utf-8 -*-
"""
词云生成模块
用于生成美观的中文词云图
"""

import os
import platform
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont

from config.config import WORDCLOUD_CONFIG, CHART_CONFIG


class WordCloudGenerator:
    """词云生成器类"""
    
    def __init__(self):
        """初始化词云生成器"""
        self.font_path = self._find_chinese_font()
        self.wordcloud = None
        
    def _find_chinese_font(self):
        """寻找系统中的中文字体"""
        # 常见的中文字体路径
        font_paths = []
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/Library/Fonts/Arial Unicode MS.ttf",
            ]
        elif system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/msyhbd.ttc",
            ]
        elif system == "Linux":
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            ]
        
        # 检查字体文件是否存在
        for font_path in font_paths:
            if os.path.exists(font_path):
                print(f"找到中文字体: {font_path}")
                return font_path
        
        print("未找到中文字体，将使用默认字体")
        return None
    
    def create_wordcloud(self, word_freq_dict, width=None, height=None, 
                        background_color=None, max_words=None, 
                        colormap=None, mask=None):
        """
        创建词云
        
        Args:
            word_freq_dict (dict): 词频字典
            width (int): 词云图宽度
            height (int): 词云图高度
            background_color (str): 背景颜色
            max_words (int): 最大词数
            colormap (str): 颜色映射
            mask (array): 词云形状掩码
            
        Returns:
            WordCloud: 词云对象
        """
        # 使用配置文件中的默认值
        config = WORDCLOUD_CONFIG.copy()
        
        if width is not None:
            config['width'] = width
        if height is not None:
            config['height'] = height
        if background_color is not None:
            config['background_color'] = background_color
        if max_words is not None:
            config['max_words'] = max_words
        if colormap is not None:
            config['colormap'] = colormap
        
        # 创建WordCloud对象
        wordcloud_kwargs = {
            'width': config['width'],
            'height': config['height'],
            'background_color': config['background_color'],
            'max_words': config['max_words'],
            'max_font_size': config['max_font_size'],
            'min_font_size': config['min_font_size'],
            'colormap': config['colormap'],
            'relative_scaling': 0.5,
            'random_state': 42,
            'collocations': False,  # 避免重复组合
        }
        
        # 设置中文字体
        if self.font_path:
            wordcloud_kwargs['font_path'] = self.font_path
        
        # 设置形状掩码
        if mask is not None:
            wordcloud_kwargs['mask'] = mask
        
        # 创建词云
        self.wordcloud = WordCloud(**wordcloud_kwargs)
        
        # 根据词频生成词云
        if isinstance(word_freq_dict, dict):
            self.wordcloud.generate_from_frequencies(word_freq_dict)
        else:
            # 如果是字符串，直接生成
            self.wordcloud.generate(word_freq_dict)
        
        return self.wordcloud
    
    def create_shaped_wordcloud(self, word_freq_dict, shape_type='circle'):
        """
        创建特定形状的词云
        
        Args:
            word_freq_dict (dict): 词频字典
            shape_type (str): 形状类型 ('circle', 'heart', 'star', 'rectangle')
            
        Returns:
            WordCloud: 词云对象
        """
        # 创建形状掩码
        mask = self._create_shape_mask(shape_type)
        
        return self.create_wordcloud(word_freq_dict, mask=mask)
    
    def _create_shape_mask(self, shape_type):
        """
        创建形状掩码
        
        Args:
            shape_type (str): 形状类型
            
        Returns:
            np.array: 掩码数组
        """
        width = WORDCLOUD_CONFIG['width']
        height = WORDCLOUD_CONFIG['height']
        
        # 创建白色背景的图像
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        if shape_type == 'circle':
            # 画圆形
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 3
            bbox = [center_x - radius, center_y - radius, 
                   center_x + radius, center_y + radius]
            draw.ellipse(bbox, fill='black')
            
        elif shape_type == 'heart':
            # 画心形
            self._draw_heart(draw, width, height)
            
        elif shape_type == 'star':
            # 画星形
            self._draw_star(draw, width, height)
            
        elif shape_type == 'rectangle':
            # 画矩形
            margin = min(width, height) // 6
            bbox = [margin, margin, width - margin, height - margin]
            draw.rectangle(bbox, fill='black')
        
        # 转换为numpy数组
        mask = np.array(img)
        
        return mask
    
    def _draw_heart(self, draw, width, height):
        """绘制心形"""
        center_x, center_y = width // 2, height // 2
        scale = min(width, height) // 6
        
        # 心形的数学方程
        points = []
        for t in np.linspace(0, 2 * np.pi, 1000):
            x = 16 * np.sin(t) ** 3
            y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
            
            # 缩放和平移
            px = center_x + x * scale // 2
            py = center_y - y * scale // 2  # 注意y轴翻转
            points.append((px, py))
        
        draw.polygon(points, fill='black')
    
    def _draw_star(self, draw, width, height):
        """绘制星形"""
        center_x, center_y = width // 2, height // 2
        outer_radius = min(width, height) // 4
        inner_radius = outer_radius // 2
        
        points = []
        for i in range(10):  # 五角星需要10个点
            angle = i * np.pi / 5
            if i % 2 == 0:
                # 外顶点
                x = center_x + outer_radius * np.cos(angle - np.pi / 2)
                y = center_y + outer_radius * np.sin(angle - np.pi / 2)
            else:
                # 内顶点
                x = center_x + inner_radius * np.cos(angle - np.pi / 2)
                y = center_y + inner_radius * np.sin(angle - np.pi / 2)
            points.append((x, y))
        
        draw.polygon(points, fill='black')
    
    def save_wordcloud(self, save_path, dpi=300):
        """
        保存词云图
        
        Args:
            save_path (str): 保存路径
            dpi (int): 图片分辨率
        """
        if self.wordcloud is None:
            print("请先生成词云")
            return False
        
        try:
            # 确保保存目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 保存词云图
            plt.figure(figsize=(CHART_CONFIG['figure_size']))
            plt.imshow(self.wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"词云图已保存到: {save_path}")
            return True
            
        except Exception as e:
            print(f"保存词云图失败: {e}")
            return False
    
    def display_wordcloud(self):
        """显示词云图"""
        if self.wordcloud is None:
            print("请先生成词云")
            return
        
        plt.figure(figsize=CHART_CONFIG['figure_size'])
        plt.imshow(self.wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('词云图', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.show()
    
    def create_comparison_wordcloud(self, word_freq_dicts, titles, save_path=None):
        """
        创建对比词云图
        
        Args:
            word_freq_dicts (list): 多个词频字典列表
            titles (list): 对应的标题列表
            save_path (str): 保存路径
        """
        if len(word_freq_dicts) != len(titles):
            print("词频字典数量与标题数量不匹配")
            return
        
        num_clouds = len(word_freq_dicts)
        
        # 创建子图
        fig, axes = plt.subplots(1, num_clouds, figsize=(CHART_CONFIG['figure_size'][0] * num_clouds // 2, 
                                                       CHART_CONFIG['figure_size'][1]))
        
        if num_clouds == 1:
            axes = [axes]
        
        for i, (word_freq_dict, title) in enumerate(zip(word_freq_dicts, titles)):
            # 为每个词频字典创建词云
            wordcloud = self.create_wordcloud(word_freq_dict)
            
            # 显示在对应子图中
            axes[i].imshow(wordcloud, interpolation='bilinear')
            axes[i].axis('off')
            axes[i].set_title(title, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 保存图片
        if save_path:
            plt.savefig(save_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
            print(f"对比词云图已保存到: {save_path}")
        
        plt.show()
    
    def create_time_wordcloud_animation(self, time_word_freq_dict, save_dir):
        """
        创建时间序列词云动画（保存为多张图片）
        
        Args:
            time_word_freq_dict (dict): 时间-词频字典
            save_dir (str): 保存目录
        """
        try:
            os.makedirs(save_dir, exist_ok=True)
            
            sorted_times = sorted(time_word_freq_dict.keys())
            
            for i, time_key in enumerate(sorted_times):
                word_freq = time_word_freq_dict[time_key]
                
                if not word_freq:
                    continue
                
                # 创建词云
                wordcloud = self.create_wordcloud(word_freq)
                
                # 保存图片
                filename = f"wordcloud_{i:03d}_{time_key}.png"
                save_path = os.path.join(save_dir, filename)
                
                plt.figure(figsize=CHART_CONFIG['figure_size'])
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title(f'词云图 - {time_key}', fontsize=16, fontweight='bold')
                plt.tight_layout()
                plt.savefig(save_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
                plt.close()
                
                print(f"生成时间词云: {save_path}")
            
            print(f"时间序列词云已保存到: {save_dir}")
            
        except Exception as e:
            print(f"生成时间序列词云失败: {e}")
    
    def get_word_frequencies_from_wordcloud(self):
        """
        从词云中获取词频信息
        
        Returns:
            dict: 词频字典
        """
        if self.wordcloud is None:
            return {}
        
        return dict(self.wordcloud.words_)
    
    def create_multilingual_wordcloud(self, word_freq_dict, languages=['zh', 'en']):
        """
        创建多语言词云（处理中英文混合）
        
        Args:
            word_freq_dict (dict): 词频字典
            languages (list): 支持的语言列表
            
        Returns:
            WordCloud: 词云对象
        """
        # 分离中英文词汇
        zh_words = {}
        en_words = {}
        
        for word, freq in word_freq_dict.items():
            if any('\u4e00' <= char <= '\u9fff' for char in word):
                # 包含中文字符
                zh_words[word] = freq
            else:
                # 英文或其他
                en_words[word] = freq
        
        # 合并处理（这里简化处理，实际可以分别设置不同字体）
        combined_words = {}
        combined_words.update(zh_words)
        combined_words.update(en_words)
        
        return self.create_wordcloud(combined_words)


def main():
    """测试函数"""
    # 测试数据
    test_word_freq = {
        '情节': 100, '演技': 90, '导演': 85, '剧情': 80, '角色': 75,
        '音乐': 70, '特效': 65, '台词': 60, '摄影': 55, '节奏': 50,
        '感动': 45, '精彩': 40, '深刻': 35, '震撼': 30, '温暖': 25,
        '经典': 20, '完美': 18, '出色': 15, '优秀': 12, '棒': 10
    }
    
    # 创建词云生成器
    generator = WordCloudGenerator()
    
    # 创建基本词云
    print("生成基本词云...")
    wordcloud = generator.create_wordcloud(test_word_freq)
    generator.save_wordcloud('output/wordclouds/basic_wordcloud.png')
    
    # 创建形状词云
    print("生成心形词云...")
    heart_wordcloud = generator.create_shaped_wordcloud(test_word_freq, 'heart')
    generator.save_wordcloud('output/wordclouds/heart_wordcloud.png')
    
    print("生成星形词云...")
    star_wordcloud = generator.create_shaped_wordcloud(test_word_freq, 'star')
    generator.save_wordcloud('output/wordclouds/star_wordcloud.png')
    
    # 创建对比词云
    print("生成对比词云...")
    word_freq_2 = {
        '故事': 95, '人物': 88, '情感': 82, '深度': 77, '思考': 72,
        '哲学': 68, '人生': 63, '现实': 58, '社会': 53, '反思': 48
    }
    
    generator.create_comparison_wordcloud(
        [test_word_freq, word_freq_2],
        ['技术层面', '内容层面'],
        'output/wordclouds/comparison_wordcloud.png'
    )
    
    print("词云生成测试完成！")


if __name__ == '__main__':
    main() 