#!/bin/bash

# 播客解答器快速启动脚本

set -e

echo "🎧 播客解答器 - 快速启动脚本"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：请先安装Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 复制环境变量配置文件..."
        cp .env.example .env
        echo "⚠️  请编辑 .env 文件，设置你的 OpenAI API Key"
        echo "   OPENAI_API_KEY=sk-your-key-here"
        read -p "按 Enter 继续，或按 Ctrl+C 退出去设置API Key..."
    else
        echo "❌ 错误：找不到环境配置文件"
        exit 1
    fi
fi

# 启动服务
echo "🚀 启动Docker服务..."
docker-compose up -d postgres redis elasticsearch

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 检查数据库连接
echo "🔍 检查数据库连接..."
until docker-compose exec -T postgres pg_isready -U postgres; do
    echo "   数据库还未就绪，继续等待..."
    sleep 2
done

echo "✅ 数据库已启动"

# 运行数据库初始化
echo "📊 初始化数据库..."
docker-compose exec -T postgres psql -U postgres -d podcast_qa_db -f /docker-entrypoint-initdb.d/01-schema.sql

# 导入样本数据
echo "📥 导入样本数据..."
cd scripts
python3 -m pip install asyncpg > /dev/null 2>&1 || true
python3 sample_data_importer.py
cd ..

# 启动后端服务
echo "🔧 启动后端API..."
docker-compose up -d backend

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 10

# 检查后端健康状态
echo "🔍 检查后端服务..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "   后端服务还未就绪，继续等待..."
    sleep 3
done

echo "✅ 后端服务已启动"

# 构建并启动前端
echo "🎨 构建前端应用..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

if [ ! -d "build" ]; then
    echo "🔨 构建前端..."
    npm run build
fi

# 启动前端开发服务器
echo "🚀 启动前端服务..."
npm start &

cd ..

# 显示完成信息
echo ""
echo "🎉 播客解答器启动成功！"
echo "=================================="
echo "📍 服务地址："
echo "   前端应用: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "📊 数据库信息："
echo "   PostgreSQL: localhost:5432"
echo "   Redis:      localhost:6379"
echo "   Elasticsearch: localhost:9200"
echo ""
echo "💡 使用提示："
echo "   1. 在前端页面输入问题进行测试"
echo "   2. 查看API文档了解接口详情"
echo "   3. 使用scripts目录下的工具管理数据"
echo ""
echo "🛠️  开发命令："
echo "   停止所有服务: docker-compose down"
echo "   查看日志:     docker-compose logs -f"
echo "   重启后端:     docker-compose restart backend"
echo ""

# 等待用户输入
read -p "按 Enter 键打开浏览器访问应用..."

# 尝试打开浏览器
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v start &> /dev/null; then
    start http://localhost:3000
else
    echo "请手动在浏览器中访问: http://localhost:3000"
fi