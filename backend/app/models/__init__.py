"""数据模型定义"""

from app.models.user import User
from app.models.config import Configuration, ServiceConfig
from app.models.dict import DictType, DictItem

__all__ = ["User", "Configuration", "ServiceConfig", "DictType", "DictItem"]
