"""
Orchestrator 服务数据模型
"""

from typing import Optional
from pydantic import BaseModel, Field, model_validator


class SearchQuery(BaseModel):
    """Torznab 搜索查询模型"""

    t: str = Field(..., description="操作类型：search | tvsearch | movie | caps")
    q: Optional[str] = Field(None, description="搜索关键词（t=search 时必填）")
    season: Optional[int] = Field(None, description="季号（t=tvsearch 时使用）")
    ep: Optional[int] = Field(None, alias="ep", description="集号（t=tvsearch 时使用）")
    tvdbid: Optional[int] = Field(None, description="TVDB ID")
    tmdbid: Optional[int] = Field(None, description="TMDB ID（用于 TMDB 别名增强）")
    rid: Optional[int] = Field(None, description="TVRage ID")
    imdbid: Optional[str] = Field(None, description="IMDB ID")
    limit: int = Field(100, description="返回结果限制")
    offset: int = Field(0, description="分页偏移")
    indexer_ids: Optional[list[int]] = Field(None, description="限制索引器 ID 列表")

    class Config:
        populate_by_name = True

    @model_validator(mode="after")
    def _validate_query(self) -> "SearchQuery":
        t_value = (self.t or "").strip().lower()
        if t_value not in {"search", "tvsearch", "movie", "caps"}:
            raise ValueError("参数错误: t 不支持")
        if t_value in {"search", "movie"} and not (self.q and self.q.strip()):
            raise ValueError("参数错误: t=search 或 t=movie 时 q 必填")
        self.t = t_value
        return self


class OrchestrationConfig(BaseModel):
    """编排服务配置"""

    max_concurrent_parsing: int = Field(10, description="最大并发解析数")
    enable_tmdb_enhancement: bool = Field(True, description="是否启用 TMDB 增强")
    tmdb_cache_ttl: int = Field(3600, description="TMDB 缓存时间（秒）")
