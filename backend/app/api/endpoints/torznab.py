from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services.torznab.service import get_torznab_caps, map_results_to_torznab_response
from app.services.torznab.xml_builder import build_caps_xml, build_search_rss_xml

router = APIRouter()

@router.get("")
async def torznab_api(
    t: str = Query(..., description="Torznab 操作类型 (caps, search, tvsearch, movie)"),
    q: Optional[str] = Query(None, description="搜索关键词"),
    season: Optional[int] = Query(None, description="季号"),
    ep: Optional[int] = Query(None, description="集号"),
    offset: int = Query(0, description="偏移量"),
    limit: int = Query(100, description="限制数量"),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Torznab API 入口，兼容 Sonarr/Radarr。
    """
    if t == "caps":
        caps = await get_torznab_caps(db)
        xml_content = build_caps_xml(caps)
        return Response(content=xml_content, media_type="application/xml")
    
    if t in ["search", "tvsearch", "movie"]:
        # TODO: 这里需要对接 B-08 的编排逻辑
        # 暂时返回一个空的 RSS 响应作为占位符
        caps = await get_torznab_caps(db)
        # 构造空响应
        from app.services.torznab.models import TorznabResponse
        empty_resp = TorznabResponse(offset=offset, total=0, items=[])
        xml_content = build_search_rss_xml(caps, empty_resp)
        return Response(content=xml_content, media_type="application/xml")

    return Response(
        content="<error code='100' description='Invalid parameter' />", 
        status_code=400, 
        media_type="application/xml"
    )
