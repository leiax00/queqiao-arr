# B-11: 系统字典管理 API 开发任务说明书

## 一、任务基本信息

- 任务ID: B-11
- 任务名称: 系统字典管理API（字典类型与字典项的增删改查、统一选项查询）
- 复杂度: S（约 2 PD）
- 优先级: P1
- 依赖任务: B-01（认证与鉴权基础能力）
- 关联前端: FE-07（系统字典管理页面）

---

## 二、目标与范围（Scope）

### 2.1 目标
- 提供系统字典类型（Dict Type）与字典项（Dict Item）的标准化 CRUD 接口。
- 支持字典项的层级关系（预留父子关系字段，V1 可选实现）。
- 提供统一的选项查询接口，供前端下拉列表与后端数据校验复用（如语言/地区/质量等）。
- 支持字典项的排序、启用/禁用状态管理。
- 统一响应结构，便于前端拦截器与文档对齐。

### 2.2 范围
- API 前缀: `/api/v1/dict/*`
- 数据模型: 
  - `DictType`（字典类型表）：`id`, `code`（唯一编码）, `name`（显示名称）, `remark`（备注说明）, `is_active`, `created_at`, `updated_at`
  - `DictItem`（字典项表）：`id`, `dict_type_code`（外键关联类型）, `code`（项编码）, `name`（显示名称）, `value`（实际值）, `sort_order`（排序）, `parent_id`（父项ID，预留层级）, `remark`（备注说明）, `is_active`, `extra_data`（JSON扩展字段）, `created_at`, `updated_at`
- 响应封装: `backend/app/utils/response.py`（`success_response` / `error_response`）

非范围（后续迭代）:
- 字典项的多语言支持、版本审计、导入导出、批量操作

---

## 三、业务规则（Business Rules）

1. 字典类型（DictType）：
   - `code` 为唯一标识（如 `language`, `region`, `quality`），不可重复。
   - `name` 为显示名称（如"语言选项"、"地区选项"、"质量标签"）。
   - `remark` 为备注说明，用于记录该字典类型的用途、使用场景、注意事项等。
   - `is_active` 控制该类型是否启用；禁用后前端不展示相关选项。

2. 字典项（DictItem）：
   - `dict_type_code` 关联到字典类型，删除类型时需考虑级联策略（建议级联删除或软删除）。
   - `code` 在同一字典类型下唯一（联合唯一约束：`dict_type_code + code`）。
   - `value` 为实际使用的值（如 `zh-CN`, `en-US`）。
   - `sort_order` 控制前端展示顺序（数值越小越靠前）。
   - `parent_id` 预留层级关系（如地区可按洲/国家/城市层级组织），V1 可为 `null`。
   - `remark` 为备注说明，用于记录该选项的使用场景、注意事项等。
   - `extra_data` 为 JSON 字段，存储扩展属性（如图标、颜色、标签等）。

3. 唯一性与状态：
   - 字典类型 `code` 全局唯一。
   - 字典项 `code` 在同一类型下唯一。
   - `is_active` 控制启用状态，禁用后前端不返回该选项。

4. 鉴权：
   - 查询接口（GET `/dict/types`, GET `/dict/items`）允许登录用户访问。
   - 写操作（POST/PUT/DELETE）限定为管理员（`is_superuser=true`）。

5. 统一响应：
   - 成功：`{ code: 200, message: "OK", data: {...} }`
   - 失败：`{ code: <业务码>, message: <错误描述>, data: <可选> }`

---

## 四、API 设计（OpenAPI 概览）

说明：以下均为包裹在统一响应结构下的 `data` 字段示例。

### 4.1 字典类型管理

#### 4.1.1 GET `/api/v1/dict/types`
- 用途：获取字典类型列表。
- 查询参数：
  - `is_active`（可选，布尔）：仅返回启用的类型。
  - `page`（可选，整数，默认1）：分页页码。
  - `page_size`（可选，整数，默认20）：每页条数。
