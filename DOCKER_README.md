# Queqiao-arr Docker 部署指南

本文档介绍如何使用 Docker 和 Docker Compose 部署 Queqiao-arr。

## 📋 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [开发环境](#开发环境)
- [生产环境](#生产环境)
- [环境变量配置](#环境变量配置)
- [常用命令](#常用命令)
- [故障排查](#故障排查)

## 环境要求

- Docker >= 20.10
- Docker Compose >= 2.0
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

### 安装 Docker

#### Windows / macOS
下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

#### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/queqiao-arr.git
cd queqiao-arr
```

### 2. 配置环境变量
```bash
# Linux/macOS
cp .env.example .env

# Windows
copy .env.example .env
```

编辑 `.env` 文件，至少修改以下配置：
- `SECRET_KEY`: 使用 `openssl rand -hex 32` 生成
- `TMDB_API_KEY`: 从 [TMDB](https://www.themoviedb.org/settings/api) 获取

### 3. 启动服务

#### 开发环境
```bash
# Linux/macOS
bash scripts/start-dev.sh

# Windows
scripts\start-dev.bat
```

#### 生产环境
```bash
# Linux/macOS
bash scripts/start-prod.sh

# Windows
scripts\start-prod.bat
```

### 4. 访问应用
打开浏览器访问: http://localhost:8000

## 开发环境

开发环境提供热重载功能，适合本地开发调试。

### 启动开发环境

**仅后端服务:**
```bash
# Linux/macOS
bash scripts/start-dev.sh

# Windows
scripts\start-dev.bat

# 或直接使用 docker-compose
docker-compose -f docker-compose.dev.yml up
```

**后端 + 前端开发服务器:**
```bash
# Linux/macOS
bash scripts/start-dev.sh --with-frontend

# Windows
scripts\start-dev.bat --with-frontend

# 或直接使用 docker-compose
docker-compose -f docker-compose.dev.yml --profile frontend up
```

### 开发环境特性

- ✅ 代码热重载（修改代码自动重启）
- ✅ 详细的调试日志（DEBUG 级别）
- ✅ 源码挂载到容器（实时同步）
- ✅ 开发专用数据库（queqiao-dev.db）
- ✅ 较短的缓存时间（便于测试）
- ✅ 长 Token 过期时间（24小时）

### 访问地址

- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **前端开发服务器**: http://localhost:3000 (如果启用)

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.dev.yml logs -f

# 仅查看后端日志
docker-compose -f docker-compose.dev.yml logs -f queqiao-arr-dev

# 仅查看前端日志
docker-compose -f docker-compose.dev.yml logs -f frontend-dev
```

## 生产环境

生产环境使用优化的配置，适合部署到服务器。

### 启动生产环境

```bash
# Linux/macOS
bash scripts/start-prod.sh

# Windows
scripts\start-prod.bat

# 或直接使用 docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### 重新构建并启动

```bash
# Linux/macOS
bash scripts/start-prod.sh --build

# Windows
scripts\start-prod.bat --build

# 或直接使用 docker-compose
docker-compose -f docker-compose.prod.yml up -d --build
```

### 生产环境特性

- ✅ 多进程模式（4个 worker）
- ✅ 非 root 用户运行
- ✅ 健康检查
- ✅ 资源限制（CPU/内存）
- ✅ 自动重启
- ✅ 持久化数据卷
- ✅ 安全配置强制检查

### 停止服务

```bash
# Linux/macOS
bash scripts/stop.sh

# Windows
scripts\stop.bat

# 或直接使用 docker-compose
docker-compose -f docker-compose.prod.yml down
```

### 查看服务状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志

```bash
# 实时查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看最近100行日志
docker-compose -f docker-compose.prod.yml logs --tail=100
```

## 环境变量配置

### 必须配置的变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `SECRET_KEY` | JWT 密钥（生产环境必须修改） | `openssl rand -hex 32` |
| `TMDB_API_KEY` | TMDB API 密钥 | 从 TMDB 网站获取 |

### 可选配置的变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEBUG` | `false` | 调试模式 |
| `PORT` | `8000` | 服务端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `CACHE_TTL` | `3600` | 缓存时间（秒） |
| `HTTP_PROXY` | - | HTTP 代理 |
| `HTTPS_PROXY` | - | HTTPS 代理 |

完整的配置说明请参考 `.env.example` 文件。

### 生成安全密钥

```bash
# Linux/macOS
openssl rand -hex 32

# 或使用 Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

## 常用命令

### 查看运行的容器
```bash
docker ps
```

### 进入容器
```bash
# 开发环境
docker exec -it queqiao-arr-dev bash

# 生产环境
docker exec -it queqiao-arr-prod bash
```

### 查看容器日志
```bash
docker logs -f queqiao-arr-dev
docker logs -f queqiao-arr-prod
```

### 重启服务
```bash
# 开发环境
docker-compose -f docker-compose.dev.yml restart

# 生产环境
docker-compose -f docker-compose.prod.yml restart
```

### 完全清理（包括数据卷）
```bash
# ⚠️ 警告：这将删除所有数据！
docker-compose -f docker-compose.prod.yml down -v
```

### 更新镜像
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build
```

## 数据备份与恢复

### 备份数据
```bash
# 创建备份目录
mkdir -p backups

# 备份数据库
cp data/queqiao.db backups/queqiao-$(date +%Y%m%d-%H%M%S).db

# 或使用 Docker 卷备份
docker run --rm \
  -v queqiao-arr_queqiao-data:/source \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/data-$(date +%Y%m%d-%H%M%S).tar.gz -C /source .
```

### 恢复数据
```bash
# 停止服务
docker-compose -f docker-compose.prod.yml down

# 恢复数据库
cp backups/queqiao-20240101-120000.db data/queqiao.db

# 重启服务
docker-compose -f docker-compose.prod.yml up -d
```

## 故障排查

### 端口冲突
如果 8000 端口被占用，修改 `.env` 文件中的 `PORT` 变量：
```bash
PORT=9000
```

### 权限问题
```bash
# Linux/macOS: 修复文件权限
sudo chown -R $USER:$USER data logs

# 或使用 Docker 用户
docker exec -it queqiao-arr-prod chown -R app:app /app/runtime
```

### 查看详细错误
```bash
# 查看容器日志
docker-compose -f docker-compose.prod.yml logs --tail=100

# 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' queqiao-arr-prod
```

### 数据库锁定
```bash
# 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 等待几秒
sleep 5

# 重新启动
docker-compose -f docker-compose.prod.yml up -d
```

### 清理未使用的资源
```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 清理所有未使用的资源
docker system prune -a --volumes
```

## 性能优化

### 生产环境优化建议

1. **调整 worker 数量**（在 Dockerfile 中）：
   ```dockerfile
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
   ```
   建议设置为 CPU 核心数的 2-4 倍。

2. **配置资源限制**（在 docker-compose.prod.yml 中）：
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

3. **使用反向代理**：
   建议在生产环境前面配置 Nginx 或 Traefik。

## 更多信息

- [项目 README](./README.md)
- [技术方案文档](./docs/Queqiao-arr技术方案与开发计划书.md)
- [开发任务清单](./TODO.md)

## 问题反馈

如遇到问题，请在 [GitHub Issues](https://github.com/yourusername/queqiao-arr/issues) 提交。

