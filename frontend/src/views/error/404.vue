<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-image">
        <el-icon class="error-icon"><Warning /></el-icon>
      </div>
      <h1 class="error-title">404</h1>
      <p class="error-message">抱歉，您访问的页面不存在</p>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          返回首页
        </el-button>
        <el-button @click="goBack">
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.error-page {
  @apply min-h-screen flex items-center justify-center;
  @apply bg-light-bg dark:bg-dark-bg;
  
  .error-content {
    @apply text-center;
    
    .error-image {
      @apply mb-8;
      
      .error-icon {
        @apply text-8xl text-primary-500;
      }
    }
    
    .error-title {
      @apply text-6xl font-bold text-gray-900 dark:text-white mb-4;
    }
    
    .error-message {
      @apply text-xl text-gray-600 dark:text-gray-400 mb-8;
    }
    
    .error-actions {
      @apply space-x-4;
    }
  }
}
</style>
