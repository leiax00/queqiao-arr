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
        assert data["services"][0]["api_key_masked"].startswith("****")


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

        # Mock httpx.AsyncClient.get 成功
        class MockResp:
            status_code = 200

        class MockClientOK:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

            async def get(self, url, headers=None):
                return MockResp()

        import app.api.endpoints.config as cfg

        async def ok_call(*a, **k):
            return MockClientOK()

        monkeypatch.setattr(cfg.httpx, "AsyncClient", MockClientOK)
        ok = await ac.post(
            "/api/v1/config/test-connection",
            headers={"Authorization": f"Bearer {token}"},
            json={"mode": "by_body", "service_name": "sonarr", "url": "http://x"},
        )
        assert ok.status_code == 200
        assert ok.json()["data"]["ok"] is True

        # Mock 异常
        class MockClientFail(MockClientOK):
            async def get(self, url, headers=None):
                raise RuntimeError("boom")

        monkeypatch.setattr(cfg.httpx, "AsyncClient", MockClientFail)
        fail = await ac.post(
            "/api/v1/config/test-connection",
            headers={"Authorization": f"Bearer {token}"},
            json={"mode": "by_body", "service_name": "sonarr", "url": "http://x"},
        )
        assert fail.status_code == 200
        assert fail.json()["data"]["ok"] is False


