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

## 七、验收标准（Acceptance Criteria）
1. `TMDBClient` 完成上述方法的实现或增强，参数支持 `language/region/include_adult/page`（必要时）。
2. 连接测试 `check_status()` 在有效 `api_key` 下返回成功；异常路径返回可读信息。
3. 输出契约满足 B-06 消费需求，字段命名清晰、单位一致。
4. 代理/超时配置可控，遵循基类实现；错误不泄漏敏感信息。
5. 文档与示例完整，包含典型调用样例。

---

## 八、实施计划（3 PD）
- Day 1：梳理方法清单与签名，补齐 `search_tv`/`get_alternative_titles` 参数，添加 `get_tv_details`
- Day 2：实现结果映射与基本校验；补充日志要点与错误语义
- Day 3：编写使用示例与最小测试用例草案（不提交实现代码，待审核后进行）

---

## 九、风险与对策
- 上游速率限制或字段变化：通过结果映射与容错字段访问降低耦合
- 中文别名覆盖有限：支持多地区获取并合并去重
- 代理/网络不稳定：提供超时设置与清晰错误提示

---

## 十、示例用法（草案，仅供说明）
```python
from app.services.clients.tmdb import TMDBClient

client = TMDBClient(api_key="<masked>", proxies=None, timeout=15)
ok, data = client.search_tv(query="凡人修仙传", language="zh-CN")
if ok and data.get("results"):
    tv_id = data["results"][0]["id"]
    ok2, aliases = client.get_alternative_titles(tv_id)
```

---

## 十一、进度清单（Checklist）
- [x] 创建分支 `feature/B-04-tmdb-client`（当前）
- [x] 审阅现有 `base.py`/`tmdb.py`，对齐返回与异常风格（当前）
- [x] 补齐方法签名与参数：`search_tv/get_tv_details/get_alternative_titles/discover_tv`
- [x] 新增 TMDB 查询端点：`/tmdb/search`、`/tmdb/tv/{id}`、`/tmdb/tv/{id}/alternative_titles`
- [x] 路由挂载与鉴权接入（复用 `get_current_user`）
- [x] 编写结果结构与字段映射方案（与 B-06 对齐）
  - [x] 明确 TMDB 原始字段与内部字段的映射关系（search/detail/alternative_titles 三类接口）
  - [x] 输出供 B-06 使用的统一数据结构说明（示例 JSON + 字段含义说明）
- [ ] 整理配置驱动的默认参数策略
  - [ ] 约定并实现从 TMDB 配置 `extra_config` 中读取 `language/region/include_adult` 等默认值
  - [ ] 在客户端或端点层应用默认值，并允许调用方覆盖
- [ ] 评估并设计 TMDB 查询结果的轻量缓存方案
  - [ ] 根据 B-08 端到端编排的访问模式，确定缓存粒度（按 `tv_id` / `query + language` 等）
  - [ ] 在性能需求明确后选择实现方式（内存 LRU / 其他），并补充失效策略说明
- [ ] 增补最小测试用例与示例
  - [ ] 为 `TMDBClient` 编写参数校验与错误路径单元测试（query/tv_id/country 非法、超时/HTTP 错误）
  - [ ] 为 `/api/v1/tmdb/*` 端点编写最小 API 测试（401/404/400/502 等典型分支）
  - [ ] 在文档或测试代码中补充典型调用示例，说明推荐用法
- [ ] 审核通过后提交代码
  - [ ] 创建指向 `develop` 分支的 PR，附上本任务文档与典型请求/响应示例
  - [ ] 完成代码评审与验收后合入主开发分支

---

## 十二、变更记录
- v0.1（2025-10-28）：创建文档与任务分支，确定范围与方法清单
- v0.2（2025-10-28）：完成 TMDBClient 方法增强与 TMDB 查询端点（search/detail/alternative_titles），文档同步
