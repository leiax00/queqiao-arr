"""
Prowlarr 相关请求/响应模型
"""

from typing import Any, Dict, List, Optional
from fastapi import Query, HTTPException, status
from pydantic import BaseModel, Field, ValidationError


class ProwlarrSearchQuery(BaseModel):
    query: str = Field(min_length=1, description="搜索关键词")
    indexer_ids: Optional[List[int]] = Field(default=None, description="索引器 ID 列表")
    categories: Optional[List[int]] = Field(default=None, description="分类 ID 列表")
    limit: Optional[int] = Field(default=100, ge=0, description="返回数量上限")
    offset: Optional[int] = Field(default=0, ge=0, description="偏移量")
    type: str = Field(default="search", description ="搜索类型，默认 search（兼容 tvsearch 等）")


async def parse_search_query(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    indexer_ids: Optional[str] = Query(default=None, description="索引器 ID 列表，逗号分隔，如：1,2,3"),
    categories: Optional[str] = Query(default=None, description="分类 ID 列表，逗号分隔，如：1000,2000"),
    limit: int = Query(default=100, ge=0, description="返回数量上限"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    type: str = Query(default="search", description="搜索类型，默认 search（兼容 tvsearch 等）")
) -> ProwlarrSearchQuery:
    """
    从查询参数解析并构建 ProwlarrSearchQuery 对象
    """
    try:
        # 解析逗号分隔的字符串为整数列表
        indexer_ids_list = None
        if indexer_ids:
            indexer_ids_list = [int(x.strip()) for x in indexer_ids.split(',') if x.strip()]

        categories_list = None
        if categories:
            categories_list = [int(x.strip()) for x in categories.split(',') if x.strip()]

        return ProwlarrSearchQuery(
            query=query,
            indexer_ids=indexer_ids_list,
            categories=categories_list,
            limit=limit,
            offset=offset,
            type=type
        )
    except (ValueError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数解析错误: {str(e)}"
        )


class ProwlarrSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
