"""
Torznab API 端点
实现 Torznab 协议，供 Sonarr/Radarr 调用
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.db.database import get_db
from app.services.clients import make_client, ProwlarrClient
from app.services.orchestrator import (
    OrchestrationService,
    SearchQuery,
    OrchestrationConfig,
)
from app.db import crud_config
from app.utils.config_helpers import (
    decrypt_if_present,
    get_active_proxy_config,
    parse_extra_config,
)

router = APIRouter()


async def _load_prowlarr_runtime(db: AsyncSession):
    """
    加载 Prowlarr 运行时配置
    """
    items = await crud_config.get_service_configs(
        db, service_name="prowlarr", is_active=True
    )
    if not items:
        return None

    svc = items[0]
    url = getattr(svc, "url", "") or ""
    api_key = decrypt_if_present(getattr(svc, "api_key", None))
    timeout = getattr(svc, "timeout", None) or 120

    if not url or not api_key:
        return None

    proxies = None
    extra = parse_extra_config(getattr(svc, "extra_config", None)) or {}
    if isinstance(extra, dict) and extra.get("use_proxy"):
        proxies = await get_active_proxy_config(db)

    client = make_client(
        "prowlarr",
        url=url,
        api_key=api_key,
        proxies=proxies,
        timeout=timeout,
    )
    assert isinstance(client, ProwlarrClient)
    return client


async def get_prowlarr_client(
    db: AsyncSession = Depends(get_db),
) -> Optional[ProwlarrClient]:
    """
    作为依赖注入的 Prowlarr 客户端构造函数
    """
    return await _load_prowlarr_runtime(db)


async def _load_tmdb_runtime(db: AsyncSession):
    """
    加载 TMDB 运行时配置
    """
    from app.services.clients import TMDBClient

    items = await crud_config.get_service_configs(
        db, service_name="tmdb", is_active=True
    )
    if not items:
        return None

    svc = items[0]
    api_key = decrypt_if_present(getattr(svc, "api_key", None))
    timeout = getattr(svc, "timeout", None) or 30

    if not api_key:
        return None

    proxies = None
    extra = parse_extra_config(getattr(svc, "extra_config", None)) or {}
    if isinstance(extra, dict) and extra.get("use_proxy"):
        proxies = await get_active_proxy_config(db)

    # 获取可选配置
    default_language = getattr(svc, "default_language", None) or "zh-CN"
    default_region = getattr(svc, "default_region", None) or "CN"
    default_include_adult = getattr(svc, "default_include_adult", None)

    client = TMDBClient(
        api_key=api_key,
        proxies=proxies,
        timeout=timeout,
        default_language=default_language,
        default_region=default_region,
        default_include_adult=default_include_adult,
    )
    return client


async def get_tmdb_client(
    db: AsyncSession = Depends(get_db),
):
    """
    作为依赖注入的 TMDB 客户端构造函数
    """
    return await _load_tmdb_runtime(db)


@router.get("")
async def torznab_api(
    t: str = Query(..., description="Torznab 操作类型 (caps, search, tvsearch, movie)"),
    q: Optional[str] = Query(None, description="搜索关键词"),
    season: Optional[int] = Query(None, description="季号"),
    ep: Optional[int] = Query(None, description="集号"),
    tmdbid: Optional[int] = Query(None, description="TMDB ID"),
    tvdbid: Optional[int] = Query(None, description="TVDB ID"),
    rid: Optional[int] = Query(None, description="TVRage ID"),
    imdbid: Optional[str] = Query(None, description="IMDB ID"),
    offset: int = Query(0, description="偏移量"),
    limit: int = Query(100, description="限制数量"),
    db: AsyncSession = Depends(get_db),
    prowlarr_client: Optional[ProwlarrClient] = Depends(get_prowlarr_client),
    tmdb_client=Depends(get_tmdb_client),
):
    """
    Torznab API 入口，兼容 Sonarr/Radarr。

    实现四阶段编排流程：
    1. 请求接收与参数解析
    2. TMDB 增强搜索词（可选）
    3. 发起搜索与并行解析
    4. 格式化响应
    """
    # 如果没有配置 Prowlarr，返回错误
    if prowlarr_client is None and t in ["search", "tvsearch", "movie"]:
        return Response(
            content='<?xml version="1.0" encoding="utf-8"?><error code="100" description="Prowlarr not configured" />',
            media_type="application/xml",
        )

    # 构建搜索查询
    try:
        search_query = SearchQuery(
            t=t,
            q=q,
            season=season,
            ep=ep,
            tmdbid=tmdbid,
            tvdbid=tvdbid,
            rid=rid,
            imdbid=imdbid,
            limit=limit,
            offset=offset,
        )
    except ValidationError as exc:
        return Response(
            content=f'<?xml version="1.0" encoding="utf-8"?><error code="200" description="{str(exc)}" />',
            media_type="application/xml",
        )

    # 创建编排服务（传入 TMDB 客户端）
    orchestrator = OrchestrationService(
        db=db,
        prowlarr_client=prowlarr_client,
        config=OrchestrationConfig(),
        tmdb_client=tmdb_client,
    )

    # 执行搜索
    success, result = await orchestrator.search(search_query)

    if success:
        return Response(content=result, media_type="application/xml")
    else:
        # 返回错误 XML（HTTP 200，XML body 包含错误信息）
        return Response(content=result, media_type="application/xml")
