<template>
  <div class="login-form">
    <div class="form-header">
      <h2 class="form-title">登录</h2>
      <p class="form-description">欢迎回来</p>
    </div>
    
    <el-form
      ref="formRef"
      :model="loginForm"
      :rules="loginRules"
      @submit.prevent="handleLogin"
    >
      <el-form-item prop="username">
        <el-input
          v-model="loginForm.username"
          placeholder="用户名"
          clearable
        >
          <template #prefix>
            <el-icon class="input-icon"><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="密码"
          show-password
          @keyup.enter="handleLogin"
        >
          <template #prefix>
            <el-icon class="input-icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item class="mt-6">
        <el-button
          type="primary"
          :loading="loading"
          @click="handleLogin"
          class="login-btn"
        >
          <span v-if="!loading">登录</span>
          <span v-else>登录中...</span>
        </el-button>
      </el-form-item>
    </el-form>
    
    <div class="form-footer">
      <div class="footer-text">
        还没有账号？
        <router-link to="/register" class="link">
          立即注册
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const result = await authStore.login(loginForm)
    
    if (result.success) {
      ElMessage.success('登录成功')
    } else {
      ElMessage.error(result.message || '登录失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-form {
  @apply w-full;
  
  .form-header {
    @apply text-center mb-6;
    
    .form-title {
      @apply text-2xl font-bold mb-2;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: -0.02em;
      
      // 移动端字体稍小
      @media (max-width: 640px) {
        @apply text-xl mb-1.5;
      }
    }
    
    .form-description {
      @apply text-sm text-gray-600 dark:text-gray-400 font-medium;
      
      @media (max-width: 640px) {
        @apply text-xs;
      }
    }
  }
  
  .input-icon {
    @apply text-gray-400;
    font-size: 16px;
  }
  
  .login-btn {
    @apply w-full font-semibold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    background-size: 200% 100%;
    border: none;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
      transition: left 0.5s;
    }
    
    &:hover:not(:disabled) {
      transform: translateY(-3px);
      box-shadow: 0 12px 24px rgba(102, 126, 234, 0.5);
      background-position: 100% 0;
      
      &::before {
        left: 100%;
      }
    }
    
    &:active:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
  }
  
  .form-footer {
    @apply text-center mt-6;
    padding-top: 1.25rem;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    
    @media (prefers-color-scheme: dark) {
      border-top-color: rgba(255, 255, 255, 0.06);
    }
    
    .footer-text {
      @apply text-sm text-gray-600 dark:text-gray-400;
      
      .link {
        @apply font-semibold transition-all ml-1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        
        &::after {
          content: '';
          position: absolute;
          bottom: -2px;
          left: 0;
          width: 0;
          height: 2px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          transition: width 0.3s ease;
        }
        
        &:hover::after {
          width: 100%;
        }
      }
    }
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 自定义 Element Plus 样式
:deep(.el-input__wrapper) {
  @apply transition-all duration-300;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: none;
  background-color: #ffffff;
  
  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transform: translateY(-1px);
    border-color: rgba(102, 126, 234, 0.3);
  }
  
  &.is-focus {
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    border-color: #667eea !important;
  }
}

:deep(.el-input__inner) {
  background-color: transparent !important;
  color: inherit;
  
  // 浏览器自动填充样式
  &:-webkit-autofill,
  &:-webkit-autofill:hover,
  &:-webkit-autofill:focus,
  &:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
    -webkit-text-fill-color: #1e293b !important;
    transition: background-color 5000s ease-in-out 0s;
  }
}

:deep(.el-input) {
  font-size: 14px;
}

:deep(.el-form-item) {
  @apply mb-5;
}

:deep(.el-button) {
  padding: 10px 16px;
  font-size: 14px;
  border-radius: 10px;
}
</style>

<style lang="scss">
// 暗黑模式样式（全局，不使用 scoped）
.dark {
  .el-input__wrapper {
    border-color: rgba(255, 255, 255, 0.15) !important;
    background-color: rgba(30, 41, 59, 0.5) !important;
    
    &:hover {
      background-color: rgba(30, 41, 59, 0.7) !important;
    }
    
    &.is-focus {
      background-color: rgba(30, 41, 59, 0.8) !important;
    }
  }
  
  .el-input__inner {
    color: #f1f5f9 !important;
    
    &::placeholder {
      color: rgba(148, 163, 184, 0.6) !important;
    }
    
    // 暗黑模式下的浏览器自动填充样式
    &:-webkit-autofill,
    &:-webkit-autofill:hover,
    &:-webkit-autofill:focus,
    &:-webkit-autofill:active {
      -webkit-box-shadow: 0 0 0 1000px rgba(30, 41, 59, 0.5) inset !important;
      -webkit-text-fill-color: #f1f5f9 !important;
      transition: background-color 5000s ease-in-out 0s;
    }
  }
}
</style>
