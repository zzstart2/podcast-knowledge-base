from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from datetime import date

from app.database import database, episodes_table, podcasts_table
from app.services.ai_service import AIService
from app.core.config import settings

router = APIRouter()

# 请求模型
class SearchRequest(BaseModel):
    question: str
    user_id: Optional[int] = None

class SearchResponse(BaseModel):
    question: str
    recommendations: List[Dict[str, Any]]
    total_results: int
    analysis: Dict[str, Any]

# 初始化AI服务
ai_service = AIService()

@router.post("/", response_model=SearchResponse)
async def search_podcasts(request: SearchRequest):
    """搜索播客推荐"""
    
    try:
        # 1. 问题预处理
        question = request.question.strip()
        if len(question) < 2:
            raise HTTPException(status_code=400, detail="问题太短，请提供更详细的描述")
        
        if len(question) > 500:
            raise HTTPException(status_code=400, detail="问题太长，请简化描述")
        
        # 2. AI分析用户问题
        print(f"分析问题: {question}")
        analysis = await ai_service.analyze_user_question(question)
        
        # 3. 生成搜索关键词
        search_keywords = await ai_service.generate_search_keywords(question, analysis)
        print(f"搜索关键词: {search_keywords}")
        
        # 4. 执行数据库搜索
        episodes = await search_episodes_in_database(search_keywords)
        print(f"找到 {len(episodes)} 个结果")
        
        # 5. AI重新排序和评分
        ranked_episodes = await ai_service.rank_episodes(episodes, question, analysis)
        
        # 6. 格式化返回结果
        recommendations = []
        for episode in ranked_episodes:
            # 获取播客信息
            podcast = await get_podcast_info(episode["podcast_id"])
            
            # 获取播客链接
            links = await get_episode_links(episode["id"])
            
            # 获取嘉宾信息
            guests = await get_episode_guests(episode["id"])
            
            recommendation = {
                "episode_id": episode["id"],
                "title": episode["title"],
                "podcast_name": podcast.get("name", "未知播客"),
                "description": episode.get("description", ""),
                "content_summary": episode.get("content_summary", ""),
                "key_insights": episode.get("key_insights", []),
                "duration_minutes": episode.get("duration_minutes"),
                "publish_date": str(episode.get("publish_date", "")),
                "difficulty_level": episode.get("difficulty_level", ""),
                "guests": guests,
                "links": links,
                "relevance_score": episode.get("relevance_score", 0),
                "quality_score": episode.get("quality_score", 0),
                "match_reason": f"匹配关键词: {', '.join(search_keywords[:3])}"
            }
            recommendations.append(recommendation)
        
        # 7. 记录搜索历史（如果有用户ID）
        if request.user_id:
            await save_search_history(request.user_id, question, recommendations, analysis)
        
        return SearchResponse(
            question=question,
            recommendations=recommendations,
            total_results=len(episodes),
            analysis=analysis
        )
        
    except Exception as e:
        print(f"搜索错误: {e}")
        raise HTTPException(status_code=500, detail=f"搜索过程中发生错误: {str(e)}")

async def search_episodes_in_database(keywords: List[str]) -> List[Dict]:
    """在数据库中搜索相关播客"""
    
    # 构建搜索查询
    search_terms = " | ".join(keywords)  # PostgreSQL全文搜索语法
    
    query = f"""
    SELECT DISTINCT e.*, p.name as podcast_name
    FROM episodes e
    JOIN podcasts p ON e.podcast_id = p.id
    WHERE 
        to_tsvector('chinese', e.title || ' ' || COALESCE(e.description, '') || ' ' || COALESCE(e.content_summary, '')) 
        @@ to_tsquery('chinese', %s)
        OR e.title ILIKE ANY(%s)
        OR e.description ILIKE ANY(%s)
        OR e.content_summary ILIKE ANY(%s)
    ORDER BY 
        ts_rank(to_tsvector('chinese', e.title || ' ' || COALESCE(e.description, '')), to_tsquery('chinese', %s)) DESC,
        e.quality_score DESC,
        e.publish_date DESC
    LIMIT 20
    """
    
    # 创建LIKE模式
    like_patterns = [f"%{keyword}%" for keyword in keywords]
    
    try:
        results = await database.fetch_all(
            query, 
            search_terms, like_patterns, like_patterns, like_patterns, search_terms
        )
        return [dict(row) for row in results]
    except Exception as e:
        print(f"数据库搜索错误: {e}")
        # 降级到简单搜索
        return await simple_search_episodes(keywords)

