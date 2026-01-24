"""seed torznab caps dict data"""

from __future__ import annotations

from typing import Iterable

from alembic import op
import sqlalchemy as sa

revision = "20260124_seed_torznab_caps_dicts"
down_revision = "20241212_seed_base_dicts"
branch_labels = None
depends_on = None

CATEGORIES = [
    ("2000", "Movie", "2000", 1, '{"kind":"builtin"}'),
    ("5000", "TV", "5000", 2, '{"kind":"builtin"}'),
    ("5070", "TV/Anime", "5070", 3, '{"kind":"builtin"}'),
]

SEARCH_MODES = [
    ("search", "通用搜索", "search", 1, '{"supportedParams":"q","kind":"builtin"}'),
    ("tvsearch", "剧集搜索", "tvsearch", 2, '{"supportedParams":"q,season,ep,tmdbid","kind":"builtin"}'),
    ("movie-search", "电影搜索", "movie-search", 3, '{"supportedParams":"q,tmdbid","kind":"builtin"}'),
]

SETTINGS = [
    ("server_name", "服务器名称", "Queqiao-arr", 1, '{"kind":"builtin"}'),
    ("max_items", "单页最大条数", "100", 2, '{"kind":"builtin"}'),
]

def _has_tables(bind, names: Iterable[str]) -> bool:
    inspector = sa.inspect(bind)
    return all(inspector.has_table(name) for name in names)

def _upsert_dict_type(bind, code: str, name: str, remark: str) -> None:
    bind.execute(
        sa.text(
            "INSERT INTO dict_types (code, name, remark, is_active) "
            "SELECT :code, :name, :remark, 1 WHERE NOT EXISTS "
            "(SELECT 1 FROM dict_types WHERE code = :code)"
        ),
        {"code": code, "name": name, "remark": remark},
    )

def _upsert_items(bind, dict_code: str, items: list[tuple[str, str, str, int, str]]) -> None:
    for code, name, value, order, extra in items:
        bind.execute(
            sa.text(
                "INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active) "
                "SELECT :dict_type_code, :code, :name, :value, :sort_order, 'builtin', :extra_data, 1 "
                "WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = :dict_type_code AND code = :code)"
            ),
            {
                "dict_type_code": dict_code,
                "code": code,
                "name": name,
                "value": value,
                "sort_order": order,
                "extra_data": extra,
            },
        )

def upgrade() -> None:
    bind = op.get_bind()
    if not _has_tables(bind, ["dict_types", "dict_items"]):
        return

    _upsert_dict_type(bind, "torznab.categories", "Torznab 资源分类", "Torznab/Newznab 标准分类")
    _upsert_items(bind, "torznab.categories", CATEGORIES)

    _upsert_dict_type(bind, "torznab.search_modes", "Torznab 搜索模式", "索引器支持的搜索模式及参数")
    _upsert_items(bind, "torznab.search_modes", SEARCH_MODES)

    _upsert_dict_type(bind, "torznab.settings", "Torznab 基础设置", "Torznab 服务器全局配置")
    _upsert_items(bind, "torznab.settings", SETTINGS)

def downgrade() -> None:
    bind = op.get_bind()
    if not _has_tables(bind, ["dict_types", "dict_items"]):
        return
    for code, _, _, _, _ in CATEGORIES:
        bind.execute(
            sa.text("DELETE FROM dict_items WHERE dict_type_code = :dict_type_code AND code = :code"),
            {"dict_type_code": "torznab.categories", "code": code},
        )
    for code, _, _, _, _ in SEARCH_MODES:
        bind.execute(
            sa.text("DELETE FROM dict_items WHERE dict_type_code = :dict_type_code AND code = :code"),
            {"dict_type_code": "torznab.search_modes", "code": code},
        )
    for code, _, _, _, _ in SETTINGS:
        bind.execute(
            sa.text("DELETE FROM dict_items WHERE dict_type_code = :dict_type_code AND code = :code"),
            {"dict_type_code": "torznab.settings", "code": code},
        )
    bind.execute(sa.text("DELETE FROM dict_types WHERE code = :code"), {"code": "torznab.categories"})
    bind.execute(sa.text("DELETE FROM dict_types WHERE code = :code"), {"code": "torznab.search_modes"})
    bind.execute(sa.text("DELETE FROM dict_types WHERE code = :code"), {"code": "torznab.settings"})
