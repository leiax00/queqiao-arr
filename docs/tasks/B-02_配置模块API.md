# B-02: 配置模块 API 开发任务说明书

## 一、任务基本信息

- 任务ID: B-02
- 任务名称: 配置模块 API（Sonarr、Prowlarr、网络代理等配置的增删改查与连接测试）
- 复杂度: M（约 3 PD）
- 优先级: P0
- 依赖任务: B-01（认证与鉴权基础能力）
- 关联前端: `frontend/src/views/config/Sonarr.vue`、`frontend/src/views/config/Prowlarr.vue`

---

## 二、目标与范围（Scope）

### 2.1 目标
- 提供外部服务配置（Sonarr、Prowlarr、Proxy）的标准化 CRUD 接口。
- 敏感字段（API Key、密码等）加密入库，默认不回显明文；提供按需解密用于连接测试。
- 提供“连接测试”端点，保存前可验证配置有效性与网络可达性。
- 统一响应结构，便于前端拦截器与文档对齐。

### 2.2 范围
- API 前缀: `/api/v1/config/*`（见 `backend/app/main.py` 与 `backend/app/api/routes.py`）
- 数据模型: `backend/app/models/config.py` 中 `Configuration` 与 `ServiceConfig`
- 响应封装: `backend/app/utils/response.py`（`success_response` / `error_response`）
- 加密能力: `backend/app/utils/encryption.py`（PBKDF2 + Fernet）

非范围（后续迭代）:
- 配置版本审计、导入导出、细粒度权限、软删除恢复、自动切换生效配置

---

## 三、业务规则（Business Rules）

1. 配置类型：
   - `ServiceConfig`：外部服务连接参数。`service_name ∈ {sonarr, prowlarr, proxy}`；`service_type ∈ {api, proxy}`。
   - `Configuration`：通用 KV 配置（例如默认语言、全局代理等）。
2. 敏感信息与回显策略：
   - 入库前对 `api_key`、`password`、以及需要保密的 KV `value` 加密。
   - 查询/列表中不回显明文，仅提供掩码（如 `****abcd`）或不返回该字段。
   - 连接测试仅在内存临时解密使用，不在响应体回显明文。
3. 唯一性与状态：
   - 建议对 `service_name + name` 保持唯一。允许多份配置并存，通过 `is_active` 表示启用状态。
4. 鉴权：
   - 所有 `/config/*` 接口要求登录态（`get_current_user`）。写操作后续可限定为超级管理员。
5. 统一响应：
   - 成功：`{ code: 200, message: "OK", data: {...} }`
   - 失败：`{ code: <业务码>, message: <错误描述>, data: <可选> }`

---

## 四、API 设计（OpenAPI 概览）

说明：以下均为包裹在统一响应结构下的 `data` 字段示例。

### 4.1 GET `/api/v1/config/`
- 用途：获取配置概要列表（服务配置与部分 KV 条目）。
- 查询参数：`service_name`（可选），`is_active`（可选）。
- 响应示例：
```json
{
  "services": [
    {
      "id": 1,
      "service_name": "sonarr",
      "service_type": "api",
      "name": "默认Sonarr",
      "url": "http://127.0.0.1:8989",
      "api_key_masked": "****9f2c",
      "is_active": true,
      "created_at": "2025-10-12T10:00:00Z",
      "updated_at": "2025-10-12T11:00:00Z"
    },
    {
      "id": 2,
      "service_name": "prowlarr",
      "service_type": "api",
      "name": "默认Prowlarr",
      "url": "http://127.0.0.1:9696",
      "api_key_masked": "****a12b",
      "is_active": true,
      "created_at": "2025-10-12T10:00:00Z",
      "updated_at": "2025-10-12T11:00:00Z"
    }
  ],
  "kv": [
    { "key": "default_language", "value": "zh-CN", "is_encrypted": false, "created_at": "2025-10-12T10:00:00Z", "updated_at": "2025-10-12T11:00:00Z" }
  ]
}
```

### 4.2 POST `/api/v1/config/`
- 用途：创建服务配置或 KV 配置。
- 请求体（服务配置示例）：
```json
{
  "type": "service",
  "service_name": "sonarr",
  "service_type": "api",
  "name": "主Sonarr",
  "url": "http://127.0.0.1:8989",
  "api_key": "<raw-key>",
  "username": null,
  "password": null,
  "extra_config": { "timeout": 3000 }
}
```
- 请求体（KV 配置示例）：
```json
{
  "type": "kv",
  "key": "http_proxy",
  "value": "http://127.0.0.1:7890",
  "description": "全局HTTP代理",
  "is_encrypted": false
}
```
- 成功：返回创建对象的概要（敏感字段不回显）。

