# B-04: TMDB API 客户端封装 任务说明书

## 一、任务信息
- 任务ID: B-04
- 名称: TMDB API 客户端封装（中文别名查询能力）
- 复杂度: M（约 3 PD）
- 优先级: P0
- 依赖: B-10（外部服务客户端层）、B-09（TMDB 配置）
- 被依赖: B-06（标题解析器 V1）、B-08（端到端编排）
- 当前分支: `feature/B-04-tmdb-client`
- 状态: 进行中

---

## 二、目标与范围（Scope）
- 目标：在现有客户端层基础上，完善 `TMDBClient` 的查询能力，支持根据剧集信息查询中文别名，为后续标题解析与搜索增强提供支撑。
- 范围：
  - 完善 `backend/app/services/clients/tmdb.py`：补全查询方法、错误处理与参数约束
  - 支持按 `language/region`、`include_adult` 等配置查询
  - 统一遵循基类 `ExternalServiceClient` 的请求封装与代理/超时策略
  - 输出结构便于后续模块消费（解析器、编排）
  - 新增后端查询端点（供前端直接调用）：`/api/v1/tmdb/search`、`/api/v1/tmdb/tv/{tv_id}`、`/api/v1/tmdb/tv/{tv_id}/alternative_titles`
- 非范围：
  - 标题解析器实现（B-06）
  - Torznab XML 生成（B-07）
  - 端到端编排（B-08）

---

## 三、设计与目录结构
- 目录：
```
backend/app/services/clients/
  base.py        # 已存在：统一请求封装/代理/超时
  tmdb.py        # 本任务完善此文件
  factory.py     # 已存在：按 service_name 生成客户端
```

### 3.1 TMDB 客户端设计要点
- API Key 通过查询参数 `api_key` 传递（已在 `tmdb.py` 覆盖 Header 构建）
- 统一通过 `_get()` 发起请求；沿用基类异常映射
- 方法与返回：均返回 `tuple[bool, Any]`，其中 `Any` 为数据或错误说明
- 输入参数校验：对 `language`、`region`、分页参数等进行基本校验（轻量，详细校验由 B-09 选项接口提供）

### 3.2 计划提供/完善的方法
- `search_tv(query: str, language: str = "zh-CN", page: int = 1)`：搜索剧集
- `get_tv_details(tv_id: int, language: str = "zh-CN")`：获取剧集详情（含名称、别名计数等）
- `get_alternative_titles(tv_id: int, country: str | None = None)`：获取替代标题（可按国家过滤，如 `CN/HK/TW`）
- `discover_tv(params: dict)`：按条件发现（可选，若 B-06 需求明确则实现）
- `check_status()`：沿用 `GET /configuration` 健康检查

注：已存在的方法将增强参数与结果映射，保持向后兼容。

---

## 四、业务规则（Business Rules）
1. `language/region/include_adult` 等参数默认从配置（B-09）层面提供，客户端方法允许覆盖但不强制。
2. 严格避免 API Key 泄漏：日志中不打印明文；错误信息保持泛化描述。
3. 代理策略：沿用基类逻辑；由调用方注入 `proxies`（B-09 中 `use_proxy=true` 时由上层注入）。
4. 速率/重试：当前不实现重试；由上层编排在 B-08 统一考虑。

---

## 五、API 映射（TMDB v3 参考）
- `GET /search/tv`：参数 `query, language, page, include_adult`
- `GET /tv/{tv_id}`：参数 `language`
- `GET /tv/{tv_id}/alternative_titles`：参数 `api_key`（可过滤 `country`）
- `GET /configuration`：健康检查

参考返回字段（精简）：
- `search_tv`：`results[] -> { id, name, original_name, origin_country, first_air_date }`
- `get_tv_details`：`{ id, name, original_name, alternative_titles? }`
- `get_alternative_titles`：`titles[] -> { title, iso_3166_1 }`

### 5.x 后端查询端点（本系统）
- 路由与文件：`app/api/endpoints/tmdb.py`，在 `app/api/routes.py` 以前缀 `/api/v1/tmdb` 挂载
- 鉴权：需登录（沿用 `get_current_user`）
- 运行时参数：自动读取启用中的 `service_name=tmdb` 配置，解密 `api_key`；若 `extra_config.use_proxy=true` 则注入全局代理

