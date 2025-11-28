# AGENT.md

## 项目概述

**Queqiao-arr** 是一个针对中文内容优化的自动化下载代理服务，作为 Sonarr 和 Prowlarr 之间的桥梁。它提供智能的中文媒体内容管理，具有增强的标题解析、通过 TMDB 的中文别名解析以及改进的搜索功能。

## 架构

**后端**: Python/FastAPI 异步架构，SQLAlchemy 2.0+，JWT 认证
**前端**: Vue 3 + TypeScript，Element Plus UI，Tailwind CSS
**数据库**: SQLite 异步支持
**外部服务**: TMDB、Prowlarr、Sonarr 通过统一客户端架构

## 开发命令

### Docker 开发（推荐）
```bash
# 启动开发环境（包含前端）
bash scripts/start-dev.sh --with-frontend

# 生产部署
docker-compose -f docker-compose.prod.yml up -d
```

### 后端开发
```bash
cd backend
pytest                           # 运行测试
pytest --cov=app                 # 测试及覆盖率
black app/                       # 代码格式化
ruff check app/                  # 代码检查
mypy app/                        # 类型检查
uvicorn app.main:app --reload    # 开发服务器
```

### 前端开发
```bash
cd frontend
npm run dev                      # 开发服务器
npm run build                    # 生产构建
npm run lint                     # 代码检查
npm run type-check              # 类型检查
```

## 核心架构模式

### 外部服务客户端
所有外部服务客户端（TMDB、Prowlarr、Sonarr）都遵循 `backend/app/services/clients/base.py` 中的基础客户端模式：
```python
class ExternalServiceClient:
    def __init__(self, base_url: str, api_key: str, proxies: Dict[str, str], timeout: int)
    def _get(self, endpoint: str, params: Dict) -> Tuple[bool, Any]
    def check_status(self) -> Tuple[bool, str]
```

### API 响应模式
一致的元组返回模式：`(success: bool, data_or_error: Any)`

### 配置管理
使用 Pydantic 设置的加密配置存储。必需环境变量：
- `SECRET_KEY`: 生产环境使用 `openssl rand -hex 32` 生成
- `TMDB_API_KEY`: 从 https://www.themoviedb.org/settings/api 获取
- `DATABASE_URL`: SQLite 路径（有默认值）

### 前端组合式函数
Composition API 使用 `use*` 命名约定的响应式功能。

## 项目结构
```
backend/app/
├── api/endpoints/     # API 路由处理器
├── api/schemas/       # Pydantic 模型
├── core/             # 配置与安全
├── db/               # 数据库模型与 CRUD
├── models/           # SQLAlchemy 模型
├── services/clients/ # 外部服务客户端
└── utils/            # 工具函数与助手

frontend/src/
├── api/              # API 客户端函数
├── components/       # Vue 组件
├── composables/      # Composition API 函数
├── layouts/          # 布局组件
├── stores/           # Pinia 状态管理
└── views/            # 页面组件
```

## 当前开发状态

**已完成**: 用户认证、配置管理、TMDB 客户端、系统字典、Docker 设置
**进行中**: Prowlarr 搜索客户端（B-05 任务）
**待开发**: 标题解析器（B-06）、Torznab XML 生成（B-07）、自动化引擎（B-08）

## 代码规范

**Python**: 4 空格缩进，Black 格式化，类型提示，snake_case 命名
**TypeScript/Vue**: 2 空格缩进，ESLint + Prettier，camelCase/PascalCase，Composition API
**提交**: Conventional Commits 中文提交信息，常见作用域：backend, frontend, api, docker, docs
**分支策略**: `main`（稳定），`develop`（集成），`feature/*`，`fix/*`

## 测试指南

**后端测试**:
- 使用 Pytest 框架，文件命名：`backend/tests/test_*.py`
- 覆盖率目标：整体 ≥ 70%，关键模块（认证、配置、客户端、路由）≥ 80%
- 优先覆盖关键路径：认证、配置、外部客户端、API 端点
- 异步用例使用 `pytest-asyncio`
- 使用 `--cov` 生成覆盖率报告

**前端测试**:
- 当前不要求编写测试用例
- 专注于手动测试、代码检查和类型检查

## 提交与 Pull Request 规范

**提交规范**:
- 遵循 Conventional Commits：`feat|fix|docs|style|refactor|test|chore(scope): message`
- 常见作用域：`backend`、`frontend`、`api`、`docker`、`docs`
- 提交信息必须使用中文

**PR 要求**:
- 清晰描述、关联 Issue、变更范围
- UI 变更附截图
- 本地通过后端测试/质量检查
- 前端 Lint/类型检查与构建通过

## 分支策略

- **默认分支**: `develop`（集成分支，默认协作基线）
- **主分支**: `main`（稳定可发布，仅在发布时更新）
- **特性分支**: 从 `develop` 切出 `feature/<short-name>`，完成后提 PR 合入 `develop`
- **修复分支**: 从 `develop` 切出 `fix/<short-name>`，完成后提 PR 合入 `develop`
- **紧急热修**: 从 `main` 切出 `hotfix/<short-name>`，合入 `main` 后回合 `develop`

## 发布与版本

**版本控制**: 语义化版本 `MAJOR.MINOR.PATCH`
**发布流程**: `develop` 达到发布标准 → 创建 `develop → main` 的发布 PR → 合并后打标签 `vX.Y.Z` → 触发 CI/CD

## 重要注意事项

- **中文内容优先**: 所有功能优先考虑中文语言支持
- **异步模式**: 后端广泛使用 async/await 进行外部服务调用
- **错误处理**: 整个代码库中使用一致的元组返回模式
- **测试**: 后端目标 70% 覆盖率，前端专注于手动测试
- **安全**: 敏感配置在数据库中加密存储
- **环境配置**: 复制 `backend/.env.example` → `backend/.env`，严禁提交密钥