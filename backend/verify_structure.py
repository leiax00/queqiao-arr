"""
验证项目结构完整性
"""

import os
from pathlib import Path

def check_file_exists(file_path, description=""):
    """检查文件是否存在"""
    exists = Path(file_path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {file_path} {description}")
    return exists

def check_directory_exists(dir_path, description=""):
    """检查目录是否存在"""
    exists = Path(dir_path).is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {dir_path}/ {description}")
    return exists

print("🔍 验证后端项目结构完整性...\n")

# 检查根目录文件
print("📁 根目录文件:")
root_files = [
    ("requirements.txt", "Python依赖配置"),
    ("pyproject.toml", "项目配置"),
    ("README.md", "项目说明"),
    ("env.example", "环境变量模板"),
    ("test_app.py", "测试脚本"),
]

root_score = 0
for file_path, desc in root_files:
    if check_file_exists(file_path, desc):
        root_score += 1

# 检查目录结构
print("\n📁 目录结构:")
directories = [
    ("app", "应用主目录"),
    ("app/api", "API路由"),
    ("app/api/endpoints", "API端点"),
    ("app/core", "核心模块"),
    ("app/db", "数据库"),
    ("app/models", "数据模型"),
    ("app/utils", "工具函数"),
    ("app/tests", "测试代码"),
    ("alembic", "数据库迁移"),
    ("venv", "虚拟环境"),
]

dir_score = 0
for dir_path, desc in directories:
    if check_directory_exists(dir_path, desc):
        dir_score += 1

# 检查关键Python文件
print("\n🐍 关键Python文件:")
python_files = [
    ("app/__init__.py", "应用包初始化"),
    ("app/main.py", "应用入口"),
    ("app/core/config.py", "配置管理"),
    ("app/core/security.py", "安全工具"),
    ("app/db/database.py", "数据库连接"),
    ("app/models/user.py", "用户模型"),
    ("app/models/config.py", "配置模型"),
    ("app/api/routes.py", "路由汇总"),
    ("app/api/endpoints/health.py", "健康检查端点"),
    ("app/api/endpoints/auth.py", "认证端点"),
    ("app/api/endpoints/config.py", "配置端点"),
    ("app/utils/logger.py", "日志工具"),
    ("app/utils/encryption.py", "加密工具"),
    ("app/tests/test_main.py", "主应用测试"),
    ("app/tests/test_security.py", "安全模块测试"),
    ("app/tests/conftest.py", "测试配置"),
]

py_score = 0
for file_path, desc in python_files:
    if check_file_exists(file_path, desc):
        py_score += 1

# 统计结果
total_files = len(root_files) + len(directories) + len(python_files)
total_score = root_score + dir_score + py_score

print(f"\n📊 结构完整性统计:")
print(f"   根目录文件: {root_score}/{len(root_files)}")
print(f"   目录结构: {dir_score}/{len(directories)}")
print(f"   Python文件: {py_score}/{len(python_files)}")
print(f"   总体完成度: {total_score}/{total_files} ({total_score/total_files*100:.1f}%)")

if total_score == total_files:
    print("\n🎉 项目结构完整！后端FastAPI框架初始化成功！")
else:
    print(f"\n⚠️  还有 {total_files - total_score} 个项目需要完成")

# 检查代码行数
print(f"\n📈 代码统计:")
total_lines = 0
for file_path, _ in python_files:
    if Path(file_path).exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
            total_lines += lines
            
print(f"   Python代码总行数: {total_lines}")
print(f"   平均每个文件: {total_lines/py_score:.1f} 行")
