# -*- coding: utf-8 -*-
import asyncio
import json
import pytest
from httpx import AsyncClient

from app.main import app
from app.db.database import drop_tables, create_tables


@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    # fresh DB for this module
    await drop_tables()
    await create_tables()
    yield
    # no teardown to allow post-test inspection if needed


@pytest.mark.asyncio
async def test_register_first_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/auth/register",
            json={"username": "admin", "password": "P@ssw0rd", "email": "admin@example.com"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["data"]["user"]["username"] == "admin"
        assert body["data"]["user"]["is_superuser"] is True
        assert body["data"]["access_token"]


@pytest.mark.asyncio
async def test_register_duplicate_forbidden():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/auth/register",
            json={"username": "other", "password": "P@ssw0rd"},
        )
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_login_and_me():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login = await ac.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "P@ssw0rd"},
        )
        assert login.status_code == 200
        token = login.json()["data"]["access_token"]
        me = await ac.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200
        assert me.json()["data"]["username"] == "admin"
