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
- [ ] 补齐方法签名与参数（设计确认）
- [ ] 编写结果结构与字段映射方案
- [ ] 输出契约确认（与 B-06 对齐）
- [ ] 审核通过后开始实现 & 提交代码
- [ ] 增补最小测试用例与示例

---

## 十二、变更记录
- v0.1（2025-10-28）：创建文档与任务分支，确定范围与方法清单
