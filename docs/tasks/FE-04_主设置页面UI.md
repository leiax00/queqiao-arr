# FE-04: 主设置页面 UI 开发任务说明书

## 一、任务信息

- 任务ID: FE-04
- 名称: 主设置页面 UI（Sonarr / Prowlarr / 代理）
- 复杂度: L（约 5 PD）
- 优先级: P0
- 依赖: F-01（项目结构）、FE-02（注册）、FE-03（登录）
- 相关: FE-05（与后端 B-02 API 联调）、B-02（配置模块 API）

---

## 二、目标与范围（Scope）

- 目标：完成“主设置”相关的前端 UI 页面与表单交互，包括 Sonarr、Prowlarr、网络代理三大配置区块的页面结构、表单字段、校验与基础交互（加载/禁用/重置等）。
- 范围：
  - 在现有路由下完成 3 个配置页面的 UI 搭建：
    - `/config/sonarr`（`frontend/src/views/config/Sonarr.vue`）
    - `/config/prowlarr`（`frontend/src/views/config/Prowlarr.vue`）
    - `/config/proxy`（`frontend/src/views/config/Proxy.vue`）
  - 完成各页面的表单结构、输入验证、基础提示、按钮状态、统一样式。
  - 使用 Element Plus 组件一致化表单体验（标签/占位/帮助文案/错误信息）。
- 非范围（交由 FE-05）：
  - 与后端接口的真实读写、连接测试请求发送与结果处理。
  - 敏感字段（API Key、密码）真实回显策略与加密遮蔽逻辑（UI 仅提供占位及说明）。

---

## 三、信息架构与导航

- 路由层：复用 `layouts/default`，在侧边栏入口或设置菜单下进入。
- 页面结构：统一“页面标题 + 说明”区块 + “表单卡片”主体。
- 视觉风格：延续现有 `macaron-card` 风格与暗色模式适配。

---

## 四、页面与交互设计

### 4.1 Sonarr 配置（`/config/sonarr`）
- 表单字段：
  - `name` 名称（必填，≤ 50 字）
  - `url` 服务地址（必填，URL 格式）
  - `apiKey` API 密钥（必填，受控输入，密文显示/支持“显示/隐藏”切换）
  - `username` 基本认证用户名（可选）
  - `password` 基本认证密码（可选，密文显示）
  - `timeoutMs` 请求超时（可选，数值，默认 3000-10000 建议）
  - `isActive` 启用开关（布尔）
  
  - 代理相关字段（服务级覆盖）：
    - `proxyMode` 代理模式（`inherit` 继承全局 / `custom` 自定义 / `direct` 直连）
    - 当为 `custom` 时：`httpProxy`、`httpsProxy`、`socks5Proxy`、`noProxy`
    - 说明：生效优先级为“服务级覆盖 > 全局默认”；测试连接应使用当前生效代理
- 操作：
  - 保存（disabled：表单未变更或校验未通过时）
  - 测试连接（FE-04 显示交互占位与 Loading；真实调用交由 FE-05）
  - 重置（恢复到页面初始值；FE-04 初始值由静态/占位）
- 校验规则：
  - `name`：必填，长度 1-50
  - `url`：必填，合法 URL（http/https）
  - `apiKey`：必填，长度 ≥ 8（占位说明：已保存密钥不会回显明文）
  - `timeoutMs`：可选，正整数，建议范围 1000-15000

### 4.2 Prowlarr 配置（`/config/prowlarr`）
- 字段与 Sonarr 类似：`name`、`url`、`apiKey`、`username`、`password`、`timeoutMs`、`isActive`。
- 交互与校验同 Sonarr；文案区分索引器语境（例如“配置 Prowlarr 索引器连接与搜索参数”）。
  
  - 代理相关字段（服务级覆盖）：
    - `proxyMode` 代理模式（`inherit` / `custom` / `direct`）
    - 当为 `custom` 时：`httpProxy`、`httpsProxy`、`socks5Proxy`、`noProxy`
    - 说明：生效优先级为“服务级覆盖 > 全局默认”；测试连接应使用当前生效代理

### 4.3 代理设置（`/config/proxy`）
- 表单字段：
  - `enabled` 启用代理（布尔）
  - `httpProxy` HTTP 代理地址（可选，URL/host:port）
  - `httpsProxy` HTTPS 代理地址（可选，URL/host:port）
  - `socks5Proxy` SOCKS5 代理地址（可选，socks5://host:port）
  - `noProxy` 绕过代理的域名列表（可选，逗号分隔）
  - `scope` 作用范围（多选）：`tmdb`（元数据）、`prowlarr`（索引搜索）、`sonarr`（系统调用）
- 操作：
  - 保存、重置
  - 连通性自检（占位，真实调用 FE-05 实现；建议对 TMDB 做 ping/health 检测并显示耗时）
- 校验规则：
  - 地址类字段：校验格式；当 `enabled=true` 时至少填写一个有效代理地址。
  - `noProxy`：按逗号分隔，支持空格清洗与重复去重提示。

### 4.4 代理策略与优先级（UI）

