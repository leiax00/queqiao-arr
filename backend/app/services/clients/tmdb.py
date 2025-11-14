"""
TMDB API 客户端
提供对 TMDB (The Movie Database) 服务的访问接口
"""

from typing import Dict, Optional, Any
from .base import ExternalServiceClient


class TMDBClient(ExternalServiceClient):
    """TMDB API 客户端"""

    def __init__(
        self,
        api_key: str,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        """
        初始化 TMDB 客户端

        Args:
            api_key: TMDB API 密钥
            proxies: 代理配置
            timeout: 请求超时时间
        """
        # TMDB 使用固定的 API 地址
        base_url = "https://api.themoviedb.org/3"
        super().__init__(base_url, api_key, proxies, timeout)

    def _build_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        重写 Header 构建方法
        TMDB 的 API Key 通过查询参数传递，而不是通过 Header

        Args:
            additional_headers: 额外的请求头

        Returns:
            完整的请求头字典
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # 合并额外的请求头
        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _add_api_key_to_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        将 API Key 添加到查询参数中

        Args:
            params: 原始查询参数

        Returns:
            包含 API Key 的查询参数
        """
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        return params

    def search_tv(
        self,
        query: str,
        language: str = "zh-CN",
        page: int = 1,
        include_adult: bool = False,
    ) -> tuple[bool, Any]:
        """
        搜索电视剧

        Args:
            query: 搜索关键词
            language: 语言代码（默认: zh-CN）
            page: 分页页码（>=1）
            include_adult: 是否包含成人内容

        Returns:
            (是否成功, 搜索结果或错误消息)

        """
        # 轻量参数校验
        if not isinstance(query, str) or not query.strip():
            return False, "参数错误: query 不能为空"
        if not isinstance(page, int) or page < 1:
            page = 1
        if not isinstance(include_adult, bool):
            include_adult = False

        params = self._add_api_key_to_params({
            "query": query.strip(),
            "language": language,
            "page": page,
            "include_adult": include_adult,
        })
        return self._get("/search/tv", params=params)

    def get_alternative_titles(self, tv_id: int, country: Optional[str] = None) -> tuple[bool, Any]:
        """
        获取电视剧的别名/替代标题

        Args:
            tv_id: TMDB 电视剧 ID
            country: 可选国家过滤（ISO 3166-1 代码，例如: CN/HK/TW/US）

        Returns:
            (是否成功, 别名列表或错误消息)

        """
        # 轻量参数校验
        if not isinstance(tv_id, int) or tv_id <= 0:
            return False, "参数错误: tv_id 必须为正整数"

        params: Dict[str, Any] = self._add_api_key_to_params()
        if country:
            # 仅做基本合法性校验（两位大写字母）
            if isinstance(country, str) and len(country) == 2 and country.isalpha():
                params["country"] = country.upper()
            else:
                return False, "参数错误: country 必须为2位字母的国家码"
        return self._get(f"/tv/{tv_id}/alternative_titles", params=params)

    def get_tv_details(self, tv_id: int, language: str = "zh-CN") -> tuple[bool, Any]:
        """
        获取电视剧详情

        Args:
            tv_id: TMDB 电视剧 ID
            language: 语言代码（默认: zh-CN）

        Returns:
            (是否成功, 详情数据或错误消息)
        """
        if not isinstance(tv_id, int) or tv_id <= 0:
            return False, "参数错误: tv_id 必须为正整数"

        params = self._add_api_key_to_params({
            "language": language,
        })
        return self._get(f"/tv/{tv_id}", params=params)

    def discover_tv(self, params: Optional[Dict[str, Any]] = None) -> tuple[bool, Any]:
        """
        发现剧集（可选能力，按条件筛选）

        Args:
            params: TMDB discover 查询参数字典

        Returns:
            (是否成功, 结果或错误消息)
        """
        base_params: Dict[str, Any] = {}
        if params and isinstance(params, dict):
            base_params.update(params)

        # 默认语言
        base_params.setdefault("language", "zh-CN")

        base_params = self._add_api_key_to_params(base_params)
        return self._get("/discover/tv", params=base_params)

    def check_status(self) -> tuple[bool, str]:
        """
        检查 TMDB 服务状态
        通过调用一个简单的 API 来验证连接

        Returns:
            (是否成功, 状态描述信息)
        """
        # 使用 configuration API 来检查连接状态
        params = self._add_api_key_to_params()
        ok, result = self._get("/configuration", params=params)

        if ok:
            return True, "TMDB 连接成功"
        else:
            return False, f"TMDB 连接失败: {result}"

