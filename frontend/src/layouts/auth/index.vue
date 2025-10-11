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
  padding: 3rem 0; // 添加上下间距，避免触顶触底
  
  @media (max-width: 640px) {
    padding: 2rem 0;
  }
}

.auth-bg {
  @apply absolute inset-0 overflow-hidden;
  
  .bg-pattern {
    @apply absolute inset-0 rounded-3xl;
    background: 
      radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 1px 1px, rgba(0, 0, 0, 0.03) 1px, transparent 0);
    background-size: 100% 100%, 100% 100%, 40px 40px;
    animation: bgFloat 15s ease-in-out infinite;
  }
}

@keyframes bgFloat {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.05);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.95);
  }
}

.auth-content {
  @apply relative z-10 w-full mx-auto px-6;
  max-width: 640px; // 从 28rem (448px) 增加到 480px
  
  // 移动端适配 - 减少左右padding
  @media (max-width: 640px) {
    @apply px-4;
  }
  
  // 超小屏幕
  @media (max-width: 375px) {
    @apply px-3;
  }
}

.auth-header {
  @apply text-center mb-8;
  animation: fadeInDown 0.6s ease-out;
  
  // 移动端间距调整
  @media (max-width: 640px) {
    @apply mb-6;
  }
  
  .logo {
    @apply w-16 h-16 mx-auto mb-4;
    filter: drop-shadow(0 8px 16px rgba(102, 126, 234, 0.3));
    transition: transform 0.3s ease;
    animation: logoFloat 3s ease-in-out infinite;
    border-radius: 20%;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    
    &:hover {
      transform: scale(1.1) rotate(5deg);
    }
    
    // 移动端logo稍小
    @media (max-width: 640px) {
      @apply w-12 h-12 mb-3;
    }
  }
  
  .title {
    @apply text-3xl font-bold mb-2;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    
    // 移动端字体调整
    @media (max-width: 640px) {
      @apply text-2xl mb-1.5;
    }
  }
  
  .subtitle {
    @apply text-gray-600 dark:text-gray-400 text-sm font-medium;
    
    // 移动端字体稍小
    @media (max-width: 640px) {
      @apply text-xs;
    }
  }
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-form {
  @apply bg-white dark:bg-dark-card rounded-3xl p-8 mb-6;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: fadeInUp 0.6s ease-out 0.2s both;
  position: relative;
  overflow: hidden;
  
  // 顶部装饰条
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    background-size: 200% 100%;
    animation: gradientShift 3s ease infinite;
  }
  
  :global(.dark) & {
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 
      0 20px 25px -5px rgba(0, 0, 0, 0.4),
      0 10px 10px -5px rgba(0, 0, 0, 0.2),
      0 0 0 1px rgba(255, 255, 255, 0.05),
      inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
  }
  
  // 移动端适配 - 减少padding
  @media (max-width: 640px) {
    @apply p-6 rounded-2xl;
  }
  
  // 超小屏幕
  @media (max-width: 375px) {
    @apply p-5 rounded-xl;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.auth-footer {
  @apply flex justify-center;
}
</style>
