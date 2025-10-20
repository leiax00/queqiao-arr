"""
系统字典相关的数据库操作 (CRUD)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dict import DictType, DictItem


# ---------- 字典类型 CRUD ----------

async def get_dict_types(
    db: AsyncSession,
    *,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[List[DictType], int]:
    """
    获取字典类型列表（分页）
    
    Args:
        db: 数据库会话
        is_active: 是否启用筛选
        page: 页码（从1开始）
        page_size: 每页条数
        
    Returns:
        (字典类型列表, 总数)
    """
    conditions = []
    if is_active is not None:
        conditions.append(DictType.is_active == is_active)
    
    # 查询总数
    count_stmt = select(func.count(DictType.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total_result = await db.execute(count_stmt)
    total = int(total_result.scalar() or 0)
    
    # 查询数据
    stmt = select(DictType).order_by(DictType.id)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    return items, total


async def get_dict_type_by_id(db: AsyncSession, *, type_id: int) -> Optional[DictType]:
    """根据ID获取字典类型"""
    stmt = select(DictType).where(DictType.id == type_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_dict_type_by_code(db: AsyncSession, *, code: str) -> Optional[DictType]:
    """根据编码获取字典类型"""
    stmt = select(DictType).where(DictType.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def is_dict_type_code_duplicate(
    db: AsyncSession, *, code: str, exclude_id: Optional[int] = None
) -> bool:
    """检查字典类型编码是否重复"""
    stmt = select(func.count(DictType.id)).where(DictType.code == code)
    if exclude_id is not None:
        stmt = stmt.where(DictType.id != exclude_id)
    result = await db.execute(stmt)
    return int(result.scalar() or 0) > 0


async def create_dict_type(
    db: AsyncSession,
    *,
    code: str,
    name: str,
    remark: Optional[str] = None,
    is_active: bool = True,
) -> DictType:
    """创建字典类型"""
    item = DictType(
        code=code,
        name=name,
        remark=remark,
        is_active=is_active,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_dict_type(
    db: AsyncSession,
    *,
    obj: DictType,
    data: Dict[str, Any],
) -> DictType:
    """更新字典类型"""
    for key, value in data.items():
        if value is not None:  # 只更新非 None 的值
            setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_dict_type(db: AsyncSession, *, obj: DictType) -> None:
    """删除字典类型（级联删除所有字典项）"""
    await db.delete(obj)
    await db.commit()


# ---------- 字典项 CRUD ----------

async def get_dict_items(
    db: AsyncSession,
    *,
    dict_type_code: str,
    is_active: Optional[bool] = None,
    parent_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[List[DictItem], int]:
    """
    获取字典项列表（分页）
    
    Args:
        db: 数据库会话
        dict_type_code: 字典类型编码（必填）
        is_active: 是否启用筛选
        parent_id: 父项ID筛选
        page: 页码（从1开始）
        page_size: 每页条数
        
    Returns:
        (字典项列表, 总数)
    """
    conditions = [DictItem.dict_type_code == dict_type_code]
    
    if is_active is not None:
        conditions.append(DictItem.is_active == is_active)
    if parent_id is not None:
        conditions.append(DictItem.parent_id == parent_id)
    
    # 查询总数
    count_stmt = select(func.count(DictItem.id)).where(and_(*conditions))
    total_result = await db.execute(count_stmt)
    total = int(total_result.scalar() or 0)
    
    # 查询数据（按 sort_order 升序，再按 id 升序）
    stmt = (
        select(DictItem)
        .where(and_(*conditions))
        .order_by(DictItem.sort_order, DictItem.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    return items, total


async def get_dict_item_by_id(db: AsyncSession, *, item_id: int) -> Optional[DictItem]:
    """根据ID获取字典项"""
    stmt = select(DictItem).where(DictItem.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def is_dict_item_code_duplicate(
    db: AsyncSession,
    *,
    dict_type_code: str,
    code: str,
    exclude_id: Optional[int] = None
) -> bool:
    """检查字典项编码在同一类型下是否重复"""
    stmt = select(func.count(DictItem.id)).where(
        and_(
            DictItem.dict_type_code == dict_type_code,
            DictItem.code == code
        )
    )
    if exclude_id is not None:
        stmt = stmt.where(DictItem.id != exclude_id)
    result = await db.execute(stmt)
    return int(result.scalar() or 0) > 0


async def create_dict_item(
    db: AsyncSession,
    *,
    dict_type_code: str,
    code: str,
    name: str,
    value: str,
    sort_order: int = 0,
    parent_id: Optional[int] = None,
    remark: Optional[str] = None,
    is_active: bool = True,
    extra_data: Optional[str] = None,
) -> DictItem:
    """创建字典项"""
    item = DictItem(
        dict_type_code=dict_type_code,
        code=code,
        name=name,
        value=value,
        sort_order=sort_order,
        parent_id=parent_id,
        remark=remark,
        is_active=is_active,
        extra_data=extra_data,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_dict_item(
    db: AsyncSession,
    *,
    obj: DictItem,
    data: Dict[str, Any],
) -> DictItem:
    """更新字典项"""
    for key, value in data.items():
        if value is not None:  # 只更新非 None 的值
            setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_dict_item(db: AsyncSession, *, obj: DictItem) -> None:
    """删除字典项（级联删除子项）"""
    await db.delete(obj)
    await db.commit()


# ---------- 选项查询 ----------

async def get_dict_options(
    db: AsyncSession,
    *,
    dict_type_code: str,
    parent_id: Optional[int] = None,
) -> List[DictItem]:
    """
    获取字典选项（仅返回启用的项，用于下拉列表）
    
    Args:
        db: 数据库会话
        dict_type_code: 字典类型编码
        parent_id: 父项ID筛选（可选）
        
    Returns:
        字典项列表
    """
    conditions = [
        DictItem.dict_type_code == dict_type_code,
        DictItem.is_active == True
    ]
    
    if parent_id is not None:
        conditions.append(DictItem.parent_id == parent_id)
    
    stmt = (
        select(DictItem)
        .where(and_(*conditions))
        .order_by(DictItem.sort_order, DictItem.id)
    )
    
    result = await db.execute(stmt)
    return list(result.scalars().all())

