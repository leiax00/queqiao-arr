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
  height: 100%;
  padding: 20px;
  background: var(--el-bg-color-page);

  .dict-container {
    display: flex;
    gap: 20px;
    height: 100%;
    max-height: calc(100vh - 100px);

    .left-panel {
      width: 320px;
      min-width: 320px;
      max-width: 400px;
      height: 100%;
      overflow: hidden;
    }

    .right-panel {
      flex: 1;
      min-width: 0;
      height: 100%;
      overflow: hidden;
    }

    // 响应式布局：小屏幕改为上下堆叠
    @media (max-width: 768px) {
      flex-direction: column;
      max-height: none;

      .left-panel {
        width: 100%;
        max-width: none;
        height: auto;
        max-height: 400px;
      }

      .right-panel {
        width: 100%;
        height: auto;
        min-height: 500px;
      }
    }
  }
}
</style>

