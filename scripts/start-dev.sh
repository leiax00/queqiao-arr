#!/bin/bash
# Queqiao-arr 开发环境启动脚本

set -e

echo "========================================="
echo "  Queqiao-arr 开发环境启动"
echo "========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未检测到 Docker，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未检测到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 检查是否存在 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    if [ -f ".env.example" ]; then
        echo "📝 正在从 .env.example 复制配置..."
        cp .env.example .env
        echo "✅ .env 文件已创建"
        echo "💡 提示: 请编辑 .env 文件配置您的环境变量"
    else
        echo "❌ 错误: .env.example 文件也不存在"
        exit 1
    fi
    echo ""
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data logs
echo "✅ 目录创建完成"
echo ""

# 启动服务
echo "🚀 启动开发环境..."
echo ""

# 判断是否需要前端服务
if [ "$1" == "--with-frontend" ] || [ "$1" == "-f" ]; then
    echo "启动模式: 后端 + 前端开发服务器"
    docker-compose -f docker-compose.dev.yml --profile frontend up --build
else
    echo "启动模式: 仅后端服务"
    echo "💡 提示: 使用 --with-frontend 或 -f 参数同时启动前端开发服务器"
    docker-compose -f docker-compose.dev.yml up --build
fi

