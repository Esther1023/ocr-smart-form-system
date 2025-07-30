#!/bin/bash

# GitHub仓库设置脚本
# 用于将OCR项目推送到GitHub

echo "🚀 OCR智能表单系统 - GitHub发布脚本"
echo "================================================"

# 检查是否提供了GitHub仓库URL
if [ -z "$1" ]; then
    echo "❌ 请提供GitHub仓库URL"
    echo ""
    echo "使用方法:"
    echo "  ./setup_github.sh https://github.com/YOUR_USERNAME/REPO_NAME.git"
    echo ""
    echo "📝 步骤:"
    echo "1. 在GitHub创建新仓库"
    echo "2. 复制仓库URL"
    echo "3. 运行此脚本"
    exit 1
fi

GITHUB_URL=$1

echo "📋 检查Git状态..."
git status

echo ""
echo "🔗 配置GitHub远程仓库..."
echo "GitHub URL: $GITHUB_URL"

# 添加GitHub作为新的远程仓库
if git remote get-url github > /dev/null 2>&1; then
    echo "⚠️  GitHub远程仓库已存在，更新URL..."
    git remote set-url github $GITHUB_URL
else
    echo "➕ 添加GitHub远程仓库..."
    git remote add github $GITHUB_URL
fi

echo ""
echo "📤 推送到GitHub..."

# 推送到GitHub
if git push github master; then
    echo ""
    echo "🎉 成功推送到GitHub!"
    echo ""
    echo "📝 下一步:"
    echo "1. 访问您的GitHub仓库确认代码已上传"
    echo "2. 前往Railway/Render等平台部署"
    echo "3. 连接GitHub仓库进行自动部署"
    echo ""
    echo "🔗 部署平台链接:"
    echo "- Railway: https://railway.app"
    echo "- Render: https://render.com"
    echo "- Vercel: https://vercel.com"
else
    echo ""
    echo "❌ 推送失败，请检查:"
    echo "1. GitHub仓库URL是否正确"
    echo "2. 是否有推送权限"
    echo "3. 网络连接是否正常"
    echo ""
    echo "🔧 手动推送命令:"
    echo "git remote add github $GITHUB_URL"
    echo "git push github master"
fi

echo ""
echo "📊 当前远程仓库:"
git remote -v
