#!/bin/bash
# Queqiao-arr 生产环境启动脚本

set -e

echo "========================================="
echo "  Queqiao-arr 生产环境启动"
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
    echo "❌ 错误: 未找到 .env 文件"
    echo "💡 提示: 请从 .env.example 复制并配置您的环境变量"
    echo "   命令: cp .env.example .env"
    exit 1
fi

# 检查SECRET_KEY是否配置
if grep -q "please-change-this-secret-key-in-production" .env; then
    echo "⚠️  警告: 检测到默认的 SECRET_KEY"
    echo "❌ 错误: 生产环境必须配置安全的 SECRET_KEY"
    echo "💡 提示: 使用以下命令生成随机密钥:"
    echo "   openssl rand -hex 32"
    exit 1
fi

echo "✅ 环境变量配置检查通过"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data logs
echo "✅ 目录创建完成"
echo ""

# 启动服务
echo "🚀 启动生产环境..."
echo ""

if [ "$1" == "--build" ] || [ "$1" == "-b" ]; then
    echo "启动模式: 重新构建并启动"
    docker-compose -f docker-compose.prod.yml up -d --build
else
    echo "启动模式: 使用现有镜像启动"
    echo "💡 提示: 使用 --build 或 -b 参数重新构建镜像"
    docker-compose -f docker-compose.prod.yml up -d
fi

echo ""
echo "========================================="
echo "✅ 服务启动成功！"
echo "========================================="
echo ""
echo "📊 查看服务状态:"
echo "   docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "📝 查看服务日志:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 停止服务:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "🌐 访问地址:"
echo "   http://localhost:8000"
echo ""

