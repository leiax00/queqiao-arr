"""
配置管理端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Literal, Any, Dict

from app.db.database import get_db
from app.api.endpoints.auth import get_current_user
from app.db import crud_config
from app.models.config import ServiceConfig, Configuration
from app.utils import success_response, error_response
from app.utils.encryption import encryption_manager

from pydantic import BaseModel, Field

router = APIRouter()


class ServiceConfigOut(BaseModel):
    id: int = Field(description="配置ID")
    service_name: str = Field(description="服务名：sonarr|prowlarr|proxy")
    service_type: str = Field(description="服务类型：api|proxy")
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
    is_encrypted: bool = Field(description="是否加密存储")
    is_active: bool = Field(description="是否启用")
    created_at: Optional[str] = Field(default=None, description="创建时间 ISO8601")
    updated_at: Optional[str] = Field(default=None, description="更新时间 ISO8601")

    class Config:
        from_attributes = True


class ServiceConfigCreate(BaseModel):
    type: Literal["service"] = Field(description="配置类型固定为 service", examples=["service"])
    service_name: Literal["sonarr", "prowlarr", "proxy"] = Field(description="服务名", examples=["sonarr"])
    service_type: Literal["api", "proxy"] = Field(description="服务类型", examples=["api"])
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


class ServiceConfigUpdate(BaseModel):
    service_name: Optional[Literal["sonarr", "prowlarr", "proxy"]] = Field(default=None, description="服务名")
    service_type: Optional[Literal["api", "proxy"]] = Field(default=None, description="服务类型")
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


class TestConnectionByBody(BaseModel):
    mode: Literal["by_body"] = Field(default="by_body", description="按请求体测试")
    service_name: Literal["sonarr", "prowlarr"] = Field(description="服务名", examples=["sonarr"])
    url: str = Field(description="服务URL", examples=["http://127.0.0.1:8989"])
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


@router.get(
    "/",
    summary="获取配置概览",
    description="返回服务配置与KV配置的概要列表（敏感字段使用掩码，不回显明文）",
    responses={
        200: {
            "description": "成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "services": [
                                {
                                    "id": 1,
                                    "service_name": "sonarr",
                                    "service_type": "api",
                                    "name": "默认Sonarr",
                                    "url": "http://127.0.0.1:8989",
                                    "api_key_masked": "****9f2c",
                                    "is_active": True,
                                    "created_at": "2025-10-12T10:00:00Z",
                                    "updated_at": "2025-10-12T11:00:00Z"
                                }
                            ],
                            "kv": [
                                {
                                    "id": 11,
                                    "key": "default_language",
                                    "value": "zh-CN",
                                    "is_encrypted": False,
                                    "is_active": True,
                                    "created_at": "2025-10-12T10:00:00Z",
                                    "updated_at": "2025-10-12T11:00:00Z"
                                }
                            ]
                        }
                    }
                }
            }
        }
    },
)
async def get_configurations(
    service_name: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    services = await crud_config.get_service_configs(db, service_name=service_name, is_active=is_active)
    kvs = await crud_config.get_configurations(db, is_active=is_active)

    def mask_api_key(value: Optional[str]) -> Optional[str]:
        """返回长度保持一致的掩码：前后各4位可见，中间以*填充。
        对于长度<=8的短密钥，出于安全考虑全部以*遮蔽。
        """
        if not value:
            return None
        length = len(value)
        if length <= 8:
            return "*" * length
        prefix = value[:4]
        suffix = value[-4:]
        middle_len = length - 8
        return f"{prefix}{'*' * middle_len}{suffix}"

    import json
    services_out = []
    for s in services:
        extra: Optional[Dict[str, Any]] = None
        if getattr(s, "extra_config", None):
            try:
                extra = json.loads(s.extra_config)
            except Exception:
                extra = None
        services_out.append(
            ServiceConfigOut(
                id=s.id,
                service_name=s.service_name,
                service_type=s.service_type,
                name=s.name,
                url=s.url,
                api_key_masked=mask_api_key(encryption_manager.decrypt(s.api_key) if s.api_key else None),
                username=s.username,
                is_active=s.is_active,
                extra_config=extra,
                created_at=s.created_at.isoformat() if getattr(s, "created_at", None) else None,
                updated_at=s.updated_at.isoformat() if getattr(s, "updated_at", None) else None,
            )
        )
    kv_out = [
        KVConfigOut(
            id=c.id,
            key=c.key,
            value=c.value,
            is_encrypted=c.is_encrypted,
            is_active=c.is_active,
            created_at=c.created_at.isoformat() if getattr(c, "created_at", None) else None,
            updated_at=c.updated_at.isoformat() if getattr(c, "updated_at", None) else None,
        )
        for c in kvs
    ]

    return success_response({"services": [x.model_dump() for x in services_out], "kv": [x.model_dump() for x in kv_out]})


@router.post(
    "/",
    summary="创建配置",
    description="创建服务配置或KV配置。服务配置的API Key/密码会加密入库，响应仅返回ID。",
    responses={
        200: {
            "description": "创建成功",
            "content": {
                "application/json": {
                    "example": {"code": 200, "message": "OK", "data": {"id": 1}}
                }
            }
        },
        409: {
            "description": "重复（服务名+名称 或 KV键 冲突）",
            "content": {"application/json": {"example": {"detail": "同名配置已存在"}}}
        }
    },
)
async def create_configuration(
    payload: ServiceConfigCreate | KVConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if isinstance(payload, ServiceConfigCreate):
        dup = await crud_config.is_service_name_duplicate(db, service_name=payload.service_name, name=payload.name)
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="同名配置已存在")
        api_key_enc = encryption_manager.encrypt(payload.api_key) if payload.api_key else None
        password_enc = encryption_manager.encrypt(payload.password) if payload.password else None
        extra_json = None
        if payload.extra_config is not None:
            import json

            extra_json = json.dumps(payload.extra_config, ensure_ascii=False)
        item = await crud_config.create_service_config(
            db,
            service_name=payload.service_name,
            service_type=payload.service_type,
            name=payload.name,
            url=payload.url,
            api_key=api_key_enc,
            username=payload.username,
            password=password_enc,
            extra_config=extra_json,
            is_active=payload.is_active,
        )
        return success_response({"id": item.id})
    else:
        dup = await crud_config.is_kv_key_duplicate(db, key=payload.key)
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Key 已存在")
        value_enc = encryption_manager.encrypt(payload.value) if payload.is_encrypted and payload.value else payload.value
        item = await crud_config.create_configuration(
            db,
            key=payload.key,
            value=value_enc,
            description=payload.description,
            is_encrypted=payload.is_encrypted,
            is_active=payload.is_active,
        )
        return success_response({"id": item.id})


@router.put(
    "/{config_id}",
    summary="更新配置",
    description="按ID更新服务或KV配置。若更新敏感字段则重新加密入库，响应仅返回ID。",
    responses={
        200: {
            "description": "更新成功",
            "content": {"application/json": {"example": {"code": 200, "message": "OK", "data": {"id": 1}}}},
        },
        404: {"description": "配置不存在", "content": {"application/json": {"example": {"detail": "配置不存在"}}}},
        409: {"description": "重复冲突", "content": {"application/json": {"example": {"detail": "Key 已存在"}}}},
    },
)
async def update_configuration(
    config_id: int,
    payload: ServiceConfigUpdate | KVConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 尝试服务配置
    svc = await crud_config.get_service_config_by_id(db, config_id=config_id)
    if svc:
        update_data: Dict[str, Any] = {}
        if payload.name and payload.service_name:
            dup = await crud_config.is_service_name_duplicate(
                db, service_name=payload.service_name, name=payload.name, exclude_id=svc.id
            )
            if dup:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="同名配置已存在")
        for field in ["service_name", "service_type", "name", "url", "username", "is_active"]:
            value = getattr(payload, field, None)
            if value is not None:
                update_data[field] = value
        if payload.api_key is not None:
            update_data["api_key"] = encryption_manager.encrypt(payload.api_key) if payload.api_key else None
        if payload.password is not None:
            update_data["password"] = encryption_manager.encrypt(payload.password) if payload.password else None
        if payload.extra_config is not None:
            import json

            update_data["extra_config"] = json.dumps(payload.extra_config, ensure_ascii=False)
        svc = await crud_config.update_service_config(db, obj=svc, data=update_data)
        return success_response({"id": svc.id})

    # 尝试 KV 配置
    kv = await crud_config.get_configuration_by_id(db, config_id=config_id)
    if not kv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
    if payload.key:
        dup = await crud_config.is_kv_key_duplicate(db, key=payload.key, exclude_id=kv.id)
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Key 已存在")
    update_data = {}
    for field in ["key", "description", "is_active"]:
        value = getattr(payload, field, None)
        if value is not None:
            update_data[field] = value
    if getattr(payload, "is_encrypted", None) is not None:
        update_data["is_encrypted"] = payload.is_encrypted  # 切换加密标志本身不改变存量明文
    if getattr(payload, "value", None) is not None:
        if payload.value and (payload.is_encrypted if payload.is_encrypted is not None else kv.is_encrypted):
            update_data["value"] = encryption_manager.encrypt(payload.value)
        else:
            update_data["value"] = payload.value
    kv = await crud_config.update_configuration(db, obj=kv, data=update_data)
    return success_response({"id": kv.id})


@router.delete(
    "/{config_id}",
    summary="删除配置",
    description="按ID删除服务或KV配置。",
    responses={
        200: {"description": "删除成功", "content": {"application/json": {"example": {"code": 200, "message": "OK", "data": {"deleted": True}}}}},
        404: {"description": "配置不存在", "content": {"application/json": {"example": {"detail": "配置不存在"}}}},
    },
)
async def delete_configuration(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = await crud_config.get_service_config_by_id(db, config_id=config_id)
    if svc:
        await crud_config.delete_service_config(db, obj=svc)
        return success_response({"deleted": True})
    kv = await crud_config.get_configuration_by_id(db, config_id=config_id)
    if not kv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
    await crud_config.delete_configuration(db, obj=kv)
    return success_response({"deleted": True})


@router.post(
    "/test-connection",
    summary="测试服务连通性",
    description="测试 Sonarr/Prowlarr 的连通性，支持按请求体或按配置ID测试。",
    responses={
        200: {
            "description": "测试结果",
            "content": {
                "application/json": {
                    "example": {"code": 200, "message": "OK", "data": {"ok": True, "details": "HTTP 200"}}
                }
            }
        },
        400: {"description": "参数错误", "content": {"application/json": {"example": {"detail": "仅支持 sonarr/prowlarr 连通性测试"}}}},
        404: {"description": "配置不存在", "content": {"application/json": {"example": {"detail": "配置不存在"}}}},
    },
)
async def test_service_connection(
    payload: TestConnectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    import httpx
    import asyncio

    async def check_service(service_name: str, url: str, api_key: Optional[str], proxy: Optional[Dict[str, str]]):
        headers: Dict[str, str] = {}
        if api_key:
            headers["X-Api-Key"] = api_key
        base = url.rstrip("/")
        # Sonarr 使用 v3，Prowlarr 使用 v1
        path = "/api/v3/system/status" if service_name == "sonarr" else "/api/v1/system/status"
        test_url = base + path
        timeout = httpx.Timeout(5.0)
        try:
            async with httpx.AsyncClient(timeout=timeout, proxies=proxy) as client:
                resp = await client.get(test_url, headers=headers)
                return resp.status_code == 200, f"HTTP {resp.status_code}"
        except Exception as e:
            return False, str(e)

    # 准备参数
    service_name: Optional[str] = None
    url: Optional[str] = None
    raw_api_key: Optional[str] = None
    proxy: Optional[Dict[str, str]] = None

    def normalize_proxies(p: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if not p:
            return None
        normalized: Dict[str, str] = {}
        for k, v in p.items():
            key = k if "://" in k else f"{k}://"
            normalized[key] = v
        return normalized

    if isinstance(payload, TestConnectionByBody):
        service_name = payload.service_name
        url = payload.url
        raw_api_key = payload.api_key
        proxy = normalize_proxies(payload.proxy)
    else:
        svc = await crud_config.get_service_config_by_id(db, config_id=payload.id)
        if not svc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
        service_name = svc.service_name
        url = svc.url
        raw_api_key = encryption_manager.decrypt(svc.api_key) if svc.api_key else None

    if service_name not in {"sonarr", "prowlarr"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 sonarr/prowlarr 连通性测试")

    ok, note = await check_service(service_name, url, raw_api_key, proxy)
    return success_response({"ok": ok, "details": note})


@router.post(
    "/test-proxy",
    summary="测试代理连通性",
    description="通过代理访问指定或默认的测试URL，返回可达性与延迟信息",
)
async def test_proxy_connectivity(
    payload: ProxyTestRequest,
    current_user=Depends(get_current_user),
):
    import httpx
    import time

    target_url = payload.url or "https://www.google.com/generate_204"
    # 允许前端传入 1-30 秒范围的超时，默认 5 秒
    timeout_seconds = 5.0
    if payload.timeout_ms is not None:
        try:
            timeout_seconds = max(1.0, min(30.0, float(payload.timeout_ms) / 1000.0))
        except Exception:
            timeout_seconds = 5.0
    timeout = httpx.Timeout(timeout_seconds)
    start = time.perf_counter()
    try:
        proxies = None
        if payload.proxy:
            proxies = {}
            for k, v in payload.proxy.items():
                proxies[k if "://" in k else f"{k}://"] = v
        # 在新版 httpx（尤其是 0.27+）中，proxies 的 key/value 格式必须是完整的 URL形式，而不是以前那种简单写 "http" 或 "https" 的形式。
        # proxies = {
        #     "http://": "http://127.0.0.1:7890",
        #     "https://": "http://127.0.0.1:7890",
        # }
        async with httpx.AsyncClient(timeout=timeout, proxies=proxies) as client:
            resp = await client.get(target_url)
            latency_ms = int((time.perf_counter() - start) * 1000)
            return success_response({
                "ok": resp.status_code < 500,
                "latency_ms": latency_ms,
                "details": f"HTTP {resp.status_code}"
            })
    except Exception as e:
        return success_response({"ok": False, "details": str(e)})
