# F-01 项目基础结构开发任务说明书

## 任务概述
- **任务ID**: F-01
- **任务名称**: 初始化项目结构（后端FastAPI + 前端Vue）
- **复杂度**: S (简单)
- **估算工时**: 2人日
- **关联里程碑**: 基础架构与配置闭环

## 后端FastAPI详细设置步骤

### 1. 项目初始化
```bash
# 创建后端项目目录
mkdir queqiao-backend
cd queqiao-backend

# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# 初始化项目依赖
pip install fastapi uvicorn[standard]
```

### 2. 项目结构创建
```bash
queqiao-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI应用入口
│   ├── api/             # API路由模块
│   │   ├── __init__.py
│   │   ├── v1/          # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py  # 认证相关接口
│   │   │   └── config.py # 配置相关接口
│   ├── core/            # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── config.py    # 配置管理
│   │   └── security.py  # 安全相关
│   ├── models/          # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py      # 用户模型
│   │   └── config.py    # 配置模型
│   ├── schemas/         # Pydantic模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── config.py
│   └── utils/           # 工具函数
│       ├── __init__.py
│       └── crypto.py    # 加密工具
├── tests/               # 测试文件
│   ├── __init__.py
│   ├── test_api.py
│   └── test_core.py
├── requirements.txt     # 生产环境依赖
├── requirements-dev.txt # 开发环境依赖
└── .env.example        # 环境变量示例
```

### 3. 基础配置
创建 `app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Queqiao-arr Backend",
    description="国漫自动化搜索增强后端API",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Queqiao-arr Backend API"}
```

## 前端Vue详细设置步骤

### 1. 项目初始化
```bash
# 使用Vite创建Vue 3 + TypeScript项目
npm create vite@latest queqiao-frontend -- --template vue-ts
cd queqiao-frontend

# 安装依赖
npm install

# 安装Element Plus UI库
npm install element-plus
npm install -D unplugin-vue-components unplugin-auto-import

# 安装路由
npm install vue-router@4

# 安装HTTP客户端
npm install axios
```

### 2. 项目结构创建
```bash
queqiao-frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 通用组件
│   │   ├── common/      # 公共组件
│   │   └── layout/      # 布局组件
│   ├── views/           # 页面组件
│   │   ├── Login.vue    # 登录页面
│   │   ├── Register.vue # 注册页面
│   │   ├── Settings.vue # 设置页面
│   │   └── Dashboard.vue # 仪表板
│   ├── router/          # 路由配置
│   │   └── index.ts
│   ├── stores/          # 状态管理
│   │   ├── index.ts
│   │   ├── auth.ts      # 认证状态
│   │   └── config.ts    # 配置状态
│   ├── services/        # API服务
│   │   ├── api.ts       # API基础配置
│   │   ├── auth.ts      # 认证API
│   │   └── config.ts    # 配置API
│   ├── types/           # TypeScript类型定义
│   │   ├── index.ts
│   │   ├── auth.ts
│   │   └── config.ts
│   ├── utils/           # 工具函数
│   │   ├── index.ts
│   │   └── request.ts   # 请求封装
│   ├── App.vue
│   ├── main.ts
│   └── env.d.ts
├── public/              # 公共文件
├── index.html
├── vite.config.ts       # Vite配置
├── tsconfig.json        # TypeScript配置
├── package.json
└── .env.example         # 环境变量示例
```

### 3. 基础配置
创建 `vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

## 代码结构要求

### 后端代码规范
1. **Python代码风格**: 遵循PEP 8规范
2. **类型注解**: 全面使用Type Hint
3. **模块划分**: 按功能模块划分目录结构
4. **错误处理**: 统一的异常处理机制
5. **日志记录**: 使用Python logging模块
6. **配置管理**: 环境变量 + 配置文件

### 前端代码规范
1. **代码风格**: 使用ESLint + Prettier
2. **类型安全**: 全面使用TypeScript
3. **组件规范**: 单文件组件，明确props定义
4. **状态管理**: 使用Pinia进行状态管理
5. **API调用**: 统一的请求拦截和错误处理
6. **响应式设计**: 支持移动端和桌面端

## 必须安装的依赖项

### 后端依赖 (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
```

### 后端开发依赖 (requirements-dev.txt)
```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.11.0
isort==5.12.0
mypy==1.7.0
```

### 前端依赖 (package.json)
```json
{
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.6",
    "axios": "^1.5.0",
    "element-plus": "^2.4.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.3.4",
    "typescript": "^5.2.2",
    "vite": "^4.4.5",
    "vue-tsc": "^1.8.5",
    "eslint": "^8.45.0",
    "prettier": "^3.0.0"
  }
}
```

## Git初始化规范

### 1. 仓库初始化
```bash
# 在项目根目录初始化Git仓库
git init

# 添加.gitignore文件
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Vue
/dist
/.vite

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

### 2. 提交规范
- **初始提交**: 项目基础结构
- **提交消息格式**: 
  - feat: 新功能
  - fix: 修复bug  
  - docs: 文档更新
  - style: 代码格式调整
  - refactor: 代码重构
  - test: 测试相关
  - chore: 构建过程或辅助工具变动

### 3. 分支策略
- **main**: 主分支，保护分支
- **develop**: 开发分支
- **feature/**: 功能开发分支
- **hotfix/**: 紧急修复分支

### 4. 首次提交
```bash
# 添加所有文件
git add .

# 初始提交
git commit -m "feat: 初始化项目基础结构 - F-01"

# 创建develop分支
git checkout -b develop
```

## 验证步骤

### 后端验证
```bash
# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 测试API访问
curl http://localhost:8000/
```

### 前端验证
```bash
# 启动开发服务器
npm run dev

# 访问应用
# 打开 http://localhost:3000
```

## 后续任务衔接
- **F-02**: Docker环境配置
- **F-03**: CI/CD流水线配置
- **B-01**: 用户认证模块开发
- **FE-01**: Vue项目完善

---
**最后更新**: 2025-09-15
**负责人**: [填写负责人姓名]