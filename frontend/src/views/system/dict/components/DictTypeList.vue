<template>
  <div class="dict-type-list">
    <!-- 标题与操作 -->
    <div class="header">
      <h3 class="title">字典类型</h3>
      <el-button
        type="primary"
        size="small"
        :icon="Plus"
        @click="handleCreate"
      >
        新增类型
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-skeleton">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="typeList.length === 0"
      description="暂无字典类型，请点击新增"
      :image-size="100"
    />

    <!-- 类型列表 -->
    <div v-else class="type-list">
      <div
        v-for="type in typeList"
        :key="type.id"
        class="type-item"
        :class="{ active: selectedTypeId === type.id }"
        @click="handleSelect(type)"
      >
        <div class="type-info">
          <div class="type-name">
            {{ type.name }}
            <el-tag
              v-if="!type.is_active"
              size="small"
              type="info"
              effect="plain"
            >
              已禁用
            </el-tag>
          </div>
          <div class="type-code">{{ type.code }}</div>
        </div>
        <div class="type-actions">
          <el-button
            text
            size="small"
            :icon="Edit"
            @click.stop="handleEdit(type)"
          />
          <el-button
            text
            size="small"
            type="danger"
            :icon="Delete"
            @click.stop="handleDelete(type)"
          />
        </div>
      </div>
    </div>

    <!-- 字典类型表单对话框 -->
    <DictTypeForm
      v-model:visible="formVisible"
      :type-data="currentType"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getDictTypes, deleteDictType } from '@/api/dict'
import type { DictType } from '@/api/types'
import DictTypeForm from './DictTypeForm.vue'

// Emits
const emit = defineEmits<{
  select: [type: DictType]
}>()

// State
const loading = ref(false)
const typeList = ref<DictType[]>([])
const selectedTypeId = ref<number | null>(null)
const formVisible = ref(false)
const currentType = ref<DictType | null>(null)

// Methods
const loadTypes = async () => {
  loading.value = true
  try {
    const res = await getDictTypes({ page: 1, page_size: 100 })
    typeList.value = res.items
  } catch (error: any) {
    ElMessage.error(error.message || '加载字典类型失败')
  } finally {
    loading.value = false
  }
}

const handleSelect = (type: DictType) => {
  selectedTypeId.value = type.id
  emit('select', type)
}

const handleCreate = () => {
  currentType.value = null
  formVisible.value = true
}

const handleEdit = (type: DictType) => {
  currentType.value = type
  formVisible.value = true
}

const handleDelete = async (type: DictType) => {
  try {
    await ElMessageBox.confirm(
      '删除字典类型将同时删除该类型下的所有字典项，此操作不可恢复，是否确认删除？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteDictType(type.id)
    ElMessage.success('删除成功')

    // 如果删除的是当前选中的类型，清空选中
    if (selectedTypeId.value === type.id) {
      selectedTypeId.value = null
    }

    await loadTypes()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleFormSuccess = async () => {
  await loadTypes()
  // 如果是新增，自动选中第一个类型
  if (!currentType.value && typeList.value.length > 0) {
    handleSelect(typeList.value[0])
  }
}

// Lifecycle
onMounted(() => {
  loadTypes()
})
</script>

<style scoped lang="scss">
.dict-type-list {
  @apply macaron-card;
  @apply flex flex-col h-full p-4;
  
  // 移除卡片悬停浮动效果，保持稳定
  &:hover {
    @apply shadow-soft transform-none;
  }

  .header {
    @apply flex justify-between items-center mb-4;

    .title {
      @apply m-0 text-base font-semibold;
      @apply text-gray-900 dark:text-white;
    }
  }

  .loading-skeleton {
    @apply p-4;
  }

  .type-list {
    @apply flex-1 overflow-y-auto;

    .type-item {
      @apply flex justify-between items-center p-3 mb-2 rounded-md cursor-pointer;
      @apply border border-gray-200 dark:border-gray-700;
      @apply bg-white dark:bg-gray-800/50;
      @apply transition-all duration-200;

      &:hover {
        @apply border-primary-500;
        @apply bg-primary-50 dark:bg-primary-900/20;
      }

      &.active {
        @apply border-primary-500;
        @apply bg-primary-50 dark:bg-primary-900/30;
      }

      .type-info {
        @apply flex-1 min-w-0;

        .type-name {
          @apply flex items-center gap-2 text-sm font-medium mb-1;
          @apply text-gray-900 dark:text-white;
        }

        .type-code {
          @apply text-xs font-mono;
          @apply text-gray-600 dark:text-gray-400;
        }
      }

      .type-actions {
        @apply flex gap-1 opacity-0 transition-opacity;
      }

      &:hover .type-actions {
        @apply opacity-100;
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
    
    // 信息状态 - 灰色
    &.el-tag--info {
      background-color: #f1f5f9 !important; // slate-100
      color: #475569 !important; // slate-600
      
      .dark & {
        background-color: rgba(148, 163, 184, 0.2) !important; // slate-400 with opacity
        color: #cbd5e1 !important; // slate-300
      }
    }
  }
}
</style>

