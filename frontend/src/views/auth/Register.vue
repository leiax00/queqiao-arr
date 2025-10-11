<template>
  <div class="register-form">
    <div class="form-header">
      <h2 class="form-title">创建管理员账号</h2>
      <p class="form-description">首次运行需要创建管理员账号</p>
    </div>
    
    <!-- 错误提示 -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="false"
      class="mb-4"
    />
    
    <el-form
      ref="formRef"
      :model="registerForm"
      :rules="registerRules"
      @submit.prevent="handleRegister"
    >
      <el-form-item prop="username">
        <el-input
          v-model="registerForm.username"
          placeholder="用户名（3-50个字符）"
          clearable
        >
          <template #prefix>
            <el-icon class="input-icon"><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item prop="email">
        <el-input
          v-model="registerForm.email"
          type="email"
          placeholder="邮箱（可选）"
          clearable
        >
          <template #prefix>
            <el-icon class="input-icon"><Message /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input
          v-model="registerForm.password"
          type="password"
          placeholder="密码（至少8个字符）"
          show-password
          @input="checkPasswordStrength"
        >
          <template #prefix>
            <el-icon class="input-icon"><Lock /></el-icon>
          </template>
        </el-input>
        
        <!-- 密码强度指示器 -->
        <div v-if="registerForm.password" class="password-strength mt-2">
          <div class="strength-bar-container">
            <div 
              class="strength-bar" 
              :class="passwordStrengthClass"
              :style="{ width: passwordStrengthWidth }"
            ></div>
          </div>
          <span class="strength-text" :class="passwordStrengthClass">
            {{ passwordStrengthText }}
          </span>
        </div>
      </el-form-item>
      
      <el-form-item prop="confirmPassword">
        <el-input
          v-model="registerForm.confirmPassword"
          type="password"
          placeholder="确认密码"
          show-password
          @keyup.enter="handleRegister"
        >
          <template #prefix>
            <el-icon class="input-icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      
      <!-- 密码要求提示 -->
      <div class="password-requirements">
        <div class="requirement-item" :class="{ 'met': passwordRequirements.length }">
          <el-icon><Check v-if="passwordRequirements.length" /><Close v-else /></el-icon>
          <span>至少8个字符</span>
        </div>
        <div class="requirement-item" :class="{ 'met': passwordRequirements.hasLetter }">
          <el-icon><Check v-if="passwordRequirements.hasLetter" /><Close v-else /></el-icon>
          <span>包含字母</span>
        </div>
        <div class="requirement-item" :class="{ 'met': passwordRequirements.hasNumber }">
          <el-icon><Check v-if="passwordRequirements.hasNumber" /><Close v-else /></el-icon>
          <span>包含数字</span>
        </div>
        <div class="requirement-item" :class="{ 'met': passwordRequirements.hasSpecial }">
          <el-icon><Check v-if="passwordRequirements.hasSpecial" /><Close v-else /></el-icon>
          <span>包含特殊字符（建议）</span>
        </div>
      </div>
      
      <el-form-item class="mt-6">
        <el-button
          type="primary"
          :loading="loading"
          @click="handleRegister"
          class="register-btn"
        >
          <span v-if="!loading">创建账号</span>
          <span v-else>创建中...</span>
        </el-button>
      </el-form-item>
    </el-form>
    
    <div class="form-footer">
      <div class="footer-text">
        已有账号？
        <router-link to="/login" class="link">
          立即登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Message, Check, Close } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMessage = ref('')

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

// 密码强度状态
const passwordStrength = ref(0) // 0-4

// 密码要求检查
const passwordRequirements = reactive({
  length: false,
  hasLetter: false,
  hasNumber: false,
  hasSpecial: false,
})

// 自定义校验规则
const validateUsername = (_rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请输入用户名'))
  } else if (value.length < 3) {
    callback(new Error('用户名至少3个字符'))
  } else if (value.length > 50) {
    callback(new Error('用户名不能超过50个字符'))
  } else {
    callback()
  }
}

