"""
认证相关端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.core.security import verify_token
from app.utils import success_response, error_response

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    email: Optional[EmailStr] = None


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

router = APIRouter()
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户依赖项
    
    Args:
        credentials: HTTP Bearer凭据
        db: 数据库会话
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = verify_token(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: 从数据库查询用户信息
    # user = await get_user_by_username(db, username)
    # if not user or not user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="用户不存在或已禁用",
    #     )
    
    return {"username": username}  # 临时返回，后续实现完整用户查询


@router.post("/login")
async def login(payload: LoginRequest):
    """
    用户登录端点
    
    TODO: 实现完整的登录逻辑
    """
    # 骨架：返回统一响应结构（后续接入真实认证逻辑）
    return success_response({
        "access_token": "",
        "token_type": "bearer",
        "expires_in": 0,
    })


@router.post("/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册端点（仅首次运行时可用）
    
    TODO: 实现完整的注册逻辑
    """
    # 骨架：返回统一响应结构（后续接入首用户创建逻辑）
    return success_response({
        "user": None,
        "access_token": "",
        "token_type": "bearer",
        "expires_in": 0,
    })


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 用户信息
    """
    return success_response(current_user)
