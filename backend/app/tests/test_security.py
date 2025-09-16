"""
安全模块测试
"""

import pytest
from app.core.security import (
    create_access_token,
    verify_token,
    verify_password,
    get_password_hash,
    generate_secret_key,
)


def test_password_hashing():
    """测试密码哈希"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_token():
    """测试JWT令牌"""
    username = "testuser"
    token = create_access_token(subject=username)
    
    assert token is not None
    assert isinstance(token, str)
    
    # 验证令牌
    decoded_username = verify_token(token)
    assert decoded_username == username


def test_invalid_token():
    """测试无效令牌"""
    invalid_token = "invalid.token.here"
    result = verify_token(invalid_token)
    assert result is None


def test_secret_key_generation():
    """测试密钥生成"""
    key1 = generate_secret_key()
    key2 = generate_secret_key()
    
    assert key1 != key2
    assert len(key1) > 20
    assert len(key2) > 20
