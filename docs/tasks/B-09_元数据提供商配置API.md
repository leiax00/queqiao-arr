# B-09 元数据提供商配置API

> 版本: v0.1（草案）  
> 日期: 2025-10-18  
> 责任域: Backend（API/模型/加密/测试）  
> 关联任务: FE-06 元数据提供商设置页面（前端联调）

---

## 1. 背景与目标

现有系统已提供通用配置 API（Sonarr、Prowlarr、代理）与「外部服务客户端层」。为实现“中文友好”的核心流程，需要引入对 TMDB 等元数据源的配置管理能力：保存 TMDB 的连接信息与行为参数（语言、地区、成人内容过滤、use_proxy 开关），并提供连接测试能力，供自动化引擎与前端配置页复用。

本任务目标：

- 新增 TMDB 配置的后端 API（CRUD/读取与更新），数据结构与 Sonarr/Prowlarr 保持一致（ServiceConfig + extra_config；`service_type=metadata`）
- 支持一键连接测试（校验 `api_key` 有效性与网络可达性）
- 约束和暴露语言/地区可选项，便于前端渲染
- 敏感信息（`api_key`）加密存储与掩码返回
- 代理策略：仅有全局代理，通过 `extra_config.use_proxy` 控制 TMDB 是否使用全局代理（不提供每服务代理覆盖）

不在本任务范围内：自动化编排与 Torznab 端点实现（见 B-08）、标题解析器（见 B-06）。

---

## 2. 名词与约定

- TMDB: The Movie Database 外部元数据服务。
- 配置项（Configuration Item）: 可持久化的 TMDB 行为参数集合。
- 掩码（Mask）：对敏感字段的部分展示（如 `ABCD****WXYZ`）。
- use_proxy：布尔开关，指示是否对 TMDB 请求启用全局代理。

---

## 3. 需求与验收标准（Acceptance Criteria）

### 3.1 需求

- 后端提供 TMDB 配置读取与更新接口；`api_key` 加密存储，读取返回掩码；更新时若未传 `api_key` 则保留原值。
- 提供连接测试接口：真实调用 TMDB 轻量端点（如 `/configuration`），返回 `ok`、`latency_ms`、`diagnosis`。
- 提供语言与地区可选项接口：静态内置或缓存化生成，保证前端可渲染选择器。
- 代理：仅支持全局代理；通过 `extra_config.use_proxy`（布尔）决定是否对 TMDB 请求启用全局代理。

### 3.2 验收标准

- 正常读取配置：返回掩码后的 `api_key`，其余字段与存储一致。
- 正常更新配置：传入合法参数后更新成功（`api_key` 可选）；未传 `api_key` 不覆盖原有密钥。
- 连接测试：
  - 有效 `api_key` 与网络可达时返回 `ok=true`，并包含 `latency_ms`；
  - 无效 `api_key` 返回 `ok=false` 且 `diagnosis=invalid_api_key`；
  - 上游网络异常/超时返回 `ok=false` 且 `diagnosis` 为对应原因（如 `timeout`）。
- 所有日志严格脱敏，不输出明文 `api_key`。

---

## 4. 接口设计（API Design）

前缀：`/api/config/tmdb`

### 4.1 读取配置

- Method: `GET /api/config/tmdb`
- Auth: 需登录（与其他配置接口一致）
- Response 200（示例，结构与 ServiceConfig 对齐）：

```json
{
  "service_name": "tmdb",
  "service_type": "metadata",
  "name": "默认TMDB",
  "url": "https://api.themoviedb.org/3",
  "api_key_masked": "ABCD****WXYZ",
  "extra_config": {
    "use_proxy": false,
    "language": "zh-CN",
    "region": "CN",
    "include_adult": false
  },
  "is_active": true
}
```

说明：`api_key` 为掩码字符串；是否使用代理由 `extra_config.use_proxy` 控制，依赖全局代理配置。

### 4.2 更新配置

- Method: `PUT /api/config/tmdb`
- Request（示例，`api_key` 可选）：

```json
{
  "service_name": "tmdb",
  "service_type": "metadata",
  "name": "默认TMDB",
  "url": "https://api.themoviedb.org/3",
  "api_key": "<real_api_key_optional>",
  "extra_config": {
    "use_proxy": false,
    "language": "zh-CN",
    "region": "CN",
    "include_adult": false
  },
  "is_active": true
}
```

- Response 200：与 4.1 相同（`api_key` 返回掩码）。
- 校验：
  - `language` 需在支持列表内；
  - `region` 需在支持列表内；
  - `extra_config.use_proxy` 为布尔值。

### 4.3 连接测试（统一接口）

- Method: `POST /api/config/test-connection`
- 两种模式：
  - by_body：传 `service_name=tmdb`、`api_key`（可选覆盖）、`proxy`（与 Sonarr/Prowlarr 一致的 `{http, https}`）。未传则直连。
  - by_id：传已保存配置的 `id`，若 `extra_config.use_proxy=true`，后端将自动读取启用中的 `service_name=proxy` 服务，构造 httpx `proxies` 注入测试。
