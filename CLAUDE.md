# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

---

## ✅ 规则来源（Single Source of Truth）

本项目所有 Agent 规则、能力定义、输出规范、行为边界**全部以 `AGENTS.md` 为唯一准则**。

你必须完整阅读并严格遵循以下文件内容：

@AGENTS.md

---

## ✅ 引用说明

- `CLAUDE.md` 仅作为 Claude Code 的入口文件存在
- 不包含任何业务逻辑或行为规则
- 不应在本文件中添加 Persona、Tool、Output 等内容
- 所有规则修改必须在 `AGENTS.md` 中完成

---

## ✅ 维护约定

当出现以下情况时，你**必须**更新 `AGENTS.md`（而不是本文件）：

- 项目结构发生明显变化
- Agent 可调用能力变更
- 工具（Tool / MCP / API）新增或删除
- Persona / 风格发生改变
- 输出格式或协议调整
- 新增安全或行为限制规则

---

## ✅ 更新规则（重要）

- 不要自动重写 `AGENTS.md`
- 所有规则变更**必须以 diff / patch 形式输出供人工审核**
- 若规则需大规模调整，需明确告知“进行重构”，否则禁止整文件重写

---

## ✅ 附加说明

如本文件与 `AGENTS.md` 内容发生冲突，以 `AGENTS.md` 为最终准则。

---