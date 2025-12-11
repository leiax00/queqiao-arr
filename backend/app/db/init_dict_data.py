"""
初始化系统字典数据
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud_system_dict
import json


async def _ensure_dict_type_with_items(
    db: AsyncSession,
    *,
    code: str,
    name: str,
    remark: str,
    items: list[dict],
) -> None:
    """
    确保字典类型和项存在（若缺失则补充），用于增量初始化。
    """
    existing_type = await crud_system_dict.get_dict_type_by_code(db, code=code)
    if not existing_type:
        await crud_system_dict.create_dict_type(
            db,
            code=code,
            name=name,
            remark=remark,
            is_active=True,
        )
    existing_items, _ = await crud_system_dict.get_dict_items(
        db,
        dict_type_code=code,
        page=1,
        page_size=500,
    )
    existing_codes = {it.code for it in existing_items}
    for item in items:
        if item["code"] in existing_codes:
            continue
        await crud_system_dict.create_dict_item(
            db,
            dict_type_code=code,
            **item,
            is_active=True,
        )


async def init_dict_data(db: AsyncSession) -> None:
    """
    初始化系统字典数据
    
    Args:
        db: 数据库会话
    """
    # 检查是否已有数据
    existing_types, _ = await crud_system_dict.get_dict_types(db, page=1, page_size=1)
    if existing_types:
        print("⏭️  字典数据已存在，跳过基础语言/地区初始化，补充解析相关字典")
        await init_parser_dict_data(db)
        return
    
    print("📝 开始初始化字典数据...")
    
    # 1. 创建语言字典类型
    language_type = await crud_system_dict.create_dict_type(
        db,
        code="language",
        name="语言选项",
        remark="系统支持的语言列表，用于TMDB API查询、前端界面显示等场景",
        is_active=True,
    )
    
    # 添加语言选项
    languages = [
        {"code": "zh-CN", "name": "简体中文", "value": "zh-CN", "sort_order": 1, 
         "remark": "中国大陆使用的简体中文，TMDB语言代码", 
         "extra_data": json.dumps({"icon": "🇨🇳"})},
        {"code": "zh-TW", "name": "繁體中文", "value": "zh-TW", "sort_order": 2,
         "remark": "台湾地区使用的繁体中文",
         "extra_data": json.dumps({"icon": "🇹🇼"})},
        {"code": "en-US", "name": "English (US)", "value": "en-US", "sort_order": 3,
         "remark": "美式英语，用于英文资源标题匹配",
         "extra_data": json.dumps({"icon": "🇺🇸"})},
        {"code": "ja-JP", "name": "日本語", "value": "ja-JP", "sort_order": 4,
         "remark": "日本语言选项，用于日语内容匹配",
         "extra_data": json.dumps({"icon": "🇯🇵"})},
        {"code": "ko-KR", "name": "한국어", "value": "ko-KR", "sort_order": 5,
         "remark": "韩语选项",
         "extra_data": json.dumps({"icon": "🇰🇷"})},
    ]
    
    for lang in languages:
        await crud_system_dict.create_dict_item(
            db,
            dict_type_code="language",
            **lang,
            is_active=True,
        )
    
    print(f"  ✓ 创建语言字典类型及 {len(languages)} 个选项")
    
    # 2. 创建地区字典类型
    region_type = await crud_system_dict.create_dict_type(
        db,
        code="region",
        name="地区选项",
        remark="内容地区分类，用于TMDB地区筛选，影响搜索结果和内容推荐",
        is_active=True,
    )
    
    # 添加地区选项
    regions = [
        {"code": "CN", "name": "中国大陆", "value": "CN", "sort_order": 1,
         "remark": "中国大陆地区",
         "extra_data": json.dumps({"icon": "🇨🇳"})},
        {"code": "TW", "name": "台湾", "value": "TW", "sort_order": 2,
         "remark": "台湾地区",
         "extra_data": json.dumps({"icon": "🇹🇼"})},
        {"code": "HK", "name": "香港", "value": "HK", "sort_order": 3,
         "remark": "香港特别行政区",
         "extra_data": json.dumps({"icon": "🇭🇰"})},
        {"code": "US", "name": "美国", "value": "US", "sort_order": 4,
         "remark": "美国地区",
         "extra_data": json.dumps({"icon": "🇺🇸"})},
        {"code": "JP", "name": "日本", "value": "JP", "sort_order": 5,
         "remark": "日本地区",
         "extra_data": json.dumps({"icon": "🇯🇵"})},
        {"code": "KR", "name": "韩国", "value": "KR", "sort_order": 6,
         "remark": "韩国地区",
         "extra_data": json.dumps({"icon": "🇰🇷"})},
    ]
    
    for region in regions:
        await crud_system_dict.create_dict_item(
            db,
            dict_type_code="region",
            **region,
            is_active=True,
        )
    
    print(f"  ✓ 创建地区字典类型及 {len(regions)} 个选项")

    # 初始化解析器相关字典
    await init_parser_dict_data(db)


async def init_parser_dict_data(db: AsyncSession) -> None:
    """
    初始化/补充标题解析相关的字典类型与内置枚举。
    """
    await _ensure_dict_type_with_items(
        db,
        code="title_parser.resolution",
        name="标题解析-分辨率",
        remark="解析器分辨率映射（内置与用户可扩展）",
        items=[
            {"code": "2160P", "name": "2160p", "value": "2160p", "sort_order": 1, "remark": "内置", "extra_data": json.dumps({"aliases": ["4K"], "kind": "builtin"})},
            {"code": "1080P", "name": "1080p", "value": "1080p", "sort_order": 2, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "720P", "name": "720p", "value": "720p", "sort_order": 3, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "480P", "name": "480p", "value": "480p", "sort_order": 4, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
        ],
    )

    await _ensure_dict_type_with_items(
        db,
        code="title_parser.source",
        name="标题解析-来源",
        remark="解析器片源映射（内置与用户可扩展）",
        items=[
            {"code": "WEB-DL", "name": "WEB-DL", "value": "WEB-DL", "sort_order": 1, "remark": "内置", "extra_data": json.dumps({"aliases": ["WEBDL", "WEB"], "kind": "builtin"})},
            {"code": "WEBRIP", "name": "WEBRip", "value": "WEBRip", "sort_order": 2, "remark": "内置", "extra_data": json.dumps({"aliases": ["WEB-RIP"], "kind": "builtin"})},
            {"code": "BLURAY", "name": "BluRay", "value": "BluRay", "sort_order": 3, "remark": "内置", "extra_data": json.dumps({"aliases": ["BDRIP", "BDRip"], "kind": "builtin"})},
            {"code": "HDTV", "name": "HDTV", "value": "HDTV", "sort_order": 4, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "DVDRIP", "name": "DVDRip", "value": "DVDRip", "sort_order": 5, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "B-GLOBAL", "name": "B-Global", "value": "WEB-DL", "sort_order": 6, "remark": "内置（B 站国际）", "extra_data": json.dumps({"aliases": ["B-Global", "B-GLOBAL"], "kind": "builtin"})},
        ],
    )

    await _ensure_dict_type_with_items(
        db,
        code="title_parser.hdr",
        name="标题解析-HDR",
        remark="解析器 HDR 映射（内置与用户可扩展）",
        items=[
            {"code": "HDR10+", "name": "HDR10+", "value": "HDR10+", "sort_order": 1, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "HDR10", "name": "HDR10", "value": "HDR10", "sort_order": 2, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "HDR", "name": "HDR", "value": "HDR", "sort_order": 3, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "DOLBYVISION", "name": "DolbyVision", "value": "DolbyVision", "sort_order": 4, "remark": "内置", "extra_data": json.dumps({"aliases": ["DOVI", "DV", "Dolby.Vision"], "kind": "builtin"})},
        ],
    )

    await _ensure_dict_type_with_items(
        db,
        code="title_parser.codec",
        name="标题解析-编码",
        remark="解析器编码映射（内置与用户可扩展）",
        items=[
            {"code": "HEVC", "name": "HEVC", "value": "HEVC", "sort_order": 1, "remark": "内置", "extra_data": json.dumps({"aliases": ["H265", "X265", "H.265"], "kind": "builtin"})},
            {"code": "H264", "name": "H264", "value": "H264", "sort_order": 2, "remark": "内置", "extra_data": json.dumps({"aliases": ["X264", "H.264"], "kind": "builtin"})},
            {"code": "AV1", "name": "AV1", "value": "AV1", "sort_order": 3, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
        ],
    )

    await _ensure_dict_type_with_items(
        db,
        code="title_parser.audio",
        name="标题解析-音轨",
        remark="解析器音轨映射（内置与用户可扩展）",
        items=[
            {"code": "AAC", "name": "AAC", "value": "AAC", "sort_order": 1, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "AC3", "name": "AC3", "value": "AC3", "sort_order": 2, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "EAC3", "name": "EAC3", "value": "EAC3", "sort_order": 3, "remark": "内置", "extra_data": json.dumps({"aliases": ["DDP"], "kind": "builtin"})},
            {"code": "FLAC", "name": "FLAC", "value": "FLAC", "sort_order": 4, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "DTS-HD", "name": "DTS-HD", "value": "DTS-HD", "sort_order": 5, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "DTS", "name": "DTS", "value": "DTS", "sort_order": 6, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
            {"code": "TRUEHD", "name": "TrueHD", "value": "TrueHD", "sort_order": 7, "remark": "内置", "extra_data": json.dumps({"aliases": [], "kind": "builtin"})},
        ],
    )

    await _ensure_dict_type_with_items(
        db,
        code="title_parser.subtitle",
        name="标题解析-字幕",
        remark="解析器字幕语言映射（内置与用户可扩展）",
        items=[
            {"code": "CHS", "name": "简体", "value": "chs", "sort_order": 1, "remark": "内置", "extra_data": json.dumps({"aliases": ["简体", "GB", "CHS"], "kind": "builtin"})},
            {"code": "CHT", "name": "繁体", "value": "cht", "sort_order": 2, "remark": "内置", "extra_data": json.dumps({"aliases": ["繁体", "繁體", "BIG5", "CHT"], "kind": "builtin"})},
            {"code": "CHS&CHT", "name": "简繁", "value": "chs&cht", "sort_order": 3, "remark": "内置", "extra_data": json.dumps({"aliases": ["简繁", "简繁内封", "简繁內封", "CHS&CHT"], "kind": "builtin"})},
        ],
    )

    await _ensure_dict_type_with_items(
        db,
        code="title_parser.tag",
        name="标题解析-标签",
        remark="解析器标签映射（内置与用户可扩展）",
        items=[
            {"code": "GLOBAL", "name": "B-Global", "value": "B-Global", "sort_order": 1, "remark": "内置", "extra_data": json.dumps({"aliases": ["B-GLOBAL", "B-Global"], "kind": "builtin"})},
            {"code": "DUAL_AUDIO", "name": "国粤双语", "value": "国粤双语", "sort_order": 2, "remark": "内置", "extra_data": json.dumps({"aliases": ["双语", "雙語"], "kind": "builtin"})},
            {"code": "COLLECTION", "name": "合集", "value": "合集", "sort_order": 3, "remark": "内置", "extra_data": json.dumps({"aliases": ["合集", "Collection", "Complete"], "kind": "builtin"})},
            {"code": "NC", "name": "NC", "value": "NC", "sort_order": 4, "remark": "内置", "extra_data": json.dumps({"aliases": ["NCOP", "NCED", "NC-OP", "NC-ED"], "kind": "builtin"})},
        ],
    )

    await _ensure_dict_type_with_items(
        db,
        code="title_parser.rule",
        name="标题解析-规则",
        remark="解析器正则规则（内置与用户可扩展）",
        items=[
            {"code": "is_finale", "name": "完结标记", "value": "true", "sort_order": 1, "remark": "内置规则：END/完结/全集", "extra_data": json.dumps({"pattern": r"\bEND\b|完结|全集|完結", "priority": 10, "kind": "builtin"})},
            {"code": "special_type", "name": "OVA/SP 标记", "value": "OVA", "sort_order": 2, "remark": "内置规则：OVA/SP", "extra_data": json.dumps({"pattern": r"\b(OVA|SP)\b", "priority": 20, "kind": "builtin"})},
        ],
    )
    
    # 3. 创建质量标签字典类型
    quality_type = await crud_system_dict.create_dict_type(
        db,
        code="quality",
        name="质量标签",
        remark="视频质量分类，用于资源标题解析和质量筛选，优先级：8K > 4K > 1080p > 720p > 480p",
        is_active=True,
    )
    
    # 添加质量标签选项
    qualities = [
        {"code": "8K", "name": "8K超高清", "value": "8K", "sort_order": 1,
         "remark": "7680×4320分辨率",
         "extra_data": json.dumps({"priority": 10, "resolution": "7680x4320"})},
        {"code": "4K", "name": "4K超高清", "value": "4K", "sort_order": 2,
         "remark": "3840×2160分辨率（UHD）",
         "extra_data": json.dumps({"priority": 9, "resolution": "3840x2160"})},
        {"code": "1080p", "name": "1080p全高清", "value": "1080p", "sort_order": 3,
         "remark": "1920×1080分辨率（FHD）",
         "extra_data": json.dumps({"priority": 8, "resolution": "1920x1080"})},
        {"code": "720p", "name": "720p高清", "value": "720p", "sort_order": 4,
         "remark": "1280×720分辨率（HD）",
         "extra_data": json.dumps({"priority": 7, "resolution": "1280x720"})},
        {"code": "480p", "name": "480p标清", "value": "480p", "sort_order": 5,
         "remark": "720×480分辨率（SD）",
         "extra_data": json.dumps({"priority": 6, "resolution": "720x480"})},
    ]
    
    for quality in qualities:
        await crud_system_dict.create_dict_item(
            db,
            dict_type_code="quality",
            **quality,
            is_active=True,
        )
    
    print(f"  ✓ 创建质量标签字典类型及 {len(qualities)} 个选项")
    
    print("✅ 字典数据初始化完成！")
