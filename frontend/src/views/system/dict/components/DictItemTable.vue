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
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="code" label="编码" width="150" fixed>
          <template #default="{ row }">
            <code class="item-code">{{ row.code }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="value" label="值" width="180" />
        <el-table-column
          prop="sort_order"
          label="排序"
          width="80"
          align="center"
        />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="extra_data" label="扩展数据" width="150">
          <template #default="{ row }">
            <div v-if="row.extra_data" class="extra-data">
              <el-tooltip
                :content="JSON.stringify(row.extra_data, null, 2)"
                placement="top"
                effect="light"
              >
                <code class="extra-preview">
                  {{ formatExtraData(row.extra_data) }}
                </code>
              </el-tooltip>
            </div>
            <span v-else class="text-secondary">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right" align="center">
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
import type { DictType, DictItem } from '@/api/types'
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
    const res = await getDictItems({
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
  // 优先显示 icon 字段
  if (data.icon) return data.icon
  // 否则显示简化的 JSON
  const str = JSON.stringify(data)
  return str.length > 20 ? str.substring(0, 20) + '...' : str
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
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 16px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      display: flex;
      align-items: center;
      gap: 12px;

      .type-tag {
        font-size: 14px;
        font-weight: 400;
        color: var(--el-color-primary);
        padding: 2px 12px;
        background: var(--el-color-primary-light-9);
        border-radius: 4px;
      }
    }

    .actions {
      display: flex;
      gap: 8px;
    }
  }

  .table-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .item-code {
      font-family: 'Courier New', monospace;
      font-size: 12px;
      color: var(--el-color-primary);
      background: var(--el-color-primary-light-9);
      padding: 2px 6px;
      border-radius: 3px;
    }

    .extra-data {
      .extra-preview {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: var(--el-text-color-regular);
        cursor: help;
      }
    }

    .text-secondary {
      color: var(--el-text-color-secondary);
    }
  }

  .pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--el-border-color-lighter);
  }
}
</style>

