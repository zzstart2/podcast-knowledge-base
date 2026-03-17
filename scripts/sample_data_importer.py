#!/usr/bin/env python3
"""
样本数据导入脚本
用于快速搭建MVP版本的测试数据
"""

import asyncio
import asyncpg
import os
import sys
from datetime import datetime, date
import json

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 样本播客数据
SAMPLE_PODCASTS = [
    {
        "name": "得到头条",
        "description": "每天10分钟，给你一个升级认知的机会",
        "author": "罗辑思维团队",
        "category": "商业财经",
        "rss_url": "https://example.com/dedao-rss",
        "cover_image": "https://example.com/covers/dedao.jpg",
        "avg_rating": 4.5
    },
    {
        "name": "商业就是这样",
        "description": "从商业案例中学习商业智慧",
        "author": "吴晓波频道",
        "category": "商业财经", 
        "avg_rating": 4.3
    },
    {
        "name": "罗辑思维",
        "description": "启发你的思维，改变你的认知",
        "author": "罗振宇",
        "category": "知识科普",
        "avg_rating": 4.6
    },
    {
        "name": "心理FM",
        "description": "心理学知识与生活智慧",
        "author": "简里里",
        "category": "心理健康",
        "avg_rating": 4.4
    },
    {
        "name": "创业内参",
        "description": "创业者必听的商业内容",
        "author": "李善友",
        "category": "创业投资",
        "avg_rating": 4.2
    }
]

# 样本嘉宾数据
SAMPLE_GUESTS = [
    {
        "name": "张三",
        "title": "时间管理专家",
        "company": "效率研究院",
        "bio": "专注时间管理和效率提升研究15年",
        "expertise_areas": ["时间管理", "效率提升", "工作流程优化"]
    },
    {
        "name": "李四",
        "title": "心理学博士",
        "company": "心理健康研究所",
        "bio": "认知行为疗法专家，帮助上万人解决心理问题",
        "expertise_areas": ["心理健康", "认知疗法", "情绪管理"]
    },
    {
        "name": "王五",
        "title": "创业导师",
        "company": "创新工场",
        "bio": "连续创业者，投资过50+成功项目",
        "expertise_areas": ["创业指导", "商业模式", "团队管理"]
    },
    {
        "name": "赵六",
        "title": "理财规划师",
        "company": "财富管理公司",
        "bio": "20年理财经验，帮助客户实现财务自由",
        "expertise_areas": ["投资理财", "财务规划", "风险管理"]
    }
]

