# **B-01: 用户认证模块 API 开发任务说明书**

## 一、任务基本信息

- **任务ID**: B-01
- **任务名称**: 用户认证模块 API（首次运行创建管理员、登录、JWT令牌生成与校验）
- **复杂度**: M（约 3 PD）
- **优先级**: P0
- **依赖任务**: F-01（项目结构初始化）
- **关联前端任务**: FE-02（注册页）、FE-03（登录页）

---

## 二、目标与范围（Scope）

### 2.1 目标
- 支持首次运行创建管理员用户（仅当系统内无用户时）
- 支持用户登录并颁发短期有效的 JWT 访问令牌
- 提供获取当前用户信息的受保护接口
- 定义并落地统一响应规范（前后端契约一致）

### 2.2 范围
- 后端 API 路径前缀：`/api/v1/auth/*`
- 数据模型：`app/models/user.py` 中 `User`
- 安全与令牌：`app/core/security.py`（bcrypt 哈希，JWT HS256）
- 配置：`app/core/config.py`（`SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM`）

不在本任务范围（可选/后续）：
- 刷新令牌持久化机制（Refresh Token 存储/黑名单）
- 多因素认证（MFA）
- 账户锁定/限速防爆破

---

## 三、业务规则（Business Rules）

1. 首次运行注册限制：当 `users` 表为空时允许注册，成功创建的首个账户自动为 `is_superuser=True`。若已存在用户，再次调用注册接口返回错误（详见错误码）。
2. 密码存储：仅存储 `hashed_password`（bcrypt，通过 `passlib`），严禁明文。
3. 登录认证：校验用户名与密码；成功后签发访问令牌（JWT，HS256），`sub` 置为用户名。
4. 令牌时效：有效期由 `ACCESS_TOKEN_EXPIRE_MINUTES` 控制；过期需重新登录（本任务不强制实现 Refresh Token）。
5. 鉴权传递：前端通过 `Authorization: Bearer <token>` 访问受保护资源。
6. 统一响应：所有接口遵循统一响应包裹结构，便于前端拦截器处理。

---

## 四、统一响应规范（Contract）

### 4.1 响应包裹结构
```json
{
  "code": 200,
  "message": "OK",
  "data": { /* 业务数据，可为空 */ },
  "trace_id": "optional-correlation-id"
}
```

- **code**: 业务码（与 HTTP 状态码语义对齐，成功固定为 200）
- **message**: 人类可读消息
- **data**: 业务数据对象
- **trace_id**: 可选，用于链路追踪/日志关联

### 4.2 错误码约定
- 200：成功
- 400：参数校验失败 / 非法请求
- 401：未认证 / 凭据无效或过期
- 403：禁止访问（如非首次运行时调用注册）
- 404：资源不存在
- 409：资源冲突（如用户名重复）
- 500：服务器内部错误

---

## 五、API 设计（OpenAPI 概览）

> 所有响应均使用“统一响应规范”包裹。

### 5.1 POST `/api/v1/auth/register`
- **用途**：首次运行创建管理员（当且仅当无任何用户存在）
- **请求体**：
```json
{
  "username": "admin",
  "password": "P@ssw0rd",
  "email": "admin@example.com" // 可选
}
```
- **业务规则**：
  - 若 `users` 表为空：创建用户，`is_superuser = true`；出于 UX，返回即登录（携带 token）。
  - 若已有用户：返回 `403` 或 `409`（见错误码），不允许再注册。
- **成功响应 data 示例**：
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_active": true,
    "is_superuser": true
  },
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 5.2 POST `/api/v1/auth/login`
- **用途**：用户登录，签发访问令牌
- **请求体**：
```json
{
  "username": "admin",
  "password": "P@ssw0rd"
}
```
- **成功响应 data 示例**：与注册成功一致

