# Repository Guidelines

## 项目结构与模块组织
- 根目录：Docker 配置、`scripts/`、`docs/`、本指南。
- 后端：`backend/app/`（FastAPI + SQLAlchemy），测试位于 `backend/tests/`。
- 前端：`frontend/src/`（Vue 3 + TypeScript，Tailwind，Element Plus）。
- 常用脚本：`scripts/start-dev.*`、`scripts/start-prod.*`（开发/生产启动）。

## 构建、测试与开发命令
- 后端依赖：`cd backend && pip install -r requirements.txt`（Python 3.11+）。
- 后端开发：`cd backend && uvicorn app.main:app --reload`。
- 后端质量：`black app/`、`ruff check app/`、`mypy app/`。
- 后端测试：`cd backend && pytest`（覆盖率：`pytest --cov=app`）。
- 前端开发：`cd frontend && npm install && npm run dev`。
- 前端构建：`cd frontend && npm run build`（Vite，含 `vue-tsc` 类型检查）。
- 前端校验：`cd frontend && npm run lint`、`npm run type-check`。
- Docker 开发：`docker-compose -f docker-compose.dev.yml up` 或执行 `scripts/start-dev.*`。
- Docker 生产：`docker-compose -f docker-compose.prod.yml up -d` 或执行 `scripts/start-prod.*`。

## 代码风格与命名规范
- Python：4 空格缩进；使用 Black 格式化；模块/函数用 `snake_case`，类用 `PascalCase`。
- TypeScript/Vue：2 空格缩进；ESLint + Prettier；变量/函数用 `camelCase`。
- Vue SFC 文件名使用 `PascalCase`（例：`ConfigFormCard.vue`）。
- 组合式函数以 `use*` 命名（例：`src/composables/useTmdbConfig.ts`）。
- 后端 API 位于 `backend/app/api/endpoints/`，统一前缀 `/api/v1/*`。

## 测试指南
- 框架：后端使用 Pytest，文件命名：`backend/tests/test_*.py`。
- 优先覆盖关键路径：认证、配置、外部客户端、API 端点；异步用例使用 `pytest-asyncio`。
- 使用 `--cov` 生成覆盖率报告，提交前补齐核心分支用例。
 - 覆盖率目标：整体 ≥ 70%，关键模块（认证、配置、客户端、路由）≥ 80%（当前为目标值，CI 暂不强制校验）。
- 前端当前不要求编写测试用例。

## 提交与 Pull Request 规范
- 提交遵循 Conventional Commits：`feat|fix|docs|style|refactor|test|chore(scope): message`。
- 常见 scope：`backend`、`frontend`、`api`、`docker`、`docs`。
- PR 要求：清晰描述、关联 Issue、变更范围、UI 变更附截图；本地通过后端测试/质量检查、前端 Lint/类型检查与构建。

## 分支策略
- 默认分支：建议将仓库默认分支设置为 `develop`（需在 GitHub 仓库 Settings → Branches 中配置）。
- 主分支：`main`（稳定可发布，仅在发布时更新）。
- 开发分支：`develop`（集成分支，默认协作基线）。
- 特性分支：从 `develop` 切出 `feature/<short-name>`，完成后提 PR 合入 `develop`。
- 修复分支：从 `develop` 切出 `fix/<short-name>`，完成后提 PR 合入 `develop`。
- 紧急热修：从 `main` 切出 `hotfix/<short-name>`，合入 `main` 后回合 `develop`。
- PR 目标分支：日常功能/修复均指向 `develop`；发布专用 PR 使用 `develop → main`。

## 发布与版本
- 语义化版本：`MAJOR.MINOR.PATCH`。
- 发布流程：`develop` 达到发布标准 → 创建 `develop → main` 的发布 PR → 合并后打标签 `vX.Y.Z` → 触发 CI/CD（构建镜像与 Release）。
- 变更记录：如维护 `CHANGELOG.md`，请在发布前更新。

## Issue 与 PR 模板
- 位置建议：`.github/ISSUE_TEMPLATE/` 与 `.github/pull_request_template.md`（如未创建，按以下要点撰写）。
- Issue 要点：问题/需求概述、复现步骤或动机、期望行为、日志/截图、环境信息。
- PR 清单：关联 Issue、变更说明与影响范围、是否破坏性变更、后端测试通过（含覆盖率）、前端构建与 Lint 通过、UI 截图（如有）、文档更新（如适用）。

## 安全与配置提示
- 复制并编辑 `backend/.env.example` → `backend/.env`；严禁提交密钥。
- 关键配置：`SECRET_KEY`、外部 API Key（如 TMDB）。
- 应用启动会创建 `runtime/logs`、`runtime/data`；在容器/宿主机上确保可写。

## Agent 指南（中文沟通约定）
- 默认语言：所有对话、代码评审意见、Issue/PR 描述与项目文档均使用中文。
- 源代码：标识符仍使用英文（遵循生态惯例与工具链兼容性）；注释中文优先、保持简洁准确。
- 提交信息：支持中文，遵循 Conventional Commits 结构（type(scope): subject）。
- 模板：Issue/PR 模板已提供中文版本，按模板填写即可。
