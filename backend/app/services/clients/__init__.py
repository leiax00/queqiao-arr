"""
外部服务客户端层
提供对 Sonarr、Prowlarr、TMDB 等外部服务的统一访问接口
"""

from .base import ExternalServiceClient
from .sonarr import SonarrClient
from .prowlarr import ProwlarrClient
from .tmdb import TMDBClient
from .factory import make_client

__all__ = [
    "ExternalServiceClient",
    "SonarrClient",
    "ProwlarrClient",
    "TMDBClient",
    "make_client",
]

