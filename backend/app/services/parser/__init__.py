"""
标题解析服务对外暴露的便捷导入。
"""

from .models import ParsedTitle, TMDBAltTitle, TMDBSearchCandidate, ParseRule, ParserConfig
from .title_parser import async_parse_title, parse_title
from .config_loader import load_parser_config

__all__ = [
    "ParsedTitle",
    "TMDBAltTitle",
    "TMDBSearchCandidate",
    "ParseRule",
    "ParserConfig",
    "load_parser_config",
    "parse_title",
    "async_parse_title",
]
