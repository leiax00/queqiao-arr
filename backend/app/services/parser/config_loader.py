"""
从系统字典加载标题解析器配置（映射/规则）。
"""

from __future__ import annotations

import json
from typing import Dict, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud_system_dict

from .models import ParseRule, ParserConfig

# 约定的字典类型编码
DICT_TYPE_RESOLUTION = "title_parser.resolution"
DICT_TYPE_SOURCE = "title_parser.source"
DICT_TYPE_HDR = "title_parser.hdr"
DICT_TYPE_CODEC = "title_parser.codec"
DICT_TYPE_AUDIO = "title_parser.audio"
DICT_TYPE_SUBTITLE = "title_parser.subtitle"
DICT_TYPE_TAG = "title_parser.tag"
DICT_TYPE_RULE = "title_parser.rule"


async def _load_map(
    db: AsyncSession,
    dict_type_code: str,
) -> Dict[str, str]:
    """
    将字典项转为 token->标准值 的映射。

    约定：
    - DictItem.value: 标准化的输出值（例如 1080p / WEB-DL / HDR10）。
    - DictItem.code/name: 作为可匹配的 token 之一。
    - DictItem.extra_data: JSON，可包含 aliases: list[str] 作为更多匹配 token。
    """
    items = await crud_system_dict.get_dict_options(db, dict_type_code=dict_type_code)
    mapping: Dict[str, str] = {}
    for it in items:
        normalized = (it.value or "").strip()
        if not normalized:
            continue
        for token in {it.code, it.name, it.value}:
            if token:
                mapping[token.upper()] = normalized
        if it.extra_data:
            try:
                data = json.loads(it.extra_data)
                aliases = data.get("aliases") if isinstance(data, dict) else None
                if isinstance(aliases, list):
                    for alias in aliases:
                        if isinstance(alias, str) and alias.strip():
                            mapping[alias.strip().upper()] = normalized
            except Exception:
                continue
    return mapping


async def _load_rules(db: AsyncSession) -> List[ParseRule]:
    """
    从字典项加载正则规则。

    约定：
    - code: 目标字段名，如 resolution/source/hdr/codec/audio/subtitle_lang/tag/release_group/version/special_type
    - value: 命中后写入的值（tag/subtitle_lang 等追加）
    - remark: 备注
    - extra_data: JSON，可包含 pattern（必填）、priority（int）、enabled（bool）
    """
    items = await crud_system_dict.get_dict_options(db, dict_type_code=DICT_TYPE_RULE)
    rules: List[ParseRule] = []
    for it in items:
        pattern = None
        priority = 100
        enabled = True
        if it.extra_data:
            try:
                data = json.loads(it.extra_data)
                pattern = data.get("pattern")
                priority = int(data.get("priority") or 100)
                enabled = bool(data.get("enabled")) if "enabled" in data else True
            except Exception:
                pattern = None
        if not pattern:
            continue
        rules.append(
            ParseRule(
                pattern=pattern,
                target_field=it.code,
                value=it.value or "",
                priority=priority,
                enabled=enabled,
                note=it.remark,
            )
        )
    # priority 小的优先
    rules.sort(key=lambda r: r.priority)
    return rules


async def load_parser_config(db: AsyncSession) -> ParserConfig:
    """
    统一入口：从系统字典加载解析映射与规则。
    """
    resolution_map, source_map, hdr_map, codec_map, audio_map, subtitle_map, tags_map = await _gather_maps(db)
    rules = await _load_rules(db)
    return ParserConfig(
        resolution_map=resolution_map,
        source_map=source_map,
        hdr_map=hdr_map,
        codec_map=codec_map,
        audio_map=audio_map,
        subtitle_map=subtitle_map,
        tag_map=tags_map,
        regex_rules=rules,
    )


async def _gather_maps(db: AsyncSession) -> Tuple[Dict[str, str], ...]:
    return (
        await _load_map(db, DICT_TYPE_RESOLUTION),
        await _load_map(db, DICT_TYPE_SOURCE),
        await _load_map(db, DICT_TYPE_HDR),
        await _load_map(db, DICT_TYPE_CODEC),
        await _load_map(db, DICT_TYPE_AUDIO),
        await _load_map(db, DICT_TYPE_SUBTITLE),
        await _load_map(db, DICT_TYPE_TAG),
    )
