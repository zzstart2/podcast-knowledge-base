import os
from typing import List, Dict, Any
import json
import sqlite3
from datetime import datetime, date
import re

class SimpleConfig:
    DATABASE_URL = "sqlite:///./podcast.db" 
    OPENAI_API_KEY = ""
    MAX_SEARCH_RESULTS = 3

# 简化的数据库模拟
class SimpleDB:
    def __init__(self):
        # 模拟播客数据
        self.episodes = [
            {
                "id": 1,
                "title": "高效工作的五个底层逻辑", 
                "podcast_name": "得到头条",
                "description": "从心理学角度解析工作效率的本质，分享五个提升工作效率的底层思维模式",
                "content_summary": "本期节目深入探讨了工作效率的心理学基础，提出了五个关键的底层逻辑：专注力管理、优先级排序、能量管理、习惯培养和反馈循环。",
                "key_insights": ["番茄工作法的科学原理", "优先级矩阵的实际应用", "能量管理比时间管理更重要"],
                "duration_minutes": 42,
                "publish_date": "2026-03-10",
                "guests": [{"name": "张三", "title": "时间管理专家"}],
                "links": [
                    {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/episode/1"},
                    {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/episode/1"}
                ],
                "quality_score": 4.7,
                "keywords": ["工作效率", "时间管理", "专注力", "习惯", "心理学"]
            },
            {
                "id": 2,
                "title": "从拖延到高效的心理转变",
                "podcast_name": "商业就是这样", 
                "description": "深度分析拖延症的心理根源，提供科学有效的解决方案",
                "content_summary": "本期节目从心理学角度剖析拖延行为的根本原因，包括完美主义、恐惧失败、缺乏动机等。通过认知行为疗法的方法，提供了系统性的拖延症治疗方案。",
                "key_insights": ["拖延的心理机制分析", "完美主义陷阱", "恐惧心理的应对"],
                "duration_minutes": 38,
                "publish_date": "2026-02-28",
                "guests": [{"name": "李四", "title": "心理学博士"}],
                "links": [
                    {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/episode/2"},
                    {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/2"}
                ],
                "quality_score": 4.5,
                "keywords": ["拖延症", "心理健康", "完美主义", "恐惧", "行动力"]
            },
            {
                "id": 3,
                "title": "情绪管理：从焦虑到平静的内心修炼",
                "podcast_name": "心理FM",
                "description": "学会管理情绪，找到内心的平静与力量", 
                "content_summary": "本期分享情绪管理的核心技巧，包括情绪识别、接纳、转化的全过程。通过冥想、呼吸法等实操方法，帮助听众建立情绪稳定性。",
                "key_insights": ["情绪的生理机制", "正念冥想技巧", "呼吸调节方法"],
                "duration_minutes": 35,
                "publish_date": "2026-03-05", 
                "guests": [{"name": "简里里", "title": "心理咨询师"}],
                "links": [
                    {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/episode/3"},
                    {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/3"}
                ],
                "quality_score": 4.6,
                "keywords": ["情绪管理", "焦虑", "压力", "冥想", "心理健康"]
            },
            {
                "id": 4,
                "title": "创业思维：从0到1的突破",
                "podcast_name": "创业内参",
                "description": "分析成功创业者的思维模式和决策逻辑",
                "content_summary": "深入分析创业思维的核心要素，包括机会识别、资源整合、风险管理、团队建设等关键能力。",
                "key_insights": ["市场机会识别", "MVP验证方法", "资源杠杆思维"],
                "duration_minutes": 52,
                "publish_date": "2026-02-20",
                "guests": [{"name": "王五", "title": "创业导师"}],
                "links": [
                    {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/episode/4"}
                ],
                "quality_score": 4.4,
                "keywords": ["创业", "商业模式", "团队管理", "机会识别", "风险管理"]
            },
            {
                "id": 5,
                "title": "理财入门：普通人的财富增长之路",
                "podcast_name": "得到头条",
                "description": "适合普通人的理财方法和投资策略",
                "content_summary": "从理财基础知识开始，逐步介绍适合普通人的投资方法。涵盖基金定投、保险配置、风险管理等实用内容。",
                "key_insights": ["理财规划的重要性", "基金定投策略", "保险的正确配置"],
                "duration_minutes": 40,
                "publish_date": "2026-03-12",
                "guests": [{"name": "赵六", "title": "理财规划师"}],
                "links": [
                    {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/episode/5"},
                    {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/5"}
                ],
                "quality_score": 4.3,
                "keywords": ["理财", "投资", "基金定投", "保险", "财务规划"]
            }
        ]
        
        self.popular_questions = [
            {"question": "如何提高工作效率？", "search_count": 150},
            {"question": "怎样管理时间？", "search_count": 120},
            {"question": "如何克服拖延症？", "search_count": 100},
            {"question": "怎么缓解工作压力？", "search_count": 90},
            {"question": "如何建立好习惯？", "search_count": 85},
            {"question": "怎样提升沟通能力？", "search_count": 80},
            {"question": "如何学会投资理财？", "search_count": 75}
        ]
    
    def search_episodes(self, keywords: List[str]) -> List[Dict]:
        """搜索播客节目"""
        results = []
        for episode in self.episodes:
            score = 0
            for keyword in keywords:
                keyword = keyword.lower()
                # 检查标题
                if keyword in episode["title"].lower():
                    score += 3
                # 检查描述
                if keyword in episode["description"].lower():
                    score += 2
                # 检查关键词
                if keyword in [k.lower() for k in episode["keywords"]]:
                    score += 4
            
            if score > 0:
                episode_copy = episode.copy()
                episode_copy["relevance_score"] = score
                results.append(episode_copy)
        
        # 按分数排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:3]
    
    def get_popular_questions(self):
        return self.popular_questions

# 全局数据库实例
db = SimpleDB()
config = SimpleConfig()
