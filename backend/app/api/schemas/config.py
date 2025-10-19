"""
配置相关的 Pydantic Schema 定义
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any


# ----------------------- 输出 Schema -----------------------

class ServiceConfigOut(BaseModel):
    id: int = Field(description="配置ID")
    service_name: str = Field(description="服务名：sonarr|prowlarr|proxy|tmdb")
    service_type: str = Field(description="服务类型：api|proxy|metadata")
    name: str = Field(description="配置名称")
    url: str = Field(description="服务基础URL")
    api_key_masked: Optional[str] = Field(default=None, description="API Key 掩码，仅展示末4位")
    username: Optional[str] = Field(default=None, description="用户名（可选）")
    is_active: bool = Field(description="是否启用")
    extra_config: Optional[Dict[str, Any]] = Field(default=None, description="额外配置（JSON 反序列化）")
    created_at: Optional[str] = Field(default=None, description="创建时间 ISO8601")
    updated_at: Optional[str] = Field(default=None, description="更新时间 ISO8601")

    class Config:
        from_attributes = True


class KVConfigOut(BaseModel):
    id: int = Field(description="配置ID")
    key: str = Field(description="键")
    value: Optional[str] = Field(default=None, description="值（若加密则不返回明文）")
    has_value: Optional[bool] = Field(default=None, description="当 is_encrypted=True 时，指示是否已设置值")
    is_encrypted: bool = Field(description="是否加密存储")
    is_active: bool = Field(description="是否启用")
    created_at: Optional[str] = Field(default=None, description="创建时间 ISO8601")
    updated_at: Optional[str] = Field(default=None, description="更新时间 ISO8601")

    class Config:
        from_attributes = True


# ----------------------- 创建 Schema -----------------------

class ServiceConfigCreate(BaseModel):
    type: Literal["service"] = Field(description="配置类型固定为 service", examples=["service"])
    service_name: Literal["sonarr", "prowlarr", "proxy", "tmdb"] = Field(description="服务名", examples=["sonarr"])
    service_type: Literal["api", "proxy", "metadata"] = Field(description="服务类型", examples=["api"])
    name: str = Field(min_length=1, max_length=100, description="配置名称", examples=["主Sonarr"])
    url: str = Field(min_length=1, max_length=255, description="服务URL", examples=["http://127.0.0.1:8989"])
    api_key: Optional[str] = Field(default=None, description="API Key（可选）")
    username: Optional[str] = Field(default=None, description="用户名（可选）")
    password: Optional[str] = Field(default=None, description="密码（可选）")
    extra_config: Optional[Dict[str, Any]] = Field(default=None, description="额外配置（JSON）")
    is_active: bool = Field(default=True, description="是否启用")


class KVConfigCreate(BaseModel):
    type: Literal["kv"] = Field(description="配置类型固定为 kv", examples=["kv"])
    key: str = Field(min_length=1, max_length=100, description="键", examples=["http_proxy"])
    value: Optional[str] = Field(default=None, description="值")
    description: Optional[str] = Field(default=None, description="描述")
    is_encrypted: bool = Field(default=False, description="是否加密存储")
    is_active: bool = Field(default=True, description="是否启用")


# ----------------------- 更新 Schema -----------------------

class ServiceConfigUpdate(BaseModel):
    service_name: Optional[Literal["sonarr", "prowlarr", "proxy", "tmdb"]] = Field(default=None, description="服务名")
    service_type: Optional[Literal["api", "proxy", "metadata"]] = Field(default=None, description="服务类型")
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="配置名称")
    url: Optional[str] = Field(default=None, min_length=1, max_length=255, description="服务URL")
    api_key: Optional[str] = Field(default=None, description="API Key")
    username: Optional[str] = Field(default=None, description="用户名")
    password: Optional[str] = Field(default=None, description="密码")
    extra_config: Optional[Dict[str, Any]] = Field(default=None, description="额外配置（JSON）")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class KVConfigUpdate(BaseModel):
    key: Optional[str] = Field(default=None, min_length=1, max_length=100, description="键")
    value: Optional[str] = Field(default=None, description="值")
    description: Optional[str] = Field(default=None, description="描述")
    is_encrypted: Optional[bool] = Field(default=None, description="是否加密存储")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


# ----------------------- 测试连接 Schema -----------------------

class TestConnectionByBody(BaseModel):
    mode: Literal["by_body"] = Field(default="by_body", description="按请求体测试")
    service_name: Literal["sonarr", "prowlarr", "tmdb"] = Field(description="服务名", examples=["sonarr"])
    url: Optional[str] = Field(default=None, description="服务URL，TMDB可省略", examples=["http://127.0.0.1:8989"])
    api_key: Optional[str] = Field(default=None, description="API Key（可选）")
    username: Optional[str] = Field(default=None, description="用户名（可选）")
    password: Optional[str] = Field(default=None, description="密码（可选）")
    proxy: Optional[Dict[str, str]] = Field(default=None, description="代理配置，如 {http, https}")


class TestConnectionById(BaseModel):
    mode: Literal["by_id"] = Field(default="by_id", description="按ID测试")
    id: int = Field(description="配置ID")


TestConnectionRequest = TestConnectionByBody | TestConnectionById


class ProxyTestRequest(BaseModel):
    url: Optional[str] = Field(default=None, description="测试目标URL，留空使用后端默认")
    proxy: Optional[Dict[str, str]] = Field(default=None, description="代理配置，如 {http, https}")
    timeout_ms: Optional[int] = Field(default=None, ge=1000, le=30000, description="超时时间（毫秒，1-30秒）")

