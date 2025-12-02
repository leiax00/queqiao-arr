# B-05: Prowlarr API 客户端封装 任务说明书

## 一、任务信息
- 任务ID: B-05
- 名称: Prowlarr API 客户端封装（搜索能力）
- 复杂度: S（约 2 PD）
- 优先级: P0
- 依赖: B-10（外部服务客户端层）
- 被依赖: B-08（端到端编排）、B-06（标题解析器）
- 当前分支: `feature/b05-prowlarr-search`
- 状态: 进行中
- 更新时间: 2025-11-28

---

## 二、目标与范围（Scope）
- 目标：在现有 `ProwlarrClient` 基础上补齐搜索能力，统一封装请求与错误处理，供后续解析和编排直接调用。
- 范围：
  - 在 `backend/app/services/clients/prowlarr.py` 新增搜索方法（建议命名 `search`）。
  - 支持核心请求参数：`query`（必填）、`indexer_ids`（可选 list[int]）、`categories`（可选 list[int]）、`limit`/`offset`、`type`（默认 `search`，兼容 `tvsearch`）。
  - 返回 `(bool, data|err)`；成功时透传 Prowlarr JSON 列表，失败时返回可读错误字符串。
  - 错误处理：捕获网络异常、超时、4xx/5xx，错误信息包含 status code / message，避免泄漏 API Key。
- 复用基类代理/超时/鉴权逻辑，保持与 Sonarr/TMDB 客户端一致的接口风格。
- 非范围：
  - 标题解析、Torznab XML 生成（B-06/B-07）。
  - 配置 CRUD、UI 变更。

### 2.1 对外 API 暴露（新增）
- 新增后端端点：`GET /api/v1/prowlarr/search`，支持鉴权后直接发起 Prowlarr 搜索，便于联调与直连。
- 请求参数沿用客户端签名：`query`、`indexer_ids`、`categories`、`limit`、`offset`、`type`。
- 返回体：统一 `success_response` 包装，`data.results` 为 Prowlarr 原始列表。

### 2.2 配置增强 - 超时控制（新增）
- 在配置表中统一添加 `timeout` 字段，适用于所有外部服务配置（包括 Prowlarr）。
- 超时字段类型：整数（秒），默认值根据服务特性设定。
- 影响：客户端创建时使用配置的超时值，覆盖基类默认超时。

---

## 三、设计与目录结构
- 目录：
```
backend/app/services/clients/
  base.py        # 已有：统一请求/异常处理/代理
  prowlarr.py    # 本任务完善：新增 search 能力
  factory.py     # 已有：按 service_name 生成客户端
```

### 3.1 搜索方法设计
- 方法签名（建议）：`search(query: str, indexer_ids: list[int] | None = None, categories: list[int] | None = None, limit: int | None = None, offset: int | None = None, type: str = "search") -> tuple[bool, Any]`
- 参数映射：
  - `query` → `q`
  - `indexer_ids` → `indexerIds`（多值）
  - `categories` → `categories`（多值）
  - `limit` → `limit`
  - `offset` → `offset`
  - `type` → `type`（默认 `search`，可传 `tvsearch` 等）
- 请求路径：`/api/v1/search`
- 调用 `_get`（或 `_request`）拼接 query string，遵循基类的 headers 与超时。

### 3.3 REST API 端点设计（新增）
- 端点路径：`GET /api/v1/prowlarr/search`
- 认证：使用系统统一的 API Key 认证机制
- 请求参数（Query Parameters）：
  - `query`（必填）：搜索关键词
  - `indexer_ids`（可选）：索引器ID列表，逗号分隔
  - `categories`（可选）：分类ID列表，逗号分隔
  - `limit`（可选）：返回结果数量限制, 默认值: 100
  - `offset`（可选）：分页偏移量, 默认值: 0
  - `type`（可选）：搜索类型，默认 `search`
