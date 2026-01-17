"""seed title parser dict data"""

from __future__ import annotations

from typing import Iterable

from alembic import op
import sqlalchemy as sa

revision = "20241212_seed_title_parser_dicts"
down_revision = None
branch_labels = None
depends_on = None


DICT_TYPES = [
    ("title_parser.resolution", "标题解析-分辨率", "Builtin mapping for resolutions"),
    ("title_parser.source", "标题解析-来源", "Builtin mapping for sources"),
    ("title_parser.hdr", "标题解析-HDR", "Builtin mapping for HDR tags"),
    ("title_parser.codec", "标题解析-编码", "Builtin mapping for codecs"),
    ("title_parser.audio", "标题解析-音轨", "Builtin mapping for audio"),
    ("title_parser.subtitle", "标题解析-字幕", "Builtin mapping for subtitle languages"),
    ("title_parser.tag", "标题解析-标签", "Builtin mapping for tags"),
    ("title_parser.rule", "标题解析-规则", "Builtin regex rules for parser"),
    ("quality", "质量标签", "Quality presets"),
]

DICT_ITEMS = {
    "title_parser.resolution": [
        ("2160P", "2160p", "2160p", 1, '{"aliases":["4K"],"kind":"builtin"}'),
        ("8K", "8k", "8k", 0, '{"aliases":["8K","7680p"],"kind":"builtin"}'),
        ("1080P", "1080p", "1080p", 2, '{"aliases":[],"kind":"builtin"}'),
        ("720P", "720p", "720p", 3, '{"aliases":[],"kind":"builtin"}'),
        ("480P", "480p", "480p", 4, '{"aliases":[],"kind":"builtin"}'),
    ],
    "title_parser.source": [
        ("WEB-DL", "WEB-DL", "WEB-DL", 1, '{"aliases":["WEBDL","WEB"],"kind":"builtin"}'),
        ("WEBRIP", "WEBRip", "WEBRip", 2, '{"aliases":["WEB-RIP"],"kind":"builtin"}'),
        ("BLURAY", "BluRay", "BluRay", 3, '{"aliases":["BDRIP","BDRip"],"kind":"builtin"}'),
        ("HDTV", "HDTV", "HDTV", 4, '{"aliases":[],"kind":"builtin"}'),
        ("DVDRIP", "DVDRip", "DVDRip", 5, '{"aliases":[],"kind":"builtin"}'),
        ("B-GLOBAL", "B-Global", "WEB-DL", 6, '{"aliases":["B-Global","B-GLOBAL"],"kind":"builtin"}'),
    ],
    "title_parser.hdr": [
        ("HDR10+", "HDR10+", "HDR10+", 1, '{"aliases":[],"kind":"builtin"}'),
        ("HDR10", "HDR10", "HDR10", 2, '{"aliases":[],"kind":"builtin"}'),
        ("HDR", "HDR", "HDR", 3, '{"aliases":[],"kind":"builtin"}'),
        ("DOLBYVISION", "DolbyVision", "DolbyVision", 4, '{"aliases":["DOVI","DV","Dolby.Vision"],"kind":"builtin"}'),
    ],
    "title_parser.codec": [
        ("HEVC", "HEVC", "HEVC", 1, '{"aliases":["H265","X265","H.265"],"kind":"builtin"}'),
        ("H264", "H264", "H264", 2, '{"aliases":["X264","H.264","AVC","AVC1"],"kind":"builtin"}'),
        ("AV1", "AV1", "AV1", 3, '{"aliases":[],"kind":"builtin"}'),
    ],
    "title_parser.audio": [
        ("AAC", "AAC", "AAC", 1, '{"aliases":[],"kind":"builtin"}'),
        ("AC3", "AC3", "AC3", 2, '{"aliases":[],"kind":"builtin"}'),
        ("EAC3", "EAC3", "EAC3", 3, '{"aliases":["DDP"],"kind":"builtin"}'),
        ("FLAC", "FLAC", "FLAC", 4, '{"aliases":[],"kind":"builtin"}'),
        ("DTS-HD", "DTS-HD", "DTS-HD", 5, '{"aliases":[],"kind":"builtin"}'),
        ("DTS", "DTS", "DTS", 6, '{"aliases":[],"kind":"builtin"}'),
        ("TRUEHD", "TrueHD", "TrueHD", 7, '{"aliases":[],"kind":"builtin"}'),
    ],
    "title_parser.subtitle": [
        ("CHS", "简体", "chs", 1, '{"aliases":["简体","GB","CHS"],"kind":"builtin"}'),
        ("CHT", "繁体", "cht", 2, '{"aliases":["繁体","繁體","BIG5","CHT"],"kind":"builtin"}'),
        ("CHS&CHT", "简繁", "chs&cht", 3, '{"aliases":["简繁","简繁内封","简繁內封","CHS&CHT"],"kind":"builtin"}'),
    ],
    "title_parser.tag": [
        ("GLOBAL", "B-Global", "B-Global", 1, '{"aliases":["B-GLOBAL","B-Global"],"kind":"builtin"}'),
        ("DUAL_AUDIO", "国粤双语", "国粤双语", 2, '{"aliases":["双语","雙語"],"kind":"builtin"}'),
        ("COLLECTION", "合集", "合集", 3, '{"aliases":["合集","Collection","Complete"],"kind":"builtin"}'),
        ("NC", "NC", "NC", 4, '{"aliases":["NCOP","NCED","NC-OP","NC-ED"],"kind":"builtin"}'),
    ],
    "title_parser.rule": [
        ("is_finale", "完结标记", "true", 1, '{"pattern":"\\\\bEND\\\\b|完结|全集|完結","priority":10,"kind":"builtin"}'),
        ("special_type", "OVA/SP 标记", "OVA", 2, '{"pattern":"\\\\b(OVA|SP)\\\\b","priority":20,"kind":"builtin"}'),
    ],
    "quality": [
        ("8K", "8K超高清", "8K", 1, '{"priority":10,"resolution":"7680x4320","kind":"builtin"}'),
        ("4K", "4K超高清", "4K", 2, '{"priority":9,"resolution":"3840x2160","kind":"builtin"}'),
        ("1080p", "1080p全高清", "1080p", 3, '{"priority":8,"resolution":"1920x1080","kind":"builtin"}'),
        ("720p", "720p高清", "720p", 4, '{"priority":7,"resolution":"1280x720","kind":"builtin"}'),
        ("480p", "480p标清", "480p", 5, '{"priority":6,"resolution":"720x480","kind":"builtin"}'),
    ],
}


