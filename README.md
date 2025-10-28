# Queqiao-arr

<div align="center">

![Queqiao-arr Logo](/frontend/public/logo.svg)

**中文内容自动化下载代理服务**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/Vue-3.3+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Docker Build](https://github.com/leiax00/queqiao-arr/actions/workflows/docker.yml/badge.svg)](https://github.com/leiax00/queqiao-arr/actions/workflows/docker.yml)
[![Release](https://github.com/leiax00/queqiao-arr/actions/workflows/release.yml/badge.svg)](https://github.com/leiax00/queqiao-arr/actions/workflows/release.yml)
[![GitHub release](https://img.shields.io/github/v/release/leiax00/queqiao-arr)](https://github.com/leiax00/queqiao-arr/releases/latest)
[![Docker Pulls](https://img.shields.io/docker/pulls/leiax00/queqiao-arr)](https://hub.docker.com/r/leiax00/queqiao-arr)

</div>

## 📖 项目介绍

Queqiao-arr 是一个专为中文内容优化的自动化下载代理服务，作为 Sonarr 和 Prowlarr 的桥梁，提供智能的中文媒体内容管理和下载解决方案。

### ✨ 核心特性

- 🎯 **中文优化**: 专门针对中文内容的智能识别和处理
- 🔄 **自动代理**: 无缝集成 Sonarr 和 Prowlarr 工作流
- 🎨 **现代界面**: 基于 Vue 3 的响应式管理界面
- 📱 **移动友好**: 完美适配桌面和移动设备
- 🌙 **主题切换**: 支持明暗主题自动切换
- 🐳 **容器化**: 完整的 Docker 部署方案
- ⚡ **高性能**: 基于 FastAPI 的高性能后端服务

### 🏗️ 技术架构

**后端技术栈:**
- **FastAPI**: 现代、高性能的 Python Web 框架
- **SQLAlchemy**: 强大的 ORM 数据库操作
- **SQLite**: 轻量级嵌入式数据库
- **Pydantic**: 数据验证和设置管理

**前端技术栈:**
- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全的 JavaScript 超集
- **Element Plus**: 企业级 Vue 3 组件库
- **Tailwind CSS**: 原子化 CSS 框架
- **Pinia**: Vue 3 官方状态管理
- **Vite**: 极速前端构建工具

## 🚀 快速开始

### 方式一：Docker 部署 (推荐)

```bash
# 克隆项目
git clone https://github.com/your-username/queqiao-arr.git
cd queqiao-arr

# 复制并配置环境变量
cp .env.example .env
# 编辑 .env 文件，至少修改 SECRET_KEY 和 TMDB_API_KEY

# 启动生产环境
bash scripts/start-prod.sh
# Windows: scripts\start-prod.bat

# 或启动开发环境
bash scripts/start-dev.sh
# Windows: scripts\start-dev.bat

# 访问应用
# 生产环境: http://localhost:8000
# 开发环境后端: http://localhost:8000
# 开发环境前端: http://localhost:3000
```

### 方式二：本地开发

#### 环境要求

- **Python**: 3.11+
- **Node.js**: 18+
- **Git**: 最新版本

#### 后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate
# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端服务

```bash
# 新开终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问前端: http://localhost:3000
```

## 🔧 开发环境搭建

### 1. 克隆项目

```bash
git clone https://github.com/your-username/queqiao-arr.git
cd queqiao-arr
```

### 2. 环境配置

```bash
# 复制环境变量模板（后端）
cp backend/.env.example backend/.env

# 编辑环境变量 (根据需要修改)
# DEBUG=true
# SECRET_KEY=your-super-secret-key
# DATABASE_URL=sqlite+aiosqlite:///./data/queqiao.db
```

### 3. 安装开发工具（可选）

```bash
# 前端依赖安装
cd frontend && npm install
# 返回项目根目录
cd ..
```

### 4. 启动开发服务

```bash
# 启动后端 (终端 1)
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload

# 启动前端 (终端 2)
cd frontend
npm install
npm run dev
```

### 5. 访问应用

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档(开发模式)**: http://localhost:8000/api/docs
- **交互式 API(开发模式)**: http://localhost:8000/api/redoc

## 🐳 Docker 部署

项目提供了完整的 Docker 部署方案，支持开发和生产两种环境。

### 快速启动

**开发环境** (包含热重载)：
```bash
# Linux/macOS
bash scripts/start-dev.sh

# Windows
scripts\start-dev.bat

# 或使用 docker-compose
docker-compose -f docker-compose.dev.yml up
```

**生产环境**：
```bash
# Linux/macOS
bash scripts/start-prod.sh

# Windows
scripts\start-prod.bat

# 或使用 docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### 常用命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 停止服务
bash scripts/stop.sh  # Linux/macOS
scripts\stop.bat      # Windows

# 健康检查
curl -f http://localhost:8000/api/v1/health
```

### Docker 环境特性对比

| 特性 | 开发环境 | 生产环境 |
|------|---------|---------|
| 热重载 | ✅ | ❌ |
| 源码挂载 | ✅ | ❌ |
| 调试日志 | ✅ | ❌ |
| 多进程 | ❌ | ✅ |
| 健康检查 | ❌ | ✅ |
| 资源限制 | ❌ | ✅ |
| 安全配置 | ❌ | ✅ |

📖 **完整的 Docker 部署文档**: 请参阅 [DOCKER_README.md](./DOCKER_README.md)

## 📚 API 文档

### 在线文档

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 主要 API 端点

```
# 健康检查
GET /api/v1/health

# 用户认证
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/auth/me

# 配置管理
GET  /api/v1/config
PUT  /api/v1/config/sonarr
PUT  /api/v1/config/prowlarr
PUT  /api/v1/config/proxy

# 系统管理
GET  /api/v1/system/status
GET  /api/v1/system/logs
```

## 🤝 贡献指南

### 开发流程

1. **Fork 项目** 到你的 GitHub 账户
2. **创建特性分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'feat: add amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **提交 Pull Request**

### 提交规范

项目使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 添加测试
- `chore`: 其他更改

**范围 (scope)**:
- `backend`: 后端相关
- `frontend`: 前端相关
- `api`: API 相关
- `docker`: Docker 相关
- `docs`: 文档相关

**示例**:
```bash
feat(backend): 添加用户认证功能
fix(frontend): 修复移动端侧边栏显示问题
docs: 更新 README 部署说明
```

### 代码质量

项目建议遵循代码质量规范（当前未强制启用钩子）：

- **后端（可选）**: Black (格式化) + Ruff (检查) + MyPy (类型检查)
- **前端**: ESLint (检查) + Vue TSC (类型检查)
- 如需提交前校验，可按需配置 commitlint/husky/lint-staged（可选）

### 本地测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test

# 类型检查
npm run type-check

# 代码格式化
npm run lint
```

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能 Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [Tailwind CSS](https://tailwindcss.com/) - 原子化 CSS 框架

## 📞 联系方式

- **项目主页**: https://github.com/leiax00/queqiao-arr
- **问题反馈**: https://github.com/leiax00/queqiao-arr/issues
- **功能建议**: https://github.com/leiax00/queqiao-arr/discussions

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐ Star!**

Made with ❤️ by [Leiax00](https://github.com/leiax00)

</div>