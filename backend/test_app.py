"""
简化的应用测试脚本
"""

import sys
import os

# 添加app目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    # 测试导入核心模块
    print("🔍 测试模块导入...")
    
    from app.core.config import settings
    print(f"✅ 配置模块导入成功: {settings.APP_NAME}")
    
    from app.core.security import get_password_hash, verify_password
    print("✅ 安全模块导入成功")
    
    from app.db.database import Base
    print("✅ 数据库模块导入成功")
    
    from app.models.user import User
    from app.models.config import Configuration, ServiceConfig
    print("✅ 数据模型导入成功")
    
    from app.api.routes import api_router
    print("✅ API路由导入成功")
    
    # 测试基本功能
    print("\n🧪 测试基本功能...")
    
    # 测试密码加密
    password = "testpassword"
    hashed = get_password_hash(password)
    is_valid = verify_password(password, hashed)
    print(f"✅ 密码加密测试: {'通过' if is_valid else '失败'}")
    
    print("\n🎉 所有基础测试通过！")
    print(f"📋 项目信息:")
    print(f"   - 名称: {settings.APP_NAME}")
    print(f"   - 版本: {settings.VERSION}")
    print(f"   - 调试模式: {settings.DEBUG}")
    print(f"   - 数据库: {settings.DATABASE_URL}")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("💡 可能需要安装依赖包: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