1) 搜索剧集
   - Method: `GET /api/v1/tmdb/search`
   - Query: `query`(必填), `language`=`zh-CN`, `page`>=1, `include_adult`=false
   - 200 示例：
   ```json
   {
     "code": 200,
     "message": "OK",
     "data": {
       "page": 1,
       "total_pages": 5,
       "results": [
         { "id": 123, "name": "名称", "original_name": "Original", "first_air_date": "2020-01-01" }
       ]
     }
   }
   ```

2) 获取剧集详情
   - Method: `GET /api/v1/tmdb/tv/{tv_id}`
   - Query: `language`=`zh-CN`
   - 200：原样透传 TMDB 详情（字段精简由消费方决定）

3) 获取替代标题
   - Method: `GET /api/v1/tmdb/tv/{tv_id}/alternative_titles`
   - Query: `country`（可选，ISO 3166-1）
   - 200 示例：
   ```json
   {
     "code": 200,
     "message": "OK",
     "data": {
       "tv_id": 123,
       "titles": [
         { "title": "国漫名", "country": "CN" }
       ]
     }
   }
   ```

错误语义与示例：
- 400：缺少或非法参数（如 tv_id 非正整数、TMDB 配置缺少 api_key）
  - 示例（query 为空字符串触发客户端校验）：
    ```json
    {
      "code": 400,
      "message": "参数错误: query 不能为空",
      "data": null
    }
    ```
  - 示例（tv_id 非法）：
    ```json
    {
      "code": 400,
      "message": "参数错误: tv_id 必须为正整数",
      "data": null
    }
    ```
- 401：未认证（FastAPI 统一认证错误格式）
  - 示例：
    ```json
    {
      "detail": "Not authenticated"
    }
    ```
- 404：未找到启用中的 TMDB 配置
  - 示例：
    ```json
    {
      "detail": "未找到启用中的 TMDB 配置"
    }
    ```
- 502：上游 TMDB 返回错误或网络异常（统一为 `error_response` 提示）
  - 示例（网络失败）：
    ```json
    {
      "code": 502,
      "message": "TMDB 连接失败: 网络请求失败: https://api.themoviedb.org/3/search/tv",
      "data": null
    }
    ```

---

## 六、输出契约（供后续模块消费）
- 别名统一结构：
```json
{
  "ok": true,
  "tv_id": 123,
  "titles": [
    { "title": "国漫名", "country": "CN" },
    { "title": "中文（香港）", "country": "HK" }
  ]
}
```
- 搜索统一结构：
```json
{
  "ok": true,
  "results": [
    { "id": 123, "name": "名称", "original_name": "Original", "first_air_date": "2020-01-01" }
  ],
  "page": 1,
  "total_pages": 5
}
```

### 6.1 字段映射（TMDB → 内部结构）

1) 搜索结果 `/search`
- 外层包装：由本系统统一添加 `code/message/data`，TMDB 原始响应不包含这三项。
- `data.page`：来源于 TMDB `/search/tv` 根字段 `page`。
- `data.total_pages`：来源于 TMDB 根字段 `total_pages`。
- `data.results[].id`：来源于 TMDB `results[].id`。
- `data.results[].name`：来源于 TMDB `results[].name`。
- `data.results[].original_name`：来源于 TMDB `results[].original_name`。
- `data.results[].first_air_date`：来源于 TMDB `results[].first_air_date`。
- `data.results[].origin_country`：来源于 TMDB `results[].origin_country`。
- 其余 TMDB 字段（如 `overview/popularity/backdrop_path` 等）当前不透出，由后续需求再决定是否扩展。

2) 剧集详情 `/tv/{tv_id}`
- 外层包装：仍由本系统统一添加 `code/message/data`。
- `data`：当前透传 TMDB `/tv/{tv_id}` 的完整 JSON 响应，字段一一对应 TMDB 文档。
- 后续若需要精简结构，可参考内部模型 `TMDBDetailsResponse` 的字段：
  - `id`：TMDB `id`
  - `name`：TMDB `name`
  - `original_name`：TMDB `original_name`
  - `first_air_date`：TMDB `first_air_date`
  - `number_of_seasons`：TMDB `number_of_seasons`
  - `number_of_episodes`：TMDB `number_of_episodes`
  - `overview`：TMDB `overview`

