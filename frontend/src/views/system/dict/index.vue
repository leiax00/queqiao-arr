<template>
  <div class="dict-management">
    <div class="dict-container">
      <!-- 左侧：字典类型列表 -->
      <div class="left-panel">
        <DictTypeList @select="handleTypeSelect" />
      </div>

      <!-- 右侧：字典项管理 -->
      <div class="right-panel">
        <DictItemTable :current-type="selectedType" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { DictType } from '@/api/types'
import DictTypeList from './components/DictTypeList.vue'
import DictItemTable from './components/DictItemTable.vue'

// State
const selectedType = ref<DictType | null>(null)

// Methods
const handleTypeSelect = (type: DictType) => {
  selectedType.value = type
}
</script>

<style scoped lang="scss">
.dict-management {
  @apply h-full p-5;

  .dict-container {
    @apply flex gap-5 h-full;
    max-height: calc(100vh - 100px);

    .left-panel {
      @apply w-80 min-w-80 max-w-96 h-full overflow-hidden;
    }

    .right-panel {
      @apply flex-1 min-w-0 h-full overflow-hidden;
    }

    // 响应式布局：小屏幕改为上下堆叠
    @media (max-width: 768px) {
      @apply flex-col;
      max-height: none;

      .left-panel {
        @apply w-full max-w-none h-auto;
        max-height: 400px;
      }

      .right-panel {
        @apply w-full h-auto;
        min-height: 500px;
      }
    }
  }
}
</style>

