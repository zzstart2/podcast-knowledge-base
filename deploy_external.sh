#!/bin/bash

# 外网部署脚本

set -e

echo "🌐 播客解答器 - 外网部署脚本"
echo "=================================="

SERVER_IP="47.237.167.8"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"

echo "🖥️  服务器IP: $SERVER_IP"
echo "📱 前端端口: $FRONTEND_PORT"
echo "🔧 后端端口: $BACKEND_PORT"

# 停止现有服务
echo "🛑 停止现有服务..."
pkill -f "python.*uvicorn" || true
pkill -f "npm start" || true
pkill -f "node.*react-scripts" || true

# 设置环境变量
export DATABASE_URL="sqlite:///./podcast.db"
export OPENAI_API_KEY="sk-placeholder"
export DEBUG="true"

# 创建简化的后端配置
echo "📝 创建简化的后端配置..."
cat > backend/app/simple_config.py << EOF
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
EOF

# 创建简化的后端应用
echo "🔧 创建简化的后端应用..."
cat > backend/simple_app.py << 'EOF'
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
EOF

# 启动后端服务
echo "🚀 启动后端服务..."
cd backend
python3 -m pip install fastapi uvicorn python-multipart > /dev/null 2>&1 || true
nohup python3 simple_app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 5

# 检查后端是否启动成功
if curl -f http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功 (PID: $BACKEND_PID)"
else
    echo "❌ 后端服务启动失败"
    cat backend.log
    exit 1
fi

# 修改前端配置指向外网IP
echo "🔧 配置前端外网访问..."
cd frontend

# 创建外网配置
cat > .env.production << EOF
REACT_APP_API_URL=http://$SERVER_IP:$BACKEND_PORT/api/v1
GENERATE_SOURCEMAP=false
EOF

cat > .env.local << EOF
REACT_APP_API_URL=http://$SERVER_IP:$BACKEND_PORT/api/v1
GENERATE_SOURCEMAP=false
EOF

# 更新API配置
cat > src/services/api.js << 'EOF'
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://47.237.167.8:8001/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    console.log('API请求:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
EOF

# 安装依赖并启动前端
echo "📦 安装前端依赖..."
if [ ! -d "node_modules" ]; then
    npm install > ../frontend-install.log 2>&1
fi

echo "🎨 启动前端服务..."
# 设置端口并启动
export PORT=$FRONTEND_PORT
nohup npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 15

# 检查前端是否启动成功
if curl -f http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "✅ 前端服务启动成功 (PID: $FRONTEND_PID)"
else
    echo "⚠️  前端可能还在启动中..."
fi

# 输出访问信息
echo ""
echo "🎉 播客解答器部署完成！"
echo "=================================="
echo "🌐 外网访问地址："
echo "   http://$SERVER_IP:$FRONTEND_PORT"
echo ""
echo "🔧 API服务："
echo "   http://$SERVER_IP:$BACKEND_PORT"
echo "   API文档: http://$SERVER_IP:$BACKEND_PORT/docs"
echo ""
echo "📊 服务状态："
echo "   后端PID: $BACKEND_PID"
echo "   前端PID: $FRONTEND_PID"
echo ""
echo "📝 日志文件："
echo "   后端日志: $(pwd)/backend.log"
echo "   前端日志: $(pwd)/frontend.log"
echo ""
echo "🛠️  管理命令："
echo "   查看后端日志: tail -f backend.log"
echo "   查看前端日志: tail -f frontend.log"
echo "   停止后端: kill $BACKEND_PID"
echo "   停止前端: kill $FRONTEND_PID"

# 保存PID到文件
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo ""
echo "🔗 点击访问: http://$SERVER_IP:$FRONTEND_PORT"
EOF