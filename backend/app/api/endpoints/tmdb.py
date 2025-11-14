"""
TMDB 查询端点
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.db.database import get_db
from app.db import crud_config
from app.services.clients import TMDBClient
from app.utils import success_response, error_response
from app.utils.config_helpers import (
    parse_extra_config,
    decrypt_if_present,
    get_active_proxy_config,
)
from app.api.schemas import (
    TMDBSearchQuery,
    TMDBSearchResponse,
    TMDBAlternativeTitlesResponse,
    TMDBDetailsResponse,
)

router = APIRouter()


async def _load_tmdb_runtime(db: AsyncSession) -> tuple[str, Optional[Dict[str, str]], Dict[str, Any]]:
    """
    加载 TMDB 的运行时参数：api_key、proxies、extra
    优先选择启用中的 `service_name=tmdb` 配置；若存在多条取第一条。
    """
    items = await crud_config.get_service_configs(db, service_name="tmdb", is_active=True)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到启用中的 TMDB 配置")
    svc = items[0]
    api_key = decrypt_if_present(svc.api_key)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TMDB 配置缺少有效 api_key")
    extra = parse_extra_config(getattr(svc, "extra_config", None)) or {}
    proxies = None
    if isinstance(extra, dict) and extra.get("use_proxy"):
        proxies = await get_active_proxy_config(db)
    return api_key, proxies, extra


@router.get(
    "/search",
    summary="搜索剧集（TMDB）",
)
async def tmdb_search(
    params: TMDBSearchQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.clients import make_client

    api_key, proxies, extra = await _load_tmdb_runtime(db)
    client = make_client("tmdb", api_key=api_key, proxies=proxies, timeout=10)
    assert isinstance(client, TMDBClient)
    params_dict = params.model_dump() if hasattr(params, "model_dump") else params.dict()
    ok, data = client.search_tv(**params_dict)
    if not ok:
        return error_response(message=str(data), code=502)
    # 透传 TMDB 的分页/结果基本字段
    data_dict = data if isinstance(data, dict) else {}
    page_out = int(data_dict.get("page", params.page))
    total_pages = int(data_dict.get("total_pages", 1))
    results = data_dict.get("results", []) or []
    response_data = TMDBSearchResponse(
        page=page_out,
        total_pages=total_pages,
        results=results,
    )
    return success_response(response_data)


@router.get(
    "/tv/{tv_id}",
    summary="获取剧集详情（TMDB）",
)
async def tmdb_tv_details(
    tv_id: int,
    language: str = Query(default="zh-CN"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.clients import make_client

    api_key, proxies, extra = await _load_tmdb_runtime(db)
    client = make_client("tmdb", api_key=api_key, proxies=proxies, timeout=10)
    ok, data = client.get_tv_details(tv_id=tv_id, language=language)
    if not ok:
        return error_response(message=str(data), code=502)
    return success_response(data)


@router.get(
    "/tv/{tv_id}/alternative_titles",
    summary="获取剧集替代标题（TMDB）",
)
async def tmdb_alternative_titles(
    tv_id: int,
    country: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.clients import make_client

    api_key, proxies, extra = await _load_tmdb_runtime(db)
    client = make_client("tmdb", api_key=api_key, proxies=proxies, timeout=10)
    ok, data = client.get_alternative_titles(tv_id=tv_id, country=country)
    if not ok:
        return error_response(message=str(data), code=502)
    # 透传并轻量规整字段名
    titles = []
    if isinstance(data, dict):
        for t in data.get("titles", []) or []:
            title = t.get("title")
            country_code = t.get("iso_3166_1")
            if title:
                titles.append({"title": title, "country": country_code})
    response_data = TMDBAlternativeTitlesResponse(tv_id=tv_id, titles=titles)
    return success_response(response_data)

