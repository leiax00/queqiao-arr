# Queqiao-arr Backend

中文内容自动化下载代理服务后端

## 快速开始

### 1. 环境准备

确保已安装Python 3.11+：

```bash
python --version
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 环境配置

复制环境变量模板：

```bash
cp backend/.env.example backend/.env
```

编辑`.env`文件，配置必要的环境变量。

### 5. 运行应用

开发模式：

```bash
python -m app.main
```

或使用uvicorn：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问应用

- 应用首页: http://localhost:8000
- API文档: http://localhost:8000/api/docs
- 健康检查: http://localhost:8000/api/v1/health

## 开发指南

### 代码质量检查

运行代码格式化：

```bash
black app/
```

运行代码检查：

```bash
ruff check app/
```

运行类型检查：

```bash
mypy app/
```

### 运行测试

```bash
pytest
```

带覆盖率报告：

```bash
pytest --cov=app --cov-report=html
```

## 项目结构

```
backend/
├── app/                    # 应用主代码
│   ├── __init__.py
│   ├── main.py            # 应用入口
│   ├── api/               # API路由
│   │   ├── routes.py      # 路由汇总
│   │   └── endpoints/     # 具体端点
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   └── security.py    # 安全工具
│   ├── db/                # 数据库相关
│   │   └── database.py    # 数据库连接
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   └── config.py      # 配置模型
│   ├── utils/             # 工具函数
│   │   ├── logger.py      # 日志配置
│   │   └── encryption.py  # 加密工具
│   └── tests/             # 测试代码（当前仓库未保留）
├── requirements.txt       # 依赖包
├── pyproject.toml        # 项目配置（当前仓库未保留）
└── README.md             # 说明文档
```

## API文档

启动应用后，访问 http://localhost:8000/api/docs 查看完整的API文档。

## 环境变量说明

详见`.env.example`文件中的注释。

## 许可证

[待定]
