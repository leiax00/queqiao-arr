import pytest
from unittest.mock import AsyncMock, patch, Mock
from app.services.torznab.service import get_torznab_caps, map_results_to_torznab_response
from app.services.parser.models import ParsedTitle

@pytest.mark.asyncio
async def test_get_torznab_caps():
    # 模拟数据库查询结果
    m1 = Mock(); m1.code = "server_name"; m1.value = "Custom Indexer"; m1.extra_data = "{}"
    m2 = Mock(); m2.code = "max_items"; m2.value = "50"; m2.extra_data = "{}"
    mock_settings = [m1, m2]
    
    m3 = Mock(); m3.code = "tvsearch"; m3.extra_data = '{"supportedParams": "q,season,ep"}'
    mock_modes = [m3]
    
    m4 = Mock(); m4.code = "5070"; m4.name = "Anime"; m4.extra_data = "{}"
    mock_cats = [m4]
    
    with patch("app.db.crud_system_dict.get_dict_options") as mock_get_options:
        mock_get_options.side_effect = [mock_settings, mock_modes, mock_cats]
        
        db = AsyncMock()
        caps = await get_torznab_caps(db)
        
        assert caps.server_title == "Custom Indexer"
        assert caps.max_items == 50
        assert len(caps.search_modes) == 1
        assert caps.search_modes[0].name == "tvsearch"
        assert "season" in caps.search_modes[0].supported_params

def test_map_results_to_torznab_response():
    raw_results = [
        {
            "title": "Raw Title S01E01",
            "size": 1000,
            "guid": "guid1",
            "publishDate": "2024-01-24T10:00:00Z",
            "seeders": 10
        }
    ]
    parsed_results = [
        ParsedTitle(
            raw_title="Raw Title S01E01",
            normalized_title="Normalized Title",
            season=1,
            episodes=[1],
            tmdb_id=123,
            resolution="1080p"
        )
    ]
    
    response = map_results_to_torznab_response(raw_results, parsed_results)
    
    assert len(response.items) == 1
    item = response.items[0]
    assert item.title == "Raw Title S01E01"
    
    # 验证属性映射
    attr_names = [a.name for a in item.attributes]
    assert "season" in attr_names
    assert "episode" in attr_names
    assert "tmdbid" in attr_names
    
    # 验证值
    season_attr = next(a for a in item.attributes if a.name == "season")
    assert season_attr.value == "1"
    
    # 验证日期格式 (RFC822)
    assert "GMT" in item.pub_date or "UT" in item.pub_date
