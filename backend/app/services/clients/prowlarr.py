"""
Prowlarr API 客户端
提供对 Prowlarr 服务的访问接口
"""

from typing import Dict, Optional
from .base import ExternalServiceClient
from app.utils.logger import logger


class ProwlarrClient(ExternalServiceClient):
    """Prowlarr API 客户端"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int = 30,  # 默认 30 秒，可通过配置动态调整
    ):
        """
        初始化 Prowlarr 客户端

        Args:
            base_url: Prowlarr 服务地址（例如: http://localhost:9696）
            api_key: Prowlarr API 密钥
            proxies: 代理配置
            timeout: 请求超时时间
        """
        super().__init__(base_url, api_key, proxies, timeout)

    def check_status(self) -> tuple[bool, str]:
        """
        检查 Prowlarr 服务状态

        Returns:
            (是否成功, 状态描述信息)
        """
        ok, result = self._get("/api/v1/system/status")

        if ok:
            # 解析响应，提取有用信息
            if isinstance(result, dict):
                version = result.get("version", "未知")
                return True, f"Prowlarr 连接成功 (版本: {version})"
            return True, "Prowlarr 连接成功"
        else:
            return False, f"Prowlarr 连接失败: {result}"

    def search(
        self,
        query: str,
        *,
        indexer_ids: Optional[list[int]] = None,
        categories: Optional[list[int]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        type: str = "search",
    ) -> tuple[bool, object]:
        """
        发起 Prowlarr 搜索请求

        Args:
            query: 搜索关键词（必填）
            indexer_ids: 指定索引器 ID 列表
            categories: 分类 ID 列表
            limit: 返回数量上限
            offset: 起始偏移量
            type: 搜索类型，默认 "search"（兼容 "tvsearch" 等）

        Returns:
            (是否成功, 数据或错误信息)
        """
        if not query or not str(query).strip():
            return False, "参数错误: query 不能为空"

        def _normalize_int_list(values: Optional[list[int]]) -> Optional[list[int]]:
            if values is None:
                return None
            normalized: list[int] = []
            for v in values:
                try:
                    normalized.append(int(v))
                except (TypeError, ValueError):
                    return None
            return normalized

        normalized_indexers = _normalize_int_list(indexer_ids)
        normalized_categories = _normalize_int_list(categories)
        if indexer_ids is not None and normalized_indexers is None:
            return False, "参数错误: indexer_ids 必须为整数列表"
        if categories is not None and normalized_categories is None:
            return False, "参数错误: categories 必须为整数列表"

        if limit is not None:
            try:
                limit_val = int(limit)
                if limit_val < 0:
                    raise ValueError
            except (TypeError, ValueError):
                return False, "参数错误: limit 必须为非负整数"
        else:
            limit_val = None

        if offset is not None:
            try:
                offset_val = int(offset)
                if offset_val < 0:
                    raise ValueError
            except (TypeError, ValueError):
                return False, "参数错误: offset 必须为非负整数"
        else:
            offset_val = None

        params: Dict[str, object] = {
            "type": type or "search",
            "q": query.strip(),  # Prowlarr API 使用 'q' 参数而不是 'query'
        }
        if normalized_indexers:
            params["indexerIds"] = normalized_indexers
        if normalized_categories:
            params["categories"] = normalized_categories
        if limit_val is not None:
            params["limit"] = limit_val
        if offset_val is not None:
            params["offset"] = offset_val

        logger.info(f"Prowlarr 搜索: {params}")

        ok, result = self._get("/api/v1/search", params=params)
        if ok:
            return True, result
        return False, f"Prowlarr 搜索失败: {result}"
