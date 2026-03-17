#!/usr/bin/env python3
"""
简单的播客解答器服务器
集成前端和后端在一个服务中
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import re
import uvicorn
import os

app = FastAPI(title="播客解答器", description="有问题，找播客")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据
episodes_data = [
    {
        "id": 1,
        "title": "高效工作的五个底层逻辑",
        "podcast_name": "得到头条",
        "description": "从心理学角度解析工作效率的本质，分享五个提升工作效率的底层思维模式",
        "content_summary": "本期节目深入探讨了工作效率的心理学基础，提出了五个关键的底层逻辑：专注力管理、优先级排序、能量管理、习惯培养和反馈循环。通过具体案例和实操方法，帮助听众建立高效的工作系统。",
        "key_insights": ["番茄工作法的科学原理", "优先级矩阵的实际应用", "能量管理比时间管理更重要", "习惯养成的21天理论", "即时反馈提升效率"],
        "duration_minutes": 42,
        "publish_date": "2026-03-10",
        "guests": [{"name": "张三", "title": "时间管理专家", "company": "效率研究院", "role": "嘉宾"}],
        "links": [
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/episode/1"},
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/episode/1"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/1"}
        ],
        "quality_score": 4.7,
        "keywords": ["工作效率", "时间管理", "专注力", "习惯", "心理学", "生产力"]
    },
    {
        "id": 2, 
        "title": "从拖延到高效的心理转变",
        "podcast_name": "商业就是这样",
        "description": "深度分析拖延症的心理根源，提供科学有效的解决方案",
        "content_summary": "本期节目从心理学角度剖析拖延行为的根本原因，包括完美主义、恐惧失败、缺乏动机等。通过认知行为疗法的方法，提供了系统性的拖延症治疗方案。",
        "key_insights": ["拖延的心理机制分析", "完美主义陷阱", "恐惧心理的应对", "行动导向的思维模式", "小步快跑策略"],
        "duration_minutes": 38,
        "publish_date": "2026-02-28",
        "guests": [{"name": "李四", "title": "心理学博士", "company": "心理健康研究所", "role": "嘉宾"}],
        "links": [
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/episode/2"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/2"}
        ],
        "quality_score": 4.5,
        "keywords": ["拖延症", "心理健康", "完美主义", "恐惧", "行动力", "认知疗法"]
    },
    {
        "id": 3,
        "title": "情绪管理：从焦虑到平静的内心修炼",
        "podcast_name": "心理FM",
        "description": "学会管理情绪，找到内心的平静与力量",
        "content_summary": "本期分享情绪管理的核心技巧，包括情绪识别、接纳、转化的全过程。通过冥想、呼吸法等实操方法，帮助听众建立情绪稳定性。",
        "key_insights": ["情绪的生理机制", "正念冥想技巧", "呼吸调节方法", "认知重构技术", "情绪日记的作用"],
        "duration_minutes": 35,
        "publish_date": "2026-03-05",
        "guests": [{"name": "简里里", "title": "心理咨询师", "company": "心理工作室", "role": "主播"}],
        "links": [
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/episode/3"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/3"}
        ],
        "quality_score": 4.6,
        "keywords": ["情绪管理", "焦虑", "压力", "冥想", "心理健康", "正念"]
    },
    {
        "id": 4,
        "title": "创业思维：从0到1的突破",
        "podcast_name": "创业内参",
        "description": "分析成功创业者的思维模式和决策逻辑",
        "content_summary": "深入分析创业思维的核心要素，包括机会识别、资源整合、风险管理、团队建设等关键能力。通过真实案例分享创业成功的关键要素。",
        "key_insights": ["市场机会识别", "MVP验证方法", "资源杠杆思维", "失败快速迭代", "团队搭建原则"],
        "duration_minutes": 52,
        "publish_date": "2026-02-20",
        "guests": [{"name": "王五", "title": "创业导师", "company": "创新工场", "role": "嘉宾"}],
        "links": [
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/episode/4"}
        ],
        "quality_score": 4.4,
        "keywords": ["创业", "商业模式", "团队管理", "机会识别", "风险管理", "MVP"]
    },
    {
        "id": 5,
        "title": "理财入门：普通人的财富增长之路",
        "podcast_name": "得到头条",
        "description": "适合普通人的理财方法和投资策略",
        "content_summary": "从理财基础知识开始，逐步介绍适合普通人的投资方法。涵盖基金定投、保险配置、风险管理等实用内容。",
        "key_insights": ["理财规划的重要性", "基金定投策略", "保险的正确配置", "风险与收益平衡", "复利的威力"],
        "duration_minutes": 40,
        "publish_date": "2026-03-12",
        "guests": [{"name": "赵六", "title": "理财规划师", "company": "财富管理公司", "role": "嘉宾"}],
        "links": [
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/episode/5"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/5"}
        ],
        "quality_score": 4.3,
        "keywords": ["理财", "投资", "基金定投", "保险", "财务规划", "复利"]
    }
]

popular_questions = [
    {"question": "如何提高工作效率？", "search_count": 150, "category": "工作效率"},
    {"question": "怎样管理时间？", "search_count": 120, "category": "时间管理"},
    {"question": "如何克服拖延症？", "search_count": 100, "category": "个人成长"},
    {"question": "怎么缓解工作压力？", "search_count": 90, "category": "心理健康"},
    {"question": "如何建立好习惯？", "search_count": 85, "category": "习惯培养"},
    {"question": "怎样提升沟通能力？", "search_count": 80, "category": "人际关系"},
    {"question": "如何学会投资理财？", "search_count": 75, "category": "财务管理"}
]

class SearchRequest(BaseModel):
    question: str
    user_id: Optional[int] = None

def extract_keywords(question: str) -> List[str]:
    """提取关键词"""
    # 关键词映射
    keyword_map = {
        "效率": ["工作效率", "效率", "生产力"],
        "时间": ["时间管理", "时间"],
        "拖延": ["拖延症", "拖延"],
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
    
    for category, words in keyword_map.items():
        for word in words:
            if word in question_lower:
                keywords.extend(words[:2])
                break
    
    if not keywords:
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', question)
        keywords = [word for word in chinese_words if len(word) >= 2][:5]
    
    return list(set(keywords))

def search_episodes(keywords: List[str]) -> List[Dict]:
    """搜索播客"""
    results = []
    for episode in episodes_data:
        score = 0
        for keyword in keywords:
            keyword = keyword.lower()
            if keyword in episode["title"].lower():
                score += 3
            if keyword in episode["description"].lower():
                score += 2
            if keyword in [k.lower() for k in episode["keywords"]]:
                score += 4
        
        if score > 0:
            episode_copy = episode.copy()
            episode_copy["relevance_score"] = score
            results.append(episode_copy)
    
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:3]

# 前端页面
@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>播客解答器 - 有问题，找播客</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .title { font-size: 3rem; margin-bottom: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { font-size: 1.2rem; color: #666; margin-bottom: 30px; }
        .search-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 40px; }
        .search-input { width: 100%; padding: 15px; font-size: 16px; border: 2px solid #e1e5e9; border-radius: 8px; resize: vertical; min-height: 100px; }
        .search-input:focus { outline: none; border-color: #667eea; }
        .search-button { width: 100%; padding: 15px; margin-top: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .search-button:hover { opacity: 0.9; }
        .popular-questions { margin-bottom: 40px; }
        .popular-title { text-align: center; margin-bottom: 20px; color: #333; }
        .questions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .question-tag { padding: 12px 16px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 20px; text-align: center; cursor: pointer; transition: all 0.3s; }
        .question-tag:hover { background: #667eea; color: white; transform: translateY(-2px); }
        .results { display: none; }
        .result-card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .result-title { font-size: 1.2rem; margin-bottom: 10px; color: #333; }
        .result-podcast { color: #667eea; font-weight: bold; }
        .result-summary { margin: 10px 0; color: #666; }
        .result-insights { margin: 10px 0; }
        .insight-tag { display: inline-block; background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin: 2px; }
        .result-links { margin-top: 15px; }
        .platform-link { display: inline-block; padding: 8px 16px; margin: 5px; background: #f5f5f5; color: #333; text-decoration: none; border-radius: 20px; font-size: 14px; }
        .platform-link:hover { background: #e0e0e0; }
        .loading { display: none; text-align: center; padding: 40px; }
        .footer { text-align: center; padding: 40px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🎧 播客解答器</h1>
            <p class="subtitle">有问题，找播客 - 输入你的困扰，获得最相关的播客推荐</p>
        </div>

        <div class="search-section">
            <textarea id="questionInput" class="search-input" placeholder="输入你遇到的问题或困扰...&#10;&#10;例如：我最近工作压力很大，总是焦虑，怎么办？"></textarea>
            <button onclick="searchPodcasts()" class="search-button">🔍 寻找播客</button>
        </div>

        <div class="popular-questions">
            <h3 class="popular-title">🔥 热门问题</h3>
            <div class="questions-grid">
                <div class="question-tag" onclick="setQuestion('如何提高工作效率？')">如何提高工作效率？</div>
                <div class="question-tag" onclick="setQuestion('怎样管理时间？')">怎样管理时间？</div>
                <div class="question-tag" onclick="setQuestion('如何克服拖延症？')">如何克服拖延症？</div>
                <div class="question-tag" onclick="setQuestion('怎么缓解工作压力？')">怎么缓解工作压力？</div>
                <div class="question-tag" onclick="setQuestion('如何建立好习惯？')">如何建立好习惯？</div>
                <div class="question-tag" onclick="setQuestion('如何学会投资理财？')">如何学会投资理财？</div>
            </div>
        </div>

        <div id="loading" class="loading">
            <div>🔍 正在为你搜索最相关的播客...</div>
        </div>

        <div id="results" class="results"></div>

        <div class="footer">
            <p>播客解答器 v1.0.0 | 让知识触手可及</p>
        </div>
    </div>

    <script>
        function setQuestion(question) {
            document.getElementById('questionInput').value = question;
        }

        async function searchPodcasts() {
            const question = document.getElementById('questionInput').value.trim();
            if (!question) {
                alert('请输入你的问题');
                return;
            }

            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            loading.style.display = 'block';
            results.style.display = 'none';

            try {
                const response = await fetch('/api/search/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });

                const data = await response.json();
                loading.style.display = 'none';
                
                if (data.recommendations && data.recommendations.length > 0) {
                    displayResults(data.question, data.recommendations);
                } else {
                    results.innerHTML = '<div class="result-card">没有找到相关播客，试试换个问法吧 😊</div>';
                    results.style.display = 'block';
                }
            } catch (error) {
                loading.style.display = 'none';
                results.innerHTML = '<div class="result-card">搜索失败，请稍后再试</div>';
                results.style.display = 'block';
                console.error('搜索错误:', error);
            }
        }

        function displayResults(question, recommendations) {
            const results = document.getElementById('results');
            let html = `<h3>🎯 针对问题："${question}"，为你推荐 ${recommendations.length} 期播客：</h3>`;
            
            recommendations.forEach((rec, index) => {
                const badges = ['🏆 最匹配', '💡 实用性强', '🔥 用户好评'];
                const badge = badges[index] || `第 ${index + 1} 推荐`;
                
                html += `
                    <div class="result-card">
                        <div style="float: right; background: linear-gradient(135deg, #ffd700, #ffed4e); color: #333; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                            ${badge}
                        </div>
                        <div class="result-title">《${rec.podcast_name}》第${rec.episode_id}期</div>
                        <div style="font-size: 1.1rem; font-weight: bold; margin: 8px 0;">💬 ${rec.title}</div>
                        
                        ${rec.guests && rec.guests.length > 0 ? `
                            <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin: 10px 0;">
                                👤 嘉宾：${rec.guests.map(g => `${g.name}${g.title ? `（${g.title}）` : ''}`).join('、')}
                            </div>
                        ` : ''}
                        
                        <div style="margin: 10px 0;">
                            ${rec.duration_minutes ? `⏱️ ${rec.duration_minutes}分钟` : ''} 
                            ${rec.publish_date ? `📅 ${rec.publish_date}` : ''}
                            ${rec.quality_score ? `⭐ ${rec.quality_score.toFixed(1)}分` : ''}
                        </div>
                        
                        ${rec.content_summary ? `
                            <div class="result-summary">
                                <strong>📝 内容摘要：</strong>${rec.content_summary}
                            </div>
                        ` : ''}
                        
                        ${rec.key_insights && rec.key_insights.length > 0 ? `
                            <div class="result-insights">
                                <strong>💡 核心要点：</strong><br>
                                ${rec.key_insights.slice(0, 5).map(insight => 
                                    `<span class="insight-tag">${insight}</span>`
                                ).join('')}
                            </div>
                        ` : ''}
                        
                        <div class="result-links">
                            <strong>🔗 收听链接：</strong><br>
                            ${rec.links && rec.links.length > 0 ? 
                                rec.links.map(link => 
                                    `<a href="${link.url}" target="_blank" class="platform-link">${link.platform_name}</a>`
                                ).join('') 
                                : '<span style="color: #999;">暂无播放链接</span>'
                            }
                        </div>
                        
                        ${rec.match_reason ? `
                            <div style="margin-top: 10px; font-size: 12px; color: #999;">
                                ${rec.match_reason}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            results.innerHTML = html;
            results.style.display = 'block';
            results.scrollIntoView({ behavior: 'smooth' });
        }

        // 支持回车键搜索
        document.getElementById('questionInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                searchPodcasts();
            }
        });
    </script>
</body>
</html>
    """

# API端点
@app.post("/api/search/")
async def search_podcasts(request: SearchRequest):
    try:
        question = request.question.strip()
        if len(question) < 2:
            raise HTTPException(status_code=400, detail="问题太短")
        
        keywords = extract_keywords(question)
        episodes = search_episodes(keywords)
        
        recommendations = []
        for episode in episodes:
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
        
        return {
            "question": question,
            "recommendations": recommendations,
            "total_results": len(episodes),
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/popular-questions")
async def get_popular_questions():
    return popular_questions

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🎧 播客解答器启动中...")
    print("🌐 外网访问地址: http://47.237.167.8:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)