const validatePassword = (_rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 8) {
    callback(new Error('密码至少8个字符'))
  } else {
    // 如果确认密码已填写，需要重新校验
    if (registerForm.confirmPassword) {
      formRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPassword = (_rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateEmail = (_rule: any, value: any, callback: any) => {
  if (!value) {
    callback() // 邮箱是可选的
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      callback(new Error('请输入有效的邮箱地址'))
    } else {
      callback()
    }
  }
}

const registerRules: FormRules = {
  username: [{ validator: validateUsername, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
}

// 检查密码强度
const checkPasswordStrength = () => {
  const password = registerForm.password
  
  // 更新密码要求状态
  passwordRequirements.length = password.length >= 8
  passwordRequirements.hasLetter = /[a-zA-Z]/.test(password)
  passwordRequirements.hasNumber = /\d/.test(password)
  passwordRequirements.hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  
  // 计算密码强度 (0-4)
  let strength = 0
  if (passwordRequirements.length) strength++
  if (passwordRequirements.hasLetter) strength++
  if (passwordRequirements.hasNumber) strength++
  if (passwordRequirements.hasSpecial) strength++
  
  passwordStrength.value = strength
}

// 密码强度样式类
const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return 'strength-none'
  if (strength === 1) return 'strength-weak'
  if (strength === 2) return 'strength-fair'
  if (strength === 3) return 'strength-good'
  return 'strength-strong'
})

// 密码强度宽度
const passwordStrengthWidth = computed(() => {
  return `${(passwordStrength.value / 4) * 100}%`
})

// 密码强度文本
const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return '无强度'
  if (strength === 1) return '弱'
  if (strength === 2) return '一般'
  if (strength === 3) return '良好'
  return '强'
})

const handleRegister = async () => {
  if (!formRef.value) return
  
  try {
    // 清除之前的错误消息
    errorMessage.value = ''
    
    // 表单校验
    await formRef.value.validate()
    loading.value = true
    
    // 调用注册接口（不传 confirmPassword）
    const result = await authStore.register({
      username: registerForm.username,
      email: registerForm.email || '',
      password: registerForm.password,
    })
    
    if (result.success) {
      ElMessage.success('注册成功，欢迎使用！')
      // 路由跳转由 store 处理
    } else if (result.shouldRedirect) {
      // 已有用户，跳转到登录页（由 store 处理）
      ElMessage.info(result.message || '系统已初始化，请登录')
    } else {
      // 显示错误消息
      errorMessage.value = result.message || '注册失败，请重试'
    }
  } catch (error: any) {
    console.error('注册失败:', error)
    errorMessage.value = error.message || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-form {
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
  
  .password-strength {
    .strength-bar-container {
      @apply h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden;
      
      .strength-bar {
        @apply h-full transition-all duration-300 rounded-full;
        
        &.strength-none {
          @apply bg-gray-300;
        }
        
        &.strength-weak {
          @apply bg-red-500;
        }
        
        &.strength-fair {
          @apply bg-orange-500;
        }
        
        &.strength-good {
          @apply bg-yellow-500;
        }
        
        &.strength-strong {
          @apply bg-green-500;
        }
      }
    }
    
    .strength-text {
      @apply text-xs mt-1 inline-block font-medium;
      
      &.strength-weak {
        @apply text-red-500;
      }
      
      &.strength-fair {
        @apply text-orange-500;
      }
      
      &.strength-good {
        @apply text-yellow-500;
      }
      
      &.strength-strong {
        @apply text-green-500;
      }
    }
  }
  
  .password-requirements {
    @apply grid grid-cols-2 gap-2 mb-4 text-xs;
    
    // 移动端改为单列
    @media (max-width: 640px) {
      @apply grid-cols-1 gap-1.5 text-xs;
    }
    
    .requirement-item {
      @apply flex items-center gap-1.5 text-gray-400 dark:text-gray-500 transition-colors;
      
      &.met {
        @apply text-green-500 dark:text-green-400;
      }
      
      .el-icon {
        @apply text-sm;
        
        @media (max-width: 640px) {
          @apply text-xs;
        }
      }
    }
  }
  
  .register-btn {
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

:deep(.el-alert) {
  @apply rounded-xl;
  border: none;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
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
