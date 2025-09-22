"""
主应用测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_ping_endpoint():
    """测试ping端点"""
    response = client.get("/api/v1/health/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"
