from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from dotenv import load_dotenv

from app.database import database, engine
from app.models import metadata
from app.routers import search, podcasts, admin, users
from app.core.config import settings

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="播客解答器 API",
    description="基于问题匹配的播客推荐系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接事件
@app.on_event("startup")
async def startup():
    await database.connect()
    # 创建数据库表
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# 路由注册
app.include_router(search.router, prefix="/api/v1/search", tags=["搜索"])
app.include_router(podcasts.router, prefix="/api/v1/podcasts", tags=["播客"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理"])

# 根路径
@app.get("/")
async def root():
    return {
        "message": "播客解答器 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health_check():
    try:
        # 检查数据库连接
        await database.fetch_one("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )