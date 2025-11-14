"""
TMDB 查询端点
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.db.database import get_db
from app.db import crud_config
from app.services.clients import TMDBClient, make_client
from app.utils import success_response, error_response
from app.utils.config_helpers import (
    parse_extra_config,
    decrypt_if_present,
    get_active_proxy_config,
)
from app.api.schemas import (
    TMDBSearchQuery,
    TMDBSearchResponse,
    TMDBAlternativeTitlesResponse,
    TMDBDetailsResponse,
)

router = APIRouter()


async def _load_tmdb_runtime(db: AsyncSession) -> tuple[str, Optional[Dict[str, str]], Dict[str, Any]]:
    """
    加载 TMDB 的运行时参数：api_key、proxies、extra
    优先选择启用中的 `service_name=tmdb` 配置；若存在多条取第一条。
    """
    items = await crud_config.get_service_configs(db, service_name="tmdb", is_active=True)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到启用中的 TMDB 配置")
    svc = items[0]
    api_key = decrypt_if_present(svc.api_key)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TMDB 配置缺少有效 api_key")
    extra = parse_extra_config(getattr(svc, "extra_config", None)) or {}
    proxies = None
    if isinstance(extra, dict) and extra.get("use_proxy"):
        proxies = await get_active_proxy_config(db)
    return api_key, proxies, extra


async def get_tmdb_client(db: AsyncSession = Depends(get_db)) -> TMDBClient:
    """
    作为依赖注入的 TMDB 客户端构造函数
    根据当前启用的 TMDB 配置创建客户端实例
    """
    api_key, proxies, extra = await _load_tmdb_runtime(db)
    client = make_client("tmdb", api_key=api_key, proxies=proxies, timeout=10)
    assert isinstance(client, TMDBClient)
    return client


@router.get(
    "/search",
    summary="搜索剧集（TMDB）",
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "page": 1,
                            "total_pages": 5,
                            "results": [
                                {
                                    "id": 123,
                                    "name": "名称",
                                    "original_name": "Original",
                                    "first_air_date": "2020-01-01",
                                    "origin_country": ["CN"],
                                }
                            ],
                        },
                    }
                }
            },
        },
        400: {
            "description": "请求参数非法",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "参数错误: query 不能为空", "data": None}
                }
            },
        },
        401: {
            "description": "未认证",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        404: {
            "description": "TMDB 配置缺失",
            "content": {
                "application/json": {
                    "example": {"detail": "未找到启用中的 TMDB 配置"}
                }
            },
        },
        502: {
            "description": "上游 TMDB 返回错误或网络异常",
            "content": {
                "application/json": {
                    "example": {
                        "code": 502,
                        "message": "TMDB 连接失败: 网络请求失败: https://api.themoviedb.org/3/search/tv",
                        "data": None,
                    }
                }
            },
        },
    },
)
async def tmdb_search(
    params: TMDBSearchQuery = Depends(),
    client: TMDBClient = Depends(get_tmdb_client),
    current_user=Depends(get_current_user),
):
    params_dict = params.model_dump() if hasattr(params, "model_dump") else params.dict()
    ok, data = client.search_tv(**params_dict)
    if not ok:
        return error_response(message=str(data), code=502)
    # 透传 TMDB 的分页/结果基本字段
    data_dict = data if isinstance(data, dict) else {}
    page_out = int(data_dict.get("page", params.page))
    total_pages = int(data_dict.get("total_pages", 1))
    results = data_dict.get("results", []) or []
    response_data = TMDBSearchResponse(
        page=page_out,
        total_pages=total_pages,
        results=results,
    )
    return success_response(response_data)


@router.get(
    "/tv/{tv_id}",
    summary="获取剧集详情（TMDB）",
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "id": 123,
                            "name": "名称",
                            "original_name": "Original",
                            "number_of_seasons": 2,
                            "number_of_episodes": 24,
                        },
                    }
                }
            },
        },
        400: {
            "description": "请求参数非法",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "参数错误: tv_id 必须为正整数", "data": None}
                }
            },
        },
        401: {
            "description": "未认证",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        404: {
            "description": "TMDB 配置缺失",
            "content": {
                "application/json": {
                    "example": {"detail": "未找到启用中的 TMDB 配置"}
                }
            },
        },
        502: {
            "description": "上游 TMDB 返回错误或网络异常",
            "content": {
                "application/json": {
                    "example": {
                        "code": 502,
                        "message": "TMDB 连接失败: HTTP 错误 500: https://api.themoviedb.org/3/tv/123",
                        "data": None,
                    }
                }
            },
        },
    },
)
async def tmdb_tv_details(
    tv_id: int,
    language: str = Query(default="zh-CN"),
    client: TMDBClient = Depends(get_tmdb_client),
    current_user=Depends(get_current_user),
):
    ok, data = client.get_tv_details(tv_id=tv_id, language=language)
    if not ok:
        return error_response(message=str(data), code=502)
    return success_response(data)


@router.get(
    "/tv/{tv_id}/alternative_titles",
    summary="获取剧集替代标题（TMDB）",
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {
                            "tv_id": 123,
                            "titles": [
                                {"title": "国漫名", "country": "CN"},
                                {"title": "中文（香港）", "country": "HK"},
                            ],
                        },
                    }
                }
            },
        },
        400: {
            "description": "请求参数非法",
            "content": {
                "application/json": {
                    "example": {"code": 400, "message": "参数错误: country 必须为2位字母的国家码", "data": None}
                }
            },
        },
        401: {
            "description": "未认证",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        404: {
            "description": "TMDB 配置缺失",
            "content": {
                "application/json": {
                    "example": {"detail": "未找到启用中的 TMDB 配置"}
                }
            },
        },
        502: {
            "description": "上游 TMDB 返回错误或网络异常",
            "content": {
                "application/json": {
                    "example": {
                        "code": 502,
                        "message": "TMDB 连接失败: 网络请求失败: https://api.themoviedb.org/3/tv/123/alternative_titles",
                        "data": None,
                    }
                }
            },
        },
    },
)
async def tmdb_alternative_titles(
    tv_id: int,
    country: Optional[str] = Query(default=None),
    client: TMDBClient = Depends(get_tmdb_client),
    current_user=Depends(get_current_user),
):
    ok, data = client.get_alternative_titles(tv_id=tv_id, country=country)
    if not ok:
        return error_response(message=str(data), code=502)
    # 透传并轻量规整字段名
    titles = []
    if isinstance(data, dict):
        for t in data.get("titles", []) or []:
            title = t.get("title")
            country_code = t.get("iso_3166_1")
            if title:
                titles.append({"title": title, "country": country_code})
    response_data = TMDBAlternativeTitlesResponse(tv_id=tv_id, titles=titles)
    return success_response(response_data)
