"""
健康检查端点
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """
    健康检查端点
    
    Returns:
        dict: 服务状态信息
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.DEBUG else "production"
    }


@router.get("/ping")
async def ping():
    """
    简单的ping端点
    
    Returns:
        dict: pong响应
    """
    return {"message": "pong"}
