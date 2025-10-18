# FE-06 元数据提供商设置页面（UI）

> 版本: v0.1（草案）  
> 日期: 2025-10-18  
> 关联后端: B-09 元数据提供商配置API（TMDB）

---

## 1. 背景与目标

当前配置中心 `/config` 已包含 Sonarr、Prowlarr、代理三个区块。短期内仅支持单一元数据提供商 TMDB，若将其单独成页会显得稀疏且增加导航成本。为保持一致体验与最小改动，本任务将「元数据（TMDB）」以独立卡片的形式合并进现有配置中心页面（非 Tab 方案），同时为未来支持多提供商预留入口与演进路径。

目标：

- 在 `/config` 页面新增「元数据（TMDB）」卡片，支持读取/保存/连接测试
- 字段：`api_key`（掩码/重置）、`language`、`region`、`include_adult`、`use_proxy`
- 操作体验与现有区块一致（保存、测试、提示）

---

## 2. 页面与布局

- 位置：现有 `views/config/index.vue` 内，新增一张卡片（`ConfigFormCard.vue` 样式）
- 区块结构：
  - 标题：元数据（TMDB）
  - 基础设置：`api_key`（掩码显示 + 重置按钮）、`language`、`region`、`include_adult`
  - 代理使用：`use_proxy`（开关，使用全局代理）
  - 操作区：保存、连接测试；右上角灰化「管理多个提供商」按钮（占位，未来跳转 `/config/providers`）
- 辅助：
  - 连接测试结果展示（成功/失败、延迟 ms、诊断信息）
  - 小徽标指示：代理是否启用、限速阈值

---

## 3. 组件复用与新增

- 复用：
  - `components/common/ConfigFormCard.vue`（卡片壳）
  - `components/form/SecretInput.vue`（密钥掩码/重置）
- 新增（如需）：
  - `components/common/AdvancedCollapse.vue`（统一折叠容器，可选）
  - `components/common/KeyValueRows.vue`（可选代理覆盖的三行输入组合）

---

## 4. 接口对接

- 读取：`GET /api/config/tmdb`
- 更新：`PUT /api/config/tmdb`
- 测试：`POST /api/config/tmdb/test`
- 选项：`GET /api/config/tmdb/options`（语言/地区）

交互约定：

- 初次加载：并行请求 配置 + 选项；配置中的 `api_key` 为掩码字符串
- 保存：未修改 `api_key` 时不传该字段；修改时由 `SecretInput` 以明文提交
- use_proxy：仅控制是否启用全局代理，不提供每服务代理覆盖
- 测试：优先使用当前表单态（未保存的临时值）执行连通性验证

---

## 5. 表单模型（前端）

```ts
type TmdbConfigForm = {
  api_key_masked?: string;     // 仅读展示
  api_key?: string;            // 用户修改时赋值
  language: string;            // 默认 zh-CN
  region: string;              // 默认 CN
  include_adult: boolean;      // 默认 false
  use_proxy: boolean;          // 默认 false（启用时走全局代理）
}
```

校验与约束：

- `language/region` 必须来自选项接口；
- `use_proxy` 为布尔开关；
- `api_key` 不回显明文，仅在用户主动“重置/更改”时出现输入框。

---

## 6. 状态管理与数据流

- API 封装：在 `frontend/src/api/config.ts` 新增 TMDB 相关方法（或新建 `metadata.ts` 以聚合元数据接口）
- 页面加载：`onMounted` 并发获取配置与选项；加载态与错误提示复用现有反馈机制
- 保存流程：禁用按钮 + 提交中 loading；成功后刷新只读态（含掩码）
- 测试流程：读取当前表单值调用测试端点，展示延迟与诊断；失败保留表单值不回滚

---

## 7. 可观测性与体验

- 空状态：未配置 `api_key` 时在卡片中部显示提示与引导
- 成功反馈：保存成功后轻量 Toast；测试成功显示延迟
- 失败反馈：表单字段级错误 + 卡片级错误信息；所有密钥相关提示脱敏

---

## 8. 可扩展性（未来多提供商）

- 入口演进：当提供商数量 > 1 或需要排序/启用开关时，抽离到 `/config/providers` 独立页面；当前卡片保留为入口跳转
- 复用：将本卡片内表单抽象为 `ProviderConfigForm.vue`，以 `provider` 参数驱动字段渲染与选项加载
- 接口演进：后端统一到 `service_name`（如 `tmdb`、`bangumi`），前端根据 `service_name` 切换 schema 与选项源

---

## 9. 验收标准（UI/联调）

- 在 `/config` 页面可完整查看并保存 TMDB 配置；`api_key` 掩码展示与重置流正确
- 选项下拉可用，`language/region` 校验生效
- 连接测试可返回 `ok/latency_ms/diagnosis` 并正确展示
- use_proxy 开关生效：开启时走全局代理，关闭时直连

---

## 10. 联调清单

- 后端：B-09 提供四个端点（GET/PUT/POST test/GET options）
- 前端：新增 API 方法、表单页面卡片、掩码与重置逻辑、use_proxy 开关、测试结果展示
- 自测：
  - 无 `api_key` → 配置保存报错提示（或后端允许空则仅测试失败）
  - 错误的 `api_key` → 测试返回 `invalid_api_key`
  - 超时/上游不可达 → 测试返回 `timeout/502` 等诊断

---

## 11. 变更记录

- v0.1（2025-10-18）：首次创建；确定采用「合并入 `/config` 页面卡片（非 Tab）」方案，定义字段、交互与联调清单。

---

## 12. 任务进度（Rolling）

- [x] 方案确定：合入 `/config` 页为独立卡片（非 Tab），字段最小化 + use_proxy（2025-10-18）
- [x] 编写 UI 文档（表单模型、交互与接口对接）（2025-10-18）
- [ ] 新增前端 API 方法与表单组件接线
- [ ] 页面实现与样式完善（卡片、掩码、use_proxy 开关、测试结果展示）
- [ ] 与 B-09 接口联调与验收