3) 替代标题 `/tv/{tv_id}/alternative_titles`
- 外层包装：同样由本系统添加 `code/message/data`。
- `data.tv_id`：来源于路径参数 `{tv_id}`，等价于 TMDB 响应中的 `id`。
- `data.titles[].title`：来源于 TMDB `titles[].title`。
- `data.titles[].country`：来源于 TMDB `titles[].iso_3166_1`（ISO 3166-1 国家码，例 `CN/HK/TW`）。
- TMDB `titles[]` 中其他字段（如 `type` 等）暂不透出。

### 6.2 面向 B-06 的统一数据结构说明

后续标题解析器（B-06）在需要访问 TMDB 数据时，推荐只依赖本节给出的统一结构，而不是直接耦合 TMDB 原始字段。

1) 搜索结果统一结构

示例：
```json
{
  "ok": true,
  "results": [
    {
      "id": 123,
      "name": "名称",
      "original_name": "Original",
      "first_air_date": "2020-01-01",
      "origin_country": ["CN"]
    }
  ],
  "page": 1,
  "total_pages": 5
}
```

字段说明：
- `ok`：布尔值，表示本次搜索调用是否被上游视为成功（B-06 可用来快速短路逻辑）；当前端点未直接返回该字段，B-06 可以在内部适配层中根据 HTTP 状态与 `code` 字段自行生成。
- `results[]`：剧集列表，每一项代表 TMDB 中的一部剧集。
  - `id`：TMDB 剧集 ID，后续获取详情与别名的关键主键。
  - `name`：本地化名称（如中文名），供 UI 展示与调试使用。
  - `original_name`：原始名称（通常为日文/英文），用于与资源标题做匹配参考。
  - `first_air_date`：首播日期（`YYYY-MM-DD`），可用于消歧或规则匹配。
  - `origin_country`：出品国家代码列表（ISO 3166-1），供规则或展示使用。
- `page`：当前页码，用于分页拉取更多结果时维持游标。
- `total_pages`：总页数，用于判断是否还有更多结果。

2) 剧集详情统一结构（建议）

当前详情端点透传 TMDB 完整 JSON，B-06 若需要使用，可定义内部视图结构：

```json
{
  "ok": true,
  "id": 123,
  "name": "名称",
  "original_name": "Original",
  "first_air_date": "2020-01-01",
  "number_of_seasons": 2,
  "number_of_episodes": 24,
  "overview": "剧情简介……"
}
```

字段说明（对应 `TMDBDetailsResponse`）：
- `ok`：同上，表示获取详情是否成功（可由 B-06 适配层生成）。
- `id`：TMDB 剧集 ID。
- `name` / `original_name`：与搜索结构含义一致。
- `first_air_date`：首播日期。
- `number_of_seasons` / `number_of_episodes`：季数与总集数，可用于规则过滤或展示。
- `overview`：剧情简介，供 UI 或辅助判断使用。

3) 替代标题统一结构

示例：
```json
{
  "ok": true,
  "tv_id": 123,
  "titles": [
    { "title": "国漫名", "country": "CN" },
    { "title": "中文（香港）", "country": "HK" }
  ]
}
```

字段说明（对应 `TMDBAlternativeTitlesResponse`）：
- `ok`：同上，表示别名查询是否成功（可由 B-06 适配层生成）。
- `tv_id`：TMDB 剧集 ID，与搜索/详情中的 `id` 一致，是关联关键。
- `titles[]`：别名列表。
  - `title`：该地区的剧集名称（本地化名称），是 B-06 做“中文别名匹配”的核心字段。
  - `country`：两位国家码（如 `CN/HK/TW`），B-06 可根据偏好或策略筛选（例如优先 `CN`，退化到 `HK/TW`）。

> 约定：B-06 不直接依赖 TMDB 原始响应，而通过一个轻量适配层，将 `/search`、`/tv/{id}`、`/tv/{id}/alternative_titles` 的返回统一整理为本节定义的结构，再交给解析器核心逻辑消费。

---

## 七、配置驱动的默认参数策略

### 7.1 配置来源与默认值

- 配置来源：启用中的 `ServiceConfig(service_name='tmdb', service_type='metadata')` 记录，其 `extra_config` 字段。
- 参与默认策略的字段（与 B-09 保持一致）：
  - `extra_config.language: string` - 语言代码，默认值：`"zh-CN"`。
  - `extra_config.region: string` - 地区代码，默认值：`"CN"`。
  - `extra_config.include_adult: boolean` - 是否包含成人内容，默认值：`false`。