### 5.3 GET `/api/v1/auth/me`
- **用途**：获取当前用户信息（受保护）
- **请求头**：`Authorization: Bearer <token>`
- **成功响应 data 示例**：
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "is_superuser": true
}
```

### 5.4 POST `/api/v1/auth/refresh`（可选）
- **用途**：刷新访问令牌（MVP 可不实现；若实现，短期内使用现有凭据签发新 token）
- **请求头**：`Authorization: Bearer <token>`
- **成功响应 data 示例**：与登录成功一致，仅 token 更新

### 5.5 POST `/api/v1/auth/logout`（可选）
- **用途**：前端态登出（JWT 无状态，后端返回 200 即可）
- **成功响应 data**：`null`

### 5.6 POST `/api/v1/auth/refresh`（可选）
- **用途**：使用现有有效令牌签发新的访问令牌
- **请求头**：`Authorization: Bearer <token>`
- **成功响应 data 示例**：与登录成功一致，仅 token 更新

### 5.7 DELETE `/api/v1/auth/users/{username}`（可选）
- **用途**：仅超级管理员可删除指定用户名的用户
- **请求头**：`Authorization: Bearer <token>`（需超级管理员）
- **规则**：禁止删除当前登录用户；用户不存在返回 404
- **成功响应 data 示例**：
```json
{
  "deleted": "user1"
}
```

---

## 六、数据模型与存储

### 6.1 表结构（`app/models/user.py`）
- `id: int` 主键，自增
- `username: str(50)` 唯一，索引，必填
- `email: str(100)` 唯一，可空
- `hashed_password: str(255)` 必填（bcrypt）
- `is_active: bool` 默认 `true`
- `is_superuser: bool` 默认 `false`（首个用户将被置为 `true`）
- `created_at, updated_at: datetime` 服务器时间

### 6.2 约束与规则
- 用户名最小长度 3，最大长度 50；密码最小长度 8（建议包含字母、数字、符号）
- `email` 可选；若提供需唯一且格式合法

---

## 七、安全与配置

- **算法**：JWT HS256（`settings.ALGORITHM`）
- **密钥**：`settings.SECRET_KEY`（生产环境必须覆写）
- **过期时间**：`settings.ACCESS_TOKEN_EXPIRE_MINUTES`（默认 30 分钟）
- **密码哈希**：`passlib CryptContext`（bcrypt）
- **Token 载荷**：`{ sub: <username>, exp: <utc> }`

---

## 八、实现计划（Tasks）

1. 定稿统一响应规范与错误码（与前端约定对齐）
2. 定义/校验 Pydantic 模型（登录/注册请求、用户响应）
3. 仓储/服务方法：`get_user_by_username`、`create_user`、`authenticate_user`
4. 首次运行守卫：当存在任意用户时拒绝注册
5. 实现端点：`POST /register`、`POST /login`、`GET /me`（必要）
6. 可选端点：`POST /refresh`、`POST /logout`
7. 统一响应封装工具（`utils/response.py`）与异常处理
8. Swagger 注释完善与示例响应
9. 单元测试与集成测试（见“测试用例”）

---

## 九、测试用例（关键场景）

- 首次运行注册成功：`users` 表为空 → 201/200 + 自动登录 token
- 非首次运行注册被拒：已有用户 → 403 或 409
- 登录成功：正确凭据 → 200 + token
- 登录失败：用户名不存在 / 密码错误 → 401
- 获取当前用户：携带有效 token → 返回用户信息
- 获取当前用户失败：无 token / 过期 / 无效 → 401
- Token 过期：到达 `exp` 后访问受保护接口 → 401

---

## 十、验收标准（Acceptance Criteria）

1. 当系统无用户时，可成功注册首个管理员，并返回 access_token；当已有用户时，注册被拒并返回明确错误码与消息。
2. 登录接口可返回可用的短期访问令牌，`/me` 能正确解析并返回用户信息。
3. 所有接口返回值遵循统一响应规范（`code/message/data`）。
4. 密码哈希、安全配置及令牌签发符合规范，无明文敏感信息入库。
5. 提供完整的 API 文档（Swagger 可见）与最小测试覆盖（包含正反用例）。

---

## 十一、与现有代码的契合点（当前仓库）

- `app/api/endpoints/auth.py`：已有路由骨架与 `get_current_user` 依赖；需补全注册/登录逻辑与统一响应。
- `app/core/security.py`：已提供 `create_access_token`、`verify_token`、`get_password_hash`、`verify_password`，与本任务契合。
- `app/models/user.py`：`User` 模型已定义，符合本任务需要。
- `app/api/routes.py`：已将 `auth` 路由挂载为 `/api/v1/auth`。

---

## 十二、进度追踪（Checklist）

- [x] 任务说明文档（本文件）
- [x] 统一响应规范与错误码定义（契约对齐）
- [x] 请求/响应 Pydantic 模型定义
- [x] 用户仓储与服务方法实现（查询/创建/认证）
- [x] 首次运行注册守卫实现
- [x] 依赖补充：email-validator 加入 requirements
- [x] 注册接口实现与测试（手动测试通过）
- [x] 登录接口实现与测试（手动测试通过）
- [x] 当前用户接口实现与测试（手动测试通过）
- [x] 可选：刷新/登出/删除端点（已实现）
- [x] 为 auth 端点补充 Swagger 注释（summary/description）
- [x] Swagger 示例响应与文档完善
- [x] 添加最小认证流程测试（用例已添加，手动测试通过）
- [x] 集成测试：前端 FE-02/FE-03 联调通过

---

## 十三、风险与对策

- **密钥配置不当**：默认 `SECRET_KEY` 被用于生产 → 提示并在文档强调必须覆盖；CI 检查（后续 F-04）。
- **爆破攻击**：登录限速/IP 限制暂不实现 → 通过日志监控与后续任务引入节流中间件。
- **前后端契约不一致**：本文件已定义统一响应结构，所有 `/auth*` 按此执行；联调时以本文件为准。

---

## 附：Curl 示例

```bash
# 首次注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"P@ssw0rd","email":"admin@example.com"}'

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"P@ssw0rd"}'

# 获取当前用户
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <jwt>"
```


