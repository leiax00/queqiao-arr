<template>
  <div class="dict-item-table">
    <!-- 标题与操作栏 -->
    <div class="header">
      <h3 class="title">
        字典项管理
        <span v-if="currentType" class="type-tag">{{ currentType.name }}</span>
      </h3>
      <div class="actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索编码或名称"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
          @input="handleSearch"
        />
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option label="全部" :value="null" />
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
        <el-button
          type="primary"
          :icon="Plus"
          :disabled="!currentType"
          @click="handleCreate"
        >
          新增字典项
        </el-button>
      </div>
    </div>

    <!-- 未选中类型提示 -->
    <el-empty
      v-if="!currentType"
      description="请在左侧选择字典类型"
      :image-size="120"
    />

    <!-- 数据表格 -->
    <div v-else class="table-container">
      <el-table
        v-loading="loading"
        :data="itemList"
        border
        style="width: 100%"
      >
        <el-table-column prop="code" label="编码" width="150" fixed>
          <template #default="{ row }">
            <code class="item-code">{{ row.code }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" width="180" show-overflow-tooltip />
        <el-table-column prop="value" label="值" width="160" show-overflow-tooltip />
        <el-table-column
          prop="sort_order"
          label="排序"
          width="70"
          align="center"
        />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="extra_data" label="扩展数据" min-width="110" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.extra_data" class="extra-data">
              <!-- 如果内容简短，直接显示 -->
              <div class="extra-display">
                {{ formatExtraData(row.extra_data) }}
              </div>
            </div>
            <span v-else class="text-secondary">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="165" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              text
              type="primary"
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              text
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 字典项表单对话框 -->
    <DictItemForm
      v-model:visible="formVisible"
      :item-data="currentItem"
      :type-code="currentType?.code"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getDictItems, deleteDictItem } from '@/api/dict'
import type { DictType, DictItem, DictItemListResponse } from '@/api/types'
import DictItemForm from './DictItemForm.vue'

// Props
const props = defineProps<{
  currentType: DictType | null
}>()

