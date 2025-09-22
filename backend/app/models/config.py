"""
配置数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Configuration(Base):
    """系统配置模型"""
    
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)  # 加密存储的配置值
    description = Column(String(255), nullable=True)
    is_encrypted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<Configuration(id={self.id}, key='{self.key}')>"


class ServiceConfig(Base):
    """外部服务配置模型"""
    
    __tablename__ = "service_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(50), nullable=False)  # sonarr, prowlarr, proxy
    service_type = Column(String(20), nullable=False)  # api, proxy
    name = Column(String(100), nullable=False)  # 配置名称
    url = Column(String(255), nullable=False)
    api_key = Column(Text, nullable=True)  # 加密存储
    username = Column(String(100), nullable=True)
    password = Column(Text, nullable=True)  # 加密存储
    extra_config = Column(Text, nullable=True)  # JSON格式的额外配置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<ServiceConfig(id={self.id}, service_name='{self.service_name}', name='{self.name}')>"
