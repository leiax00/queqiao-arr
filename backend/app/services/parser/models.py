"""
Pydantic 数据模型定义，用于标题解析输入输出。
"""

from typing import Any, List, Optional, Tuple

from pydantic import BaseModel, Field


class TMDBSearchCandidate(BaseModel):
    """
    兼容 TMDB 搜索结果的简化结构
    """

    id: int
    name: Optional[str] = None
    original_name: Optional[str] = None
    first_air_date: Optional[str] = None
    origin_country: Optional[List[str]] = None


class TMDBAltTitle(BaseModel):
    """
    TMDB 别名结构，允许附带 tv_id 方便回填
    """

    title: str
    country: Optional[str] = Field(default=None, description="ISO 3166-1 代码，如 CN/HK/TW")
    tv_id: Optional[int] = Field(default=None, description="所属 TMDB 剧集 ID")


class ParsedTitle(BaseModel):
    """
    标题解析结果结构
    """

    raw_title: str
    normalized_title: str
    matched_title: Optional[str] = None
    tmdb_id: Optional[int] = None
    season: Optional[int] = 1
    episodes: List[int] = Field(default_factory=list)
    episode_range: Optional[Tuple[int, int]] = None
    special_type: Optional[str] = None
    is_finale: bool = False
    resolution: Optional[str] = None
    source: Optional[str] = None
    hdr: Optional[str] = None
    codec: Optional[str] = None
    audio: Optional[str] = None
    subtitle_lang: List[str] = Field(default_factory=list)
    release_group: Optional[str] = None
    version: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    unparsed_segments: List[str] = Field(default_factory=list)
