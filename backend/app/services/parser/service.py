"""
解析服务封装：将字典驱动配置加载与解析入口组合起来，便于上层模块直接调用。
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from .config_loader import load_parser_config
from .models import ParsedTitle
from .title_parser import parse_title


async def async_parse_title_with_db_config(
    db: AsyncSession,
    raw_title: str,
    *,
    tmdb_candidates: Optional[Sequence[Any]] = None,
    tmdb_alternative_titles: Optional[Sequence[Any]] = None,
    language_pref: Optional[List[str]] = None,
) -> Tuple[bool, ParsedTitle | str]:
    """
    组合入口：从系统字典加载解析器配置，然后执行标题解析。
    """
    config = await load_parser_config(db)
    return parse_title(
        raw_title=raw_title,
        tmdb_candidates=tmdb_candidates,
        tmdb_alternative_titles=tmdb_alternative_titles,
        language_pref=language_pref,
        config=config,
    )
