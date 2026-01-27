"""
Orchestrator 服务单元测试
"""

from app.services.orchestrator import SearchQuery, OrchestrationConfig


def test_search_query_creation():
    """测试 SearchQuery 模型创建"""
    query = SearchQuery(
        t="search",
        q="测试关键词",
        season=1,
        ep=10,
        limit=50,
        offset=0,
    )
    assert query.t == "search"
    assert query.q == "测试关键词"
    assert query.season == 1
    assert query.ep == 10
    assert query.limit == 50
    assert query.offset == 0


def test_search_query_tvsearch():
    """测试 tvsearch 查询"""
    query = SearchQuery(
        t="tvsearch",
        q="斗破苍穹",
        season=3,
        ep=24,
    )
    assert query.t == "tvsearch"
    assert query.season == 3
    assert query.ep == 24


def test_search_query_movie_requires_q():
    """测试 movie 查询必须有 q"""
    try:
        SearchQuery(t="movie", q=None)
        assert False, "movie 查询缺少 q 应该报错"
    except Exception:
        assert True


def test_search_query_normalizes_t():
    """测试 t 字段规范化"""
    query = SearchQuery(t="SEARCH", q="关键词")
    assert query.t == "search"


def test_search_query_with_ids():
    """测试带外部 ID 的查询"""
    query = SearchQuery(
        t="search",
        q="测试",
        tmdbid=12345,
        tvdbid=67890,
        rid=111,
        imdbid="tt123456",
    )
    assert query.tmdbid == 12345
    assert query.tvdbid == 67890
    assert query.rid == 111
    assert query.imdbid == "tt123456"


def test_orchestration_config_defaults():
    """测试 OrchestrationConfig 默认值"""
    config = OrchestrationConfig()
    assert config.max_concurrent_parsing == 10
    assert config.enable_tmdb_enhancement is True
    assert config.tmdb_cache_ttl == 3600


def test_orchestration_config_custom():
    """测试自定义 OrchestrationConfig"""
    config = OrchestrationConfig(
        max_concurrent_parsing=20,
        enable_tmdb_enhancement=False,
        tmdb_cache_ttl=7200,
    )
    assert config.max_concurrent_parsing == 20
    assert config.enable_tmdb_enhancement is False
    assert config.tmdb_cache_ttl == 7200
