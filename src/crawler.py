# -*- coding: utf-8 -*-
"""
豆瓣爬虫模块
用于从豆瓣网站收集电影/图书评论数据
"""

import time
import random
import json
import os
import re
from datetime import datetime
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

from config.config import CRAWLER_CONFIG, DOUBAN_CONFIG


class DoubanCrawler:
    """豆瓣爬虫类"""
    
    def __init__(self, content_type='movie', max_comments=1000):
        """
        初始化爬虫
        
        Args:
            content_type (str): 内容类型，'movie' 或 'book'
            max_comments (int): 最大评论数量
        """
        self.content_type = content_type
        self.max_comments = max_comments
        self.driver = None
        self.comments = []
        
    def _setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            options = Options()
            options.add_argument('--headless')  # 无头模式
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # 随机选择用户代理
            user_agent = random.choice(CRAWLER_CONFIG['user_agents'])
            options.add_argument(f'--user-agent={user_agent}')
            
            # 自动下载ChromeDriver
            service = webdriver.chrome.service.Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 设置超时时间
            self.driver.set_page_load_timeout(CRAWLER_CONFIG['page_load_timeout'])
            self.driver.implicitly_wait(CRAWLER_CONFIG['implicit_wait'])
            
            print("浏览器驱动初始化成功")
            return True
            
        except Exception as e:
            print(f"浏览器驱动初始化失败: {e}")
            return False
    
    def _random_delay(self):
        """随机延迟"""
        delay = random.uniform(CRAWLER_CONFIG['delay_min'], CRAWLER_CONFIG['delay_max'])
        time.sleep(delay)
    
    def search_content(self, content_name):
        """
        搜索电影或图书
        
        Args:
            content_name (str): 电影或图书名称
            
        Returns:
            str: 内容详情页URL，如果未找到返回None
        """
        try:
            if self.content_type == 'movie':
                search_url = DOUBAN_CONFIG['movie_search_url'].format(quote(content_name))
                base_url = DOUBAN_CONFIG['movie_base_url']
            else:
                search_url = DOUBAN_CONFIG['book_search_url'].format(quote(content_name))
                base_url = DOUBAN_CONFIG['book_base_url']
            
            print(f"正在搜索: {content_name}")
            self.driver.get(search_url)
            self._random_delay()
            
            # 查找第一个搜索结果
            try:
                first_result = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.item-root a, .pic a'))
                )
                content_url = first_result.get_attribute('href')
                
                if content_url and base_url in content_url:
                    print(f"找到内容页面: {content_url}")
                    return content_url
                else:
                    print("未找到有效的内容页面")
                    return None
                    
            except TimeoutException:
                print("搜索超时，未找到结果")
                return None
                
        except Exception as e:
            print(f"搜索过程中出现错误: {e}")
            return None
    
    def get_comments_from_page(self, page_url):
        """
        从单个页面获取评论
        
        Args:
            page_url (str): 页面URL
            
        Returns:
            list: 评论列表
        """
        comments = []
        try:
            self.driver.get(page_url)
            self._random_delay()
            
            # 等待评论加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.comment-item, .review-item'))
            )
            
            # 获取评论元素
            comment_elements = self.driver.find_elements(By.CSS_SELECTOR, '.comment-item, .review-item')
            
            for element in comment_elements:
                try:
                    # 提取评论内容
                    content_elem = element.find_element(By.CSS_SELECTOR, '.comment-content, .short-content, .review-content')
                    content = content_elem.text.strip()
                    
                    # 提取评论时间
                    try:
                        time_elem = element.find_element(By.CSS_SELECTOR, '.comment-time, .main-meta')
                        comment_time = time_elem.text.strip()
                    except NoSuchElementException:
                        comment_time = datetime.now().strftime('%Y-%m-%d')
                    
                    # 提取评分
                    try:
                        rating_elem = element.find_element(By.CSS_SELECTOR, '.rating, .allstar')
                        rating_class = rating_elem.get_attribute('class')
                        rating = self._extract_rating_from_class(rating_class)
                    except NoSuchElementException:
                        rating = None
                    
                    # 提取用户名
                    try:
                        user_elem = element.find_element(By.CSS_SELECTOR, '.comment-info a, .name a')
                        username = user_elem.text.strip()
                    except NoSuchElementException:
                        username = "匿名用户"
                    
                    if content and len(content) > 10:  # 过滤太短的评论
                        comment_data = {
                            'content': content,
                            'time': comment_time,
                            'rating': rating,
                            'username': username,
                            'url': page_url
                        }
                        comments.append(comment_data)
                        
                except Exception as e:
                    print(f"解析单条评论时出错: {e}")
                    continue
            
            print(f"从当前页面获取到 {len(comments)} 条评论")
            return comments
            
        except Exception as e:
            print(f"获取页面评论时出错: {e}")
            return []
    
    def _extract_rating_from_class(self, class_str):
        """从CSS类名中提取评分"""
        if not class_str:
            return None
        
        # 豆瓣评分类名格式：allstar50, allstar40 等
        rating_match = re.search(r'allstar(\d+)', class_str)
        if rating_match:
            return int(rating_match.group(1)) / 10
        
        return None
    
    def crawl_comments(self, content_name):
        """
        爬取评论主函数
        
        Args:
            content_name (str): 电影或图书名称
            
        Returns:
            list: 评论数据列表
        """
        if not self._setup_driver():
            return []
        
        try:
            # 搜索内容
            content_url = self.search_content(content_name)
            if not content_url:
                return []
            
            # 获取评论页面URL
            comments_url = self._get_comments_url(content_url)
            if not comments_url:
                return []
            
            # 爬取评论
            page_num = 0
            total_comments = 0
            
            print(f"开始爬取评论，目标数量: {self.max_comments}")
            
            with tqdm(total=self.max_comments, desc="爬取进度") as pbar:
                while total_comments < self.max_comments:
                    # 构建当前页面URL
                    current_url = f"{comments_url}?start={page_num * 20}&limit=20"
                    
                    # 获取当前页面评论
                    page_comments = self.get_comments_from_page(current_url)
                    
                    if not page_comments:
                        print("没有更多评论，停止爬取")
                        break
                    
                    self.comments.extend(page_comments)
                    total_comments += len(page_comments)
                    page_num += 1
                    
                    # 更新进度条
                    pbar.update(len(page_comments))
                    
                    # 检查是否达到目标数量
                    if total_comments >= self.max_comments:
                        self.comments = self.comments[:self.max_comments]
                        break
                    
                    # 随机延迟
                    self._random_delay()
            
            print(f"爬取完成，共获得 {len(self.comments)} 条评论")
            return self.comments
            
        except Exception as e:
            print(f"爬取过程中出现错误: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _get_comments_url(self, content_url):
        """获取评论页面URL"""
        try:
            # 从内容URL提取ID
            content_id = re.search(r'/subject/(\d+)/', content_url)
            if not content_id:
                print("无法从URL中提取内容ID")
                return None
                
            # 根据内容类型构建评论页面URL
            if self.content_type == 'movie':
                comments_url = DOUBAN_CONFIG['movie_comments_url'].format(content_id.group(1))
            else:
                comments_url = DOUBAN_CONFIG['book_comments_url'].format(content_id.group(1))
                
            print(f"找到评论页面: {comments_url}")
            return comments_url
                
        except Exception as e:
            print(f"获取评论页面URL时出错: {e}")
            return None
    
    def save_comments(self, filename):
        """
        保存评论到文件
        
        Args:
            filename (str): 文件名
        """
        try:
            # 确保data目录存在
            os.makedirs('data', exist_ok=True)
            
            # 确保文件名有正确的扩展名
            if not filename.endswith('.txt'):
                filename = f"{filename}.txt"
            
            filepath = os.path.join('data', filename)
            
            # 保存为文本格式
            with open(filepath, 'w', encoding='utf-8') as f:
                for comment in self.comments:
                    f.write(f"评论时间: {comment['time']}\n")
                    f.write(f"用户: {comment['username']}\n")
                    if comment['rating']:
                        f.write(f"评分: {comment['rating']}\n")
                    f.write(f"内容: {comment['content']}\n")
                    f.write("-" * 50 + "\n")
            
            # 同时保存为JSON格式（用于后续分析）
            json_filepath = filepath.replace('.txt', '.json')
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.comments, f, ensure_ascii=False, indent=2)
            
            print(f"评论已保存到: {filepath}")
            print(f"JSON格式已保存到: {json_filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"保存评论时出错: {e}")
            return None


def main():
    """测试函数"""
    crawler = DoubanCrawler(content_type='movie', max_comments=100)
    comments = crawler.crawl_comments('肖申克的救赎')
    if comments:
        filepath = crawler.save_comments('肖申克的救赎')
        if filepath:
            print(f"评论已保存到: {filepath}")


if __name__ == '__main__':
    main() 