async def simple_search_episodes(keywords: List[str]) -> List[Dict]:
    """简单的关键词搜索（降级方案）"""
    
    like_conditions = []
    params = []
    
    for keyword in keywords:
        like_conditions.append("(e.title ILIKE %s OR e.description ILIKE %s OR e.content_summary ILIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    
    query = f"""
    SELECT DISTINCT e.*, p.name as podcast_name
    FROM episodes e
    JOIN podcasts p ON e.podcast_id = p.id
    WHERE ({' OR '.join(like_conditions)})
    ORDER BY e.quality_score DESC, e.publish_date DESC
    LIMIT 20
    """
    
    try:
        results = await database.fetch_all(query, *params)
        return [dict(row) for row in results]
    except Exception as e:
        print(f"简单搜索也失败: {e}")
        return []

async def get_podcast_info(podcast_id: int) -> Dict:
    """获取播客信息"""
    query = "SELECT * FROM podcasts WHERE id = %s"
    result = await database.fetch_one(query, podcast_id)
    return dict(result) if result else {}

async def get_episode_links(episode_id: int) -> List[Dict]:
    """获取播客链接"""
    query = """
    SELECT platform, platform_name, url 
    FROM episode_links 
    WHERE episode_id = %s AND is_active = true
    """
    results = await database.fetch_all(query, episode_id)
    return [dict(row) for row in results]

async def get_episode_guests(episode_id: int) -> List[Dict]:
    """获取播客嘉宾"""
    query = """
    SELECT g.name, g.title, g.company, eg.role
    FROM guests g
    JOIN episode_guests eg ON g.id = eg.guest_id
    WHERE eg.episode_id = %s
    """
    results = await database.fetch_all(query, episode_id)
    return [dict(row) for row in results]

async def save_search_history(user_id: int, question: str, results: List[Dict], analysis: Dict):
    """保存搜索历史"""
    query = """
    INSERT INTO search_history (user_id, question, search_results, created_at)
    VALUES (%s, %s, %s, NOW())
    """
    
    # 简化结果用于存储
    simplified_results = [
        {"episode_id": r["episode_id"], "title": r["title"], "relevance_score": r["relevance_score"]}
        for r in results
    ]
    
    try:
        await database.execute(query, user_id, question, {"results": simplified_results, "analysis": analysis})
    except Exception as e:
        print(f"保存搜索历史失败: {e}")

@router.get("/popular-questions")
async def get_popular_questions():
    """获取热门问题"""
    query = """
    SELECT question, search_count, category
    FROM popular_questions
    ORDER BY search_count DESC
    LIMIT 10
    """
    
    results = await database.fetch_all(query)
    return [dict(row) for row in results]

@router.get("/suggestions")
async def get_search_suggestions(q: str):
    """搜索建议"""
    if len(q) < 2:
        return []
    
    # 从历史搜索中获取建议
    query = """
    SELECT DISTINCT question
    FROM search_history
    WHERE question ILIKE %s
    ORDER BY created_at DESC
    LIMIT 5
    """
    
    results = await database.fetch_all(query, f"%{q}%")
    suggestions = [row["question"] for row in results]
    
    # 添加一些预设建议
    preset_suggestions = [
        "如何提高工作效率？",
        "怎样管理时间？",
        "如何克服拖延症？",
        "怎么缓解工作压力？",
        "如何建立好习惯？"
    ]
    
    for suggestion in preset_suggestions:
        if q.lower() in suggestion.lower() and suggestion not in suggestions:
            suggestions.append(suggestion)
    
    return suggestions[:5]