def _has_tables(bind, names: Iterable[str]) -> bool:
    inspector = sa.inspect(bind)
    return all(inspector.has_table(name) for name in names)


def _upsert_dict_types(bind, types: list[tuple[str, str, str]]) -> None:
    for code, name, remark in types:
        bind.execute(
            sa.text(
                "INSERT INTO dict_types (code, name, remark, is_active) "
                "SELECT :code, :name, :remark, 1 WHERE NOT EXISTS "
                "(SELECT 1 FROM dict_types WHERE code = :code)"
            ),
            {"code": code, "name": name, "remark": remark},
        )


def _upsert_dict_items(bind, dict_code: str, items: list[tuple[str, str, str, int, str]]) -> None:
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

    _upsert_dict_types(bind, DICT_TYPES)
    for dict_code, items in DICT_ITEMS.items():
        _upsert_dict_items(bind, dict_code, items)


def downgrade() -> None:
    bind = op.get_bind()
    if not _has_tables(bind, ["dict_types", "dict_items"]):
        return
    for dict_code, items in DICT_ITEMS.items():
        for code, _, _, _, _ in items:
            bind.execute(
                sa.text(
                    "DELETE FROM dict_items WHERE dict_type_code = :dict_type_code "
                    "AND code = :code"
                ),
                {"dict_type_code": dict_code, "code": code},
            )
    for code, _, _ in DICT_TYPES:
        bind.execute(sa.text("DELETE FROM dict_types WHERE code = :code"), {"code": code})
