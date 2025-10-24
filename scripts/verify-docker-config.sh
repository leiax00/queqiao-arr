#!/bin/bash
# Docker 配置验证脚本

set -e

echo "========================================="
echo "  Docker 配置验证"
echo "========================================="
echo ""

# 检查 Docker 是否安装
echo "1. 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo "✅ Docker 环境正常"
echo ""

# 验证 Dockerfile
echo "2. 验证 Dockerfile..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile 不存在"
    exit 1
fi
echo "✅ Dockerfile 存在"
echo ""

# 验证 docker-compose 配置文件
echo "3. 验证 docker-compose 配置..."

if [ -f "docker-compose.dev.yml" ]; then
    echo "   检查开发环境配置..."
    docker-compose -f docker-compose.dev.yml config --quiet
    echo "   ✅ 开发环境配置正常"
else
    echo "   ❌ docker-compose.dev.yml 不存在"
    exit 1
fi

# 生产环境需要 .env 文件
if [ -f ".env" ]; then
    echo "   检查生产环境配置..."
    docker-compose -f docker-compose.prod.yml config --quiet
    echo "   ✅ 生产环境配置正常"
else
    echo "   ⚠️  .env 文件不存在，跳过生产环境配置检查"
fi

echo "   检查默认配置..."
if [ -f ".env" ]; then
    docker-compose config --quiet
    echo "   ✅ 默认配置正常"
else
    echo "   ⚠️  .env 文件不存在，跳过默认配置检查"
fi

echo ""

# 检查必要文件
echo "4. 检查必要文件..."
files=(
    ".dockerignore"
    ".env.example"
    "scripts/start-dev.sh"
    "scripts/start-prod.sh"
    "scripts/stop.sh"
)

all_exists=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file 不存在"
        all_exists=false
    fi
done

if [ "$all_exists" = false ]; then
    exit 1
fi

echo ""
echo "========================================="
echo "✅ 所有配置验证通过！"
echo "========================================="
echo ""
echo "💡 下一步:"
echo "   1. 复制环境变量: cp .env.example .env"
echo "   2. 编辑 .env 文件配置必要的环境变量"
echo "   3. 运行开发环境: bash scripts/start-dev.sh"
echo "   4. 运行生产环境: bash scripts/start-prod.sh"
echo ""

