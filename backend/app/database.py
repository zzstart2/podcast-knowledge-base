import databases
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# 数据库连接
database = databases.Database(settings.DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(settings.DATABASE_URL)

# 数据库表定义
Base = declarative_base()

# 播客表
podcasts_table = sqlalchemy.Table(
    "podcasts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("author", sqlalchemy.String(255)),
    sqlalchemy.Column("category", sqlalchemy.String(100)),
    sqlalchemy.Column("language", sqlalchemy.String(10), default="zh"),
    sqlalchemy.Column("rss_url", sqlalchemy.Text),
    sqlalchemy.Column("official_website", sqlalchemy.Text),
    sqlalchemy.Column("cover_image", sqlalchemy.Text),
    sqlalchemy.Column("total_episodes", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("avg_rating", sqlalchemy.DECIMAL(3,2)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now())
)

# 单集表
episodes_table = sqlalchemy.Table(
    "episodes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("podcast_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("podcasts.id")),
    sqlalchemy.Column("episode_number", sqlalchemy.Integer),
    sqlalchemy.Column("title", sqlalchemy.String(500), nullable=False),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("publish_date", sqlalchemy.Date),
    sqlalchemy.Column("duration_minutes", sqlalchemy.Integer),
    sqlalchemy.Column("file_url", sqlalchemy.Text),
    sqlalchemy.Column("content_summary", sqlalchemy.Text),
    sqlalchemy.Column("key_insights", sqlalchemy.ARRAY(sqlalchemy.Text)),
    sqlalchemy.Column("problems_addressed", sqlalchemy.ARRAY(sqlalchemy.Text)),
    sqlalchemy.Column("target_audience", sqlalchemy.String(100)),
    sqlalchemy.Column("difficulty_level", sqlalchemy.String(20)),
    sqlalchemy.Column("quality_score", sqlalchemy.DECIMAL(3,2)),
    sqlalchemy.Column("listen_count", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now())
)

# 嘉宾表
guests_table = sqlalchemy.Table(
    "guests",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("title", sqlalchemy.String(255)),
    sqlalchemy.Column("company", sqlalchemy.String(255)),
    sqlalchemy.Column("bio", sqlalchemy.Text),
    sqlalchemy.Column("expertise_areas", sqlalchemy.ARRAY(sqlalchemy.Text)),
    sqlalchemy.Column("social_links", sqlalchemy.JSON),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now())
)

# 用户表
users_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(100), unique=True),
    sqlalchemy.Column("email", sqlalchemy.String(255), unique=True),
    sqlalchemy.Column("password_hash", sqlalchemy.String(255)),
    sqlalchemy.Column("is_premium", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("search_count_today", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("last_search_date", sqlalchemy.Date),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now())
)

# 搜索历史表
search_history_table = sqlalchemy.Table(
    "search_history",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("question", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("search_results", sqlalchemy.JSON),
    sqlalchemy.Column("clicked_episodes", sqlalchemy.ARRAY(sqlalchemy.Integer)),
    sqlalchemy.Column("satisfaction_rating", sqlalchemy.Integer),
    sqlalchemy.Column("feedback", sqlalchemy.Text),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now())
)