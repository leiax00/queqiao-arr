---
name: smart-commit
type: workflow
description: 智能检查修改并自动提交（使用中文提交信息）
---

// turbo-all

## 工作流程

当用户请求执行 smart-commit 时，按以下步骤进行：

### 1. 检查变更状态
执行 `git status` 查看是否有未提交的变更。如果没有变更，告知用户并停止。

### 2. 分析变更内容
- 执行 `git diff` 查看详细修改
- 执行 `git log -5 --oneline` 查看最近的提交风格
- 识别变更涉及的模块（backend/frontend/api/docker/docs）

### 3. 代码质量检查
根据变更内容执行相应的检查：
- **Backend**: 如果修改了 `backend/app/**/*.py`，运行代码检查
  - `ruff check backend/app/` 或 `black --check backend/app/`
- **Frontend**: 如果修改了 `frontend/src/**/*.{ts,vue}`，运行类型检查
  - `cd frontend && npm run type-check`

### 4. 运行相关测试（如果需要）
- **Backend**: 如果修改了核心逻辑，运行 `pytest backend/tests/ -v`
- **Frontend**: 当前不要求测试

如果测试/检查失败，**停止提交流程**并告知用户问题。

### 5. 生成中文提交信息
根据 Conventional Commits 规范和项目规范生成提交信息：

**格式**: `<type>(<scope>): <中文描述>`

**类型选择**:
- `feat` - 新功能
- `fix` - Bug 修复
- `refactor` - 代码重构（不改变功能）
- `docs` - 文档更新
- `style` - 代码风格调整（不影响逻辑）
- `test` - 测试相关
- `chore` - 构建/工具/依赖更新
- `opt` - 性能优化
- `improve` - 功能改进或增强

**作用域选择**: `backend` | `frontend` | `api` | `docker` | `docs`

**示例**:
- `feat(parser): 支持解析 8K 分辨率标识`
- `fix(api): 修正认证中间件的 Token 验证逻辑`
- `refactor(backend): 优化数据库连接池配置`

### 6. 执行提交
1. 向用户展示：
   - 变更文件列表
   - 拟定的中文提交信息
2. 等待用户确认（可选，可默认直接提交）
3. 执行：
   ```bash
   git add .
   git commit -m "<拟定的中文提交信息>"
   ```
   **重要**: 不要添加 `Co-Authored-By` 等协作者信息
4. 展示提交结果

### 7. 汇报结果
向用户简洁汇报：
- ✅ 提交成功
- 📝 提交信息
- 📊 变更统计（新增/修改/删除的文件数）