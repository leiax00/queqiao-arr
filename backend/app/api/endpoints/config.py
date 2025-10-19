"""
配置管理端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import json

from app.db.database import get_db
from app.api.endpoints.auth import get_current_user
from app.db import crud_config
from app.utils import success_response, error_response
from app.utils.encryption import encryption_manager
from app.utils.config_helpers import (
    mask_api_key,
    parse_extra_config,
    encrypt_if_present,
    decrypt_if_present,
    get_active_proxy_config,
    normalize_proxy_dict,
)
from app.api.schemas.config import (
    ServiceConfigOut,
    KVConfigOut,
    ServiceConfigCreate,
    KVConfigCreate,
    ServiceConfigUpdate,
    KVConfigUpdate,
    TestConnectionByBody,
    TestConnectionById,
    TestConnectionRequest,
    ProxyTestRequest,
)

router = APIRouter()


# ----------------------- 配置概览 -----------------------

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

    # 构建服务配置输出
    services_out = []
    for s in services:
        extra = parse_extra_config(getattr(s, "extra_config", None))
        services_out.append(
            ServiceConfigOut(
                id=s.id,
                service_name=s.service_name,
                service_type=s.service_type,
                name=s.name,
                url=s.url,
                api_key_masked=mask_api_key(decrypt_if_present(s.api_key)),
                username=s.username,
                is_active=s.is_active,
                extra_config=extra,
                created_at=s.created_at.isoformat() if getattr(s, "created_at", None) else None,
                updated_at=s.updated_at.isoformat() if getattr(s, "updated_at", None) else None,
            )
        )
    
    # 构建 KV 配置输出
    kv_out = []
    for c in kvs:
        if c.is_encrypted:
            # 加密项：不返回密文，改为返回 has_value 并令 value 为空
            kv_out.append(
                KVConfigOut(
                    id=c.id,
                    key=c.key,
                    value=None,
                    has_value=bool(c.value),
                    is_encrypted=c.is_encrypted,
                    is_active=c.is_active,
                    created_at=c.created_at.isoformat() if getattr(c, "created_at", None) else None,
                    updated_at=c.updated_at.isoformat() if getattr(c, "updated_at", None) else None,
                )
            )
        else:
            # 明文项：按原样返回 value，has_value 为空
            kv_out.append(
                KVConfigOut(
                    id=c.id,
                    key=c.key,
                    value=c.value,
                    has_value=None,
                    is_encrypted=c.is_encrypted,
                    is_active=c.is_active,
                    created_at=c.created_at.isoformat() if getattr(c, "created_at", None) else None,
                    updated_at=c.updated_at.isoformat() if getattr(c, "updated_at", None) else None,
                )
            )

    return success_response({"services": [x.model_dump() for x in services_out], "kv": [x.model_dump() for x in kv_out]})


# ----------------------- 创建配置 -----------------------

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
        
        extra_json = json.dumps(payload.extra_config, ensure_ascii=False) if payload.extra_config else None
        
        item = await crud_config.create_service_config(
            db,
            service_name=payload.service_name,
            service_type=payload.service_type,
            name=payload.name,
            url=payload.url,
            api_key=encrypt_if_present(payload.api_key),
            username=payload.username,
            password=encrypt_if_present(payload.password),
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


# ----------------------- 更新配置 -----------------------

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
            update_data["api_key"] = encrypt_if_present(payload.api_key)
        if payload.password is not None:
            update_data["password"] = encrypt_if_present(payload.password)
        if payload.extra_config is not None:
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
        update_data["is_encrypted"] = payload.is_encrypted
    
    if getattr(payload, "value", None) is not None:
        if payload.value and (payload.is_encrypted if payload.is_encrypted is not None else kv.is_encrypted):
            update_data["value"] = encryption_manager.encrypt(payload.value)
        else:
            update_data["value"] = payload.value
    
    kv = await crud_config.update_configuration(db, obj=kv, data=update_data)
    return success_response({"id": kv.id})


# ----------------------- 删除配置 -----------------------

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


# ----------------------- 连接测试 -----------------------

@router.post(
    "/test-connection",
    summary="测试服务连通性",
    description="测试 Sonarr/Prowlarr/TMDB 的连通性，支持按请求体（by_body）或按配置ID（by_id）测试。",
    responses={
        200: {
            "description": "测试结果",
            "content": {
                "application/json": {
                    "example": {"code": 200, "message": "OK", "data": {"ok": True, "details": "HTTP 200", "latency_ms": 123}}
                }
            }
        },
        400: {"description": "参数错误", "content": {"application/json": {"example": {"detail": "仅支持 sonarr/prowlarr/tmdb 连通性测试"}}}},
        404: {"description": "配置不存在", "content": {"application/json": {"example": {"detail": "配置不存在"}}}},
    },
)
async def test_service_connection(
    payload: TestConnectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.clients import make_client

    # 准备参数
    service_name: Optional[str] = None
    url: Optional[str] = None
    raw_api_key: Optional[str] = None
    proxy: Optional[Dict[str, str]] = None

    if isinstance(payload, TestConnectionByBody):
        service_name = payload.service_name
        url = payload.url
        raw_api_key = payload.api_key
        proxy = normalize_proxy_dict(payload.proxy)
    else:
        svc = await crud_config.get_service_config_by_id(db, config_id=payload.id)
        if not svc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
        
        service_name = svc.service_name
        url = svc.url
        raw_api_key = decrypt_if_present(svc.api_key)
        
        # 解析 use_proxy 并注入"proxy 类型服务"作为代理
        extra = parse_extra_config(getattr(svc, "extra_config", None)) or {}
        if isinstance(extra, dict) and extra.get("use_proxy"):
            proxy = await get_active_proxy_config(db)

    if service_name not in {"sonarr", "prowlarr", "tmdb"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 sonarr/prowlarr/tmdb 连通性测试")

    # 使用客户端层进行连接测试
    try:
        client = make_client(
            service_name=service_name,
            url=url,
            api_key=raw_api_key,
            proxies=proxy,
            timeout=5
        )
        ok, note = client.check_status()
        return success_response({"ok": ok, "details": note})
    except ValueError as e:
        return error_response(message=str(e), code=400)


# ----------------------- TMDB 专用端点 -----------------------

# TMDB 配置已统一使用通用接口（GET / POST / PUT /{id}），此处仅保留特定于 TMDB 的选项接口

@router.get(
    "/tmdb/options",
    summary="TMDB 选项（语言/地区）",
    responses={
        200: {
            "description": "成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "languages": [
                                {"code": "zh-CN", "label": "中文（简体）"},
                                {"code": "zh-TW", "label": "中文（繁體）"},
                                {"code": "en-US", "label": "English (US)"}
                            ],
                            "regions": [
                                {"code": "CN", "label": "中国大陆"},
                                {"code": "HK", "label": "中国香港"},
                                {"code": "TW", "label": "中国台湾"},
                                {"code": "US", "label": "United States"}
                            ]
                        }
                    }
                }
            }
        }
    },
)
async def get_tmdb_options(
    current_user=Depends(get_current_user),
):
    data = {
        "languages": [
            {"code": "zh-CN", "label": "中文（简体）"},
            {"code": "zh-TW", "label": "中文（繁體）"},
            {"code": "en-US", "label": "English (US)"},
        ],
        "regions": [
            {"code": "CN", "label": "中国大陆"},
            {"code": "HK", "label": "中国香港"},
            {"code": "TW", "label": "中国台湾"},
            {"code": "US", "label": "United States"},
        ],
    }
    return success_response(data)


# ----------------------- 代理测试 -----------------------

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
        proxies = normalize_proxy_dict(payload.proxy)
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