// State
const loading = ref(false)
const itemList = ref<DictItem[]>([])
const searchQuery = ref('')
const statusFilter = ref<boolean | null>(null)
const formVisible = ref(false)
const currentItem = ref<DictItem | null>(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

// Methods
const loadItems = async () => {
  if (!props.currentType) {
    itemList.value = []
    return
  }

  loading.value = true
  try {
    const res: DictItemListResponse = await getDictItems({
      dict_type_code: props.currentType.code,
      is_active: statusFilter.value ?? undefined,
      page: pagination.page,
      page_size: pagination.pageSize,
    })
    
    // 前端搜索过滤（如果后端不支持 q 参数）
    let items = res.items
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      items = items.filter(
        (item) =>
          item.code.toLowerCase().includes(query) ||
          item.name.toLowerCase().includes(query)
      )
    }
    
    itemList.value = items
    pagination.total = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载字典项失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadItems()
}

const handlePageChange = () => {
  loadItems()
}

const handleCreate = () => {
  currentItem.value = null
  formVisible.value = true
}

const handleEdit = (item: DictItem) => {
  currentItem.value = item
  formVisible.value = true
}

const handleDelete = async (item: DictItem) => {
  try {
    await ElMessageBox.confirm(
      '是否确认删除该字典项？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteDictItem(item.id)
    ElMessage.success('删除成功')
    await loadItems()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleFormSuccess = async () => {
  await loadItems()
}

const formatExtraData = (data: any): string => {
  if (!data) return '—'
  
  // 如果是字符串类型的 JSON，先解析
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data)
    } catch {
      return data
    }
  }
  
  // 如果是对象
  if (typeof data === 'object' && data !== null) {
    // 显示主要字段的组合
    const keys = Object.keys(data)
    if (keys.length === 0) return '{}'
    
    // 如果只有1-2个字段，尝试友好展示
    if (keys.length <= 2) {
      const parts = keys.map(key => {
        const value = data[key]
        return `${key}: ${value}`
      })
      return parts.join(', ')
    }
    
    // 多个字段，显示 JSON 字符串
    return JSON.stringify(data)
  }
  
  // 其他类型直接转字符串
  return String(data)
}

// Watch
watch(
  () => props.currentType,
  () => {
    pagination.page = 1
    searchQuery.value = ''
    statusFilter.value = null
    loadItems()
  }
)
</script>

<style scoped lang="scss">
.dict-item-table {
  @apply macaron-card;
  @apply flex flex-col h-full p-4;
  width: 100%; // 确保卡片填满容器
  box-sizing: border-box; // 包含 padding 在宽度内
  
  // 移除卡片悬停浮动效果，避免表格闪动
  &:hover {
    @apply shadow-soft transform-none;
  }

  .header {
    @apply flex justify-between items-center mb-4;

    .title {
      @apply m-0 text-base font-semibold flex items-center gap-3;
      @apply text-gray-900 dark:text-white;

      .type-tag {
        @apply text-sm font-normal px-3 py-0.5 rounded;
        @apply text-primary-600 dark:text-primary-400;
        @apply bg-primary-50 dark:bg-primary-900/30;
      }
    }

    .actions {
      @apply flex gap-2;
    }
  }

  .table-container {
    @apply flex-1 flex flex-col;
    overflow-x: auto; // 表格横向滚动
    overflow-y: hidden;
    width: 100%; // 确保容器宽度正确
    
    :deep(.el-table) {
      width: 100% !important; // 强制表格使用容器宽度
    }

    .item-code {
      @apply font-mono text-xs px-1.5 py-1.5 rounded;
      @apply text-primary-600 dark:text-primary-400;
      @apply bg-primary-50 dark:bg-primary-900/30;
    }

    .extra-data {
      .extra-display {
        @apply text-sm;
        @apply text-gray-700 dark:text-gray-300;
      }
    }

    .text-secondary {
      @apply text-gray-500 dark:text-gray-400;
    }

    // Element Plus 表格样式优化 - 参考 F-01 主题配色方案
    :deep(.el-table) {
      @apply bg-transparent;
      
      // 自定义边框颜色变量 - 统一边框颜色
      --el-table-border-color: #e2e8f0 !important; // 浅色主题边框
      
      // 暗色模式下的边框颜色
      .dark & {
        --el-table-border-color: #334155 !important;
      }

      // 表头样式 - 使用卡片背景色
      th.el-table__cell {
        @apply bg-light-card dark:bg-dark-card;
        @apply text-light-text dark:text-dark-text;
        @apply font-semibold text-sm;
        border-bottom: 2px solid #0ea5e9 !important; // 主色调分隔线
        
        .dark & {
          border-bottom-color: #0284c7 !important;
        }
      }

      // 数据单元格样式 - 保持边框一致性
      td.el-table__cell {
        @apply bg-white dark:bg-dark-bg;
        @apply text-light-text dark:text-dark-text;
        @apply text-sm;
        border-color: var(--el-table-border-color) !important;
      }

      // 行样式 - 悬停时只改变背景色，不影响边框
      .el-table__row {
        @apply transition-colors duration-150;

        &:hover > td {
          @apply bg-light-card dark:bg-dark-card;
          border-color: var(--el-table-border-color) !important;
        }
      }

      // 空状态文本
      .el-table__empty-text {
        @apply text-light-text-secondary dark:text-dark-text-secondary;
      }
    }
  }

  .pagination {
    @apply flex justify-end mt-4 pt-4;
    @apply border-t border-gray-200 dark:border-gray-700;

    // Element Plus 分页组件样式优化 - 使用 F-01 配色方案
    :deep(.el-pagination) {
      // 按钮样式
      .btn-prev,
      .btn-next,
      .el-pager li {
        @apply bg-white dark:bg-dark-card;
        @apply text-light-text dark:text-dark-text;
        @apply border border-light-border dark:border-dark-border;
        
        &:hover:not(.is-disabled) {
          @apply text-primary-600 dark:text-primary-400;
        }
        
        &.is-active {
          @apply bg-primary-500 dark:bg-primary-600;
          @apply text-white;
          @apply border-primary-500 dark:border-primary-600;
        }
      }
      
      // 输入框样式
      .el-input__wrapper {
        @apply bg-white dark:bg-dark-card;
        @apply border-light-border dark:border-dark-border;
        box-shadow: none !important;
        
        &:hover,
        &.is-focus {
          @apply border-primary-500 dark:border-primary-400;
        }
        
        .el-input__inner {
          @apply text-light-text dark:text-dark-text;
          @apply bg-transparent;
        }
      }
      
      // 选择器样式
      .el-select .el-input__wrapper {
        @apply bg-white dark:bg-dark-card;
      }
      
      // 文本样式
      .el-pagination__total,
      .el-pagination__jump {
        @apply text-light-text-secondary dark:text-dark-text-secondary;
      }
    }
  }

  // Element Plus 按钮样式优化 - 统一按钮风格
  :deep(.el-button) {
    // text 类型按钮样式
    &.is-text {
      @apply font-medium;
      
      &:not(.is-disabled) {
        &:hover {
          @apply bg-light-card dark:bg-dark-card;
        }
        
        &:active {
          opacity: 0.8;
        }
      }
      
      // primary 文本按钮
      &.el-button--primary {
        color: #0ea5e9;
        
        .dark & {
          color: #38bdf8;
        }
        
        &:hover {
          background-color: #f0f9ff !important;
          
          .dark & {
            background-color: rgba(14, 165, 233, 0.1) !important;
          }
        }
      }
      
      // danger 文本按钮
      &.el-button--danger {
        color: #ef4444;
        
        .dark & {
          color: #f87171;
        }
        
        &:hover {
          background-color: #fef2f2 !important;
          
          .dark & {
            background-color: rgba(239, 68, 68, 0.1) !important;
          }
        }
      }
    }
  }

  // Element Plus Tag 组件样式优化 - 使用 F-01 配色方案
  :deep(.el-tag) {
    @apply border-0 font-medium;
    
    // 成功状态 - 翠绿色
    &.el-tag--success {
      background-color: #dcfce7 !important; // success-100
      color: #15803d !important; // success-700
      
      .dark & {
        background-color: rgba(34, 197, 94, 0.2) !important; // success-500 with opacity
        color: #86efac !important; // success-300
      }
    }
    
    // 信息状态 - 灰色
    &.el-tag--info {
      background-color: #f1f5f9 !important; // slate-100
      color: #475569 !important; // slate-600
      
      .dark & {
        background-color: rgba(148, 163, 184, 0.2) !important; // slate-400 with opacity
        color: #cbd5e1 !important; // slate-300
      }
    }
    
    // 警告状态 - 琥珀色
    &.el-tag--warning {
      background-color: #fef3c7 !important; // warning-100
      color: #b45309 !important; // warning-700
      
      .dark & {
        background-color: rgba(245, 158, 11, 0.2) !important; // warning-500 with opacity
        color: #fcd34d !important; // warning-300
      }
    }
    
    // 危险状态 - 玫瑰红
    &.el-tag--danger {
      background-color: #fee2e2 !important; // error-100
      color: #b91c1c !important; // error-700
      
      .dark & {
        background-color: rgba(239, 68, 68, 0.2) !important; // error-500 with opacity
        color: #fca5a5 !important; // error-300
      }
    }
  }
}
</style>

