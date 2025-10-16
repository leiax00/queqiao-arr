"""
外部服务客户端基类
提供统一的 HTTP 请求封装、超时、代理、Header 管理等功能
"""

from typing import Any, Dict, Optional
import httpx
from app.utils.logger import logger


class ExternalServiceClient:
    """外部服务客户端基类"""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        """
        初始化外部服务客户端

        Args:
            base_url: 服务的基础 URL（例如: http://localhost:8989）
            api_key: API 密钥（如果服务需要）
            proxies: 代理配置字典（例如: {"http://": "...", "https://": "..."}）
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.proxies = proxies
        self.timeout = timeout

    def _build_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        构建请求头

        Args:
            additional_headers: 额外的请求头

        Returns:
            完整的请求头字典
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # 如果有 API Key，添加到 Header
        if self.api_key:
            headers["X-Api-Key"] = self.api_key

        # 合并额外的请求头
        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> tuple[bool, Any]:
        """
        发送 GET 请求

        Args:
            path: API 路径（例如: /api/v3/system/status）
            params: 查询参数
            headers: 额外的请求头

        Returns:
            (成功标志, 响应数据或错误消息)
        """
        url = f"{self.base_url}{path}"
        request_headers = self._build_headers(headers)

        try:
            # 构建 httpx 客户端配置
            client_kwargs = {
                "timeout": self.timeout,
                "follow_redirects": True,
            }

            # 如果有代理配置，添加到客户端
            if self.proxies:
                client_kwargs["proxies"] = self.proxies

            with httpx.Client(**client_kwargs) as client:
                response = client.get(url, headers=request_headers, params=params)
                response.raise_for_status()

                # 尝试解析 JSON 响应
                try:
                    return True, response.json()
                except Exception:
                    # 如果不是 JSON，返回文本
                    return True, response.text

        except httpx.TimeoutException as e:
            error_msg = f"请求超时: {url}"
            logger.error(f"{error_msg} - {str(e)}")
            return False, error_msg

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP 错误 {e.response.status_code}: {url}"
            logger.error(f"{error_msg} - {str(e)}")
            return False, error_msg

        except httpx.RequestError as e:
            error_msg = f"网络请求失败: {url}"
            logger.error(f"{error_msg} - {str(e)}")
            return False, error_msg

        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(f"请求 {url} 时发生未知错误: {str(e)}")
            return False, error_msg

    def _post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> tuple[bool, Any]:
        """
        发送 POST 请求

        Args:
            path: API 路径
            data: 请求体数据
            headers: 额外的请求头

        Returns:
            (成功标志, 响应数据或错误消息)
        """
        url = f"{self.base_url}{path}"
        request_headers = self._build_headers(headers)

        try:
            # 构建 httpx 客户端配置
            client_kwargs = {
                "timeout": self.timeout,
                "follow_redirects": True,
            }

            # 如果有代理配置，添加到客户端
            if self.proxies:
                client_kwargs["proxies"] = self.proxies

            with httpx.Client(**client_kwargs) as client:
                response = client.post(url, headers=request_headers, json=data)
                response.raise_for_status()

                # 尝试解析 JSON 响应
                try:
                    return True, response.json()
                except Exception:
                    # 如果不是 JSON，返回文本
                    return True, response.text

        except httpx.TimeoutException as e:
            error_msg = f"请求超时: {url}"
            logger.error(f"{error_msg} - {str(e)}")
            return False, error_msg

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP 错误 {e.response.status_code}: {url}"
            logger.error(f"{error_msg} - {str(e)}")
            return False, error_msg

        except httpx.RequestError as e:
            error_msg = f"网络请求失败: {url}"
            logger.error(f"{error_msg} - {str(e)}")
            return False, error_msg

        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(f"请求 {url} 时发生未知错误: {str(e)}")
            return False, error_msg

