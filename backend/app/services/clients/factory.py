"""
客户端工厂
根据服务名称创建对应的客户端实例
"""

from typing import Dict, Optional
from .base import ExternalServiceClient
from .sonarr import SonarrClient
from .prowlarr import ProwlarrClient
from .tmdb import TMDBClient


def make_client(
    service_name: str,
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    proxies: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> ExternalServiceClient:
    """
    根据服务名称创建对应的客户端实例

    Args:
        service_name: 服务名称（sonarr, prowlarr, tmdb）
        url: 服务地址（TMDB 不需要此参数）
        api_key: API 密钥
        proxies: 代理配置
        timeout: 请求超时时间

    Returns:
        对应的客户端实例

    Raises:
        ValueError: 如果服务名称未知或参数缺失
    """
    service_name = service_name.lower()

    if service_name == "sonarr":
        if not url or not api_key:
            raise ValueError("Sonarr 客户端需要 url 和 api_key 参数")
        return SonarrClient(base_url=url, api_key=api_key, proxies=proxies, timeout=timeout)

    elif service_name == "prowlarr":
        if not url or not api_key:
            raise ValueError("Prowlarr 客户端需要 url 和 api_key 参数")
        return ProwlarrClient(base_url=url, api_key=api_key, proxies=proxies, timeout=timeout)

    elif service_name == "tmdb":
        if not api_key:
            raise ValueError("TMDB 客户端需要 api_key 参数")
        return TMDBClient(api_key=api_key, proxies=proxies, timeout=timeout)

    else:
        raise ValueError(f"未知的服务名称: {service_name}. 支持的服务: sonarr, prowlarr, tmdb")

