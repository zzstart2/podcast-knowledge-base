-- 播客解答器数据库设计
-- 创建数据库
CREATE DATABASE podcast_qa_db;
USE podcast_qa_db;

-- 播客表
CREATE TABLE podcasts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    category VARCHAR(100),
    language VARCHAR(10) DEFAULT 'zh',
    rss_url TEXT,
    official_website TEXT,
    cover_image TEXT,
    total_episodes INTEGER DEFAULT 0,
    avg_rating DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 播客单集表
CREATE TABLE episodes (
    id SERIAL PRIMARY KEY,
    podcast_id INTEGER REFERENCES podcasts(id) ON DELETE CASCADE,
    episode_number INTEGER,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    publish_date DATE,
    duration_minutes INTEGER,
    file_url TEXT,
    file_size BIGINT,
    content_summary TEXT,
    key_insights TEXT[], -- 核心观点数组
    problems_addressed TEXT[], -- 解决的问题数组
    target_audience VARCHAR(100),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('入门', '进阶', '专业')),
    quality_score DECIMAL(3,2), -- 内容质量评分
    listen_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 嘉宾表
CREATE TABLE guests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    company VARCHAR(255),
    bio TEXT,
    expertise_areas TEXT[], -- 专业领域
    social_links JSONB, -- 社交媒体链接
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 单集嘉宾关联表
CREATE TABLE episode_guests (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES episodes(id) ON DELETE CASCADE,
    guest_id INTEGER REFERENCES guests(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT '嘉宾', -- 嘉宾、主持人、对话者等
    UNIQUE(episode_id, guest_id)
);

-- 播客平台链接表
CREATE TABLE episode_links (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES episodes(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- apple_podcasts, spotify, xiaoyuzhou, etc.
    platform_name VARCHAR(100),
    url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 话题标签表
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 单集话题关联表
CREATE TABLE episode_topics (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES episodes(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 1.0, -- 相关度评分
    UNIQUE(episode_id, topic_id)
);

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    is_premium BOOLEAN DEFAULT FALSE,
    search_count_today INTEGER DEFAULT 0,
    last_search_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户搜索历史表
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    search_results JSONB, -- 搜索结果JSON
    clicked_episodes INTEGER[], -- 用户点击的剧集ID
    satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户收藏表
CREATE TABLE user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    episode_id INTEGER REFERENCES episodes(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, episode_id)
);

-- 热门问题表
CREATE TABLE popular_questions (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    search_count INTEGER DEFAULT 1,
    last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(100),
    recommended_episodes INTEGER[], -- 推荐的剧集ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引优化查询性能
CREATE INDEX idx_episodes_podcast_id ON episodes(podcast_id);
CREATE INDEX idx_episodes_publish_date ON episodes(publish_date);
CREATE INDEX idx_episodes_difficulty_level ON episodes(difficulty_level);
CREATE INDEX idx_episode_topics_episode_id ON episode_topics(episode_id);
CREATE INDEX idx_episode_topics_topic_id ON episode_topics(topic_id);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_created_at ON search_history(created_at);
CREATE INDEX idx_popular_questions_search_count ON popular_questions(search_count);

-- 创建全文搜索索引
CREATE INDEX idx_episodes_fulltext ON episodes USING gin(to_tsvector('chinese', title || ' ' || COALESCE(description, '') || ' ' || COALESCE(content_summary, '')));
CREATE INDEX idx_topics_fulltext ON topics USING gin(to_tsvector('chinese', name || ' ' || COALESCE(description, '')));

-- 插入初始数据
INSERT INTO topics (name, category, description) VALUES
('工作效率', '职场发展', '提高工作效率的方法和技巧'),
('时间管理', '个人成长', '如何更好地管理时间和提高生产力'),
('心理健康', '生活方式', '心理调适、压力管理、情绪管理'),
('职业规划', '职场发展', '职业发展路径和规划建议'),
('人际关系', '社交技能', '改善人际关系和沟通技巧'),
('创业经验', '商业思维', '创业心得和商业洞察'),
('学习方法', '个人成长', '高效学习和知识管理方法'),
('投资理财', '财务管理', '个人投资和财务管理建议'),
('健康生活', '生活方式', '健康饮食、运动和生活习惯'),
('科技趋势', '行业洞察', '最新科技发展和趋势分析');