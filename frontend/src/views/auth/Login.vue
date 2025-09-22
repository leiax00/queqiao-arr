<template>
  <div class="login-form">
    <h2 class="form-title">登录</h2>
    
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
          size="large"
          :prefix-icon="User"
        />
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="密码"
          size="large"
          :prefix-icon="Lock"
          show-password
          @keyup.enter="handleLogin"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleLogin"
          class="login-btn"
        >
          登录
        </el-button>
      </el-form-item>
    </el-form>
    
    <div class="form-footer">
      <router-link to="/register" class="link">
        还没有账号？立即注册
      </router-link>
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
  .form-title {
    @apply text-2xl font-bold text-center mb-6 text-gray-900 dark:text-white;
  }
  
  .login-btn {
    @apply w-full;
  }
  
  .form-footer {
    @apply text-center mt-4;
    
    .link {
      @apply text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300;
      @apply text-sm transition-colors;
    }
  }
}
</style>