- 运行时加载逻辑（`_load_tmdb_runtime` + `get_tmdb_client`）：
  - 读取数据库中的 TMDB 配置，优先使用第一条启用中的记录。
  - 解密 `api_key`，解析 `extra_config` 为字典。
  - 构造默认值并注入 `TMDBClient` 实例：
    - `default_language = extra.get("language") or "zh-CN"`
    - `default_region = extra.get("region") or "CN"`
    - `default_include_adult = bool(extra.get("include_adult"))`（缺省视为 `False`）。

### 7.2 参数优先级规则

整体遵循「调用方覆盖配置，配置覆盖代码内置默认」的原则：

1. **显式请求参数（per-call）最高优先级**
   - 例如：`/tmdb/search?language=zh-TW&include_adult=true`。
   - 只要调用方明确传入（且通过基本校验），就优先使用该值。
2. **TMDB 配置中的 `extra_config` 作为全局默认**
   - 当前请求未显式传入的字段，优先回落到 `extra_config` 中对应值。
3. **代码内置兜底值（硬编码常量）最低优先级**
   - 当既没有请求参数，又没有配置（或配置为空/非法）时，才使用：
     - `language = "zh-CN"`；
     - `region = "CN"`；
     - `include_adult = False`。

> 结论：`请求参数 > extra_config > 硬编码默认值`。

### 7.3 TMDBClient 中的落地

- 扩展 `TMDBClient` 构造函数，接收配置驱动默认值：
  - 新增参数：`default_language: str | None`、`default_region: str | None`、`default_include_adult: bool | None`。
  - 在 `__init__` 中设置属性：
    - `self.default_language = (default_language or "zh-CN").strip() or "zh-CN"`；
    - `self.default_region = (default_region or "CN").strip() or "CN"`；
    - `self.default_include_adult = default_include_adult if isinstance(default_include_adult, bool) else False`。
- 方法内应用默认策略：
  - `search_tv`：
    - `language` 允许为 `None`，内部：为空或非法时使用 `self.default_language`。
    - `include_adult` 允许为 `None`，内部：为 `None` 或非法时使用 `self.default_include_adult`。
  - `get_tv_details`：
    - `language` 允许为 `None`，内部：未提供或为空时使用 `self.default_language`。
  - `get_alternative_titles`：
    - `country` 允许为 `None`，内部：`effective_country = country or self.default_region`，再做两位大写字母校验。

### 7.4 端点层的具体行为

1) `GET /api/v1/tmdb/search`

- 请求模型 `TMDBSearchQuery`：
  - `language: Optional[str]`，默认 `None`，表示「由配置决定」。
  - `include_adult: Optional[bool]`，默认 `None`，表示「由配置决定」。
- 端点逻辑：
  - 提取参数后：
    - `language = params.language or client.default_language`；
    - `include_adult = client.default_include_adult if params.include_adult is None else params.include_adult`。
  - 调用 `client.search_tv(...)`。

2) `GET /api/v1/tmdb/tv/{tv_id}`

- Query `language` 为可选，如果未提供：
  - 使用 `client.default_language` 调用 `get_tv_details`。

3) `GET /api/v1/tmdb/tv/{tv_id}/alternative_titles`

- Query `country` 为可选，如果未提供：
  - 在端点层先计算 `effective_country = country or client.default_region`，再调用 `get_alternative_titles`。
  - 客户端内部仍会做 2 位大写字母校验。

### 7.5 与 B-09 / B-06 的关系

- 与 B-09：
  - `extra_config.language/region/include_adult` 成为 TMDB 查询行为的实际入口默认值，配置变更后所有调用自动受影响。
- 与 B-06：
  - B-06 仅消费统一结构（第六节），默认策略在客户端与端点层已经应用完毕。
  - 如 B-06 需要特殊场景（例如强制使用其他语言或包含成人内容），可以通过端点参数临时覆盖配置默认值。

---

## 八、TMDB 查询结果持久化与映射策略（替代轻量缓存）

> 结论：本任务 **不再实现进程内缓存**，而是将“关键词 → TMDB 剧集”的映射结果持久化入库，由后续的元数据模块/编排模块作为主数据源使用。

### 8.1 目标与基本思路

