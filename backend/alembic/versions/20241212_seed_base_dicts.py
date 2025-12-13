"""seed base dict data (language, region)"""

from __future__ import annotations

from typing import Iterable

from alembic import op
import sqlalchemy as sa

revision = "20241212_seed_base_dicts"
down_revision = "20241212_seed_title_parser_dicts"
branch_labels = None
depends_on = None

LANGUAGES = [
    ("zh-CN", "简体中文", "zh-CN", 1, '{"icon":"🇨🇳","kind":"builtin"}'),
    ("zh-TW", "繁體中文", "zh-TW", 2, '{"icon":"🇹🇼","kind":"builtin"}'),
    ("en-US", "English (US)", "en-US", 3, '{"icon":"🇺🇸","kind":"builtin"}'),
    ("ja-JP", "日本語", "ja-JP", 4, '{"icon":"🇯🇵","kind":"builtin"}'),
    ("ko-KR", "한국어", "ko-KR", 5, '{"icon":"🇰🇷","kind":"builtin"}'),
]

REGIONS = [
    ("CN", "中国大陆", "CN", 1, '{"icon":"🇨🇳","kind":"builtin"}'),
    ("TW", "台湾", "TW", 2, '{"icon":"🇹🇼","kind":"builtin"}'),
    ("HK", "香港", "HK", 3, '{"icon":"🇭🇰","kind":"builtin"}'),
    ("US", "美国", "US", 4, '{"icon":"🇺🇸","kind":"builtin"}'),
    ("JP", "日本", "JP", 5, '{"icon":"🇯🇵","kind":"builtin"}'),
    ("KR", "韩国", "KR", 6, '{"icon":"🇰🇷","kind":"builtin"}'),
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

    _upsert_dict_type(bind, "language", "语言选项", "系统语言枚举（builtin）")
    _upsert_items(bind, "language", LANGUAGES)

    _upsert_dict_type(bind, "region", "地区选项", "地区枚举（builtin）")
    _upsert_items(bind, "region", REGIONS)


def downgrade() -> None:
    bind = op.get_bind()
    if not _has_tables(bind, ["dict_types", "dict_items"]):
        return
    for code, _, _, _, _ in LANGUAGES:
        bind.execute(
            sa.text("DELETE FROM dict_items WHERE dict_type_code = :dict_type_code AND code = :code"),
            {"dict_type_code": "language", "code": code},
        )
    for code, _, _, _, _ in REGIONS:
        bind.execute(
            sa.text("DELETE FROM dict_items WHERE dict_type_code = :dict_type_code AND code = :code"),
            {"dict_type_code": "region", "code": code},
        )
    bind.execute(sa.text("DELETE FROM dict_types WHERE code = :code"), {"code": "language"})
    bind.execute(sa.text("DELETE FROM dict_types WHERE code = :code"), {"code": "region"})
