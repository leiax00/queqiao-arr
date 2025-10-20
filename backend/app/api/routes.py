"""
API路由汇总
"""

from fastapi import APIRouter

from app.api.endpoints import auth, config, health, dict

# 创建主路由器
api_router = APIRouter()

# 包含各个子路由
api_router.include_router(health.router, prefix="/health", tags=["健康检查"])
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(config.router, prefix="/config", tags=["配置管理"])
api_router.include_router(dict.router, prefix="/dict", tags=["字典管理"])
