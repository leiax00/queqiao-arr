"""
认证相关端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.core.security import verify_token, create_access_token
from app.core.config import settings
from app.db.crud_user import (
    get_user_by_username,
    get_user_count,
    create_user,
    authenticate_user,
    delete_user_by_username,
)
from app.utils import success_response, error_response

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        description="用户名（3-50字符，需唯一）",
        examples=["admin"],
    )
    password: str = Field(
        min_length=8,
        max_length=32,
        description="密码（8-32字符）",
        examples=["P@ssw0rd"],
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="邮箱（可选，用于找回与通知）",
        examples=["admin@example.com"],
    )


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        description="用户名",
        examples=["admin"],
    )
    password: str = Field(
        min_length=8,
        max_length=32,
        description="密码（8-32字符）",
        examples=["P@ssw0rd"],
    )


class UserOut(BaseModel):
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    email: Optional[EmailStr] = Field(default=None, description="邮箱")
    is_active: bool = Field(description="是否启用")
    is_superuser: bool = Field(description="是否为超级管理员")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str = Field(description="访问令牌 (JWT)")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="令牌有效期（秒）")

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
    
    user = await get_user_by_username(db, username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
        )
    return user


async def get_current_superuser(
    current_user=Depends(get_current_user)
):
    """
    获取当前超级管理员用户依赖项
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        User: 当前超级管理员用户对象
        
    Raises:
        HTTPException: 非超级管理员时抛出403错误
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅超级管理员可执行此操作",
        )
    return current_user


@router.post(
    "/login",
    summary="用户登录",
    description="使用用户名与密码登录，成功后返回短期有效的访问令牌",
    responses={
        200: {
            "description": "登录成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "access_token": "<jwt>",
                            "token_type": "bearer",
                            "expires_in": 1800
                        }
                    }
                }
            }
        },
        401: {
            "description": "用户名或密码错误",
            "content": {
                "application/json": {
                    "example": {"detail": "用户名或密码错误"}
                }
            }
        }
    },
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录端点
    """
    user = await authenticate_user(db, username=payload.username, password=payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token(subject=user.username)
    return success_response({"access_token": token, "token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60})


@router.post(
    "/register",
    summary="首次运行注册管理员",
    description="当且仅当系统无用户时允许注册首个管理员账户，成功后自动登录返回令牌",
    responses={
        200: {
            "description": "注册成功并返回令牌",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "user": {
                                "id": 1,
                                "username": "admin",
                                "email": "admin@example.com",
                                "is_active": True,
                                "is_superuser": True
                            },
                            "access_token": "<jwt>",
                            "token_type": "bearer",
                            "expires_in": 1800
                        }
                    }
                }
            }
        },
        403: {
            "description": "已有用户时禁止再次注册",
            "content": {
                "application/json": {
                    "example": {"detail": "已存在用户，禁止再次注册"}
                }
            }
        },
        409: {
            "description": "用户名冲突",
            "content": {
                "application/json": {
                    "example": {"detail": "用户名已存在"}
                }
            }
        }
    },
)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册端点（仅首次运行时可用）
    """
    # 仅当系统无用户时允许注册首个管理员
    total = await get_user_count(db)
    if total > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="已存在用户，禁止再次注册")
    # 用户名重复检查（理论上无用户时不会触发，此处稳健防御）
    exists = await get_user_by_username(db, payload.username)
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user = await create_user(db, username=payload.username, password=payload.password, email=payload.email, is_superuser=True)
    token = create_access_token(subject=user.username)
    return success_response({
        "user": UserOut.model_validate(user).model_dump(),
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    })


@router.get(
    "/me",
    summary="获取当前用户信息",
    description="基于 Bearer 令牌解析当前登录用户并返回其信息",
    responses={
        200: {
            "description": "成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "id": 1,
                            "username": "admin",
                            "email": "admin@example.com",
                            "is_active": True,
                            "is_superuser": True
                        }
                    }
                }
            }
        },
        401: {
            "description": "未认证或令牌无效",
            "content": {
                "application/json": {
                    "example": {"detail": "未提供认证凭据"}
                }
            }
        }
    },
)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 用户信息
    """
    return success_response(UserOut.model_validate(current_user).model_dump())


@router.post(
    "/refresh",
    summary="刷新令牌",
    description="使用现有有效令牌签发新的访问令牌（简单刷新机制）",
    responses={
        200: {
            "description": "刷新成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "access_token": "<jwt>",
                            "token_type": "bearer",
                            "expires_in": 1800
                        }
                    }
                }
            }
        },
        401: {
            "description": "未认证",
            "content": {
                "application/json": {
                    "example": {"detail": "未提供认证凭据"}
                }
            }
        }
    },
)
async def refresh_token(current_user=Depends(get_current_user)):
    token = create_access_token(subject=current_user.username)
    return success_response({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    })


@router.post(
    "/logout",
    summary="用户登出",
    description="无状态 JWT 登出：前端清理本地令牌即可，此端点返回 200",
    responses={
        200: {
            "description": "登出成功",
            "content": {
                "application/json": {
                    "example": {"code": 200, "message": "Logged out", "data": None}
                }
            }
        }
    },
)
async def logout():
    return success_response(None, message="Logged out")


@router.delete(
    "/users/{username}",
    summary="删除用户（仅超级管理员）",
    description="删除指定用户名的用户，要求当前用户为超级管理员",
    responses={
        200: {
            "description": "删除成功",
            "content": {
                "application/json": {
                    "example": {"code": 200, "message": "OK", "data": {"deleted": "user1"}}
                }
            }
        },
        400: {
            "description": "非法操作（自删）",
            "content": {
                "application/json": {
                    "example": {"detail": "不能删除当前登录用户"}
                }
            }
        },
        401: {
            "description": "未认证",
            "content": {
                "application/json": {
                    "example": {"detail": "未提供认证凭据"}
                }
            }
        },
        403: {
            "description": "权限不足",
            "content": {
                "application/json": {
                    "example": {"detail": "仅超级管理员可删除用户"}
                }
            }
        },
        404: {
            "description": "用户不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "用户不存在"}
                }
            }
        }
    },
)
async def delete_user(
    username: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅超级管理员可删除用户")
    if current_user.username == username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除当前登录用户")
    ok = await delete_user_by_username(db, username)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return success_response({"deleted": username})
