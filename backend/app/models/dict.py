"""
系统字典数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class DictType(Base):
    """字典类型模型"""
    
    __tablename__ = "dict_types"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="类型编码（唯一）")
    name = Column(String(100), nullable=False, comment="类型名称")
    remark = Column(Text, nullable=True, comment="备注说明")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<DictType(id={self.id}, code='{self.code}', name='{self.name}')>"


class DictItem(Base):
    """字典项模型"""
    
    __tablename__ = "dict_items"
    
    id = Column(Integer, primary_key=True, index=True)
    dict_type_code = Column(
        String(50), 
        ForeignKey("dict_types.code", ondelete="CASCADE"), 
        nullable=False, 
        index=True, 
        comment="字典类型编码"
    )
    code = Column(String(50), nullable=False, index=True, comment="项编码")
    name = Column(String(100), nullable=False, comment="显示名称")
    value = Column(String(200), nullable=False, comment="实际值")
    sort_order = Column(Integer, default=0, comment="排序（升序）")
    parent_id = Column(
        Integer, 
        ForeignKey("dict_items.id", ondelete="CASCADE"), 
        nullable=True, 
        comment="父项ID（层级）"
    )
    remark = Column(Text, nullable=True, comment="备注说明")
    is_active = Column(Boolean, default=True, comment="是否启用")
    extra_data = Column(Text, nullable=True, comment="扩展数据（JSON）")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    __table_args__ = (
        UniqueConstraint('dict_type_code', 'code', name='uq_dict_item_type_code'),
    )
    
    def __repr__(self) -> str:
        return f"<DictItem(id={self.id}, dict_type_code='{self.dict_type_code}', code='{self.code}', name='{self.name}')>"