- 响应示例：
```json
{
  "items": [
    {
      "id": 1,
      "code": "language",
      "name": "语言选项",
      "remark": "系统支持的语言列表，用于TMDB API查询、前端界面显示等场景",
      "is_active": true,
      "created_at": "2025-10-19T10:00:00Z",
      "updated_at": "2025-10-19T10:00:00Z"
    },
    {
      "id": 2,
      "code": "region",
      "name": "地区选项",
      "remark": "内容地区分类，用于TMDB地区筛选，影响搜索结果和内容推荐",
      "is_active": true,
      "created_at": "2025-10-19T10:00:00Z",
      "updated_at": "2025-10-19T10:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

#### 4.1.2 POST `/api/v1/dict/types`
- 用途：创建字典类型。
- 鉴权：仅管理员。
- 请求体：
```json
{
  "code": "quality",
  "name": "质量标签",
  "remark": "视频质量分类（如1080p, 4K等），用于资源标题解析和质量筛选，优先级：4K > 1080p > 720p",
  "is_active": true
}
```
- 成功：返回创建的类型对象。

#### 4.1.3 PUT `/api/v1/dict/types/{type_id}`
- 用途：更新字典类型。
- 鉴权：仅管理员。
- 规则：不允许修改 `code`（唯一标识）。
- 成功：返回更新后的类型对象。

#### 4.1.4 DELETE `/api/v1/dict/types/{type_id}`
- 用途：删除字典类型。
- 鉴权：仅管理员。
- 规则：级联删除该类型下所有字典项（建议前端二次确认）。
- 成功：`{ deleted: true }`。

### 4.2 字典项管理

#### 4.2.1 GET `/api/v1/dict/items`
- 用途：获取字典项列表。
- 查询参数：
  - `dict_type_code`（必填，字符串）：字典类型编码。
  - `is_active`（可选，布尔）：仅返回启用的项。
  - `parent_id`（可选，整数）：按父项筛选（层级查询）。
  - `page`（可选，整数，默认1）：分页页码。
  - `page_size`（可选，整数，默认50）：每页条数。
- 响应示例：
```json
{
  "items": [
    {
      "id": 1,
      "dict_type_code": "language",
      "code": "zh-CN",
      "name": "简体中文",
      "value": "zh-CN",
      "sort_order": 1,
      "parent_id": null,
      "remark": "中国大陆使用的简体中文，TMDB语言代码",
      "is_active": true,
      "extra_data": { "icon": "🇨🇳" },
      "created_at": "2025-10-19T10:00:00Z",
      "updated_at": "2025-10-19T10:00:00Z"
    },
    {
      "id": 2,
      "dict_type_code": "language",
      "code": "en-US",
      "name": "English (US)",
      "value": "en-US",
      "sort_order": 2,
      "parent_id": null,
      "remark": "美式英语，用于英文资源标题匹配",
      "is_active": true,
      "extra_data": { "icon": "🇺🇸" },
      "created_at": "2025-10-19T10:00:00Z",
      "updated_at": "2025-10-19T10:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 50
}
```

#### 4.2.2 GET `/api/v1/dict/items/{item_id}`
- 用途：获取单个字典项详情。
- 成功：返回字典项对象。

#### 4.2.3 POST `/api/v1/dict/items`
- 用途：创建字典项。
- 鉴权：仅管理员。
- 请求体：
```json
{
  "dict_type_code": "language",
  "code": "ja-JP",
  "name": "日本語",
  "value": "ja-JP",
  "sort_order": 3,
  "parent_id": null,
  "remark": "日本语言选项，用于日语内容匹配",
  "is_active": true,
  "extra_data": { "icon": "🇯🇵" }
}
```
- 成功：返回创建的字典项对象。

#### 4.2.4 PUT `/api/v1/dict/items/{item_id}`
- 用途：更新字典项。
- 鉴权：仅管理员。
- 规则：不允许修改 `dict_type_code` 与 `code`（唯一标识）。
- 成功：返回更新后的字典项对象。

#### 4.2.5 DELETE `/api/v1/dict/items/{item_id}`
- 用途：删除字典项。
- 鉴权：仅管理员。
- 规则：若有子项，需级联删除或拒绝删除（建议前端二次确认）。
- 成功：`{ deleted: true }`。

### 4.3 统一选项查询接口

#### 4.3.1 GET `/api/v1/dict/options/{dict_type_code}`
- 用途：获取指定字典类型的所有启用选项（用于前端下拉列表）。
- 查询参数：
  - `parent_id`（可选，整数）：按父项筛选（层级查询）。
- 响应示例：
```json
{
  "dict_type": {
    "code": "language",
    "name": "语言选项"
  },
  "options": [
    {
      "code": "zh-CN",
      "name": "简体中文",
      "value": "zh-CN",
      "extra_data": { "icon": "🇨🇳" }
    },
    {
      "code": "en-US",
      "name": "English (US)",
      "value": "en-US",
      "extra_data": { "icon": "🇺🇸" }
    }
  ]
}
```
- 说明：
  - 仅返回 `is_active=true` 的类型与项。
  - 按 `sort_order` 升序排列。
  - 简化字段，仅返回前端必要信息。

---

## 五、数据模型（Schema 定义）

### 5.1 字典类型（DictType）
```python
class DictType(Base):
    __tablename__ = "dict_types"
    
    id: int = Column(Integer, primary_key=True, index=True)
    code: str = Column(String(50), unique=True, nullable=False, index=True, comment="类型编码（唯一）")
    name: str = Column(String(100), nullable=False, comment="类型名称")
    remark: str = Column(Text, nullable=True, comment="备注说明")
    is_active: bool = Column(Boolean, default=True, comment="是否启用")
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 5.2 字典项（DictItem）
```python
class DictItem(Base):
    __tablename__ = "dict_items"
    
    id: int = Column(Integer, primary_key=True, index=True)
    dict_type_code: str = Column(String(50), ForeignKey("dict_types.code", ondelete="CASCADE"), nullable=False, index=True, comment="字典类型编码")
    code: str = Column(String(50), nullable=False, index=True, comment="项编码")
    name: str = Column(String(100), nullable=False, comment="显示名称")
    value: str = Column(String(200), nullable=False, comment="实际值")
    sort_order: int = Column(Integer, default=0, comment="排序（升序）")
    parent_id: int = Column(Integer, ForeignKey("dict_items.id", ondelete="CASCADE"), nullable=True, comment="父项ID（层级）")
    remark: str = Column(Text, nullable=True, comment="备注说明")
    is_active: bool = Column(Boolean, default=True, comment="是否启用")
    extra_data: str = Column(Text, nullable=True, comment="扩展数据（JSON）")
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('dict_type_code', 'code', name='uq_dict_item_type_code'),
    )
```

### 5.3 Pydantic 请求/响应模型
- `DictTypeCreate`, `DictTypeUpdate`, `DictTypeOut`
- `DictItemCreate`, `DictItemUpdate`, `DictItemOut`
- `DictOptionOut`（简化选项模型，用于 `/options` 接口）

---

## 六、错误码与消息
- 200：成功
- 400：参数不合法（缺少必填/格式错误）
- 401：未认证
- 403：禁止访问（仅管理员可写）
- 404：字典类型或字典项不存在
- 409：编码冲突（`code` 重复）
- 500：服务器内部错误

---

## 七、实现计划（Tasks）

1. **数据模型与迁移**：
   - 创建 `DictType` 与 `DictItem` 模型（`backend/app/models/dict.py`）。
   - 编写 Alembic 迁移脚本，创建表与索引。

2. **CRUD 操作层**：
   - 创建 `backend/app/db/crud_dict.py`，实现字典类型与字典项的 CRUD 方法。
   - 支持分页、筛选、排序。

3. **API 端点**：
   - 创建 `backend/app/api/endpoints/dict.py`，实现所有接口。
   - 接入统一响应封装（`success_response` / `error_response`）。
   - 鉴权装饰器：查询接口 `get_current_user`，写接口 `get_current_superuser`。

4. **路由注册**：
   - 在 `backend/app/api/routes.py` 中注册 `dict` 路由（前缀 `/api/v1/dict`）。

5. **Swagger 文档**：
   - 为所有接口添加 OpenAPI 注释与示例。
   - 标签：`字典管理`。

6. **单元测试**：
   - 编写 `backend/tests/test_dict.py`，覆盖 CRUD 与选项查询的成功/失败路径。

7. **初始化数据（可选）**：
   - 提供脚本或迁移后钩子，初始化常用字典类型与选项（如语言、地区）。

---

## 八、关键测试用例（示例）

### 字典类型
- 创建类型成功：`code` 唯一，返回完整对象。
- 创建重复类型：同 `code` 冲突 → 409。
- 更新类型成功：允许修改 `name`、`remark`、`is_active`。
- 删除类型成功：级联删除所有字典项。

### 字典项
- 创建字典项成功：`dict_type_code + code` 唯一，返回完整对象。
- 创建重复项：同类型下 `code` 冲突 → 409。
- 更新字典项成功：允许修改 `name`、`value`、`sort_order`、`remark`、`is_active`、`extra_data`。
- 删除字典项成功：若有子项，级联删除或拒绝（根据实现选择）。

### 选项查询
- 查询启用选项：仅返回 `is_active=true` 的项，按 `sort_order` 排序。
- 查询不存在的类型：404。
- 按 `parent_id` 筛选：返回指定层级的子项。

---

## 九、验收标准（Acceptance Criteria）

1. `/api/v1/dict/*` 提供完整的字典类型与字典项 CRUD 接口，统一响应结构与错误码对齐。
2. `/api/v1/dict/options/{dict_type_code}` 接口可供前端快速查询下拉选项，响应轻量。
3. 写操作限定为管理员，查询接口允许登录用户访问。
4. 数据库表结构合理，支持层级关系（`parent_id`）与扩展字段（`extra_data`）。
5. Swagger 文档完整，前端可据此对接；最小测试覆盖通过关键正反场景。

---

## 十、进度清单（Checklist）

- [x] 任务说明文档（本文件）
- [x] 数据模型定义（`models/dict.py`）
- [x] 数据表创建（项目使用 `create_tables` 自动创建）
- [x] CRUD 操作层（`db/crud_dict.py`）
- [x] Pydantic Schema 定义（`api/schemas/dict.py`）
- [x] API 端点实现（`api/endpoints/dict.py`）
- [x] 路由注册（`api/routes.py`）
- [x] Swagger 注释完善
- [x] 初始化数据脚本（改为 Alembic 数据迁移：`alembic/versions/*seed*_dicts.py`）
- [ ] 单元测试（`tests/test_dict.py`）
- [x] 与前端 FE-07 联调通过 ✅ **2025-10-22 完成**

---

## 十一、风险与对策

- **级联删除风险**：删除字典类型或父项时需谨慎，建议前端二次确认；后端提供级联删除或软删除选项。
- **编码冲突**：严格校验 `code` 唯一性，避免数据重复。
- **扩展性**：`extra_data` 为 JSON 字段，支持灵活扩展；`parent_id` 预留层级关系，V1 可为 `null`。

---

## 十二、与现有代码的契合点

- 统一响应封装：`backend/app/utils/response.py`。
- 鉴权依赖：`backend/app/api/dependencies.py`（`get_current_user`, `get_current_superuser`）。
- 数据库会话：`backend/app/db/database.py`（`get_db`）。
- 路由注册：`backend/app/api/routes.py`。

---

## 十三、后续扩展方向

- 多语言支持：为字典项增加多语言字段（`locale`）。
- 批量操作：支持批量导入/导出字典数据（CSV/JSON）。
- 版本审计：记录字典项的变更历史。
- 软删除：增加 `deleted_at` 字段，支持逻辑删除与恢复。

---

## 十四、参考与附件

- 统一响应工具：`backend/app/utils/response.py`
- 鉴权依赖：`backend/app/core/security.py` 与 `backend/app/api/dependencies.py`
- 数据库模型参考：`backend/app/models/config.py`、`backend/app/models/user.py`
