#!/bin/bash

# GitHub部署脚本

echo "🎧 播客解答器 - GitHub部署脚本"
echo "=================================="

# 检查是否有GitHub仓库URL参数
if [ -z "$1" ]; then
    echo "❌ 错误：请提供GitHub仓库URL"
    echo "用法: ./deploy-to-github.sh https://github.com/用户名/podcast-qa-system.git"
    echo ""
    echo "📋 步骤："
    echo "1. 在GitHub上创建新仓库 'podcast-qa-system'"
    echo "2. 复制仓库的HTTPS克隆链接"
    echo "3. 运行: ./deploy-to-github.sh 仓库链接"
    exit 1
fi

REPO_URL=$1
echo "🔗 目标仓库: $REPO_URL"

# 检查Git状态
if [ ! -d ".git" ]; then
    echo "❌ 错误：当前目录不是Git仓库"
    exit 1
fi

# 添加远程仓库
echo "📡 添加远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 发现未提交的更改，正在添加..."
    git add .
    git commit -m "🔄 更新部署配置"
fi

# 推送到GitHub
echo "🚀 推送代码到GitHub..."
git push -u origin master

echo ""
echo "✅ 代码已成功推送到GitHub!"
echo ""
echo "📋 下一步操作："
echo "=================================="
echo "1. 访问你的GitHub仓库"
echo "2. 点击 Settings（设置）"
echo "3. 滚动到 Pages 部分"
echo "4. Source选择: Deploy from a branch"
echo "5. Branch选择: master"
echo "6. Folder选择: / (root)"
echo "7. 点击 Save 保存"
echo ""
echo "⏳ 等待几分钟后，你的应用将在以下地址可用："

# 从仓库URL提取用户名和仓库名
if [[ $REPO_URL =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
    USERNAME="${BASH_REMATCH[1]}"
    REPO_NAME="${BASH_REMATCH[2]}"
    echo "🌐 https://${USERNAME}.github.io/${REPO_NAME}/"
else
    echo "🌐 https://用户名.github.io/仓库名/"
fi

echo ""
echo "📖 查看完整部署指南: cat DEPLOY.md"
echo "🎉 播客解答器即将上线！"