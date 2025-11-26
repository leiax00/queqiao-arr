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
        default_language: Optional[str] = None,
        default_region: Optional[str] = None,
        default_include_adult: Optional[bool] = None,
    ):
        """
        初始化 TMDB 客户端

        Args:
            api_key: TMDB API 密钥
            proxies: 代理配置
            timeout: 请求超时时间
            default_language: 默认语言代码
            default_region: 默认地区代码
            default_include_adult: 默认是否包含成人内容
        """
        # TMDB 使用固定的 API 地址
        base_url = "https://api.themoviedb.org/3"
        super().__init__(base_url, api_key, proxies, timeout)

        # 配置驱动的默认参数，提供兜底值
        self.default_language: str = (default_language or "zh-CN").strip() or "zh-CN"
        self.default_region: str = (default_region or "CN").strip() or "CN"
        if isinstance(default_include_adult, bool):
            self.default_include_adult: bool = default_include_adult
        else:
            self.default_include_adult = False

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
        language: Optional[str] = None,
        page: int = 1,
        include_adult: Optional[bool] = None,
    ) -> tuple[bool, Any]:
        """
        搜索电视剧

        Args:
            query: 搜索关键词
            language: 语言代码；为空时使用实例默认配置
            page: 分页页码（>=1）
            include_adult: 是否包含成人内容；None 时使用实例默认配置

        Returns:
            (是否成功, 搜索结果或错误消息)

        """
        # 轻量参数校验
        if not isinstance(query, str) or not query.strip():
            return False, "参数错误: query 不能为空"
        if not isinstance(page, int) or page < 1:
            page = 1

        # 语言与成人内容标志应用默认策略
        if not isinstance(language, str) or not language.strip():
            language = self.default_language
        if include_adult is None:
            include_adult = self.default_include_adult
        elif not isinstance(include_adult, bool):
            include_adult = self.default_include_adult

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
            country: 可选国家过滤（ISO 3166-1 代码，例如: CN/HK/TW/US）；
                     为空时使用实例默认地区

        Returns:
            (是否成功, 别名列表或错误消息)

        """
        # 轻量参数校验
        if not isinstance(tv_id, int) or tv_id <= 0:
            return False, "参数错误: tv_id 必须为正整数"

        params: Dict[str, Any] = self._add_api_key_to_params()
        # 默认国家策略：未传入时回落到默认地区
        effective_country = country or self.default_region
        if effective_country:
            # 仅做基本合法性校验（两位大写字母）
            if isinstance(effective_country, str) and len(effective_country) == 2 and effective_country.isalpha():
                params["country"] = effective_country.upper()
            else:
                return False, "参数错误: country 必须为2位字母的国家码"
        return self._get(f"/tv/{tv_id}/alternative_titles", params=params)

    def get_tv_details(self, tv_id: int, language: Optional[str] = None) -> tuple[bool, Any]:
        """
        获取电视剧详情

        Args:
            tv_id: TMDB 电视剧 ID
            language: 语言代码；为空时使用实例默认配置

        Returns:
            (是否成功, 详情数据或错误消息)
        """
        if not isinstance(tv_id, int) or tv_id <= 0:
            return False, "参数错误: tv_id 必须为正整数"

        if not isinstance(language, str) or not language.strip():
            language = self.default_language

        params = self._add_api_key_to_params(
            {
                "language": language,
            }
        )
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
