<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">个人资料</h1>
      <p class="page-subtitle">管理您的账户信息</p>
    </div>
    
    <div class="profile-content">
      <el-card class="profile-card">
        <div class="coming-soon">
          <el-icon class="icon"><Tools /></el-icon>
          <p>个人资料页面开发中...</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Tools } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.profile-page {
  .page-header {
    @apply mb-6;
    
    .page-title {
      @apply text-2xl font-bold text-gray-900 dark:text-white mb-2;
    }
    
    .page-subtitle {
      @apply text-gray-600 dark:text-gray-400;
    }
  }
  
  .profile-card {
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
