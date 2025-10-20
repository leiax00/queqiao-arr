"""
系统字典相关的 Pydantic Schema 定义
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# ----------------------- 字典类型 Schema -----------------------

class DictTypeBase(BaseModel):
    """字典类型基础 Schema"""
    code: str = Field(min_length=1, max_length=50, description="类型编码（唯一）", examples=["language"])
    name: str = Field(min_length=1, max_length=100, description="类型名称", examples=["语言选项"])
    remark: Optional[str] = Field(default=None, description="备注说明")
    is_active: bool = Field(default=True, description="是否启用")


class DictTypeCreate(DictTypeBase):
    """创建字典类型 Schema"""
    pass


class DictTypeUpdate(BaseModel):
    """更新字典类型 Schema（不允许修改 code）"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="类型名称")
    remark: Optional[str] = Field(default=None, description="备注说明")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class DictTypeOut(DictTypeBase):
    """字典类型输出 Schema"""
    id: int = Field(description="类型ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


# ----------------------- 字典项 Schema -----------------------

class DictItemBase(BaseModel):
    """字典项基础 Schema"""
    dict_type_code: str = Field(min_length=1, max_length=50, description="字典类型编码", examples=["language"])
    code: str = Field(min_length=1, max_length=50, description="项编码", examples=["zh-CN"])
    name: str = Field(min_length=1, max_length=100, description="显示名称", examples=["简体中文"])
    value: str = Field(min_length=1, max_length=200, description="实际值", examples=["zh-CN"])
    sort_order: int = Field(default=0, ge=0, le=9999, description="排序（升序）")
    parent_id: Optional[int] = Field(default=None, description="父项ID（层级）")
    remark: Optional[str] = Field(default=None, description="备注说明")
    is_active: bool = Field(default=True, description="是否启用")
    extra_data: Optional[str] = Field(default=None, description="扩展数据（JSON字符串）")


class DictItemCreate(DictItemBase):
    """创建字典项 Schema"""
    pass


class DictItemUpdate(BaseModel):
    """更新字典项 Schema（不允许修改 dict_type_code 和 code）"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="显示名称")
    value: Optional[str] = Field(default=None, min_length=1, max_length=200, description="实际值")
    sort_order: Optional[int] = Field(default=None, ge=0, le=9999, description="排序")
    parent_id: Optional[int] = Field(default=None, description="父项ID")
    remark: Optional[str] = Field(default=None, description="备注说明")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    extra_data: Optional[str] = Field(default=None, description="扩展数据（JSON字符串）")


class DictItemOut(DictItemBase):
    """字典项输出 Schema"""
    id: int = Field(description="字典项ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


# ----------------------- 选项查询 Schema -----------------------

class DictOptionOut(BaseModel):
    """字典选项输出 Schema（简化版，用于下拉列表）"""
    code: str = Field(description="项编码")
    name: str = Field(description="显示名称")
    value: str = Field(description="实际值")
    extra_data: Optional[str] = Field(default=None, description="扩展数据（JSON字符串）")
    
    class Config:
        from_attributes = True


class DictOptionsResponse(BaseModel):
    """字典选项响应 Schema"""
    dict_type: Dict[str, str] = Field(description="字典类型信息")
    options: list[DictOptionOut] = Field(description="选项列表")


# ----------------------- 分页响应 Schema -----------------------

class DictTypeListResponse(BaseModel):
    """字典类型列表响应 Schema"""
    items: list[DictTypeOut] = Field(description="字典类型列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页条数")


class DictItemListResponse(BaseModel):
    """字典项列表响应 Schema"""
    items: list[DictItemOut] = Field(description="字典项列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页条数")

