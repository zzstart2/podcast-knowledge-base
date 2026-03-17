import openai
from typing import List, Dict, Any
import json
import re
from app.core.config import settings

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI()
    
    async def analyze_user_question(self, question: str) -> Dict[str, Any]:
        """分析用户问题，提取关键信息"""
        
        system_prompt = """你是一个播客推荐专家。请分析用户的问题，提取以下信息：

1. 核心问题类型（工作、生活、学习、情感、健康、财务等）
2. 具体关键词
3. 紧急程度（低、中、高）
4. 适合的播客类型（教育、访谈、故事、新闻等）
5. 目标听众特征

请以JSON格式返回分析结果。"""

        user_prompt = f"用户问题：{question}"
        
        try:
            response = await self.client.chat.completions.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # 解析AI响应
            ai_response = response.choices[0].message.content
            
            # 尝试提取JSON
            try:
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    # 如果没有找到JSON，使用默认分析
                    analysis = self._default_analysis(question)
            except json.JSONDecodeError:
                analysis = self._default_analysis(question)
            
            return analysis
            
        except Exception as e:
            print(f"AI分析错误: {e}")
            return self._default_analysis(question)
    
    def _default_analysis(self, question: str) -> Dict[str, Any]:
        """默认问题分析逻辑"""
        keywords = self._extract_keywords(question)
        
        return {
            "core_problem": "通用问题",
            "keywords": keywords,
            "urgency": "中",
            "podcast_type": "教育访谈",
            "target_audience": "一般听众",
            "categories": ["个人成长"]
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """简单的关键词提取"""
        # 常见问题关键词映射
        keyword_map = {
            "工作": ["效率", "职场", "管理", "领导力", "团队"],
            "学习": ["方法", "技巧", "知识", "技能", "成长"],
            "情感": ["关系", "沟通", "心理", "焦虑", "压力"],
            "健康": ["运动", "饮食", "睡眠", "养生", "医疗"],
            "财务": ["投资", "理财", "赚钱", "财富", "经济"],
            "生活": ["习惯", "时间", "生活方式", "家庭"]
        }
        
        keywords = []
        for category, words in keyword_map.items():
            for word in words:
                if word in text:
                    keywords.append(word)
        
        return keywords[:5]  # 返回最多5个关键词
    
    async def generate_search_keywords(self, question: str, analysis: Dict[str, Any]) -> List[str]:
        """基于问题分析生成搜索关键词"""
        base_keywords = analysis.get("keywords", [])
        
        # 添加问题中的直接关键词
        direct_keywords = re.findall(r'[\u4e00-\u9fff]+', question)
        direct_keywords = [kw for kw in direct_keywords if len(kw) >= 2]
        
        # 合并并去重
        all_keywords = list(set(base_keywords + direct_keywords))
        
        return all_keywords[:10]  # 返回最多10个关键词
    
    async def rank_episodes(self, episodes: List[Dict], question: str, analysis: Dict[str, Any]) -> List[Dict]:
        """对搜索到的播客进行智能排序"""
        
        # 简单的评分算法
        for episode in episodes:
            score = 0
            
            # 关键词匹配度
            keywords = analysis.get("keywords", [])
            title = episode.get("title", "").lower()
            description = episode.get("description", "").lower()
            
            for keyword in keywords:
                if keyword.lower() in title:
                    score += 3
                if keyword.lower() in description:
                    score += 2
            
            # 质量评分
            quality_score = episode.get("quality_score", 0)
            score += quality_score * 10
            
            # 时效性（越新越好）
            # 这里需要根据publish_date计算时效性
            
            episode["relevance_score"] = score
        
        # 按评分排序
        episodes.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return episodes[:3]  # 返回前3个结果