- 成功示例：

```json
{ "ok": true, "latency_ms": 132, "diagnosis": "ok", "endpoint": "/configuration" }
```

### 4.4 选项列表（语言/地区）

- Method: `GET /api/config/tmdb/options`
- Response 200（示例）：

```json
{
  "languages": [
    { "code": "zh-CN", "label": "中文（简体）" },
    { "code": "zh-TW", "label": "中文（繁體）" },
    { "code": "en-US", "label": "English (US)" }
  ],
  "regions": [
    { "code": "CN", "label": "中国大陆" },
    { "code": "HK", "label": "中国香港" },
    { "code": "TW", "label": "中国台湾" },
    { "code": "US", "label": "United States" }
  ]
}
```

### 4.5 错误码与语义

- 400：参数非法（枚举超出、布尔非法）
- 401：未认证或权限不足
- 408：连接测试超时
- 502/503：上游不可用或服务降级

日志与错误信息需脱敏，不含明文 `api_key`。

---

## 5. 数据模型与存储

沿用现有配置存储与加密机制（参考 `app/models/config.py`、`app/db/crud_config.py`、`app/utils/encryption.py`），采用统一结构：

- 表：`service_configs`
  - `service_name`: `tmdb`
  - `service_type`: `metadata`（新增类别，便于过滤查询）
  - `url`: 默认 `https://api.themoviedb.org/3`
  - `api_key`: 加密存储（读取返回掩码；更新未传则保留）
  - `extra_config`（JSON）：
    - `use_proxy` (bool, default: false)
    - `language` (str, default: zh-CN)
    - `region` (str, default: CN)
    - `include_adult` (bool, default: false)

---

## 6. 行为与复用

- 客户端层：复用 `app/services/clients/tmdb.py` 与 `app/services/clients/factory.py` 构造请求客户端；当 `use_proxy=true` 时注入全局代理。
- 安全：复用 `app/utils/encryption.py`；所有日志打印需对 `api_key` 脱敏。
- API 组织：可复用 `app/api/endpoints/config.py` 路由分组，或新增 `tmdb.py` 子路由以分离责任。
- 校验与响应：复用 `app/utils/response.py` 的标准响应包装（若已有）。

---

## 7. 开发拆解与进度（仅文档阶段）

本 MR 仅交付文档；实现将另起 MR：

1) 定义后端 Pydantic Schema（读/写/测试/选项）  
2) 定义路由与处理器（GET/PUT/POST test/GET options）  
3) 放宽/扩展后端枚举：允许 `service_name='tmdb'`、`service_type='metadata'`  
4) 客户端层接入：`use_proxy`（启用全局代理）、`language/region/include_adult`  
5) 日志脱敏与错误映射（400/401/408/502/503）  
6) 单元测试与集成测试  
7) 前端 FE-06 联调（表单/掩码展示/测试按钮）

DoD（Definition of Done，面向实现 MR）：

- 通过单测（覆盖 CRUD、掩码、连接测试分支、参数校验）
- 通过集成测试（含 HTTPX mock 上游与真实超时分支）
- Swagger 文档完整、示例清晰
- 前端可获取选项列表并成功保存与测试
- 日志全局脱敏检查通过

---

## 8. 测试计划

- 单元测试：
  - 读取返回 `api_key` 掩码；
  - 更新保留旧 `api_key`（未提供时）；
  - 参数越界/非法枚举触发 400；
  - 连接测试：有效 key（200）、无效 key（401/403）、超时（408 模拟）、上游异常（502/503）。

- 集成测试：
  - 端点鉴权一致性（需登录）
  - 与客户端层注入参数一致性（use_proxy 生效）

---

## 9. 风险与对策

- 上游速率限制变动：默认即可，后续再开放限速参数
- 语言/地区兼容性：保留通用枚举且允许回退（若 TMDB 不支持指定组合时回退默认）
- 安全风险：统一脱敏日志；`api_key` 仅在内存中短暂明文存在，用后即丢弃。

---

## 10. 变更记录

- v0.1（2025-10-18）：创建初稿，定义需求、API、数据模型与测试计划（已对齐 ServiceConfig + use_proxy）。

---

## 11. 任务进度（Rolling）

- [x] 创建分支 `feature/B-09-metadata-provider-config`（2025-10-18）
- [x] 编写/对齐文档（ServiceConfig + extra_config、`service_type=metadata`、`use_proxy` 全局代理）（2025-10-18）
- [ ] 后端接口定义与路由（GET/PUT/test/options）
- [ ] 后端参数校验与日志脱敏，放宽枚举（`service_name=tmdb`、`service_type=metadata`）
- [ ] 单元测试与集成测试用例
- [ ] 前后端联调与验收