- 响应格式：
```json
{
  "success": true,
  "data": {
    "results": [/* Prowlarr 原始搜索结果列表 */]
  }
}
```
- 错误响应：
```json
{
  "success": false,
  "error": "错误描述信息"
}
```

### 3.2 错误与日志
- 返回格式：`(True, data_json)` 或 `(False, "Prowlarr 搜索失败: <原因>")`。
- 捕获连接/超时/HTTP 错误；错误信息包含 status code 及上游 message。
- 日志：在请求/失败路径打印简要上下文（URL、type、query），不记录 API Key。

---

## 四、业务规则（Business Rules）
1. `query` 必填且非空；为空直接返回参数错误。
2. `limit`、`offset` 如提供需为非负整数；缺省使用 Prowlarr 默认值。
3. `indexer_ids`、`categories` 允许为空；提供时需为整数列表，拼接为多值参数。
4. 请求类型 `type` 默认 `search`；如传入其他类型需保留原值转发。
5. 复用基类代理/超时配置；不在客户端层做重试。

---

## 五、API 映射（Prowlarr）
- Endpoint: `GET /api/v1/search`
- 关键查询参数：
  - `type`: `search | tvsearch | ...`
  - `q`: 搜索关键词（必填）
  - `indexerIds`: 逗号或多值列表（按 Prowlarr 支持）
  - `categories`: 逗号或多值列表
  - `limit`、`offset`: 分页
- 返回（示例简化）：
```json
[
  {
    "title": "Example",
    "size": 12345,
    "indexerId": 1,
    "guid": "magnet:...",
    "downloadUrl": "https://...",
    "publishDate": "2023-01-01T00:00:00Z",
    "grabs": 10,
    "seeders": 20,
    "peers": 25
  }
]
```
- 错误示例：`{"error": "indexer is unavailable"}` → 返回 `(False, "Prowlarr 搜索失败: HTTP 503 indexer is unavailable")`

---

## 六、输出契约（供后续模块消费）
- 成功：`(True, list[dict])`，透传 Prowlarr JSON 数组；调用方自行选择字段（如 title/size/indexerId/guid/seeders/...）。
- 失败：`(False, str)`；字符串包含错误来源（参数/网络/HTTP code）。

---

## 七、验收标准（Acceptance Criteria）
1. `ProwlarrClient` 提供可用的 `search` 方法，参数与映射符合上述约定。
2. 异常路径覆盖：参数非法、连接/超时、4xx/5xx 均返回 `(False, <errmsg>)`。
3. 与 `ExternalServiceClient` 风格一致（代理、超时、鉴权 header）。
4. 新增/补充单测覆盖成功与典型失败分支。
5. 暴露 `GET /api/v1/prowlarr/search` 端点，鉴权后可直连 Prowlarr 调用。
6. 文档更新到位（本文件），与 TODO 对齐。

---

## 八、实施计划（2 PD）
- Day 1：确定参数映射与默认值，完善 `search` 方法实现与日志/错误语义。
- Day 2：补充单元测试（成功/超时/4xx/5xx/参数错误），本地自测。

---

## 九、风险与对策
- Prowlarr 版本差异导致参数名或类型差异：采用多值兼容（列表 -> 重复参数/逗号拼接），异常信息回传具体字段。
- 上游不可用或超时：提供清晰错误提示并可由上层做重试/降级。
- 类目/索引器 ID 与配置不一致：在调用方做来源校验；客户端保持透明转发。

---

## 十、进度清单（Checklist）
- [x] 创建任务分支 `feature/b05-prowlarr-search`
- [x] 需求梳理与文档落地（当前文档）
- [x] 设计搜索方法签名与参数映射细节
- [x] 实现 `search` 请求与错误处理逻辑
- [x] 增加单元测试（成功/异常场景）
- [x] 暴露接口 `/api/v1/prowlarr/search` 便于联调
- [x] 添加配置表 `timeout` 字段，支持所有外部服务超时控制
- [x] 实现 REST API 端点完整功能与参数验证
- [x] 本地自测并整理结果（必要时附示例）
