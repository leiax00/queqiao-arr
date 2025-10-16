"""
外部服务客户端单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.clients import make_client, SonarrClient, ProwlarrClient, TMDBClient


class TestClientFactory:
    """客户端工厂测试"""

    def test_make_sonarr_client(self):
        """测试创建 Sonarr 客户端"""
        client = make_client(
            service_name="sonarr",
            url="http://localhost:8989",
            api_key="test_key"
        )
        assert isinstance(client, SonarrClient)
        assert client.base_url == "http://localhost:8989"
        assert client.api_key == "test_key"

    def test_make_prowlarr_client(self):
        """测试创建 Prowlarr 客户端"""
        client = make_client(
            service_name="prowlarr",
            url="http://localhost:9696",
            api_key="test_key"
        )
        assert isinstance(client, ProwlarrClient)
        assert client.base_url == "http://localhost:9696"
        assert client.api_key == "test_key"

    def test_make_tmdb_client(self):
        """测试创建 TMDB 客户端"""
        client = make_client(
            service_name="tmdb",
            api_key="test_key"
        )
        assert isinstance(client, TMDBClient)
        assert client.api_key == "test_key"

    def test_unknown_service_raises_error(self):
        """测试未知服务名称抛出异常"""
        with pytest.raises(ValueError, match="未知的服务名称"):
            make_client(service_name="unknown", url="http://test", api_key="key")

    def test_sonarr_missing_params_raises_error(self):
        """测试 Sonarr 缺少必要参数时抛出异常"""
        with pytest.raises(ValueError, match="需要 url 和 api_key"):
            make_client(service_name="sonarr", api_key="key")

    def test_prowlarr_missing_params_raises_error(self):
        """测试 Prowlarr 缺少必要参数时抛出异常"""
        with pytest.raises(ValueError, match="需要 url 和 api_key"):
            make_client(service_name="prowlarr", url="http://test")

    def test_tmdb_missing_api_key_raises_error(self):
        """测试 TMDB 缺少 API Key 时抛出异常"""
        with pytest.raises(ValueError, match="需要 api_key"):
            make_client(service_name="tmdb")


class TestSonarrClient:
    """Sonarr 客户端测试"""

    @patch('httpx.Client')
    def test_check_status_success(self, mock_client_class):
        """测试成功检查 Sonarr 状态"""
        # 模拟 HTTP 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "3.0.9"}
        mock_response.raise_for_status = Mock()

        # 模拟 httpx.Client 上下文管理器
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = SonarrClient(
            base_url="http://localhost:8989",
            api_key="test_key"
        )
        ok, note = client.check_status()

        assert ok is True
        assert "成功" in note
        assert "3.0.9" in note

    @patch('httpx.Client')
    def test_check_status_connection_error(self, mock_client_class):
        """测试连接失败时的 Sonarr 状态检查"""
        # 模拟连接错误
        import httpx
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.side_effect = httpx.ConnectError("Connection refused")
        mock_client_class.return_value = mock_client

        client = SonarrClient(
            base_url="http://localhost:8989",
            api_key="test_key"
        )
        ok, note = client.check_status()

        assert ok is False
        assert "失败" in note

    @patch('httpx.Client')
    def test_check_status_http_error(self, mock_client_class):
        """测试 HTTP 错误时的 Sonarr 状态检查"""
        # 模拟 HTTP 错误
        import httpx
        mock_response = Mock()
        mock_response.status_code = 401
        mock_http_error = httpx.HTTPStatusError(
            "Unauthorized",
            request=Mock(),
            response=mock_response
        )

        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.side_effect = mock_http_error
        mock_client_class.return_value = mock_client

        client = SonarrClient(
            base_url="http://localhost:8989",
            api_key="wrong_key"
        )
        ok, note = client.check_status()

        assert ok is False
        assert "失败" in note


class TestProwlarrClient:
    """Prowlarr 客户端测试"""

    @patch('httpx.Client')
    def test_check_status_success(self, mock_client_class):
        """测试成功检查 Prowlarr 状态"""
        # 模拟 HTTP 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "1.5.2"}
        mock_response.raise_for_status = Mock()

        # 模拟 httpx.Client 上下文管理器
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = ProwlarrClient(
            base_url="http://localhost:9696",
            api_key="test_key"
        )
        ok, note = client.check_status()

        assert ok is True
        assert "成功" in note
        assert "1.5.2" in note

    @patch('httpx.Client')
    def test_check_status_timeout(self, mock_client_class):
        """测试超时时的 Prowlarr 状态检查"""
        # 模拟超时错误
        import httpx
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.side_effect = httpx.TimeoutException("Timeout")
        mock_client_class.return_value = mock_client

        client = ProwlarrClient(
            base_url="http://localhost:9696",
            api_key="test_key",
            timeout=1
        )
        ok, note = client.check_status()

        assert ok is False
        assert "失败" in note


class TestTMDBClient:
    """TMDB 客户端测试"""

    @patch('httpx.Client')
    def test_check_status_success(self, mock_client_class):
        """测试成功检查 TMDB 状态"""
        # 模拟 HTTP 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"images": {"base_url": "http://image.tmdb.org"}}
        mock_response.raise_for_status = Mock()

        # 模拟 httpx.Client 上下文管理器
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = TMDBClient(api_key="test_key")
        ok, note = client.check_status()

        assert ok is True
        assert "成功" in note

    @patch('httpx.Client')
    def test_search_tv(self, mock_client_class):
        """测试搜索电视剧（占位实现）"""
        # 模拟 HTTP 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": 12345, "name": "斗罗大陆"}
            ]
        }
        mock_response.raise_for_status = Mock()

        # 模拟 httpx.Client 上下文管理器
        mock_client = MagicMock()
        mock_client.__enter__.return_value.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = TMDBClient(api_key="test_key")
        ok, result = client.search_tv("斗罗大陆")

        assert ok is True
        assert isinstance(result, dict)


class TestBaseClient:
    """基础客户端测试"""

    def test_build_headers_with_api_key(self):
        """测试带 API Key 的 Header 构建"""
        client = SonarrClient(
            base_url="http://localhost:8989",
            api_key="test_key"
        )
        headers = client._build_headers()

        assert "X-Api-Key" in headers
        assert headers["X-Api-Key"] == "test_key"
        assert headers["Content-Type"] == "application/json"

    def test_build_headers_without_api_key(self):
        """测试不带 API Key 的 Header 构建"""
        from app.services.clients.base import ExternalServiceClient
        client = ExternalServiceClient(
            base_url="http://localhost:8989"
        )
        headers = client._build_headers()

        assert "X-Api-Key" not in headers
        assert headers["Content-Type"] == "application/json"

    def test_proxy_configuration(self):
        """测试代理配置"""
        proxies = {
            "http://": "http://127.0.0.1:7890",
            "https://": "http://127.0.0.1:7890",
        }
        client = SonarrClient(
            base_url="http://localhost:8989",
            api_key="test_key",
            proxies=proxies
        )

        assert client.proxies == proxies

    def test_timeout_configuration(self):
        """测试超时配置"""
        client = SonarrClient(
            base_url="http://localhost:8989",
            api_key="test_key",
            timeout=60
        )

        assert client.timeout == 60

