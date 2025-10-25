#!/bin/bash
# Queqiao-arr 停止脚本

echo "停止 Queqiao-arr 服务..."
echo ""

# 停止所有可能运行的服务
if [ -f "docker-compose.dev.yml" ]; then
    echo "停止开发环境..."
    docker-compose -f docker-compose.dev.yml --profile frontend down 2>/dev/null || true
fi

if [ -f "docker-compose.prod.yml" ]; then
    echo "停止生产环境..."
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
fi

if [ -f "docker-compose.yml" ]; then
    echo "停止默认环境..."
    docker-compose down 2>/dev/null || true
fi

echo ""
echo "✅ 所有服务已停止"

