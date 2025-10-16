"""
Prowlarr API 客户端
提供对 Prowlarr 服务的访问接口
"""

from typing import Dict, Optional
from .base import ExternalServiceClient


class ProwlarrClient(ExternalServiceClient):
    """Prowlarr API 客户端"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int = 30,
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

