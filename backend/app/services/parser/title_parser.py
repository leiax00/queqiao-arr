"""
标题解析核心逻辑（B-06）

实现基于常见国漫/番剧命名规则的解析，输出结构化字段供后续模块消费。
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .models import ParsedTitle, TMDBAltTitle, TMDBSearchCandidate

# 供匹配的常见映射
_RESOLUTION_MAP = {
    "2160P": "2160p",
    "4K": "2160p",
    "1080P": "1080p",
    "720P": "720p",
    "480P": "480p",
}

_SOURCE_MAP = {
    "WEB-DL": "WEB-DL",
    "WEBDL": "WEB-DL",
    "WEB": "WEB-DL",
    "WEBRIP": "WEBRip",
    "WEB-RIP": "WEBRip",
    "WEBrip": "WEBRip",
    "BLURAY": "BluRay",
    "BDRIP": "BluRay",
    "BDRip": "BluRay",
    "B-Global": "WEB-DL",
    "B-GLOBAL": "WEB-DL",
    "B-GLOBAL]": "WEB-DL",
    "HDTV": "HDTV",
    "DVDRIP": "DVDRip",
}

_HDR_MAP = {
    "HDR10+": "HDR10+",
    "HDR10": "HDR10",
    "HDR": "HDR",
    "DOLBYVISION": "DolbyVision",
    "DOVI": "DolbyVision",
    "DV": "DolbyVision",
}

_CODEC_MAP = {
    "HEVC": "HEVC",
    "H265": "HEVC",
    "X265": "HEVC",
    "H.265": "HEVC",
    "H264": "H264",
    "X264": "H264",
    "H.264": "H264",
    "AV1": "AV1",
}

_AUDIO_MAP = {
    "AAC": "AAC",
    "AC3": "AC3",
    "EAC3": "EAC3",
    "DDP": "EAC3",
    "FLAC": "FLAC",
    "DTS-HD": "DTS-HD",
    "DTS": "DTS",
    "TRUEHD": "TrueHD",
}

_SPECIAL_TYPES = ["SP", "OVA", "OAD", "PV", "NCOP", "NCED", "TRAILER"]

_CHINESE_DIGITS = {
    "零": 0,
    "〇": 0,
    "○": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def _convert_chinese_number(fragment: str) -> str:
    """
    将简单中文数字（0-99）转换为阿拉伯数字，便于匹配。
    """
    if not fragment:
        return fragment
    # 仅处理纯中文数字的片段
    if not all(ch in _CHINESE_DIGITS for ch in fragment):
        return fragment
    if fragment in _CHINESE_DIGITS:
        return str(_CHINESE_DIGITS[fragment])
    # 处理十位 + 个位，如 十一、二十、二十三
    total = 0
    if fragment.startswith("十"):
        total = 10 + _CHINESE_DIGITS.get(fragment[1:], 0)
    elif "十" in fragment:
        parts = fragment.split("十")
        high = _CHINESE_DIGITS.get(parts[0], 0)
        low = _CHINESE_DIGITS.get(parts[1], 0) if len(parts) > 1 and parts[1] else 0
        total = high * 10 + low
    return str(total or fragment)


def _normalize_text(raw_title: str) -> str:
    """
    基础预处理：替换常见分隔符、转中文数字、压缩空格。
    """
    text = raw_title
    replacements = {
        "【": " ",
        "】": " ",
        "[": " ",
        "]": " ",
        "（": " ",
        "）": " ",
        "(": " ",
        ")": " ",
        "·": " ",
        "・": " ",
        "/": " / ",
        "\\": " ",
        "_": " ",
        ".": " ",
        "—": " ",
        "–": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # 转换中文数字
    text = re.sub(
        r"[零〇○一二三四五六七八九十]+",
        lambda m: _convert_chinese_number(m.group(0)),
        text,
    )
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _strip_release_group(raw_title: str) -> Tuple[Optional[str], str]:
    """
    提取发布组（前缀括号或结尾 -Group），并返回剩余文本。
    """
    release_group = None
    text = raw_title.strip()

    prefix = re.match(r"^\s*[\[\(【](.+?)[\]\)】]\s*(.*)$", text)
    if prefix:
        candidate = prefix.group(1).strip() or None
        if candidate and candidate.upper() not in _RESOLUTION_MAP and candidate.upper() not in _HDR_MAP and candidate.upper() not in _CODEC_MAP:
            release_group = candidate
        text = prefix.group(2).strip()

    suffix = re.search(r"-([A-Za-z0-9&._]+)$", text)
    if suffix:
        candidate = suffix.group(1)
        # 避免误把编码/HDR 识别为组名
        if "." in candidate:
            pass
        elif candidate.upper() not in _CODEC_MAP and candidate.upper() not in _HDR_MAP and not candidate.endswith("P"):
            release_group = release_group or candidate
            text = text[: suffix.start()].strip()
    return release_group, text


def _strip_version(text: str) -> Tuple[Optional[str], str]:
    """
    提取版本号（V2/V3/REPACK/Proper）并返回剩余文本。
    """
    match = re.search(r"\b(V\d+|REPACK|Proper)\b", text, flags=re.IGNORECASE)
    version = None
    if match:
        version = match.group(1).upper()
        text = (text[: match.start()] + text[match.end() :]).strip()
    return version, text


def _detect_season(text: str) -> Optional[int]:
    """
    识别季信息，默认返回 None（由上层填充缺省值 1）。
    """
    season_match = re.search(r"S(?P<num>\d{1,2})", text, flags=re.IGNORECASE)
    if season_match:
        try:
            return int(season_match.group("num"))
        except ValueError:
            pass
    season_cn = re.search(r"第\s?(?P<num>\d{1,2})\s?(季|期|部)", text)
    if season_cn:
        try:
            return int(season_cn.group("num"))
        except ValueError:
            pass
    season_en = re.search(r"Season\s*(?P<num>\d{1,2})", text, flags=re.IGNORECASE)
    if season_en:
        try:
            return int(season_en.group("num"))
        except ValueError:
            pass
    return None


def _detect_episode_range(text: str) -> Optional[Tuple[int, int]]:
    """
    识别连播区间（xx-yy 或 xx~yy）。
    """
    for pattern in [
        r"(?<![A-Za-z0-9])(?P<start>\d{1,3})\s*-\s*(?P<end>\d{1,3})(?![A-Za-z0-9])",
        r"(?<![A-Za-z0-9])(?P<start>\d{1,3})\s*~\s*(?P<end>\d{1,3})(?![A-Za-z0-9])",
        r"EP?\s?(?P<start>\d{1,3})\s*[-~]\s*(?P<end>\d{1,3})",
        r"第\s?(?P<start>\d{1,3})\s?(集|话|話)\s*[-~]\s*(?P<end>\d{1,3})",
    ]:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                start = int(match.group("start"))
                end = int(match.group("end"))
                if start <= 0 or end < start or start > 300 or end > 300:
                    continue
                return start, end
            except ValueError:
                continue
    return None


def _detect_episodes(text: str) -> Tuple[List[int], Optional[Tuple[int, int]], Optional[int]]:
    """
    识别集号，返回（集列表，区间，可能的季号）。
    """
    episodes: set[int] = set()
    episode_range = _detect_episode_range(text)
    detected_season: Optional[int] = None

    season_spans: List[Tuple[int, int]] = []
    for match in re.finditer(r"S(?P<num>\d{1,2})", text, flags=re.IGNORECASE):
        season_spans.append(match.span("num"))
    for match in re.finditer(r"Season\s*(?P<num>\d{1,2})", text, flags=re.IGNORECASE):
        season_spans.append(match.span("num"))
    for match in re.finditer(r"第\s?(?P<num>\d{1,2})\s?(季|期|部)", text):
        season_spans.append(match.span("num"))

    def _overlaps(target_span: Tuple[int, int], spans: Sequence[Tuple[int, int]]) -> bool:
        return any(not (target_span[1] <= s[0] or target_span[0] >= s[1]) for s in spans)

    # SxxEyy 强模式
    for match in re.finditer(r"S(?P<season>\d{1,2})E(?P<ep>\d{1,3})", text, flags=re.IGNORECASE):
        try:
            episodes.add(int(match.group("ep")))
            detected_season = detected_season or int(match.group("season"))
        except ValueError:
            continue

    # EPxx / Exx
    for match in re.finditer(r"\bEP?\s?(?P<ep>\d{1,3})\b", text, flags=re.IGNORECASE):
        try:
            episodes.add(int(match.group("ep")))
        except ValueError:
            continue

    # 中文“第xx集/话”
    for match in re.finditer(r"第\s?(?P<ep>\d{1,3})\s?(集|话|話)", text):
        try:
            episodes.add(int(match.group("ep")))
        except ValueError:
            continue

    # 单独数字（排除常见分辨率/年份）
    for match in re.finditer(r"\b(?P<num>\d{1,3})\b", text):
        try:
            num = int(match.group("num"))
        except ValueError:
            continue
        if num in {2160, 1080, 720, 480} or num >= 300:
            continue
        if _overlaps(match.span("num"), season_spans):
            continue
        episodes.add(num)

    if episode_range:
        start, end = episode_range
        for num in range(start, end + 1):
            episodes.add(num)

    ep_list = sorted(episodes)
    return ep_list, episode_range, detected_season


def _detect_special_type(text: str) -> Optional[str]:
    for stype in _SPECIAL_TYPES:
        if re.search(rf"\b{stype}\b", text, flags=re.IGNORECASE):
            return stype.upper()
    return None


def _detect_finale(text: str) -> bool:
    return bool(re.search(r"\bEND\b|完结|全集|完結", text, flags=re.IGNORECASE))


def _detect_resolution(text: str) -> Optional[str]:
    for raw, normalized in _RESOLUTION_MAP.items():
        if re.search(rf"\b{raw}\b", text, flags=re.IGNORECASE):
            return normalized
    # 4K 可能连写
    if "4K" in text.upper():
        return "2160p"
    return None


def _detect_source(text: str) -> Optional[str]:
    for raw, normalized in _SOURCE_MAP.items():
        if re.search(rf"\b{raw}\b", text, flags=re.IGNORECASE):
            return normalized
    return None


def _detect_hdr(text: str) -> Optional[str]:
    upper = text.upper()
    for raw, normalized in _HDR_MAP.items():
        if raw in upper:
            return normalized
    return None


def _detect_codec(text: str) -> Optional[str]:
    upper = text.upper()
    for raw, normalized in _CODEC_MAP.items():
        if raw in upper:
            return normalized
    return None


def _detect_audio(text: str) -> Optional[str]:
    upper = text.upper()
    for raw, normalized in _AUDIO_MAP.items():
        if raw in upper:
            return normalized
    return None


def _detect_subtitle_and_tags(text: str) -> Tuple[List[str], List[str]]:
    subtitle_lang: set[str] = set()
    tags: List[str] = []
    upper = text.upper()
    if re.search(r"简繁|内封|內封|CHS&CHT|BIG5|GB", text, flags=re.IGNORECASE):
        subtitle_lang.update(["chs", "cht"])
    if re.search(r"简体|CHS|GB", text, flags=re.IGNORECASE):
        subtitle_lang.add("chs")
    if re.search(r"繁体|CHT|BIG5|繁體|內嵌", text, flags=re.IGNORECASE):
        subtitle_lang.add("cht")
    if "双语" in text or "雙語" in text:
        tags.append("国粤双语")
    if re.search(r"合集|Complete|Collection", text, flags=re.IGNORECASE):
        tags.append("合集")
    if "NC-" in text.upper() or "NC " in text.upper():
        tags.append("NC")
    if "B-GLOBAL" in upper or "B-Global" in text:
        tags.append("B-Global")
    return sorted(subtitle_lang), tags


def _extract_base_title(text: str) -> str:
    """
    尝试截取剧名部分：取第一个核心模式出现前的文本。
    """
    candidates = []
    patterns = [
        r"S\d{1,2}E\d{1,3}",
        r"S\d{1,2}",
        r"第\s?\d{1,2}\s?(季|期|部)",
        r"Season\s*\d{1,2}",
        r"EP?\s?\d{1,3}",
        r"第\s?\d{1,3}\s?(集|话|話)",
        r"\d{1,3}\s*[-~]\s*\d{1,3}",
        r"\bEND\b|完结|全集|完結",
        r"2160P|1080P|720P|4K",
        r"HDR|AV1|HEVC|H265|H264|WEB-DL|WEBRIP|BLURAY|HDTV",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            candidates.append(m.start())
    cut = min(candidates) if candidates else len(text)
    base = text[:cut].strip(" -._/|")
    base = re.sub(r"\s+", " ", base)
    return base.strip()


def _normalize_for_match(title: str) -> str:
    """
    用于模糊匹配的规范化：小写、去空格和分隔符。
    """
    text = title.lower()
    text = re.sub(r"[^\w]+", "", text)
    return text


def _flatten_alt_titles(
    alt_titles: Optional[Sequence[Any]],
) -> List[TMDBAltTitle]:
    """
    兼容不同输入格式，将别名列表扁平化为 TMDBAltTitle。
    """
    result: List[TMDBAltTitle] = []
    if not alt_titles:
        return result
    for item in alt_titles:
        # 包含 titles 数组的包装结构
        if isinstance(item, dict) and "titles" in item:
            tv_id = item.get("tv_id")
            for t in item.get("titles") or []:
                title = t.get("title") if isinstance(t, dict) else None
                country = t.get("country") if isinstance(t, dict) else None
                if title:
                    result.append(TMDBAltTitle(title=title, country=country, tv_id=tv_id))
            continue
        if isinstance(item, TMDBAltTitle):
            result.append(item)
        elif isinstance(item, dict) and item.get("title"):
            result.append(
                TMDBAltTitle(
                    title=item.get("title"),
                    country=item.get("country"),
                    tv_id=item.get("tv_id"),
                )
            )
    return result


def _flatten_candidates(candidates: Optional[Sequence[Any]]) -> List[TMDBSearchCandidate]:
    """
    兼容不同输入格式，将搜索候选扁平化。
    """
    result: List[TMDBSearchCandidate] = []
    if not candidates:
        return result
    for item in candidates:
        if isinstance(item, TMDBSearchCandidate):
            result.append(item)
        elif isinstance(item, dict) and "id" in item:
            result.append(
                TMDBSearchCandidate(
                    id=item.get("id"),
                    name=item.get("name"),
                    original_name=item.get("original_name") or item.get("originalName"),
                    first_air_date=item.get("first_air_date"),
                    origin_country=item.get("origin_country"),
                )
            )
    return result


def _match_tmdb_title(
    normalized_title: str,
    candidates: Optional[Sequence[Any]] = None,
    alt_titles: Optional[Sequence[Any]] = None,
    language_pref: Optional[List[str]] = None,
) -> Tuple[Optional[str], Optional[int], bool]:
    """
    根据剧名/别名匹配 TMDB，返回 (匹配到的标题, tmdb_id, 是否命中)。
    """
    base_norm = _normalize_for_match(normalized_title)
    if not base_norm:
        return None, None, False
    language_pref = language_pref or ["CN", "HK", "TW", "US", "JP"]

    flattened_alt = _flatten_alt_titles(alt_titles)
    best_title = None
    best_id = None
    best_score = 0.0

    def _score_match(candidate_title: str, country: Optional[str] = None) -> float:
        cand_norm = _normalize_for_match(candidate_title)
        if not cand_norm:
            return 0.0
        if cand_norm == base_norm:
            score = 1.0
        elif cand_norm in base_norm or base_norm in cand_norm:
            score = 0.8
        else:
            score = 0.0
        if score > 0 and country:
            try:
                bias = max(len(language_pref) - language_pref.index(country.upper()), 0) * 0.05
                score += bias
            except ValueError:
                pass
        return score

    for alt in flattened_alt:
        score = _score_match(alt.title, alt.country)
        if score > best_score:
            best_title = alt.title
            best_id = alt.tv_id
            best_score = score

    flattened_candidates = _flatten_candidates(candidates)
    for cand in flattened_candidates:
        for field_name in ["name", "original_name"]:
            title_val = getattr(cand, field_name)
            if not title_val:
                continue
            score = _score_match(title_val, None)
            if score > best_score:
                best_score = score
                best_title = title_val
                best_id = cand.id

    hit = best_score >= 0.8 or (best_score >= 0.6 and best_id is not None)
    return best_title, best_id, hit


def _collect_unparsed_segments(
    normalized_text: str,
    normalized_title: str,
    recognized_tokens: Iterable[str],
    episodes: Sequence[int],
) -> List[str]:
    """
    将解析未覆盖的片段收集起来，便于后续调优。
    """
    recognized = {tok.lower() for tok in recognized_tokens if tok}
    recognized.update(str(ep) for ep in episodes)
    recognized.update(f"{ep:02d}" for ep in episodes)
    base_tokens = set(filter(None, normalized_title.lower().split()))
    segments: List[str] = []
    for token in normalized_text.split():
        low = token.lower()
        if low in base_tokens or low in recognized:
            continue
        segments.append(token)
    return segments


def _calculate_confidence(
    has_alias_hit: bool,
    episodes: Sequence[int],
    episode_range: Optional[Tuple[int, int]],
    resolution: Optional[str],
    source: Optional[str],
    codec: Optional[str],
    subtitle_lang: Sequence[str],
    special_type: Optional[str],
    is_finale: bool,
) -> float:
    """
    简单的置信度打分：字段越完整分值越高。
    """
    score = 0.2
    if episodes:
        score += 0.25
    if episode_range:
        score += 0.05
    if resolution:
        score += 0.1
    if source:
        score += 0.05
    if codec:
        score += 0.05
    if subtitle_lang:
        score += 0.05
    if special_type or is_finale:
        score += 0.05
    if has_alias_hit:
        score += 0.2
    return round(min(score, 1.0), 2)


def parse_title(
    raw_title: str,
    tmdb_candidates: Optional[Sequence[Any]] = None,
    tmdb_alternative_titles: Optional[Sequence[Any]] = None,
    language_pref: Optional[List[str]] = None,
) -> Tuple[bool, ParsedTitle | str]:
    """
    标题解析主入口。成功返回 (True, ParsedTitle)，失败返回 (False, errmsg)。
    """
    if not raw_title or not isinstance(raw_title, str) or not raw_title.strip():
        return False, "标题解析失败: 输入为空"

    release_group, stripped = _strip_release_group(raw_title)
    version, stripped = _strip_version(stripped)
    normalized_text = _normalize_text(stripped)

    if not normalized_text:
        return False, "标题解析失败: 无法解析有效文本"

    season = _detect_season(normalized_text)
    episodes, episode_range, season_from_episode = _detect_episodes(normalized_text)
    season = season or season_from_episode or 1

    special_type = _detect_special_type(normalized_text)
    is_finale = _detect_finale(normalized_text)
    resolution = _detect_resolution(normalized_text)
    source = _detect_source(normalized_text)
    hdr = _detect_hdr(normalized_text)
    codec = _detect_codec(normalized_text)
    audio = _detect_audio(normalized_text)
    subtitle_lang, extra_tags = _detect_subtitle_and_tags(normalized_text)

    base_title = _extract_base_title(normalized_text) or normalized_text

    matched_title, tmdb_id, alias_hit = _match_tmdb_title(
        base_title,
        candidates=tmdb_candidates,
        alt_titles=tmdb_alternative_titles,
        language_pref=language_pref,
    )

    # 集数缺失时返回可读错误
    if not episodes and not episode_range:
        return False, "标题解析失败: 未能识别集数信息"

    recognized_tokens: List[str] = [
        resolution,
        source,
        hdr,
        codec,
        audio,
        version,
        special_type,
        "END" if is_finale else "",
        *subtitle_lang,
        *extra_tags,
    ]
    unparsed_segments = _collect_unparsed_segments(
        normalized_text=normalized_text,
        normalized_title=base_title,
        recognized_tokens=recognized_tokens,
        episodes=episodes,
    )

    confidence = _calculate_confidence(
        has_alias_hit=alias_hit,
        episodes=episodes,
        episode_range=episode_range,
        resolution=resolution,
        source=source,
        codec=codec,
        subtitle_lang=subtitle_lang,
        special_type=special_type,
        is_finale=is_finale,
    )

    parsed = ParsedTitle(
        raw_title=raw_title,
        normalized_title=base_title,
        matched_title=matched_title,
        tmdb_id=tmdb_id,
        season=season,
        episodes=episodes,
        episode_range=episode_range,
        special_type=special_type,
        is_finale=is_finale,
        resolution=resolution,
        source=source,
        hdr=hdr,
        codec=codec,
        audio=audio,
        subtitle_lang=subtitle_lang,
        release_group=release_group,
        version=version,
        tags=extra_tags,
        confidence=confidence,
        unparsed_segments=unparsed_segments,
    )
    return True, parsed


async def async_parse_title(
    raw_title: str,
    tmdb_candidates: Optional[Sequence[Any]] = None,
    tmdb_alternative_titles: Optional[Sequence[Any]] = None,
    language_pref: Optional[List[str]] = None,
) -> Tuple[bool, ParsedTitle | str]:
    """
    异步包装，便于 B-08 在协程流程中直接调用。
    """
    return parse_title(
        raw_title=raw_title,
        tmdb_candidates=tmdb_candidates,
        tmdb_alternative_titles=tmdb_alternative_titles,
        language_pref=language_pref,
    )
