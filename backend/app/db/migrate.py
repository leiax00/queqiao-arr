"""
Alembic 迁移入口，供应用启动时调用。
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config


def _upgrade_head() -> None:
    cfg_path = Path(__file__).resolve().parents[2] / "alembic.ini"
    cfg = Config(str(cfg_path))
    command.upgrade(cfg, "head")


async def run_db_migrations() -> None:
    """
    在异步上下文中运行 Alembic 升级。
    """
    try:
        await asyncio.to_thread(_upgrade_head)
        print("🛠️  数据库迁移完成 (alembic upgrade head)")
    except Exception as exc:
        print(f"⚠️  数据库迁移失败: {exc}")