- 目标：
  - 避免每次解析或搜索都直接访问 TMDB，而是尽量复用既有的本地 TMDB 数据。
  - 让“关键词 / TVDB ID / 本地番剧实体”和“TMDB 剧集 ID”之间形成稳定的映射关系，方便后续复用。
- 基本思路：
  - 第一次需要 TMDB 数据时，通过 `/search` / `/tv/{id}` 等接口查到目标 `tmdb_id`。
  - 将该 `tmdb_id` 及其 TMDB 详情、别名信息一并写入本地元数据存储（例如 `tmdb_tv` 表）。
  - 将“关键词 / TVDB ID / 本地番剧 ID”等与 `tmdb_id` 建立关联（例如 `tmdb_keyword_mapping` / `tvdb_tmdb_mapping` 表）。
  - 后续再遇到相同关键词或同一部番剧时，优先从本地映射表和 TMDB 元数据表读取，而不是重新请求 TMDB。

### 8.2 关键词与 TMDB ID 的映射

建议的逻辑流程（在后续 B-06/B-08 中落地）：

1. 解析器或前端传入关键词 `keyword`（可以是番剧中文名/原名/常用别名）。
2. 在本地“关键词映射表”中查询：
   - 若存在记录：`(keyword, tmdb_id)`，则直接使用该 `tmdb_id`，并从本地 TMDB 表获取详细信息。
   - 若不存在记录：
     - 调用 TMDB `/search/tv` 接口获取候选列表；
     - 根据规则（例如年份、地区、用户手动确认）选出一个 `tmdb_id`；
     - 将 `(keyword, tmdb_id)` 写入关键词映射表，后续再次使用该关键词时直接命中本地。
3. 对于一部番剧往往存在多个关联关键词（别名）：
   - 可以为同一个 `tmdb_id` 维护多条 `(keyword, tmdb_id)` 记录；
   - 也可以在本地番剧表上维护“推荐关键词列表”，方便后续匹配和 UI 展示。

### 8.3 与 TVDB / Sonarr 的 ID 映射

考虑 Sonarr 及 TVDB 生态的实际情况：

- Sonarr 本身常以 `tvdb_id` 作为主键；
- 本系统只要建立 `tvdb_id ↔ tmdb_id` 的映射，即可在不同元数据源之间对齐同一部番剧。

建议：

- 维护一张“跨源 ID 映射表”，字段类似：
  - `tvdb_id`
  - `tmdb_id`
  - `local_series_id`（本地番剧实体 ID，可选）
  - `source` / `note` / `created_at` 等元数据
- 解析流程：
  - 若已有 `tvdb_id`：优先查映射表获取 `tmdb_id`，从本地 TMDB 元数据表拿详情；
  - 若尚无映射：可以用 TVDB 提供的信息（名称、年份等）作为关键词/条件去 TMDB 搜索，人工或规则选中后，建立 `tvdb_id ↔ tmdb_id` 映射并落库。

### 8.4 B-04 与后续任务的边界

- 在 B-04 中：
  - 仅负责提供稳定的 TMDB 客户端与查询端点（search/detail/alternative_titles），以及清晰的输出契约。
  - 不在客户端层实现任何缓存/落库逻辑，以保持职责单一。
- 在后续 B-06/B-08 或新的“元数据存储”任务中：
  - 负责定义本地 TMDB 元数据表结构（如 `tmdb_tv`、`tmdb_alternative_title`）。
  - 定义关键词映射、TVDB ↔ TMDB 映射的表结构和写入/更新策略。
  - 将“关键词解析 → TMDB 查询 → 映射落库”的业务流程固化下来，并优先使用本地数据。

> 因此，本节结论是：**不实现运行时内存缓存，而是通过持久化映射和本地元数据存储来减少 TMDB 请求**。B-04 仅提供查询能力和数据契约，具体落库策略交由 B-06/B-08 设计与实现。

---

## 九、验收标准（Acceptance Criteria）
1. `TMDBClient` 完成上述方法的实现或增强，参数支持 `language/region/include_adult/page`（必要时）。
2. 连接测试 `check_status()` 在有效 `api_key` 下返回成功；异常路径返回可读信息。
3. 输出契约满足 B-06 消费需求，字段命名清晰、单位一致。
4. 代理/超时配置可控，遵循基类实现；错误不泄漏敏感信息。
5. 文档与示例完整，包含典型调用样例。

---

