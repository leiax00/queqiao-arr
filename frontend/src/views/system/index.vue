<template>
  <div class="system-page">
    <div class="page-header">
      <h1 class="page-title">系统监控</h1>
      <p class="page-subtitle">查看系统运行状态和性能指标</p>
    </div>
    
    <div class="system-content">
      <el-card class="system-card">
        <div class="coming-soon">
          <el-icon class="icon"><Tools /></el-icon>
          <p>系统监控页面开发中...</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Tools } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.system-page {
  .page-header {
    @apply mb-6;
    
    .page-title {
      @apply text-2xl font-bold text-gray-900 dark:text-white mb-2;
    }
    
    .page-subtitle {
      @apply text-gray-600 dark:text-gray-400;
    }
  }
  
  .system-card {
    @apply macaron-card;
    
    .coming-soon {
      @apply text-center py-16;
      
      .icon {
        @apply text-6xl text-primary-500 mb-4;
      }
      
      p {
        @apply text-xl text-gray-600 dark:text-gray-400;
      }
    }
  }
}
</style>
