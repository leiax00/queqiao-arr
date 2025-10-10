"""统一响应封装工具"""

from typing import Any, Optional, Dict


def success_response(data: Optional[Any] = None, message: str = "OK", code: int = 200) -> Dict[str, Any]:
    """
    构建统一成功响应
    """
    return {
        "code": code,
        "message": message,
        "data": data,
    }


def error_response(message: str, code: int, data: Optional[Any] = None) -> Dict[str, Any]:
    """
    构建统一错误响应
    """
    return {
        "code": code,
        "message": message,
        "data": data,
    }


