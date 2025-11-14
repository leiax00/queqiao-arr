"""
Queqiao-arr FastAPI应用入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from app.core.config import settings
from app.api.routes import api_router
from app.db.database import create_tables, AsyncSessionLocal
from app.db.init_dict_data import init_dict_data
from app.services.clients.base import close_all_shared_clients


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    print(f"🚀 启动 {settings.APP_NAME} v{settings.VERSION}")

    # 创建必要的目录
    os.makedirs("runtime/logs", exist_ok=True)
    os.makedirs("runtime/data", exist_ok=True)
    print("📁 目录结构创建完成")
    
    # 创建数据库表
    await create_tables()
    print("📊 数据库表创建完成")
    
    # 初始化字典数据
    async with AsyncSessionLocal() as session:
        try:
            await init_dict_data(session)
        except Exception as e:
            print(f"⚠️  字典数据初始化失败: {e}")
    
    yield
    
    # 关闭时执行
    print("👋 应用正在关闭...")
    # 关闭共享 httpx 客户端池
    try:
        close_all_shared_clients()
        print("🔌 共享HTTP客户端已关闭")
    except Exception as e:
        print(f"⚠️  关闭共享HTTP客户端失败: {e}")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="中文内容自动化下载代理服务",
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# 静态文件服务（用于服务前端构建文件）
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    @app.get("/")
    async def read_index():
        """服务前端应用的根路由"""
        return FileResponse("static/index.html")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        SPA路由处理 - 对于前端路由，返回index.html
        
        Args:
            full_path: 完整路径
            
        Returns:
            FileResponse: 静态文件响应
        """
        # 如果请求的是静态资源文件，直接返回
        static_file = static_dir / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(static_file)
        
        # 否则返回index.html让前端路由处理
        return FileResponse("static/index.html")
else:
    @app.get("/")
    async def root():
        """根路由 - 开发环境下的欢迎页面"""
        return {
            "message": f"欢迎使用 {settings.APP_NAME}",
            "version": settings.VERSION,
            "docs": "/api/docs",
            "health": "/api/v1/health"
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
