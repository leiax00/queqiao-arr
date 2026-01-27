"""
编排服务核心逻辑
"""

import asyncio
import time
from typing import List, Optional, Tuple, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.clients import ProwlarrClient
from app.services.parser.service import async_parse_title_with_db_config
from app.services.torznab.service import map_results_to_torznab_response
from app.services.torznab.xml_builder import build_search_rss_xml, build_caps_xml
from app.services.torznab.models import TorznabResponse
from app.services.parser.models import ParsedTitle
from .models import SearchQuery, OrchestrationConfig

_TMDB_ALIAS_CACHE: Dict[int, Tuple[float, List[str]]] = {}
_TMDB_FIND_CACHE: Dict[str, Tuple[float, Optional[int]]] = {}


class OrchestrationService:
    """
    端到端自动化编排服务
    整合 Prowlarr 搜索、标题解析、TMDB 增强、XML 生成
    """

    def __init__(
        self,
        db: AsyncSession,
        prowlarr_client: ProwlarrClient,
        config: Optional[OrchestrationConfig] = None,
        tmdb_client: Optional[Any] = None,
    ):
        self.db = db
        self.prowlarr_client = prowlarr_client
        self.config = config or OrchestrationConfig()
        self.tmdb_client = tmdb_client

    async def search(self, query: SearchQuery) -> Tuple[bool, str]:
        """
        执行编排搜索流程

        Args:
            query: 搜索查询参数

        Returns:
            (success, xml_string): 成功返回 XML 字符串，失败返回错误信息
        """
        try:
            # 1. 处理 caps 请求
            if query.t == "caps":
                return await self._handle_caps()

            # 2. 处理 search 和 tvsearch 请求
            if query.t in ["search", "tvsearch", "movie"]:
                return await self._handle_search(query)

            # 3. 不支持的操作类型
            return False, self._error_xml(200, "Invalid parameter")

        except Exception as e:
            # 记录异常并返回错误
            return False, self._error_xml(900, f"Internal error: {str(e)}")

    async def _handle_caps(self) -> Tuple[bool, str]:
        """
        处理 caps 能力集请求
        """
        from app.services.torznab.service import get_torznab_caps

        caps = await get_torznab_caps(self.db)
        xml_content = build_caps_xml(caps)
        return True, xml_content

    async def _handle_search(self, query: SearchQuery) -> Tuple[bool, str]:
        """
        处理搜索请求（四阶段管道）

        阶段 1: 请求接收与参数解析（已完成，query 参数已传入）
        阶段 2: TMDB 增强搜索词（可选）
        阶段 3: 发起搜索与并行解析
        阶段 4: 格式化响应
        """
        # 阶段 2: TMDB 增强（如果启用且有外部 ID）
        search_terms = await self._enhance_search_with_tmdb(query)

        # 阶段 3: 发起 Prowlarr 搜索
        ok, prowlarr_results, total = await self._search_prowlarr_multi(
            queries=search_terms if search_terms else ([query.q] if query.q else []),
            query_type=query.t,
            season=query.season,
            ep=query.ep,
            limit=query.limit,
            offset=query.offset,
        )

        if not ok:
            # Prowlarr 搜索失败，返回错误 XML
            return False, self._error_xml(
                900, f"Prowlarr search failed: {prowlarr_results}"
            )

        # 如果没有结果，返回空响应
        if not prowlarr_results:
            return await self._build_empty_response(query.offset, query.limit)

        # 并行解析标题
        parsed_results = await self._parallel_parse(prowlarr_results)

        # 映射为 TorznabResponse
        torznab_response = map_results_to_torznab_response(
            prowlarr_results=prowlarr_results,
            parsed_results=parsed_results,
            offset=query.offset,
            total=total,
        )

        # 阶段 4: 生成 XML 响应
        return await self._build_xml_response(torznab_response)

    async def _enhance_search_with_tmdb(self, query: SearchQuery) -> List[str]:
        """
        使用 TMDB 增强搜索词

        1. 如果有外部 ID（tmdbid/tvdbid/rid/imdbid），先获取 TMDB ID
        2. 使用 TMDB ID 获取中文别名
        3. 返回原始搜索词 + 别名列表

        Returns:
            搜索词列表 [原始词, 别名1, 别名2, ...]
        """
        # movie 搜索暂不使用 TV 别名增强
        if query.t == "movie":
            return [query.q] if query.q else []

        # 如果未启用 TMDB 增强或没有客户端，直接返回原始查询词
        if not self.config.enable_tmdb_enhancement or not self.tmdb_client:
            return [query.q] if query.q else []

        # 尝试获取 TMDB ID
        tmdb_id = await self._resolve_tmdb_id(query)

        if not tmdb_id:
            # 无法解析 TMDB ID，返回原始查询词
            return [query.q] if query.q else []

        # 获取别名（带缓存）
        aliases = await self._get_tmdb_aliases(tmdb_id)

        if not aliases:
            return [query.q] if query.q else []

        # 返回原始查询词 + 别名列表
        search_terms = [query.q] if query.q else []
        search_terms.extend(aliases)

        return search_terms

    async def _resolve_tmdb_id(self, query: SearchQuery) -> Optional[int]:
        """
        从外部 ID 解析 TMDB ID

        优先级：tmdbid > tvdbid > imdbid > rid
        """
        # 如果直接提供了 tmdbid，直接返回
        if query.tmdbid:
            return query.tmdbid

        if query.t == "movie":
            return None

        cache_ttl = self.config.tmdb_cache_ttl
        now = time.monotonic()

        if query.tvdbid:
            cache_key = f"tvdb:{query.tvdbid}"
            cached = _TMDB_FIND_CACHE.get(cache_key)
            if cached and (now - cached[0]) < cache_ttl:
                return cached[1]

            ok, data = await self.tmdb_client.find_by_external_id_async(
                external_id=str(query.tvdbid),
                external_source="tvdb_id",
            )
            tmdb_id = _extract_tmdb_tv_id(data) if ok else None
            _TMDB_FIND_CACHE[cache_key] = (now, tmdb_id)
            return tmdb_id

        if query.imdbid:
            cache_key = f"imdb:{query.imdbid}"
            cached = _TMDB_FIND_CACHE.get(cache_key)
            if cached and (now - cached[0]) < cache_ttl:
                return cached[1]

            ok, data = await self.tmdb_client.find_by_external_id_async(
                external_id=str(query.imdbid),
                external_source="imdb_id",
            )
            tmdb_id = _extract_tmdb_tv_id(data) if ok else None
            _TMDB_FIND_CACHE[cache_key] = (now, tmdb_id)
            return tmdb_id

        if query.rid:
            cache_key = f"tvrage:{query.rid}"
            cached = _TMDB_FIND_CACHE.get(cache_key)
            if cached and (now - cached[0]) < cache_ttl:
                return cached[1]

            ok, data = await self.tmdb_client.find_by_external_id_async(
                external_id=str(query.rid),
                external_source="tvrage_id",
            )
            tmdb_id = _extract_tmdb_tv_id(data) if ok else None
            _TMDB_FIND_CACHE[cache_key] = (now, tmdb_id)
            return tmdb_id

        return None

    async def _get_tmdb_aliases(self, tmdb_id: int) -> List[str]:
        """
        获取 TMDB 别名（带缓存）

        Args:
            tmdb_id: TMDB 电视剧 ID

        Returns:
            别名列表
        """
        if not self.tmdb_client:
            return []

        cache_ttl = self.config.tmdb_cache_ttl
        now = time.monotonic()
        cached = _TMDB_ALIAS_CACHE.get(tmdb_id)
        if cached and (now - cached[0]) < cache_ttl:
            return cached[1]

        try:
            ok, result = await self.tmdb_client.get_alternative_titles_async(
                tv_id=tmdb_id, country="CN"
            )

            if ok and isinstance(result, dict):
                titles = result.get("results", [])
                aliases = [t.get("title", "") for t in titles if t.get("title")]

                # 如果 CN 别名少于 3 个，再尝试 HK 和 TW
                if len(aliases) < 3:
                    ok_hk, result_hk = await self.tmdb_client.get_alternative_titles_async(
                        tv_id=tmdb_id, country="HK"
                    )
                    if ok_hk and isinstance(result_hk, dict):
                        titles_hk = result_hk.get("results", [])
                        aliases.extend(
                            [t.get("title", "") for t in titles_hk if t.get("title")]
                        )

                    ok_tw, result_tw = await self.tmdb_client.get_alternative_titles_async(
                        tv_id=tmdb_id, country="TW"
                    )
                    if ok_tw and isinstance(result_tw, dict):
                        titles_tw = result_tw.get("results", [])
                        aliases.extend(
                            [t.get("title", "") for t in titles_tw if t.get("title")]
                        )

                # 去重并限制数量（最多 10 个别名）
                unique_aliases = list(dict.fromkeys(aliases))[:10]
                _TMDB_ALIAS_CACHE[tmdb_id] = (now, unique_aliases)
                return unique_aliases

        except Exception:
            # TMDB 查询失败，静默处理
            pass

        _TMDB_ALIAS_CACHE[tmdb_id] = (now, [])
        return []

    async def _search_prowlarr_multi(
        self,
        queries: List[str],
        query_type: str = "search",
        season: Optional[int] = None,
        ep: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[bool, List[dict], int]:
        """
        调用 Prowlarr 搜索接口

        如果有多个搜索词（原始词 + 别名），会多次搜索并合并去重结果
        """
        try:
            normalized_queries = []
            for term in queries:
                term = (term or "").strip()
                if term and term not in normalized_queries:
                    normalized_queries.append(term)

            if not normalized_queries:
                return True, [], 0

            desired = max(int(limit or 0), 0)
            if desired <= 0:
                desired = 100
            fetch_size = desired + max(int(offset or 0), 0)

            merged: List[dict] = []
            seen_keys = set()

            for term in normalized_queries:
                params: Dict[str, Any] = {
                    "query": term,
                    "type": query_type,
                    "limit": fetch_size,
                    "offset": 0,
                }
                if season is not None:
                    params["season"] = season
                if ep is not None:
                    params["ep"] = ep

                ok, data = await self.prowlarr_client.search_async(**params)
                if not ok:
                    return False, data, 0

                results = data if isinstance(data, list) else []
                for item in results:
                    key = _get_result_key(item)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    merged.append(item)
                    if len(merged) >= fetch_size:
                        break

                if len(merged) >= fetch_size:
                    break

            total = len(merged)
            start = max(int(offset or 0), 0)
            end = start + desired
            return True, merged[start:end], total

        except Exception as e:
            return False, str(e), 0

    async def _parallel_parse(
        self,
        prowlarr_results: List[dict],
    ) -> List[Optional[ParsedTitle]]:
        """
        并行解析标题

        使用 Semaphore 限制并发数，防止 CPU 尖峰
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrent_parsing)

        async def parse_with_limit(raw_item: dict) -> Optional[ParsedTitle]:
            """带并发限制的解析"""

            async with semaphore:
                try:
                    title = raw_item.get("title", "")
                    if not title:
                        return None

                    # 调用标题解析器
                    ok, result = await async_parse_title_with_db_config(
                        self.db, raw_title=title
                    )

                    if ok and isinstance(result, ParsedTitle):
                        return result
                    return None

                except Exception:
                    # 解析失败返回 None，保留原始结果
                    return None

        # 并行执行所有解析任务
        tasks = [parse_with_limit(item) for item in prowlarr_results]
        return await asyncio.gather(*tasks)

    async def _build_xml_response(self, response: TorznabResponse) -> Tuple[bool, str]:
        """
        构建 Torznab XML 响应
        """
        try:
            # 获取 caps 信息（用于构建 RSS）
            from app.services.torznab.service import get_torznab_caps

            caps = await get_torznab_caps(self.db)

            # 构建 XML
            xml_content = build_search_rss_xml(caps, response)
            return True, xml_content

        except Exception as e:
            return False, self._error_xml(900, f"Failed to build XML: {str(e)}")

    async def _build_empty_response(self, offset: int, limit: int) -> Tuple[bool, str]:
        """
        构建空响应
        """
        from app.services.torznab.service import get_torznab_caps

        caps = await get_torznab_caps(self.db)
        empty_resp = TorznabResponse(offset=offset, total=0, items=[])
        xml_content = build_search_rss_xml(caps, empty_resp)
        return True, xml_content

    @staticmethod
    def _error_xml(code: int, description: str) -> str:
        """
        生成 Torznab 错误 XML
        """
        return f'<?xml version="1.0" encoding="utf-8"?><error code="{code}" description="{description}" />'


def _extract_tmdb_tv_id(data: Any) -> Optional[int]:
    """
    从 TMDB /find 返回中提取 tv_id
    """
    if not isinstance(data, dict):
        return None
    tv_results = data.get("tv_results") or []
    if not tv_results:
        return None
    first = tv_results[0]
    if isinstance(first, dict):
        tv_id = first.get("id")
        if isinstance(tv_id, int):
            return tv_id
        try:
            return int(tv_id)
        except (TypeError, ValueError):
            return None
    return None


def _get_result_key(item: dict) -> str:
    """
    生成 Prowlarr 结果的去重 Key
    """
    if not isinstance(item, dict):
        return ""
    for key in ("guid", "infoHash", "downloadUrl", "magnetUrl", "infoUrl"):
        value = item.get(key)
        if value:
            return str(value)
    title = item.get("title")
    size = item.get("size")
    if title or size:
        return f"{title}:{size}"
    return ""
