"""
Prowlarr 搜索端点
"""

from typing import Any, Dict, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.api.schemas import ProwlarrSearchQuery, ProwlarrSearchResponse, parse_search_query
from app.db import crud_config
from app.db.database import get_db
from app.services.clients import ProwlarrClient, make_client
from app.utils import success_response, error_response
from app.utils.config_helpers import (
    parse_extra_config,
    decrypt_if_present,
    get_active_proxy_config,
)

router = APIRouter()


async def _load_prowlarr_runtime(db: AsyncSession) -> tuple[str, str, int, Optional[Dict[str, str]]]:
    """
    加载 Prowlarr 运行时参数：url、api_key、timeout、proxies
    """
    items = await crud_config.get_service_configs(db, service_name="prowlarr", is_active=True)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到启用中的 Prowlarr 配置")
    svc = items[0]
    url = getattr(svc, "url", "") or ""
    api_key = decrypt_if_present(getattr(svc, "api_key", None))
    timeout = getattr(svc, "timeout", None) or 120  # 默认 120 秒，适应远程 Prowlarr 搜索

    if not url or not api_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prowlarr 配置缺少 url 或 api_key")

    proxies = None
    extra = parse_extra_config(getattr(svc, "extra_config", None)) or {}
    if isinstance(extra, dict) and extra.get("use_proxy"):
        proxies = await get_active_proxy_config(db)

    return url, api_key, timeout, proxies


async def get_prowlarr_client(db: AsyncSession = Depends(get_db)) -> ProwlarrClient:
    """
    作为依赖注入的 Prowlarr 客户端构造函数
    """
    url, api_key, timeout, proxies = await _load_prowlarr_runtime(db)
    client = make_client(
        "prowlarr",
        url=url,
        api_key=api_key,
        proxies=proxies,
        timeout=timeout,
    )
    assert isinstance(client, ProwlarrClient)
    return client


@router.get(
    "/search",
    summary="Prowlarr 搜索",
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "results": [
                                {
                                    "title": "Example",
                                    "indexerId": 1,
                                    "size": 12345,
                                    "guid": "magnet:...",
                                    "magnetUrl": "https://...",
                                    "fileName": "xxxx",
                                }
                            ]
                        },
                    }
                }
            },
        },
        400: {"description": "参数错误", "content": {"application/json": {"example": {"code": 400, "message": "参数错误: query 不能为空", "data": None}}}},
        401: {"description": "未认证", "content": {"application/json": {"example": {"detail": "Not authenticated"}}}},
        404: {"description": "Prowlarr 配置缺失", "content": {"application/json": {"example": {"detail": "未找到启用中的 Prowlarr 配置"}}}},
        502: {"description": "上游 Prowlarr 返回错误或网络异常", "content": {"application/json": {"example": {"code": 502, "message": "Prowlarr 搜索失败: HTTP 错误 503: http://...", "data": None}}}},
    },
)
async def prowlarr_search(
    params: Annotated[ProwlarrSearchQuery, Depends(parse_search_query)],
    client: ProwlarrClient = Depends(get_prowlarr_client),
    current_user=Depends(get_current_user),
):
    ok, data = await client.search_async(**params.model_dump())
    if not ok:
        return error_response(message=str(data), code=502)
    results = data if isinstance(data, list) else []
    return success_response(ProwlarrSearchResponse(results=results))
