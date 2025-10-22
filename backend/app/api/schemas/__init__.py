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
]

