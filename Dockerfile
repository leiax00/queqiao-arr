# ==================== 前端构建阶段 ====================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# 配置npm国内镜像源（加速国内构建）
RUN npm config set registry https://registry.npmmirror.com

# 复制package文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci

# 复制前端源码
COPY frontend/ .

# 构建前端
RUN npm run build

# ==================== 开发环境基础镜像 ====================
FROM python:3.11-slim as base

WORKDIR /app

# 配置apt国内镜像源（加速国内构建）
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 配置pip国内镜像源并升级pip
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com

# ==================== 开发环境 ====================
FROM base as development

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖（包含开发工具）
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p /app/runtime/data /app/runtime/logs /app/static

# 暴露端口
EXPOSE 8000

# 开发环境使用热重载
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==================== 生产环境 ====================
FROM base as production

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖（仅生产依赖）
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y pytest pytest-asyncio black ruff mypy

# 复制后端代码
COPY backend/ .

# 复制前端构建结果
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建必要的目录
RUN mkdir -p /app/runtime/data /app/runtime/logs

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 生产环境启动
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
