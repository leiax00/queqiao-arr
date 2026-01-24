# B-07: Torznab XML 生成模块 任务说明书

## 一、任务信息
- 任务ID: B-07
- 名称: Torznab XML 生成模块
- 复杂度: L（约 5 PD）
- 优先级: P0
- 依赖: B-06（标题解析器）、B-04（TMDB 客户端）
- 被依赖: B-08（端到端编排）
- 当前分支: `feature/B-07-torznab-xml`
- 状态: 已完成
- 更新时间: 2026-01-17

---

## 二、目标与范围（Scope）
- 目标：将开发好的标题解析结果（`ParsedTitle`）以及 Prowlarr 的原始搜索项，封装并转换为符合 Torznab 协议规范的 XML 响应。
- 范围：
  - 定义 Torznab XML 结构：包含 RSS 频道信息、分页响应信息（newznab:response）和多项子条目（Item）。
  - 条目字段映射：将 `ParsedTitle` 增强后的季、集、分辨率、编码等与 Prowlarr 原始数据（大小、发布日期、做种数等）合并映射。
  - 处理 `caps` 功能请求：支持 Sonarr/Radarr 的 `t=caps` 查询。
  - 处理 `search` 请求响应：输出包含 `enclosure`、`pubDate` 和 `torznab:attr` 的标准化 XML。
  - 兼容性：确保输出符合 RFC822 日期格式，且能被 Sonarr 索引器逻辑正常解析。

---

## 三、关键技术场景
### 3.1 核心 XML 结构示例 (Item)
```xml
<item>
    <title>识别并规范化后的标题 (或保留原始标题)</title>
    <guid isPermaLink="false">唯一标识（由原始条目继承或生成）</guid>
    <link>种子下载或磁力链接</link>
    <pubDate>Sat, 24 Jan 2026 10:00:00 +0800</pubDate>
    <size>12345678</size>
    <enclosure url="下载地址" length="12345678" type="application/x-bittorrent" />
    
    <!-- Torznab 必备属性 -->
    <torznab:attr name="season" value="1"/>
    <torznab:attr name="episode" value="1"/>
    <torznab:attr name="tmdbid" value="12345"/>
    
    <!-- 其他增强属性 -->
    <torznab:attr name="resolution" value="1080p"/>
    <torznab:attr name="video" value="H264"/>
    <torznab:attr name="seeders" value="10"/>
    <torznab:attr name="peers" value="5"/>
    <torznab:attr name="infohash" value="ABCDEF123456..."/>
</item>
```

### 3.2 Torznab 属性映射逻辑
- `season/episode`: 从 `ParsedTitle` 中提取。若为连播（如 01-02），需输出多个 `episode` 类型的 `torznab:attr`。
- `tmdbid`: 仅在 `ParsedTitle` 成功匹配 TMDB 时输出。
- `resolution/video/audio/codec`: 映射到对应的标准化枚举。
- `seeders/peers`: 从原始搜索结果（Prowlarr）继承，用于 Sonarr 排序筛选。

### 3.3 能力集 (Caps) 定义
- `categories`: 映射 `5070` (TV/Anime), `5000` (TV), `2000` (Movies) 等。
- `search modes`: 声明支持 `q` (关键字), `tvsearch` (季集搜索) 等模式。

---

## 四、实施计划
- Day 1: 研究 Torznab 协议细节，重点关注 RFC822 日期格式与 enclosure 标签要求。
- Day 2: 定义 Pydantic 解析/序列化模型，用于内部处理 RSS/Torznab 数据结构。
- Day 3: 实现 `t=caps` 响应逻辑与静态 XML 构建。
- Day 4: 实现 `t=search` 转换逻辑：合并 `ParsedTitle` 与原始结果，处理多集与分页属性。
- Day 5: 编写单元测试，验证 XML 模式有效性及 Sonarr 兼容性字段。

---

## 五、验收标准
1. 生成的 XML 包含正确的 `xmlns:torznab` 和 `xmlns:newznab` 命名空间。
2. 每一个 `<item>` 必须包含有效的 `<enclosure>` 标签（url, length, type）。
3. 时间字段 `pubDate` 必须符合 RFC822 标准，避免 Sonarr 解析日期错误。
4. 正确处理连播集数：支持在同一个 item 中输出多个 `name="episode"` 的属性标签。
5. 分页支持：`<channel>` 下包含 `<newznab:response offset="x" total="y" />`。
6. 能力集响应：`t=caps` 能返回正确的分类和支持的搜索参数。
7. 通过单元测试验证典型番剧和电影的 XML 生成结果。
