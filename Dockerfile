# 多阶段构建
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# 配置npm国内镜像源（加速国内构建）
RUN npm config set registry https://registry.npmmirror.com

COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

# Python后端
FROM python:3.11-slim

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

# 复制Python依赖并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制前端构建结果
COPY --from=frontend-builder /app/backend/static ./static

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
