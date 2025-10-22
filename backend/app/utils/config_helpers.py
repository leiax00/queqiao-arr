"""
配置相关的辅助函数
"""

import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud_config
from app.utils.encryption import encryption_manager


def mask_api_key(value: Optional[str]) -> Optional[str]:
    """
    返回长度保持一致的掩码：前后各4位可见，中间以*填充。
    对于长度<=8的短密钥，出于安全考虑全部以*遮蔽。
    
    Examples:
        >>> mask_api_key("12345678")
        "********"
        >>> mask_api_key("1234567890abcdef")
        "1234****cdef"
    """
    if not value:
        return None
    length = len(value)
    if length <= 8:
        return "*" * length
    prefix = value[:4]
    suffix = value[-4:]
    middle_len = length - 8
    return f"{prefix}{'*' * middle_len}{suffix}"


def parse_extra_config(extra_config_str: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    安全地解析 extra_config JSON 字符串
    
    Args:
        extra_config_str: JSON 字符串
        
    Returns:
        解析后的字典，失败返回 None
    """
    if not extra_config_str:
        return None
    try:
        return json.loads(extra_config_str)
    except Exception:
        return None


def encrypt_if_present(value: Optional[str]) -> Optional[str]:
    """
    如果值存在则加密，否则返回 None
    
    Args:
        value: 待加密的字符串
        
    Returns:
        加密后的字符串或 None
    """
    return encryption_manager.encrypt(value) if value else None


def decrypt_if_present(value: Optional[str]) -> Optional[str]:
    """
    如果值存在则解密，否则返回 None
    
    Args:
        value: 待解密的字符串
        
    Returns:
        解密后的字符串或 None
    """
    return encryption_manager.decrypt(value) if value else None


async def get_active_proxy_config(db: AsyncSession) -> Optional[Dict[str, str]]:
    """
    读取启用中的 proxy 类型 ServiceConfig，构造 httpx proxies。
    
    优先使用 extra_config.http / extra_config.https；
    若缺失且 url 为完整代理URL，则回填到 http/https 两个协议。
    若存在 socks5 字段，可同时回填 http/https。
    
    Args:
        db: 数据库会话
        
    Returns:
        httpx proxies 格式的字典，如 {"http://": "...", "https://": "..."}
        若未配置或加载失败则返回 None
    """
    try:
        items = await crud_config.get_service_configs(db, service_name="proxy", is_active=True)
        if not items:
            return None
        svc = items[0]
        proxies: Dict[str, str] = {}
        
        extra = parse_extra_config(getattr(svc, "extra_config", None)) or {}
        
        if extra.get("http"):
            proxies["http://"] = extra["http"]
        if extra.get("https"):
            proxies["https://"] = extra["https"]
        if not proxies and extra.get("socks5"):
            proxies = {"http://": extra["socks5"], "https://": extra["socks5"]}
        if not proxies and getattr(svc, "url", None) and "://" in svc.url:
            proxies = {"http://": svc.url, "https://": svc.url}
        
        return proxies or None
    except Exception:
        return None


def normalize_proxy_dict(proxy: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    规范化代理字典的键格式，确保包含 ://
    
    Args:
        proxy: 原始代理字典，如 {"http": "...", "https": "..."}
        
    Returns:
        规范化后的字典，如 {"http://": "...", "https://": "..."}
    """
    if not proxy:
        return None
    normalized: Dict[str, str] = {}
    for k, v in proxy.items():
        key = k if "://" in k else f"{k}://"
        normalized[key] = v
    return normalized