## 十、实施计划（3 PD）
- Day 1：梳理方法清单与签名，补齐 `search_tv`/`get_alternative_titles` 参数，添加 `get_tv_details`
- Day 2：实现结果映射与基本校验；补充日志要点与错误语义
- Day 3：编写使用示例与最小测试用例草案（不提交实现代码，待审核后进行）

---

## 十一、风险与对策
- 上游速率限制或字段变化：通过结果映射与容错字段访问降低耦合
- 中文别名覆盖有限：支持多地区获取并合并去重
- 代理/网络不稳定：提供超时设置与清晰错误提示

---

## 十二、示例用法（草案，仅供说明）
```python
from app.services.clients import make_client

async def example_usage():
    # 1. 创建客户端 (通常由依赖注入自动完成)
    # 注意：实际使用中应优先使用 get_tmdb_client 依赖
    client = make_client(
        "tmdb",
        api_key="<your_api_key>",
        default_language="zh-CN",
        default_region="CN"
    )

    # 2. 搜索剧集
    ok, result = client.search_tv(query="凡人修仙传")
    if ok:
        print(f"搜索成功，共找到 {result.get('total_results')} 条结果")
        if result.get("results"):
            tv_id = result["results"][0]["id"]
            print(f"首个结果 ID: {tv_id}")
            
            # 3. 获取详情
            ok_detail, detail = client.get_tv_details(tv_id)
            if ok_detail:
                print(f"剧集名称: {detail.get('name')}")
                print(f"季数: {detail.get('number_of_seasons')}")

            # 4. 获取中文别名
            ok_alias, aliases = client.get_alternative_titles(tv_id, country="CN")
            if ok_alias:
                cn_titles = [t['title'] for t in aliases.get('titles', []) if t.get('iso_3166_1') == 'CN']
                print(f"中国大陆别名: {cn_titles}")
    else:
        print(f"搜索失败: {result}")

    # 5. 错误处理示例
    ok_err, err_msg = client.search_tv(query="")
    if not ok_err:
        print(f"预期内的错误: {err_msg}")  # 输出: 参数错误: query 不能为空
```

---

## 十三、进度清单（Checklist）
- [x] 创建分支 `feature/B-04-tmdb-client`（当前）
- [x] 审阅现有 `base.py`/`tmdb.py`，对齐返回与异常风格（当前）
- [x] 补齐方法签名与参数：`search_tv/get_tv_details/get_alternative_titles/discover_tv`
- [x] 新增 TMDB 查询端点：`/tmdb/search`、`/tmdb/tv/{id}`、`/tmdb/tv/{id}/alternative_titles`
- [x] 路由挂载与鉴权接入（复用 `get_current_user`）
- [x] 编写结果结构与字段映射方案（与 B-06 对齐）
  - [x] 明确 TMDB 原始字段与内部字段的映射关系（search/detail/alternative_titles 三类接口）
  - [x] 输出供 B-06 使用的统一数据结构说明（示例 JSON + 字段含义说明）
- [x] 整理配置驱动的默认参数策略
  - [x] 约定并实现从 TMDB 配置 `extra_config` 中读取 `language/region/include_adult` 等默认值
  - [x] 在客户端或端点层应用默认值，并允许调用方覆盖
- [x] 评估并设计 TMDB 查询结果的轻量缓存方案
  - [x] 评估典型访问模式后，确认不在客户端层实现运行时缓存
  - [x] 采用“关键词/TVDB ↔ TMDB 映射 + 本地元数据持久化”方案替代轻量缓存
- [x] 增补最小测试用例与示例
  - [x] 为 `TMDBClient` 编写参数校验与错误路径单元测试（query/tv_id/country 非法、超时/HTTP 错误）
  - [x] 为 `/api/v1/tmdb/*` 端点编写最小 API 测试（401/404/400/502 等典型分支）
  - [x] 在文档或测试代码中补充典型调用示例，说明推荐用法
- [ ] 审核通过后提交代码
  - [ ] 创建指向 `develop` 分支的 PR，附上本任务文档与典型请求/响应示例
  - [ ] 完成代码评审与验收后合入主开发分支

---

## 十四、变更记录
- v0.1（2025-10-28）：创建文档与任务分支，确定范围与方法清单
- v0.2（2025-10-28）：完成 TMDBClient 方法增强与 TMDB 查询端点（search/detail/alternative_titles），文档同步
