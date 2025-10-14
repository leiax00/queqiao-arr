# FE-05: 主设置页面 API 联调 任务说明书

## 一、任务信息

- 任务ID: FE-05
- 名称: 主设置页面与后端 B-02 API 联调（读取/保存/连接测试）
- 复杂度: L（约 5 PD）
- 优先级: P0
- 依赖: FE-04（主设置页面 UI）、B-02（配置模块 API）
- 分支: `feat/fe-05-config-api-integration`（自 `develop` 拉出）

---

## 二、目标与范围（Scope）

- 目标：打通前端配置页面与后端配置 API（B-02），实现 Sonarr、Prowlarr、代理 配置的读取、保存与连接测试（服务类）。
- 范围：
  - 对齐并改造前端 API 层（`frontend/src/api/config.ts`）以适配 B-02 统一 REST 设计
  - 在 `views/config/index.vue` 接入真实请求：初始化加载、保存、测试连接
  - 处理敏感字段（API Key）遮蔽与占位的前端交互策略
  - 将“使用代理”逻辑与已保存的代理配置联动，向后端测试接口传递 `proxy`
- 非范围：
  - 新增后端接口或变更后端数据模型
  - 代理独立连通性测试（后端暂未提供专门端点，保留 UI 提示态）

---

## 三、现状与差异

- 现状：
  - UI 已完成（见 FE-04），目前页面内逻辑为本地占位，未调用后端
  - 前端 `frontend/src/api/config.ts` 使用占位路径：`/config/sonarr`、`/config/prowlarr`、`/config/proxy`、`/config/{type}/test`
- 后端（B-02）现有接口：统一前缀 `/api/v1/config`
  - 获取概览：`GET /api/v1/config`
  - 创建：`POST /api/v1/config`
  - 更新：`PUT /api/v1/config/{id}`
  - 删除：`DELETE /api/v1/config/{id}`
  - 测试连接：`POST /api/v1/config/test-connection`

---

## 四、数据契约与字段映射

### 4.1 服务配置（Sonarr / Prowlarr）

- 后端模型（简要）：
  - `ServiceConfigOut`: `id`、`service_name`、`service_type`、`name`、`url`、`api_key_masked?`、`is_active`、时间戳
  - 创建/更新：`service_name` in {`sonarr`,`prowlarr`}，`service_type`=`api`，`name`（默认“默认”），`url`，`api_key?`，`extra_config?`
- 前端表单 → 后端字段：
  - `url` → `url`
  - `apiKey` → `api_key`（仅当用户明确修改时发送；留空不覆盖）
  - `useProxy` → `extra_config.useProxy: boolean`
  - `name` 固定使用 "默认"（如后续支持多实例再开启命名）
- 读写策略：
  - 读取：`GET /api/v1/config` → 在 `services[]` 中以 `service_name` 筛选对应一条（未找到则视为未配置）
  - 保存：若存在 → `PUT /api/v1/config/{id}`；否则 → `POST /api/v1/config`

### 4.2 代理配置（Proxy）

- 存储形态：使用 `ServiceConfig`，`service_name`=`proxy`，`service_type`=`proxy`
- 字段映射：
  - 表单 `address` → `url`
  - 表单 `type` → `extra_config.type`（`http`|`https`|`socks5`）
  - 表单 `timeout` → `extra_config.timeout_ms: number`
- 读写策略与服务类似（按 `service_name=proxy` 找一条；无则创建，有则更新）。
- 连接测试：不直接对代理做连通性验证；在 Sonarr/Prowlarr 测试时，若 `useProxy=true` 且存在代理配置，则拼装 `proxy` 传给后端：
  - `proxy = { http: `${type}://${addressHost}`, https: `${type}://${addressHost}` }`

### 4.3 测试连接（后端 `POST /api/v1/config/test-connection`）

- 请求体（二选一）：
  - `by_body`：`{ mode: 'by_body', service_name, url, api_key?, username?, password?, proxy? }`
  - `by_id`：`{ mode: 'by_id', id }`
- FE-05 采用：`by_body`
  - 来源：当前编辑表单值；若 `useProxy=true` 且找到代理配置，则附带 `proxy`
  - 仅支持 `sonarr`、`prowlarr`；返回 `{ ok: boolean, details: string }`

---

## 五、前端实现改造点

### 5.1 API 层（`frontend/src/api/config.ts`）

