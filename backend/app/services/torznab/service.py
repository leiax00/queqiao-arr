import json
from datetime import datetime
from email.utils import formatdate
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud_system_dict
from .models import TorznabCaps, TorznabCategory, TorznabSearchMode, TorznabItem, TorznabResponse, TorznabAttr

if TYPE_CHECKING:
    from app.services.parser.models import ParsedTitle

async def get_torznab_caps(db: AsyncSession) -> TorznabCaps:
    """
    从系统字典加载 Torznab 能力集配置。
    """
    # 1. 加载基础设置
    settings_items = await crud_system_dict.get_dict_options(db, dict_type_code="torznab.settings")
    settings = {it.code: it.value for it in settings_items}
    
    # 2. 加载搜索模式
    mode_items = await crud_system_dict.get_dict_options(db, dict_type_code="torznab.search_modes")
    search_modes = []
    for it in mode_items:
        params = []
        if it.extra_data:
            try:
                data = json.loads(it.extra_data)
                # 某种情况下可能是逗号分隔的字符串
                if isinstance(data.get("supportedParams"), str):
                    params = data["supportedParams"].split(",")
                else:
                    params = data.get("supportedParams") or []
            except:
                pass
        search_modes.append(TorznabSearchMode(name=it.code, supportedParams=params))

    # 3. 加载分类
    cat_items = await crud_system_dict.get_dict_options(db, dict_type_code="torznab.categories")
    categories = []
    for it in cat_items:
        # TODO: 处理层级分类（从 parent_id 或 extra_data）
        categories.append(TorznabCategory(id=int(it.code), name=it.name))

    return TorznabCaps(
        server_title=settings.get("server_name", "Queqiao-arr"),
        max_items=int(settings.get("max_items", 100)),
        categories=categories,
        search_modes=search_modes
    )


def map_results_to_torznab_response(
    prowlarr_results: List[dict],
    parsed_results: List[Optional["ParsedTitle"]],
    offset: int = 0,
    total: int = 0,
) -> TorznabResponse:
    """
    将 Prowlarr 原始项与标题解析结果合并映射为 TorznabResponse。
    """
    items = []
    for raw, parsed in zip(prowlarr_results, parsed_results):
        item = _map_single_item(raw, parsed)
        if item:
            items.append(item)
            
    return TorznabResponse(
        offset=offset,
        total=total or len(items),
        items=items
    )


def _map_single_item(raw: dict, parsed: Optional["ParsedTitle"]) -> Optional[TorznabItem]:
    """
    单个条目的转换映射。
    """
    # 基础字段：优先使用 Prowlarr 提供的，或者补充 Parsed 数据
    title = raw.get("title", "")
    guid = raw.get("guid") or raw.get("infoUrl") or ""
    link = raw.get("downloadUrl") or raw.get("guid") or ""
    
    # 日期转换：Prowlarr 可能是 ISO，RSS 需要 RFC822
    pub_date = _parse_date(raw.get("publishDate", ""))
    
    size = int(raw.get("size") or 0)
    
    # 构造 Attribute 列表
    # ... (原有 attrs 逻辑)
    attrs = []
    
    # 质量信息（做种/下载数）
    if "seeders" in raw:
        attrs.append(TorznabAttr(name="seeders", value=str(raw["seeders"])))
    if "peers" in raw:
        attrs.append(TorznabAttr(name="peers", value=str(raw["peers"])))
    if raw.get("infoHash"):
        attrs.append(TorznabAttr(name="infohash", value=raw["infoHash"]))

    # 增强字段 (ParsedTitle)
    if parsed:
        if parsed.season is not None:
            attrs.append(TorznabAttr(name="season", value=str(parsed.season)))
        
        if parsed.episodes:
            for ep in parsed.episodes:
                attrs.append(TorznabAttr(name="episode", value=str(ep)))
        
        if parsed.tmdb_id:
            attrs.append(TorznabAttr(name="tmdbid", value=str(parsed.tmdb_id)))
            
        if parsed.resolution:
            attrs.append(TorznabAttr(name="resolution", value=parsed.resolution))
            
        if parsed.codec:
            attrs.append(TorznabAttr(name="video", value=parsed.codec))
        
        if parsed.audio:
            attrs.append(TorznabAttr(name="audio", value=parsed.audio))

    return TorznabItem(
        title=title,
        guid=guid,
        link=link,
        pubDate=pub_date,
        size=size,
        enclosure_url=link,
        enclosure_length=size,
        attributes=attrs
    )


def _parse_date(date_str: str) -> str:
    """
    将 ISO 格式日期转换为 RFC822 格式。
    """
    if not date_str:
        return formatdate(usegmt=True)
    try:
        # 处理 Z 结尾和毫秒
        clean_date = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_date)
        return formatdate(dt.timestamp(), usegmt=True)
    except Exception:
        return date_str