# 样本播客节目数据
SAMPLE_EPISODES = [
    {
        "podcast_id": 1,
        "episode_number": 234,
        "title": "高效工作的五个底层逻辑",
        "description": "从心理学角度解析工作效率的本质，分享五个提升工作效率的底层思维模式",
        "publish_date": date(2026, 3, 10),
        "duration_minutes": 42,
        "content_summary": "本期节目深入探讨了工作效率的心理学基础，提出了五个关键的底层逻辑：专注力管理、优先级排序、能量管理、习惯培养和反馈循环。通过具体案例和实操方法，帮助听众建立高效的工作系统。",
        "key_insights": ["番茄工作法的科学原理", "优先级矩阵的实际应用", "能量管理比时间管理更重要", "习惯养成的21天理论", "即时反馈提升效率"],
        "problems_addressed": ["工作效率低下", "时间管理困难", "注意力不集中", "工作拖延", "任务优先级混乱"],
        "target_audience": "职场人士",
        "difficulty_level": "进阶",
        "quality_score": 4.7,
        "guest_ids": [1]
    },
    {
        "podcast_id": 2,
        "episode_number": 89,
        "title": "从拖延到高效的心理转变",
        "description": "深度分析拖延症的心理根源，提供科学有效的解决方案",
        "publish_date": date(2026, 2, 28),
        "duration_minutes": 38,
        "content_summary": "本期节目从心理学角度剖析拖延行为的根本原因，包括完美主义、恐惧失败、缺乏动机等。通过认知行为疗法的方法，提供了系统性的拖延症治疗方案。",
        "key_insights": ["拖延的心理机制分析", "完美主义陷阱", "恐惧心理的应对", "行动导向的思维模式", "小步快跑策略"],
        "problems_addressed": ["严重拖延", "完美主义倾向", "行动力不足", "心理阻抗", "自我怀疑"],
        "target_audience": "有拖延问题的人群",
        "difficulty_level": "入门",
        "quality_score": 4.5,
        "guest_ids": [2]
    },
    {
        "podcast_id": 3,
        "episode_number": 567,
        "title": "效率革命：重新定义工作",
        "description": "在AI时代，如何重新定义工作效率和价值创造",
        "publish_date": date(2026, 3, 15),
        "duration_minutes": 45,
        "content_summary": "探讨AI时代背景下工作效率的新定义，分析深度工作vs浅度工作的区别，提出知识工作者的核心竞争力模型。",
        "key_insights": ["深度工作的重要性", "注意力经济时代", "AI协作的工作模式", "价值创造的新标准", "终身学习的必要性"],
        "problems_addressed": ["AI焦虑", "工作价值困惑", "技能更新压力", "注意力分散", "职业规划迷茫"],
        "target_audience": "知识工作者",
        "difficulty_level": "专业",
        "quality_score": 4.8
    },
    {
        "podcast_id": 4,
        "episode_number": 156,
        "title": "情绪管理：从焦虑到平静的内心修炼",
        "description": "学会管理情绪，找到内心的平静与力量",
        "publish_date": date(2026, 3, 5),
        "duration_minutes": 35,
        "content_summary": "本期分享情绪管理的核心技巧，包括情绪识别、接纳、转化的全过程。通过冥想、呼吸法等实操方法，帮助听众建立情绪稳定性。",
        "key_insights": ["情绪的生理机制", "正念冥想技巧", "呼吸调节方法", "认知重构技术", "情绪日记的作用"],
        "problems_addressed": ["焦虑情绪", "情绪波动大", "压力管理", "负面思维", "情绪失控"],
        "target_audience": "有情绪管理需求的人群",
        "difficulty_level": "入门",
        "quality_score": 4.6,
        "guest_ids": [2]
    },
    {
        "podcast_id": 5,
        "episode_number": 78,
        "title": "创业思维：从0到1的突破",
        "description": "分析成功创业者的思维模式和决策逻辑",
        "publish_date": date(2026, 2, 20),
        "duration_minutes": 52,
        "content_summary": "深入分析创业思维的核心要素，包括机会识别、资源整合、风险管理、团队建设等关键能力。通过真实案例分享创业成功的关键要素。",
        "key_insights": ["市场机会识别", "MVP验证方法", "资源杠杆思维", "失败快速迭代", "团队搭建原则"],
        "problems_addressed": ["创业方向不明", "资源不足", "团队问题", "市场验证困难", "风险管控"],
        "target_audience": "创业者和有创业意向的人",
        "difficulty_level": "进阶",
        "quality_score": 4.4,
        "guest_ids": [3]
    },
    {
        "podcast_id": 1,
        "episode_number": 235,
        "title": "理财入门：普通人的财富增长之路",
        "description": "适合普通人的理财方法和投资策略",
        "publish_date": date(2026, 3, 12),
        "duration_minutes": 40,
        "content_summary": "从理财基础知识开始，逐步介绍适合普通人的投资方法。涵盖基金定投、保险配置、风险管理等实用内容。",
        "key_insights": ["理财规划的重要性", "基金定投策略", "保险的正确配置", "风险与收益平衡", "复利的威力"],
        "problems_addressed": ["不会理财", "投资亏损", "保险困惑", "财务规划", "风险控制"],
        "target_audience": "理财新手",
        "difficulty_level": "入门",
        "quality_score": 4.3,
        "guest_ids": [4]
    }
]

# 播客平台链接数据
PLATFORM_LINKS = [
    {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "base_url": "https://podcasts.apple.com"},
    {"platform": "spotify", "platform_name": "Spotify", "base_url": "https://open.spotify.com"},
    {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "base_url": "https://www.xiaoyuzhoufm.com"}
]

async def create_connection():
    """创建数据库连接"""
    return await asyncpg.connect(
        host="localhost",
        database="podcast_qa_db",
        user="postgres",
        password="password"
    )

