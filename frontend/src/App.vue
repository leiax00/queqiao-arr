<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from './stores/theme'
import { useAuthStore } from './stores/auth'

const themeStore = useThemeStore()
const authStore = useAuthStore()

onMounted(() => {
  // 初始化主题
  themeStore.initTheme()
  
  // 检查登录状态
  authStore.checkAuth()
})
</script>

<style lang="scss">
// 全局样式已在main.scss中定义
</style>