- 全局默认：在“代理设置”中配置 `enabled` 与默认代理地址，并通过 `scope` 指定默认应用范围（建议默认仅勾选 `tmdb`）。
- 服务级覆盖：在 Sonarr/Prowlarr 页面提供 `proxyMode`；当选择 `custom` 时可填写服务专用代理；当选择 `direct` 时强制直连。
- 优先级：服务级覆盖 > 全局默认；测试连接与后续实际请求应基于“生效代理”进行。
- 兼容性：保留 `noProxy`（全局与服务级）共同生效，用于覆盖局部域名直连场景。

---

## 五、组件与技术方案

- 技术栈：Vue 3 + TypeScript + Element Plus + Pinia（仅本地 UI 状态）。
- 组件建议：
  - `ConfigFormCard`：统一卡片容器（标题、副标题、操作栏插槽）。
  - `SecretInput`：密钥/密码输入组件（显示/隐藏、粘贴拦截、复制按钮可选）。
  - `ConnectionResult`：测试连接结果展示组件（状态/耗时/消息）。
- 状态管理：FE-04 阶段使用组件本地 `ref` 存储编辑态，保留与 FE-05 对接的钩子方法占位（`onSave`/`onTest`）。

---

## 六、样式与可用性

- 输入框对齐、标签对齐与错误提示一致化；错误信息放置在输入下方。
- 按钮状态：
  - 未变更或校验失败 → 保存禁用
  - 测试中 → 禁用相应按钮并显示 Loading
- 文案：对敏感字段提供说明（例如“出于安全考虑，已保存的密钥不会回显明文”）。
- 可访问性：为输入/按钮添加可读 `aria-label`，保证键盘可导航与聚焦态可视。

---

## 七、与后端契约（占位说明，联调移交 FE-05）

- 后端参考：`docs/tasks/B-02_配置模块API.md`，统一前缀 `/api/v1/config/*`。
- 前端当前占位 API：`frontend/src/api/config.ts` 中存在与 B-02 不一致的路径（如 `/config/sonarr`、`/config/prowlarr`、`/config/proxy`、`/config/{type}/test`）。
- 约定：FE-04 仅实现 UI，不触发真实请求；FE-05 将完成：
  - API 路径统一与适配（建议收敛至 B-02 的 REST 设计与 `test-connection` 端点）。
  - 敏感字段遮蔽与占位提示的联动处理。

---

## 八、验收标准（Acceptance Criteria）

1. 三个配置页面均具备完整表单字段、占位说明与校验规则，样式一致。
2. 表单的保存/测试/重置按钮具备合理的启用/禁用与 Loading 交互（占位逻辑即可）。
3. 密钥与密码输入提供“显示/隐藏”切换，默认密文显示；提供安全提示文案。
4. UI 在暗色/亮色模式下均显示清晰；在常见分辨率下布局稳健。
5. 路由可直达三页面并通过面包屑/标题清晰标识位置。

---

## 九、测试要点（UI 层）

- 表单渲染：字段与标签完整，默认值与占位符正确。
- 校验：必填项拦截、生效提示、边界长度/格式校验。
- 按钮：在不同状态下的禁用/加载态切换正确。
- 可访问性：键盘导航、焦点样式、屏幕阅读器标签。
- 暗黑模式：颜色对比度与可读性。

---

## 十、实现要点与拆解

- 为每个视图页面引入统一的表单容器与操作栏插槽，减少样式分散。
- 将校验规则抽取为 `rules` 对象，便于后续 FE-05 共享与单测。
- 为“测试连接”预留 `onTest()` 钩子（仅 UI 态变化），后续接入 B-02 的 `test-connection`。
- 对敏感输入使用受控组件，禁止浏览器自动填充（`autocomplete="new-password"`）。

---

## 十一、进度追踪（Checklist）

- [x] 任务文档（本文件）
- [ ] 低保真交互稿（字段与按钮排布）
- [ ] Sonarr 表单 UI 完成
- [ ] Prowlarr 表单 UI 完成
- [ ] 代理设置表单 UI 完成
- [ ] 统一表单校验与错误提示
- [ ] 按钮状态/Loading/重置逻辑完成
- [ ] 暗黑模式与可访问性检查
- [ ] UI 自测与截图记录

---

## 十二、里程碑与估算（5 PD）

- Day 1：交互稿与表单字段清单确认；搭建 `ConfigFormCard` 原型。
- Day 2：完成 Sonarr 表单 UI 与校验。
- Day 3：完成 Prowlarr 表单 UI 与校验。
- Day 4：完成 代理设置 UI 与校验；统一 Loading/禁用态。
- Day 5：整体样式打磨、无障碍与暗黑模式检查、补充文档与截图。

---

## 十三、风险与对策

- 契约差异：前端现有路径与 B-02 设计不一致 → FE-05 做统一适配层；FE-04 避免写死具体路径。
- 敏感字段回显策略：UI 需有明确说明，FE-05 承接具体遮蔽与占位处理。
- 代理设置复杂度：多种代理并存与 `no_proxy` 语义 → 明确前端输入格式与清洗规则。

---

## 十四、参考与附件

- 后端 API 设计：`docs/tasks/B-02_配置模块API.md`
- 现有路由：`frontend/src/router/index.ts`
- 视图文件：`frontend/src/views/config/Sonarr.vue`、`Prowlarr.vue`、`Proxy.vue`


