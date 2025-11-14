"""
TMDB 相关请求/响应模型
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class TMDBSearchQuery(BaseModel):
    query: str = Field(min_length=1, description="搜索关键词")
    language: str = Field(default="zh-CN", description="语言代码")
    page: int = Field(default=1, ge=1, description="页码（>=1）")
    include_adult: bool = Field(default=False, description="是否包含成人内容")


class TMDBSearchItem(BaseModel):
    id: int
    name: Optional[str] = None
    original_name: Optional[str] = None
    first_air_date: Optional[str] = None
    origin_country: Optional[List[str]] = None


class TMDBSearchResponse(BaseModel):
    page: int
    total_pages: int
    results: List[TMDBSearchItem]


class TMDBAlternativeTitle(BaseModel):
    title: str
    country: Optional[str] = Field(default=None, description="ISO 3166-1 代码")


class TMDBAlternativeTitlesResponse(BaseModel):
    tv_id: int
    titles: List[TMDBAlternativeTitle]


class TMDBDetailsResponse(BaseModel):
    id: int
    name: Optional[str] = None
    original_name: Optional[str] = None
    first_air_date: Optional[str] = None
    number_of_seasons: Optional[int] = None
    number_of_episodes: Optional[int] = None
    overview: Optional[str] = None


