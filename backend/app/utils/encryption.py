"""
加密解密工具
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import str as String, bytes as Bytes

from app.core.config import settings


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, password: String = None):
        """
        初始化加密管理器
        
        Args:
            password: 加密密码，默认使用配置中的SECRET_KEY
        """
        if password is None:
            password = settings.SECRET_KEY
        
        self._password = password.encode()
        self._salt = b'queqiao-arr-salt'  # 在生产环境中应该使用随机salt
        
    def _get_key(self) -> Bytes:
        """
        生成加密密钥
        
        Returns:
            bytes: 加密密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self._password))
        return key
    
    def encrypt(self, data: String) -> String:
        """
        加密字符串
        
        Args:
            data: 要加密的字符串
            
        Returns:
            str: 加密后的字符串（Base64编码）
        """
        if not data:
            return data
        
        key = self._get_key()
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: String) -> String:
        """
        解密字符串
        
        Args:
            encrypted_data: 加密的字符串（Base64编码）
            
        Returns:
            str: 解密后的字符串
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            key = self._get_key()
            f = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")


# 全局加密管理器实例
encryption_manager = EncryptionManager()
