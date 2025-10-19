# FE-06: 元数据提供商设置页面（UI）任务说明书

## 一、任务信息

- 任务ID: FE-06
- 名称: 元数据提供商设置页面（合入配置中心卡片，TMDB 首发）
- 复杂度: M（约 3 PD）
- 优先级: P0
- 依赖: B-09（元数据提供商配置 API）
- 分支: `feat/fe-06-metadata-config-ui`（自 `develop` 拉出）

---

## 二、目标与范围（Scope）

- 目标：在 `/config` 页面新增“元数据（TMDB）”卡片，支持读取/保存/连接测试。
- 范围：
  - 表单字段：`api_key`（掩码/重置）、`language`、`region`、`include_adult`、`use_proxy`
  - 交互：保存、连接测试、提示反馈；测试遵循统一接口与代理策略
- 非范围：
  - 独立“元数据管理”页（等多提供商后演进）

---

## 三、现状与对齐

- 后端接口（B-09）：
  - `GET /api/config/tmdb`
  - `PUT /api/config/tmdb`
  - `POST /api/config/test-connection`（by_body：`service_name=tmdb` 支持 `proxy`；by_id：`use_proxy=true` 自动注入 proxy 服务）
  - `GET /api/config/tmdb/options`
- 统一响应：`{ code, message, data }`

---

## 四、数据契约与字段映射

- 读取：`api_key_masked` 只读回显；`extra_config` → `language/region/include_adult/use_proxy`
- 更新：未修改 `api_key` 不传；修改时明文提交
- 测试：
  - by_body：优先使用当前表单态；勾选 `use_proxy` 时拼装 `proxy` 传参
  - by_id：页面可选跳转入口，后端按 `use_proxy` 自动注入

---

## 五、页面与组件

- 位置：`views/config/index.vue` 新增卡片（复用 `ConfigFormCard.vue`）
- 组件：
  - 复用 `components/form/SecretInput.vue`
  - 可选新增 `AdvancedCollapse.vue`（如需分组呈现）
- 反馈：Toast / 错误提示 / 测试结果延迟

---

## 六、接口对接

- 读取：`GET /api/config/tmdb`
- 更新：`PUT /api/config/tmdb`
- 测试：`POST /api/config/test-connection`
- 选项：`GET /api/config/tmdb/options`

---

## 七、表单模型（前端）

```ts
type TmdbConfigForm = {
  api_key_masked?: string;  // 仅读展示
  api_key?: string;         // 用户修改时赋值
  language: string;         // 默认 zh-CN
  region: string;           // 默认 CN
  include_adult: boolean;   // 默认 false
  use_proxy: boolean;       // 默认 false（启用时走全局代理）
}
```

校验：`language/region` 来自选项；`use_proxy` 为布尔；`api_key` 仅在用户修改时出现。

---

## 八、错误处理与状态

- 统一响应处理；请求中按钮禁用；错误信息显式提示
- 敏感字段占位：读取后不回显明文，仅在用户输入时提交

---

## 九、验收标准（Acceptance Criteria）

1. `/config` 页面可完整读取并保存 TMDB 配置（敏感字段不回显明文）
2. 选项下拉正常可用；校验规则生效
3. 测试连接支持展示 `ok/latency_ms/diagnosis`，`use_proxy` 生效

---

## 十、测试要点

- 无/有 `api_key` 两种读写场景
- `use_proxy` 开关的直连/代理路径
- 错误 key / 超时 / 上游异常的提示与恢复

---

## 十一、实施计划（3 PD）

- Day 1：API 封装与类型补全；选项加载
- Day 2：表单与保存对接；掩码/重置处理
- Day 3：连接测试展示与细节完善；自测与走查

---

## 十二、进度清单（Checklist）

- [x] 任务文档（本文件）
- [x] API 层方法与类型
- [x] 页面实现与样式
- [x] 连接测试与错误反馈
- [ ] 与 B-09 联调通过（待后端接口测试）


