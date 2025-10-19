# B-09: 元数据提供商配置 API 开发任务说明书

## 一、任务基本信息

- 任务ID: B-09
- 任务名称: 元数据提供商配置 API（TMDB 配置CRUD、连接测试与选项）
- 复杂度: M（约 3 PD）
- 优先级: P0
- 依赖任务: B-02（配置模块基础能力）
- 关联前端: FE-06（元数据提供商设置页面 UI）

---

## 二、目标与范围（Scope）

### 2.1 目标
- **统一使用通用配置接口**：TMDB 配置完全复用 Sonarr/Prowlarr 的通用接口（GET/POST/PUT），数据结构一致（ServiceConfig + extra_config，`service_type=metadata`）。
- 支持一键连接测试（校验 `api_key` 有效性与网络可达性，统一走 `/api/config/test-connection`）。
- 提供语言/地区选项接口（`GET /api/config/tmdb/options`），便于前端渲染。
- 敏感信息（`api_key`）加密存储与掩码返回。
- API URL 支持自定义配置（默认 `https://api.themoviedb.org/3`）。
- 代理策略：仅使用全局代理，通过 `extra_config.use_proxy` 控制是否启用（不提供每服务代理覆盖）。

### 2.2 范围
- API 前缀: `/api/config/*` - **复用通用配置接口**
- 模型/存储: 复用 `ServiceConfig`；`service_name=tmdb`、`service_type=metadata`，`url` 可自定义，`extra_config` 持久化 `use_proxy/language/region/include_adult`。
- 测试连接：统一入口 `POST /api/config/test-connection`，by_body/by_id 均支持 TMDB；by_id 且 `use_proxy=true` 时自动注入"proxy 类型服务"。
- **专用端点**：仅保留 `GET /api/config/tmdb/options`（语言/地区选项）。

### 2.3 非范围（Out of Scope）
- 自动化编排与 Torznab 端点（B-08）。
- 标题解析器（B-06）。

---

## 三、业务规则（Business Rules）
1. 存储结构：`ServiceConfig(service_name='tmdb', service_type='metadata')`；`extra_config` JSON 包含：
   - `use_proxy: boolean`（默认 false）
   - `language: string`（默认 `zh-CN`）
   - `region: string`（默认 `CN`）
   - `include_adult: boolean`（默认 false）
2. 掩码策略：读取返回 `api_key_masked`，不回显明文；更新时仅在传入 `api_key` 才覆盖。
3. 连接测试：
   - by_body：允许传 `proxy`（与 Sonarr/Prowlarr 一致的 `{http, https}`）
   - by_id：若 `use_proxy=true`，后端自动读取启用中的 `service_name=proxy` 服务，构造 httpx `proxies` 注入测试
4. 鉴权：所有接口需登录态。

---

## 四、需求与验收标准（Acceptance Criteria）
- 读取：返回掩码后的 `api_key` 与 `extra_config`；结构与 ServiceConfig 对齐。
- 更新：未传 `api_key` 不覆盖旧值；校验 `language/region/use_proxy` 合法性。
- 测试连接：有效 `api_key` → `ok=true` 并返回 `latency_ms`；无效 key 或超时/上游错误按码返回。
- 日志脱敏：不输出明文 `api_key`。

---

## 五、API 设计（OpenAPI 概览）

> **重要变更**：TMDB 配置已统一使用通用 config 接口（与 Sonarr/Prowlarr 一致），不再使用专用端点。

### 5.1 读取配置（通用接口）
- Method: `GET /api/config/`
- Query: `?service_name=tmdb` (可选，用于过滤)
- Auth: 需登录
- 200 示例：
```json
{
  "code": 200,
  "message": "OK",
  "data": {
    "services": [
      {
        "id": 1,
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
        "is_active": true,
        "created_at": "2025-10-19T...",
        "updated_at": "2025-10-19T..."
      }
    ],
    "kv": []
  }
}
```

### 5.2 创建配置（通用接口）
- Method: `POST /api/config/`
- 请求体：
```json
{
  "type": "service",
  "service_name": "tmdb",
  "service_type": "metadata",
  "name": "默认TMDB",
  "url": "https://api.themoviedb.org/3",
  "api_key": "<real_api_key>",
  "extra_config": {
    "use_proxy": false,
    "language": "zh-CN",
    "region": "CN",
    "include_adult": false
  },
  "is_active": true
}
```
- 200：`{ "code": 200, "message": "OK", "data": { "id": 1 } }`
- 校验：`url` 必填，`language/region` 在支持列表，`extra_config.use_proxy` 为布尔

### 5.3 更新配置（通用接口）
- Method: `PUT /api/config/{id}`
- 请求体（所有字段可选，仅传递需要更新的字段）：
```json
{
  "url": "https://api.themoviedb.org/3",
  "api_key": "<real_api_key_optional>",
  "extra_config": {
    "use_proxy": false,
    "language": "zh-CN",
    "region": "CN",
    "include_adult": false
  }
}
```
- 200：`{ "code": 200, "message": "OK", "data": { "id": 1 } }`
- 注：未传 `api_key` 时保留原密钥

### 5.4 连接测试（统一接口）
- Method: `POST /api/config/test-connection`
- 模式1 - by_body（新配置或修改密钥）：
```json
{
  "mode": "by_body",
  "service_name": "tmdb",
  "url": "https://api.themoviedb.org/3",
  "api_key": "<real_api_key>",
  "proxy": {
    "http://": "http://127.0.0.1:7890",
    "https://": "http://127.0.0.1:7890"
  }
}
```
- 模式2 - by_id（已保存配置）：
```json
{
  "mode": "by_id",
  "id": 1
}
```
  - 后端自动从数据库读取 `api_key` 和配置
  - 若 `extra_config.use_proxy=true`，自动注入全局代理配置
