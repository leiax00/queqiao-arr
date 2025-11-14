# Changelog

本项目遵循 Keep a Changelog 规范，并使用语义化版本（Semantic Versioning）。

## [Unreleased]

### Added
- 初始化变更日志与 Issue/PR 模板
- 文档：贡献指南（AGENTS.md）

### Changed
- 分支策略：采用 `develop` 作为日常开发基线，发布时合入 `main`

### Fixed
- N/A

### Removed
- N/A

## [0.1.0] - YYYY-MM-DD

项目初始版本（示例占位）。

## [1.0.0] - 2025-11-14

### Added
- 后端：FastAPI 应用与核心模块（配置、认证、安全、日志）；API 端点：`auth`、`config`、`tmdb`、`system_dict`、`health`；数据库与模型（SQLAlchemy + SQLite）；外部客户端封装（TMDB、Sonarr、Prowlarr）。
- 前端：Vue 3 + TypeScript 应用，基础布局与页面（登录/注册、配置、字典、仪表盘等），Tailwind/Element Plus 集成。
- 基础测试：后端 Pytest 用例与异步测试支持。
- 脚本与容器：`scripts/start-dev.*`、`scripts/start-prod.*`，`docker-compose.dev.yml`、`docker-compose.prod.yml`、`Dockerfile`。
- 文档：仓库 README、后端 README、任务/设计文档、贡献指南（AGENTS.md）、Issue/PR 模板、变更日志（本文件）。

### Changed
- 分支策略：采用 `develop` 为默认协作分支，发布时合入 `main` 并打标签。

### Fixed
- N/A

### Removed
- 前端测试：当前版本不包含前端测试脚本。

---

说明：将新变更记录到 Unreleased，小版本发布时整理并替换为对应版本号与日期。
