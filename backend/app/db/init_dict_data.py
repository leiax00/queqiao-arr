"""
初始化系统字典数据
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud_system_dict
import json


async def init_dict_data(db: AsyncSession) -> None:
    """
    初始化系统字典数据
    
    Args:
        db: 数据库会话
    """
    # 检查是否已有数据
    existing_types, _ = await crud_system_dict.get_dict_types(db, page=1, page_size=1)
    if existing_types:
        print("⏭️  字典数据已存在，跳过初始化")
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