- 成功示例：
```json
{
  "code": 200,
  "message": "OK",
  "data": {
    "ok": true,
    "details": "TMDB API 连接成功"
  }
}
```

### 5.5 选项列表（语言/地区）- TMDB 专用端点
- Method: `GET /api/config/tmdb/options`
- Auth: 需登录
- 200 示例：
```json
{
  "code": 200,
  "message": "OK",
  "data": {
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
}
```

### 5.6 错误码与语义
- 400：参数非法（枚举/布尔非法）
- 401：未认证或权限不足
- 408：连接测试超时
- 502/503：上游不可用或服务降级

---

## 六、数据模型（当前仓库）
- `ServiceConfig`（外部服务）- 完全复用通用模型
  - `id`：配置 ID
  - `service_name: 'tmdb'`：服务标识
  - `service_type: 'metadata'`：服务类型
  - `name`：配置名称（默认："默认TMDB"）
  - `url`：API 地址（默认："https://api.themoviedb.org/3"，**支持自定义**）
  - `api_key`（加密存储，返回时掩码）
  - `extra_config`（JSON）：
    - `use_proxy: boolean` - 是否启用全局代理
    - `language: string` - 语言代码（如 "zh-CN"）
    - `region: string` - 地区代码（如 "CN"）
    - `include_adult: boolean` - 是否包含成人内容
  - `is_active: boolean`：是否启用
  - `created_at`, `updated_at`：时间戳
- 加密：`app/utils/encryption.py`
- 掩码策略：前4位+中间星号+后4位（如 "ABCD****WXYZ"）

---

## 七、与现有代码的契合点
- 路由聚合：`backend/app/api/routes.py` 已挂载 `config` 为 `/api/v1/config`
- 模型与CRUD：`backend/app/models/config.py`、`backend/app/db/crud_config.py`
- 加密与响应：`backend/app/utils/encryption.py`、`backend/app/utils/response.py`
- 客户端：`backend/app/services/clients/{tmdb,factory}.py`

---

## 八、实现计划（Tasks）
1) ✅ 放宽/扩展枚举：`service_name=tmdb`、`service_type=metadata`  
2) ✅ **统一使用通用接口**：删除专用 GET/PUT 端点，复用 ServiceConfig 通用 CRUD  
3) ✅ 保留选项接口：`GET /api/config/tmdb/options`（语言/地区列表）  
4) ✅ 统一 test-connection 支持 TMDB（by_body/by_id 双模式）  
5) ✅ 客户端层接入：`use_proxy`（启用全局代理）、`language/region/include_adult`  
6) ✅ 日志脱敏与错误映射（400/401/408/502/503）  
7) ✅ 前端 FE-06 联调（表单/掩码展示/测试按钮/by_id 测试模式）  
8) ✅ 性能优化：前端统一加载所有配置，减少 API 请求  
9) [ ] 单元测试与集成测试用例

---

## 九、验收标准（DoD）
- 通过单测（覆盖 CRUD、掩码、连接测试分支、参数校验）
- 通过集成测试（含 HTTPX mock 上游与真实超时分支）
- Swagger 文档完整、示例清晰
- 前端可获取选项列表并成功保存与测试
- 日志全局脱敏检查通过

---

## 十、测试计划（示例）
- 单元测试：
  - 读取返回 `api_key` 掩码
  - 更新保留旧 `api_key`（未提供时）
  - 参数越界/非法枚举触发 400
  - 连接测试：有效 key（200）、无效 key（401/403）、超时（408 模拟）、上游异常（502/503）
- 集成测试：
  - 端点鉴权一致性（需登录）
  - 与客户端层注入参数一致性（use_proxy 生效）

---

## 十一、风险与对策
- 上游速率限制变动：默认即可，后续再开放限速参数
- 语言/地区兼容性：保留通用枚举且允许回退
- 安全风险：统一脱敏日志；`api_key` 仅在内存中短暂明文存在，用后即丢弃

---

## 十二、变更记录
- v0.1（2025-10-18）：创建；统一接入 `ServiceConfig + use_proxy`，测试走 `test-connection`。
- v0.2（2025-10-19）：**架构重构**；删除专用 GET/PUT 端点，完全统一到通用配置接口；保留选项端点；支持 API URL 可编辑；实现 by_id 测试模式；优化前端加载流程。

---

## 十三、进度清单（Checklist）
- [x] 创建分支 `feature/B-09-metadata-provider-config`（2025-10-18）
- [x] 文档对齐（结构、数据模型、接口示例）（2025-10-18）
- [x] 后端端点与路由（统一 test-connection 支持 TMDB，GET options）（2025-10-18）
- [x] 放宽枚举（`service_name=tmdb`、`service_type=metadata`）（2025-10-18）
- [x] **架构重构：统一使用通用配置接口**（2025-10-19）
  - 删除专用 GET/PUT `/api/config/tmdb` 端点
  - 复用通用 GET/POST/PUT 接口
  - 保留 GET `/api/config/tmdb/options` 选项端点
- [x] 前后端数据契约对齐（添加id字段，修复选项结构）（2025-10-19）
- [x] 前端实现（FE-06）
  - 表单 UI 与布局
  - 掩码显示与敏感信息处理
  - by_id 测试模式（已保存配置）
  - 统一加载优化（减少 API 请求）
  - API URL 可编辑功能
- [ ] 单元测试与集成测试用例
- [ ] 手动功能测试与验收




