<template>
  <div class="auth-layout">
    <!-- 背景装饰 -->
    <div class="auth-bg">
      <div class="bg-pattern"></div>
    </div>
    
    <!-- 主内容区 -->
    <div class="auth-content">
      <!-- Logo和标题 -->
      <div class="auth-header">
        <img src="/logo.svg" alt="Queqiao-arr" class="logo" />
        <h1 class="title">Queqiao-arr</h1>
        <p class="subtitle">中文内容自动化下载代理服务</p>
      </div>
      
      <!-- 表单区域 -->
      <div class="auth-form">
        <router-view />
      </div>
      
      <!-- 主题切换 -->
      <div class="auth-footer">
        <ThemeToggle />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ThemeToggle from '../components/ThemeToggle.vue'
</script>

<style lang="scss" scoped>
.auth-layout {
  @apply relative min-h-screen flex items-center justify-center;
  @apply bg-gradient-to-br from-primary-50 to-secondary-50;
  @apply dark:from-dark-bg dark:to-gray-900;
}

.auth-bg {
  @apply absolute inset-0 overflow-hidden;
  
  .bg-pattern {
    @apply absolute inset-0 opacity-10;
    background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0);
    background-size: 20px 20px;
  }
}

.auth-content {
  @apply relative z-10 w-full max-w-md mx-auto px-6;
}

.auth-header {
  @apply text-center mb-8;
  
  .logo {
    @apply w-16 h-16 mx-auto mb-4;
  }
  
  .title {
    @apply text-3xl font-bold text-gray-900 dark:text-white mb-2;
    @apply bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent;
  }
  
  .subtitle {
    @apply text-gray-600 dark:text-gray-400 text-sm;
  }
}

.auth-form {
  @apply bg-white dark:bg-dark-card rounded-2xl shadow-soft-lg p-8 mb-6;
  @apply border border-light-border dark:border-dark-border;
}

.auth-footer {
  @apply flex justify-center;
}
</style>
