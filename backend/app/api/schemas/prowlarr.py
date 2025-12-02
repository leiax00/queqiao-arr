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
    indexer_ids: Optional[List[str]] = Query(default=None, description="索引器 ID 列表，支持重复参数（如：indexer_ids=1&indexer_ids=2）或逗号分隔（如：indexer_ids=1,2,3）"),
    categories: Optional[List[str]] = Query(default=None, description="分类 ID 列表，支持重复参数（如：categories=1000&categories=2000）或逗号分隔（如：categories=1000,2000）"),
    limit: int = Query(default=100, ge=0, description="返回数量上限"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    type: str = Query(default="search", description="搜索类型，默认 search（兼容 tvsearch 等）")
) -> ProwlarrSearchQuery:
    """
    从查询参数解析并构建 ProwlarrSearchQuery 对象

    支持两种参数格式：
    1. 重复参数：indexer_ids=1&indexer_ids=2&indexer_ids=3
    2. 逗号分隔：indexer_ids=1,2,3（单个参数值内包含逗号）
    """
    try:
        def parse_list_param(param_list: Optional[List[str]]) -> Optional[List[int]]:
            """解析列表参数，处理重复参数和逗号分隔"""
            if not param_list:
                return None

            result = []
            for param_value in param_list:
                # 处理逗号分隔的情况，如 "1,2,3"
                if ',' in param_value:
                    for part in param_value.split(','):
                        part = part.strip()
                        if part:
                            try:
                                result.append(int(part))
                            except ValueError:
                                continue  # 跳过无效的数值
                else:
                    # 处理单个值的情况
                    try:
                        result.append(int(param_value.strip()))
                    except ValueError:
                        continue  # 跳过无效的数值

            return result if result else None

        # 解析参数
        indexer_ids_list = parse_list_param(indexer_ids)
        categories_list = parse_list_param(categories)

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
