from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import re
import uvicorn
from app.simple_config import db, config

app = FastAPI(
    title="播客解答器 API",
    description="基于问题匹配的播客推荐系统", 
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    question: str
    user_id: Optional[int] = None

class SearchResponse(BaseModel):
    question: str
    recommendations: List[Dict[str, Any]]
    total_results: int
    analysis: Dict[str, Any]

def extract_keywords(question: str) -> List[str]:
    """简单的关键词提取"""
    # 移除标点符号
    clean_text = re.sub(r'[^\w\s]', ' ', question)
    
    # 常见问题关键词映射
    keyword_map = {
        "效率": ["工作效率", "效率", "生产力"],
        "时间": ["时间管理", "时间"],
        "拖延": ["拖延症", "拖延", "procrastination"],
        "焦虑": ["焦虑", "压力", "紧张"],
        "情绪": ["情绪管理", "情绪", "心理"],
        "创业": ["创业", "商业", "startup"],
        "理财": ["理财", "投资", "财务", "金融"],
        "管理": ["管理", "领导", "团队"],
        "学习": ["学习", "知识", "技能"],
        "沟通": ["沟通", "交流", "人际关系"]
    }
    
    keywords = []
    question_lower = question.lower()
    
    # 直接匹配关键词
    for category, words in keyword_map.items():
        for word in words:
            if word in question_lower:
                keywords.extend(words[:2])  # 添加相关词汇
                break
    
    # 如果没有匹配到，提取中文词汇
    if not keywords:
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', question)
        keywords = [word for word in chinese_words if len(word) >= 2][:5]
    
    return list(set(keywords))

@app.get("/")
async def root():
    return {"message": "播客解答器 API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/search/", response_model=SearchResponse)
async def search_podcasts(request: SearchRequest):
    try:
        question = request.question.strip()
        
        if len(question) < 2:
            raise HTTPException(status_code=400, detail="问题太短")
        
        # 提取关键词
        keywords = extract_keywords(question)
        
        # 搜索播客
        episodes = db.search_episodes(keywords)
        
        # 格式化结果
        recommendations = []
        for i, episode in enumerate(episodes):
            rec = {
                "episode_id": episode["id"],
                "title": episode["title"],
                "podcast_name": episode["podcast_name"],
                "description": episode["description"],
                "content_summary": episode["content_summary"],
                "key_insights": episode["key_insights"],
                "duration_minutes": episode["duration_minutes"], 
                "publish_date": episode["publish_date"],
                "guests": episode["guests"],
                "links": episode["links"],
                "relevance_score": episode["relevance_score"],
                "quality_score": episode["quality_score"],
                "match_reason": f"匹配关键词: {', '.join(keywords[:3])}"
            }
            recommendations.append(rec)
        
        analysis = {
            "core_problem": "通用问题",
            "keywords": keywords,
            "podcast_type": "教育访谈"
        }
        
        return SearchResponse(
            question=question,
            recommendations=recommendations,
            total_results=len(episodes),
            analysis=analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/search/popular-questions")
async def get_popular_questions():
    return db.get_popular_questions()

@app.get("/api/v1/search/suggestions")
async def get_suggestions(q: str):
    suggestions = [
        "如何提高工作效率？",
        "怎样管理时间？", 
        "如何克服拖延症？",
        "怎么缓解工作压力？",
        "如何建立好习惯？"
    ]
    
    return [s for s in suggestions if q.lower() in s.lower()][:5]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
