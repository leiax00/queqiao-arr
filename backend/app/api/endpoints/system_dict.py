"""
系统字典管理端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.api.endpoints.auth import get_current_user, get_current_superuser
from app.db import crud_system_dict
from app.utils import success_response, error_response
from app.api.schemas.system_dict import (
    DictTypeOut,
    DictTypeCreate,
    DictTypeUpdate,
    DictTypeListResponse,
    DictItemOut,
    DictItemCreate,
    DictItemUpdate,
    DictItemListResponse,
    DictOptionOut,
    DictOptionsResponse,
)

router = APIRouter()


# ----------------------- 字典类型管理 -----------------------

@router.get(
    "/types",
    summary="获取字典类型列表",
    description="获取字典类型列表（分页）",
    response_model=None,
)
async def get_dict_types(
    is_active: Optional[bool] = Query(default=None, description="是否启用筛选"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取字典类型列表"""
    items, total = await crud_system_dict.get_dict_types(
        db,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    
    response_data = DictTypeListResponse(
        items=[DictTypeOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    
    return success_response(response_data.model_dump())


@router.post(
    "/types",
    summary="创建字典类型",
    description="创建字典类型（仅管理员）",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def create_dict_type(
    data: DictTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_superuser),
):
    """创建字典类型"""
    # 检查编码是否重复
    if await crud_system_dict.is_dict_type_code_duplicate(db, code=data.code):
        return error_response(code=409, message=f"字典类型编码 '{data.code}' 已存在")
    
    # 创建字典类型
    item = await crud_system_dict.create_dict_type(
        db,
        code=data.code,
        name=data.name,
        remark=data.remark,
        is_active=data.is_active,
    )
    
    return success_response(DictTypeOut.model_validate(item).model_dump())


@router.put(
    "/types/{type_id}",
    summary="更新字典类型",
    description="更新字典类型（不允许修改编码，仅管理员）",
    response_model=None,
)
async def update_dict_type(
    type_id: int,
    data: DictTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_superuser),
):
    """更新字典类型"""
    # 查询字典类型
    dict_type = await crud_system_dict.get_dict_type_by_id(db, type_id=type_id)
    if not dict_type:
        return error_response(code=404, message="字典类型不存在")
    
    # 更新字典类型
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        dict_type = await crud_system_dict.update_dict_type(db, obj=dict_type, data=update_data)
    
    return success_response(DictTypeOut.model_validate(dict_type).model_dump())


@router.delete(
    "/types/{type_id}",
    summary="删除字典类型",
    description="删除字典类型（级联删除所有字典项，仅管理员）",
    response_model=None,
)
async def delete_dict_type(
    type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_superuser),
):
    """删除字典类型"""
    # 查询字典类型
    dict_type = await crud_system_dict.get_dict_type_by_id(db, type_id=type_id)
    if not dict_type:
        return error_response(code=404, message="字典类型不存在")
    
    # 删除字典类型（级联删除字典项）
    await crud_system_dict.delete_dict_type(db, obj=dict_type)
    
    return success_response({"deleted": True})


# ----------------------- 字典项管理 -----------------------

@router.get(
    "/items",
    summary="获取字典项列表",
    description="获取字典项列表（分页）",
    response_model=None,
)
async def get_dict_items(
    dict_type_code: str = Query(..., description="字典类型编码（必填）"),
    is_active: Optional[bool] = Query(default=None, description="是否启用筛选"),
    parent_id: Optional[int] = Query(default=None, description="父项ID筛选"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=50, ge=1, le=200, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取字典项列表"""
    # 验证字典类型是否存在
    dict_type = await crud_system_dict.get_dict_type_by_code(db, code=dict_type_code)
    if not dict_type:
        return error_response(code=404, message=f"字典类型 '{dict_type_code}' 不存在")
    
    # 获取字典项列表
    items, total = await crud_system_dict.get_dict_items(
        db,
        dict_type_code=dict_type_code,
        is_active=is_active,
        parent_id=parent_id,
        page=page,
        page_size=page_size,
    )
    
    response_data = DictItemListResponse(
        items=[DictItemOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    
    return success_response(response_data.model_dump())


@router.get(
    "/items/{item_id}",
    summary="获取字典项详情",
    description="获取单个字典项详情",
    response_model=None,
)
async def get_dict_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取字典项详情"""
    item = await crud_system_dict.get_dict_item_by_id(db, item_id=item_id)
    if not item:
        return error_response(code=404, message="字典项不存在")
    
    return success_response(DictItemOut.model_validate(item).model_dump())


@router.post(
    "/items",
    summary="创建字典项",
    description="创建字典项（仅管理员）",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def create_dict_item(
    data: DictItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_superuser),
):
    """创建字典项"""
    # 验证字典类型是否存在
    dict_type = await crud_system_dict.get_dict_type_by_code(db, code=data.dict_type_code)
    if not dict_type:
        return error_response(code=404, message=f"字典类型 '{data.dict_type_code}' 不存在")
    
    # 检查编码是否重复
    if await crud_system_dict.is_dict_item_code_duplicate(
        db, dict_type_code=data.dict_type_code, code=data.code
    ):
        return error_response(
            code=409,
            message=f"字典项编码 '{data.code}' 在类型 '{data.dict_type_code}' 下已存在"
        )
    
    # 如果指定了父项，验证父项是否存在且属于同一类型
    if data.parent_id:
        parent = await crud_system_dict.get_dict_item_by_id(db, item_id=data.parent_id)
        if not parent:
            return error_response(code=404, message=f"父项ID {data.parent_id} 不存在")
        if parent.dict_type_code != data.dict_type_code:
            return error_response(code=400, message="父项必须属于同一字典类型")
    
    # 创建字典项
    item = await crud_system_dict.create_dict_item(
        db,
        dict_type_code=data.dict_type_code,
        code=data.code,
        name=data.name,
        value=data.value,
        sort_order=data.sort_order,
        parent_id=data.parent_id,
        remark=data.remark,
        is_active=data.is_active,
        extra_data=data.extra_data,
    )
    
    return success_response(DictItemOut.model_validate(item).model_dump())


@router.put(
    "/items/{item_id}",
    summary="更新字典项",
    description="更新字典项（不允许修改字典类型编码和项编码，仅管理员）",
    response_model=None,
)
async def update_dict_item(
    item_id: int,
    data: DictItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_superuser),
):
    """更新字典项"""
    # 查询字典项
    item = await crud_system_dict.get_dict_item_by_id(db, item_id=item_id)
    if not item:
        return error_response(code=404, message="字典项不存在")
    
    # 如果更新了父项，验证父项是否存在且属于同一类型
    if data.parent_id is not None and data.parent_id != item.parent_id:
        if data.parent_id == item_id:
            return error_response(code=400, message="不能将自己设置为父项")
        
        parent = await crud_system_dict.get_dict_item_by_id(db, item_id=data.parent_id)
        if not parent:
            return error_response(code=404, message=f"父项ID {data.parent_id} 不存在")
        if parent.dict_type_code != item.dict_type_code:
            return error_response(code=400, message="父项必须属于同一字典类型")
    
    # 更新字典项
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        item = await crud_system_dict.update_dict_item(db, obj=item, data=update_data)
    
    return success_response(DictItemOut.model_validate(item).model_dump())


@router.delete(
    "/items/{item_id}",
    summary="删除字典项",
    description="删除字典项（级联删除子项，仅管理员）",
    response_model=None,
)
async def delete_dict_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_superuser),
):
    """删除字典项"""
    # 查询字典项
    item = await crud_system_dict.get_dict_item_by_id(db, item_id=item_id)
    if not item:
        return error_response(code=404, message="字典项不存在")
    
    # 删除字典项（级联删除子项）
    await crud_system_dict.delete_dict_item(db, obj=item)
    
    return success_response({"deleted": True})


# ----------------------- 统一选项查询 -----------------------

@router.get(
    "/options/{dict_type_code}",
    summary="获取字典选项",
    description="获取指定字典类型的所有启用选项（用于前端下拉列表）",
    response_model=None,
)
async def get_dict_options(
    dict_type_code: str,
    parent_id: Optional[int] = Query(default=None, description="父项ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取字典选项"""
    # 验证字典类型是否存在且启用
    dict_type = await crud_system_dict.get_dict_type_by_code(db, code=dict_type_code)
    if not dict_type:
        return error_response(code=404, message=f"字典类型 '{dict_type_code}' 不存在")
    
    if not dict_type.is_active:
        return error_response(code=400, message=f"字典类型 '{dict_type_code}' 未启用")
    
    # 获取启用的字典项
    items = await crud_system_dict.get_dict_options(
        db,
        dict_type_code=dict_type_code,
        parent_id=parent_id,
    )
    
    response_data = DictOptionsResponse(
        dict_type={"code": dict_type.code, "name": dict_type.name},
        options=[DictOptionOut.model_validate(item) for item in items],
    )
    
    return success_response(response_data.model_dump())