async def import_podcasts(conn):
    """导入播客数据"""
    print("导入播客数据...")
    
    for podcast in SAMPLE_PODCASTS:
        podcast_id = await conn.fetchval(
            """
            INSERT INTO podcasts (name, description, author, category, language, rss_url, cover_image, avg_rating)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            podcast["name"],
            podcast["description"],
            podcast["author"],
            podcast["category"],
            "zh",
            podcast.get("rss_url"),
            podcast.get("cover_image"),
            podcast["avg_rating"]
        )
        print(f"  插入播客: {podcast['name']} (ID: {podcast_id})")

async def import_guests(conn):
    """导入嘉宾数据"""
    print("导入嘉宾数据...")
    
    for guest in SAMPLE_GUESTS:
        guest_id = await conn.fetchval(
            """
            INSERT INTO guests (name, title, company, bio, expertise_areas)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            guest["name"],
            guest["title"],
            guest["company"],
            guest["bio"],
            guest["expertise_areas"]
        )
        print(f"  插入嘉宾: {guest['name']} (ID: {guest_id})")

async def import_episodes(conn):
    """导入播客集数据"""
    print("导入播客集数据...")
    
    for episode in SAMPLE_EPISODES:
        episode_id = await conn.fetchval(
            """
            INSERT INTO episodes (
                podcast_id, episode_number, title, description, publish_date,
                duration_minutes, content_summary, key_insights, problems_addressed,
                target_audience, difficulty_level, quality_score
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            """,
            episode["podcast_id"],
            episode["episode_number"],
            episode["title"],
            episode["description"],
            episode["publish_date"],
            episode["duration_minutes"],
            episode["content_summary"],
            episode["key_insights"],
            episode["problems_addressed"],
            episode["target_audience"],
            episode["difficulty_level"],
            episode["quality_score"]
        )
        
        print(f"  插入播客集: {episode['title']} (ID: {episode_id})")
        
        # 插入嘉宾关联
        if "guest_ids" in episode:
            for guest_id in episode["guest_ids"]:
                await conn.execute(
                    """
                    INSERT INTO episode_guests (episode_id, guest_id, role)
                    VALUES ($1, $2, $3)
                    """,
                    episode_id, guest_id, "嘉宾"
                )
        
        # 插入平台链接
        for platform in PLATFORM_LINKS:
            await conn.execute(
                """
                INSERT INTO episode_links (episode_id, platform, platform_name, url)
                VALUES ($1, $2, $3, $4)
                """,
                episode_id,
                platform["platform"],
                platform["platform_name"],
                f"{platform['base_url']}/episode/{episode_id}"
            )

async def import_popular_questions(conn):
    """导入热门问题"""
    print("导入热门问题...")
    
    popular_questions = [
        {"question": "如何提高工作效率？", "category": "工作效率", "search_count": 150},
        {"question": "怎样管理时间？", "category": "时间管理", "search_count": 120},
        {"question": "如何克服拖延症？", "category": "个人成长", "search_count": 100},
        {"question": "怎么缓解工作压力？", "category": "心理健康", "search_count": 90},
        {"question": "如何建立好习惯？", "category": "习惯培养", "search_count": 85},
        {"question": "怎样提升沟通能力？", "category": "人际关系", "search_count": 80},
        {"question": "如何学会投资理财？", "category": "财务管理", "search_count": 75},
        {"question": "怎么保持工作生活平衡？", "category": "生活方式", "search_count": 70}
    ]
    
    for question in popular_questions:
        await conn.execute(
            """
            INSERT INTO popular_questions (question, category, search_count)
            VALUES ($1, $2, $3)
            """,
            question["question"],
            question["category"],
            question["search_count"]
        )
        print(f"  插入热门问题: {question['question']}")

async def main():
    """主函数"""
    try:
        print("开始导入样本数据...")
        conn = await create_connection()
        
        # 按顺序导入数据
        await import_podcasts(conn)
        await import_guests(conn)
        await import_episodes(conn)
        await import_popular_questions(conn)
        
        print("样本数据导入完成！")
        
        # 显示统计信息
        podcasts_count = await conn.fetchval("SELECT COUNT(*) FROM podcasts")
        episodes_count = await conn.fetchval("SELECT COUNT(*) FROM episodes")
        guests_count = await conn.fetchval("SELECT COUNT(*) FROM guests")
        
        print(f"""
数据统计：
- 播客数量: {podcasts_count}
- 播客集数: {episodes_count}
- 嘉宾数量: {guests_count}
        """)
        
        await conn.close()
        
    except Exception as e:
        print(f"导入数据时出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())