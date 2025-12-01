"""
API Schemas
"""

from .config import (
    ServiceConfigOut,
    KVConfigOut,
    ServiceConfigCreate,
    KVConfigCreate,
    ServiceConfigUpdate,
    KVConfigUpdate,
    TestConnectionByBody,
    TestConnectionById,
    TestConnectionRequest,
    ProxyTestRequest,
)
from .tmdb import (
    TMDBSearchQuery,
    TMDBSearchResponse,
    TMDBAlternativeTitlesResponse,
    TMDBDetailsResponse,
)
from .prowlarr import (
    ProwlarrSearchQuery,
    ProwlarrSearchResponse,
)

__all__ = [
    "ServiceConfigOut",
    "KVConfigOut",
    "ServiceConfigCreate",
    "KVConfigCreate",
    "ServiceConfigUpdate",
    "KVConfigUpdate",
    "TestConnectionByBody",
    "TestConnectionById",
    "TestConnectionRequest",
    "ProxyTestRequest",
    "TMDBSearchQuery",
    "TMDBSearchResponse",
    "TMDBAlternativeTitlesResponse",
    "TMDBDetailsResponse",
    "ProwlarrSearchQuery",
    "ProwlarrSearchResponse",
]
