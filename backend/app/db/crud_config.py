"""
配置相关的数据库操作 (CRUD)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.config import Configuration, ServiceConfig


# ---------- ServiceConfig ----------

async def get_service_configs(
    db: AsyncSession,
    *,
    service_name: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> List[ServiceConfig]:
    conditions = []
    if service_name:
        conditions.append(ServiceConfig.service_name == service_name)
    if is_active is not None:
        conditions.append(ServiceConfig.is_active == is_active)

    stmt = select(ServiceConfig)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_service_config_by_id(db: AsyncSession, *, config_id: int) -> Optional[ServiceConfig]:
    stmt = select(ServiceConfig).where(ServiceConfig.id == config_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def is_service_name_duplicate(
    db: AsyncSession, *, service_name: str, name: str, exclude_id: Optional[int] = None
) -> bool:
    stmt = select(func.count(ServiceConfig.id)).where(
        and_(ServiceConfig.service_name == service_name, ServiceConfig.name == name)
    )
    if exclude_id is not None:
        stmt = stmt.where(ServiceConfig.id != exclude_id)
    res = await db.execute(stmt)
    return int(res.scalar() or 0) > 0


async def create_service_config(
    db: AsyncSession,
    *,
    service_name: str,
    service_type: str,
    name: str,
    url: str,
    api_key: Optional[str],
    username: Optional[str],
    password: Optional[str],
    extra_config: Optional[str],
    is_active: bool = True,
) -> ServiceConfig:
    item = ServiceConfig(
        service_name=service_name,
        service_type=service_type,
        name=name,
        url=url,
        api_key=api_key,
        username=username,
        password=password,
        extra_config=extra_config,
        is_active=is_active,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_service_config(
    db: AsyncSession,
    *,
    obj: ServiceConfig,
    data: Dict[str, Any],
) -> ServiceConfig:
    for key, value in data.items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_service_config(db: AsyncSession, *, obj: ServiceConfig) -> None:
    await db.delete(obj)
    await db.commit()


# ---------- Configuration (KV) ----------

async def get_configurations(
    db: AsyncSession,
    *,
    keys: Optional[List[str]] = None,
    is_active: Optional[bool] = None,
) -> List[Configuration]:
    stmt = select(Configuration)
    if keys:
        stmt = stmt.where(Configuration.key.in_(keys))
    if is_active is not None:
        stmt = stmt.where(Configuration.is_active == is_active)
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_configuration_by_id(db: AsyncSession, *, config_id: int) -> Optional[Configuration]:
    stmt = select(Configuration).where(Configuration.id == config_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def is_kv_key_duplicate(
    db: AsyncSession, *, key: str, exclude_id: Optional[int] = None
) -> bool:
    stmt = select(func.count(Configuration.id)).where(Configuration.key == key)
    if exclude_id is not None:
        stmt = stmt.where(Configuration.id != exclude_id)
    res = await db.execute(stmt)
    return int(res.scalar() or 0) > 0


async def create_configuration(
    db: AsyncSession,
    *,
    key: str,
    value: Optional[str],
    description: Optional[str],
    is_encrypted: bool,
    is_active: bool = True,
) -> Configuration:
    item = Configuration(
        key=key,
        value=value,
        description=description,
        is_encrypted=is_encrypted,
        is_active=is_active,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_configuration(
    db: AsyncSession,
    *,
    obj: Configuration,
    data: Dict[str, Any],
) -> Configuration:
    for key, value in data.items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_configuration(db: AsyncSession, *, obj: Configuration) -> None:
    await db.delete(obj)
    await db.commit()


