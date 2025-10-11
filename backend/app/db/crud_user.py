"""User 相关的数据库操作 (CRUD)"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.core.security import get_password_hash, verify_password


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def get_user_count(db: AsyncSession) -> int:
    stmt = select(func.count(User.id))
    res = await db.execute(stmt)
    return int(res.scalar() or 0)


async def create_user(
    db: AsyncSession,
    *,
    username: str,
    password: str,
    email: Optional[str] = None,
    is_superuser: bool = False,
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        is_superuser=is_superuser,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, *, username: str, password: str
) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def delete_user_by_username(db: AsyncSession, username: str) -> bool:
    user = await get_user_by_username(db, username)
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True


