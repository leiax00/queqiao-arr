<template>
  <div class="register-form">
    <h2 class="form-title">注册</h2>
    <p class="form-desc">创建您的 Queqiao-arr 账户</p>
    
    <!-- 注册表单内容 -->
    <div class="coming-soon">
      <el-icon class="icon"><Tools /></el-icon>
      <p>注册功能开发中...</p>
      <router-link to="/login" class="link">返回登录</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Tools } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.register-form {
  .form-title {
    @apply text-2xl font-bold text-center mb-2 text-gray-900 dark:text-white;
  }
  
  .form-desc {
    @apply text-center mb-6 text-gray-600 dark:text-gray-400;
  }
  
  .coming-soon {
    @apply text-center py-8;
    
    .icon {
      @apply text-4xl text-primary-500 mb-4;
    }
    
    p {
      @apply text-gray-600 dark:text-gray-400 mb-4;
    }
    
    .link {
      @apply text-primary-600 hover:text-primary-700 dark:text-primary-400;
    }
  }
}
</style>
