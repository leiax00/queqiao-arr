"""
Prowlarr 相关请求/响应模型
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProwlarrSearchQuery(BaseModel):
    query: str = Field(min_length=1, description="搜索关键词")
    indexer_ids: Optional[List[int]] = Field(default=None, description="索引器 ID 列表")
    categories: Optional[List[int]] = Field(default=None, description="分类 ID 列表")
    limit: Optional[int] = Field(default=100, ge=0, description="返回数量上限")
    offset: Optional[int] = Field(default=0, ge=0, description="偏移量")
    type: str = Field(default="search", description ="搜索类型，默认 search（兼容 tvsearch 等）")


class ProwlarrSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