### 4.3 PUT `/api/v1/config/{config_id}`
- 用途：按 ID 更新服务配置或 KV 配置。
- 规则：更新敏感字段需重新加密；允许切换 `is_active`。
- 成功：返回更新后概要对象。

### 4.4 DELETE `/api/v1/config/{config_id}`
- 用途：删除指定配置。
- 说明：若为唯一活跃配置，后续可在前端做 UX 提醒；MVP 后端允许直接删除。
- 成功：`{ deleted: true }`。

### 4.5 POST `/api/v1/config/test-connection`
- 用途：测试连通性（可基于请求体临时参数，或基于已存在配置 ID）。
- 请求体：
```json
{
  "mode": "by_body",
  "id": null,
  "service_name": "sonarr",
  "url": "http://127.0.0.1:8989",
  "api_key": "<raw-key>",
  "username": null,
  "password": null,
  "proxy": {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  }
}
```
- 响应示例：
```json
{ "ok": true, "latency_ms": 123, "details": "Ping /api/v3/system/status 成功" }
```

---

## 五、数据模型（当前仓库）

- `Configuration`（通用 KV）
  - `id: int`，`key: str(unique)`，`value: Text`（可加密），`description: str`，`is_encrypted: bool`，`is_active: bool`，`created_at: datetime`，`updated_at: datetime`
- `ServiceConfig`（外部服务）
  - `id: int`，`service_name: str`，`service_type: str`，`name: str`，`url: str`
  - `api_key: Text`（加密），`username: str?`，`password: Text?`（加密）
  - `extra_config: Text(JSON)`，`is_active: bool`，`created_at: datetime`，`updated_at: datetime`
- 加密工具：`EncryptionManager`（PBKDF2 派生 + Fernet 对称加密）
- 统一响应：`success_response` / `error_response`

---

## 六、错误码与消息
- 200：成功
- 400：参数不合法（缺少必填/格式错误）
- 401：未认证
- 403：禁止访问（预留：仅管理员可写）
- 404：配置不存在（按 ID 操作）
- 409：配置冲突（`service_name + name` 重复）
- 500：服务器内部错误

---

## 七、实现计划（Tasks）
1. 定义 Pydantic 模型：`ServiceConfigCreate/Update`，`ConfigurationCreate/Update`，`ConnectionTestRequest`。
2. 完成 `backend/app/api/endpoints/config.py` 的 CRUD 与连接测试逻辑，接入统一响应。
3. 接入加密/解密：入库加密、读取屏蔽显示、连接测试按需解密。
4. Swagger 注释与示例响应完善（tags: 配置管理）。
5. 单元测试与最小集成测试（覆盖成功/失败路径）。

---

## 八、关键测试用例（示例）
- 创建 Sonarr 配置成功：响应对象中 `api_key` 不回显，仅提供 `api_key_masked`。
- 创建重复配置：同 `service_name + name` 冲突 → 409。
- 更新配置切换 `is_active`：成功；其他同类配置不强制失活（MVP）。
- 测试连接成功：请求 Sonarr `/api/v3/system/status` 200 → `ok=true`，返回 `latency_ms`。
- 测试连接失败：URL 不可达或鉴权失败 → `ok=false`，`details` 描述原因。
- KV 配置加密：`is_encrypted=true` 时入库加密；查询不回显明文。

---

## 九、验收标准（Acceptance Criteria）
1. `/api/v1/config` 提供完整 CRUD 与连接测试端点，统一响应结构与错误码对齐。
2. 敏感信息全程加密存储，接口响应不回显明文；日志无敏感明文泄露。
3. Swagger 文档可见，前端可据此对接；最小测试覆盖通过关键正反场景。

---

## 十、进度清单（Checklist）
- [x] 任务说明文档（本文件）
- [ ] API 请求/响应模型定义
- [ ] `config` 端点 CRUD 实现
- [ ] 连接测试逻辑实现
- [ ] 加密接入与字段遮蔽
- [ ] Swagger 注释完善
- [ ] 最小测试用例完成（含失败路径）
- [ ] 与前端配置页联调通过

---

## 十一、风险与对策
- 明文泄露风险：统一遮蔽策略；日志/异常处理禁止打印敏感明文。
- 多环境差异：引入“测试连接”与多配置并存，用户选择启用项。
- 外部接口不稳定：设置合理超时；失败信息面向用户可读。

---

## 十二、与现有代码的契合点
- `backend/app/api/routes.py` 已挂载 `config` 为 `/api/v1/config`。
- `backend/app/api/endpoints/config.py` 已有端点占位（GET/POST/PUT/DELETE/POST test-connection），需补全。
- `backend/app/models/config.py`、`backend/app/utils/encryption.py`、`backend/app/utils/response.py` 已具备基础能力。
