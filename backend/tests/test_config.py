# -*- coding: utf-8 -*-
import json
import pytest
from httpx import AsyncClient

from app.main import app
from app.db.database import drop_tables, create_tables


@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    await drop_tables()
    await create_tables()
    yield


@pytest.mark.asyncio
async def test_create_and_list_service_config(monkeypatch):
    # mock login: 简化，直接调用需要鉴权的接口前先获取一个token
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await drop_tables(); await create_tables()
        # bootstrap: 注册管理员
        r = await ac.post("/api/v1/auth/register", json={"username": "admin", "password": "P@ssw0rd"})
        token = r.json()["data"]["access_token"]

        # 创建服务配置（包含敏感字段）
        resp = await ac.post(
            "/api/v1/config/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "type": "service",
                "service_name": "sonarr",
                "service_type": "api",
                "name": "主Sonarr",
                "url": "http://127.0.0.1:8989",
                "api_key": "TESTKEY123456",
                "username": "u",
                "password": "p",
                "extra_config": {"timeout": 3000},
            },
        )
        assert resp.status_code == 200
        created_id = resp.json()["data"]["id"]
        assert created_id > 0

        # 列表：应返回掩码 api_key_masked
        lst = await ac.get("/api/v1/config/", headers={"Authorization": f"Bearer {token}"})
        assert lst.status_code == 200
        data = lst.json()["data"]
        assert len(data["services"]) == 1
        # API Key "TESTKEY123456" (13位) 的掩码应为 "TEST*****3456" (前4位+中间5个星号+后4位)
        assert data["services"][0]["api_key_masked"] == "TEST*****3456"


@pytest.mark.asyncio
async def test_update_delete_service_config():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 登录
        login = await ac.post("/api/v1/auth/login", json={"username": "admin", "password": "P@ssw0rd"})
        token = login.json()["data"]["access_token"]

        # 获取现有配置ID
        lst = await ac.get("/api/v1/config/", headers={"Authorization": f"Bearer {token}"})
        sid = lst.json()["data"]["services"][0]["id"]

        # 更新URL
        upd = await ac.put(
            f"/api/v1/config/{sid}",
            headers={"Authorization": f"Bearer {token}"},
            json={"url": "http://localhost:8989"},
        )
        assert upd.status_code == 200

        # 删除
        dele = await ac.delete(f"/api/v1/config/{sid}", headers={"Authorization": f"Bearer {token}"})
        assert dele.status_code == 200


@pytest.mark.asyncio
async def test_kv_create_update():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 登录
        login = await ac.post("/api/v1/auth/login", json={"username": "admin", "password": "P@ssw0rd"})
        token = login.json()["data"]["access_token"]

        # 创建加密KV
        resp = await ac.post(
            "/api/v1/config/",
            headers={"Authorization": f"Bearer {token}"},
            json={"type": "kv", "key": "secret", "value": "v1", "is_encrypted": True},
        )
        assert resp.status_code == 200
        cid = resp.json()["data"]["id"]

        # 更新值（依旧加密）
        upd = await ac.put(
            f"/api/v1/config/{cid}",
            headers={"Authorization": f"Bearer {token}"},
            json={"value": "v2", "is_encrypted": True},
        )
        assert upd.status_code == 200


@pytest.mark.asyncio
async def test_connection_success_and_fail(monkeypatch):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 登录
        login = await ac.post("/api/v1/auth/login", json={"username": "admin", "password": "P@ssw0rd"})
        token = login.json()["data"]["access_token"]

        # Mock 客户端工厂和客户端的 check_status 方法
        class MockClientOK:
            def __init__(self, *args, **kwargs):
                pass
            
            def check_status(self):
                return True, "连接成功"

        class MockClientFail:
            def __init__(self, *args, **kwargs):
                pass
            
            def check_status(self):
                return False, "连接失败: boom"

        # Mock 成功情况 - patch 客户端层的工厂
        def make_client_ok(*args, **kwargs):
            return MockClientOK()
        
        monkeypatch.setattr("app.services.clients.make_client", make_client_ok)
        ok = await ac.post(
            "/api/v1/config/test-connection",
            headers={"Authorization": f"Bearer {token}"},
            json={"mode": "by_body", "service_name": "sonarr", "url": "http://x", "api_key": "test_key"},
        )
        assert ok.status_code == 200
        ok_data = ok.json()
        assert ok_data is not None
        assert "data" in ok_data
        assert ok_data["data"]["ok"] is True

        # Mock 失败情况
        def make_client_fail(*args, **kwargs):
            return MockClientFail()
        
        monkeypatch.setattr("app.services.clients.make_client", make_client_fail)
        fail = await ac.post(
            "/api/v1/config/test-connection",
            headers={"Authorization": f"Bearer {token}"},
            json={"mode": "by_body", "service_name": "sonarr", "url": "http://x", "api_key": "test_key"},
        )
        assert fail.status_code == 200
        assert fail.json()["data"]["ok"] is False