- 替换为 REST 风格方法：
  - `getOverview(): GET /api/v1/config`
  - `createConfig(payload)`、`updateConfig(id, payload)`、`deleteConfig(id)`
  - `testConnection(body)` → `POST /api/v1/config/test-connection`
- 类型定义：对齐后端 `ServiceConfigOut`、`KVConfigOut` 和创建/更新 payload
- 兼容敏感字段策略：`api_key` 可选；仅在用户输入时携带

### 5.2 视图层（`frontend/src/views/config/index.vue`）

- 初始化：进入页面时调用 `getOverview()`，将 `sonarr/prowlarr/proxy` 三类配置映射至表单初值
- 保存：分别对三张卡进行“存在则更新/不存在则创建”的分支处理
- 测试：
  - Sonarr/Prowlarr：构造 `by_body` 调用后端；依据返回 `ok` 与否更新按钮图标与消息提示
  - 代理：维持 UI 测试占位提示（不触发后端）
- 敏感字段：
  - 若读取到 `api_key_masked`，则表单 `apiKey` 为空并显示提示文案；
  - 仅当用户输入新值时，将 `api_key` 放入保存/测试请求；否则不传，避免清空已存密钥。

---

## 六、错误处理与状态

- 按后端统一响应 `{ code, message, data }` 处理；异常用全局拦截器兜底
- 按钮状态：请求中禁用，结束后恢复；错误时以 `ElMessage.error` 呈现
- 表单校验：与 FE-04 保持一致；测试按钮在校验通过时可用

---

## 七、验收标准（Acceptance Criteria）

1. 进入 `/config` 自动拉取并正确回显三类配置（敏感字段不回显明文）
2. Sonarr/Prowlarr 配置支持创建与更新；代理配置支持创建与更新
3. 测试连接：对 Sonarr、Prowlarr 可成功发起并根据后端结果展示成功/失败
4. 当 `useProxy=true` 且存在代理配置时，测试请求携带 `proxy` 字段；关闭时不携带
5. 留空 `apiKey` 保存时不会覆盖后端已存密钥（仅用户填写才更新）
6. 所有请求与后端 B-02 契约一致；错误提示清晰，按钮状态切换合理

---

## 八、测试要点

- 初始化：后端有/无配置两种场景的表单初值与禁用态
- 保存：
  - 首次创建与后续更新均可成功，重复命名冲突时给出后端 409 错误
  - 留空 `apiKey` 不覆盖已存密钥；填写后成功更新并测试通过
- 测试连接：
  - 正确的 `url + apiKey` 返回 `ok=true`，错误时 `ok=false` 且展示 `details`
  - 勾选 `useProxy` 且已配置代理时，后端可收到 `proxy` 并正常工作

---

## 九、实施计划与里程碑（5 PD）

- Day 1：API 层改造与类型补全；对齐 B-02 契约
- Day 2：视图层接入读取/保存逻辑（Sonarr/Prowlarr）
- Day 3：接入代理保存；实现 `useProxy` → `proxy` 拼装与传参
- Day 4：测试连接逻辑与错误/状态处理完善；边界自测
- Day 5：文档与截图更新、代码走查与提交 PR

---

## 十、进度追踪（Checklist）

- [x] 任务文档（本文件）
- [ ] API 层改造（`frontend/src/api/config.ts`）
- [ ] 视图接入读取/保存（Sonarr / Prowlarr）
- [ ] 视图接入读取/保存（Proxy）
- [ ] 测试连接（Sonarr / Prowlarr by_body）
- [ ] 敏感字段遮蔽与占位策略落地
- [ ] 自测与截图记录
- [ ] 提交 PR，申请评审

---

## 十一、参考

- 后端实现：
```110:199:backend/app/api/endpoints/config.py
@router.get(
    "/",
    summary="获取配置概览",
    description="返回服务配置与KV配置的概要列表（敏感字段使用掩码，不回显明文）",
)
async def get_configurations(...):
    ...
    return success_response({"services": [x.model_dump() for x in services_out], "kv": [x.model_dump() for x in kv_out]})
```

```357:418:backend/app/api/endpoints/config.py
@router.post(
    "/test-connection",
    summary="测试服务连通性",
)
async def test_service_connection(payload: TestConnectionRequest, ...):
    ...
    if service_name not in {"sonarr", "prowlarr"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 sonarr/prowlarr 连通性测试")
    ok, note = await check_sonarr(url, raw_api_key, proxy)
    return success_response({"ok": ok, "details": note})
```

- FE-04 UI 说明：`docs/tasks/FE-04_主设置页面UI.md`


