import pytest

from app.services.parser import async_parse_title, parse_title


def test_parse_single_episode_with_quality():
    raw = "[桜都字幕组&LoliHouse] 斗破苍穹 年番 - 118 [WebRip 1080p HEVC-10bit AAC][简繁内封]"
    ok, parsed = parse_title(raw)
    assert ok, parsed
    assert parsed.release_group == "桜都字幕组&LoliHouse"
    assert parsed.episodes == [118]
    assert parsed.resolution == "1080p"
    assert parsed.source == "WEBRip"
    assert parsed.codec == "HEVC"
    assert parsed.audio == "AAC"
    assert set(parsed.subtitle_lang) == {"chs", "cht"}
    assert parsed.confidence > 0.5


def test_parse_chinese_season_and_episode():
    raw = "[喵萌奶茶屋&LoliHouse] 凡人修仙传 S03 - 24 [WebRip 1080p HEVC AAC][简体]"
    ok, parsed = parse_title(raw)
    assert ok, parsed
    assert parsed.season == 3
    assert parsed.episodes == [24]
    assert parsed.source == "WEBRip"
    assert parsed.subtitle_lang == ["chs"]


def test_parse_finale_and_release_group_suffix():
    raw = "【1080p】镇魂街.第三季.EP10.END.Web-DL.H264.AAC-YSJ"
    ok, parsed = parse_title(raw)
    assert ok, parsed
    assert parsed.season == 3
    assert parsed.episodes == [10]
    assert parsed.is_finale is True
    assert parsed.release_group == "YSJ"
    assert parsed.source == "WEB-DL"
    assert parsed.codec == "H264"


def test_parse_alias_matching_with_tmdb():
    raw = "[Lilith-Raws] 伍六七之暗影宿命 / Scissor Seven S04 - 07 [B-Global][1080p][AV1][CHS]"
    alt_titles = [
        {"tv_id": 1234, "titles": [{"title": "伍六七之暗影宿命", "country": "CN"}]},
    ]
    candidates = [
        {"id": 1234, "name": "Scissor Seven", "original_name": "Cike Wuliuqi"},
    ]
    ok, parsed = parse_title(raw, tmdb_candidates=candidates, tmdb_alternative_titles=alt_titles)
    assert ok, parsed
    assert parsed.tmdb_id == 1234
    assert parsed.matched_title in {"伍六七之暗影宿命", "Scissor Seven"}
    assert parsed.resolution == "1080p"
    assert parsed.codec == "AV1"
    assert parsed.subtitle_lang == ["chs"]


def test_parse_hdr_and_range():
    raw = "武庚纪.第08话.国粤双语.繁體內嵌.4K.HDR10+.WEB-DL.H265"
    ok, parsed = parse_title(raw)
    assert ok, parsed
    assert parsed.episodes == [8]
    assert parsed.resolution == "2160p"
    assert parsed.hdr == "HDR10+"
    assert parsed.codec == "HEVC"
    assert "国粤双语" in parsed.tags
    assert "cht" in parsed.subtitle_lang


@pytest.mark.asyncio
async def test_async_parse_with_episode_range():
    raw = "China Joy 2024 - 01-02合集 4K WEB-DL H265 HDR V2"
    ok, parsed = await async_parse_title(raw)
    assert ok, parsed
    assert parsed.episode_range == (1, 2)
    assert parsed.episodes == [1, 2]
    assert parsed.version == "V2"
    assert parsed.resolution == "2160p"
    assert parsed.hdr == "HDR"
    assert parsed.source == "WEB-DL"
