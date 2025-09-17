<template>
  <el-button
    :icon="isDark ? Moon : Sunny"
    circle
    @click="toggleTheme"
    class="theme-toggle-btn"
    :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sunny, Moon } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const isDark = computed(() => themeStore.isDark)

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>

<style lang="scss" scoped>
.theme-toggle-btn {
  @apply transition-all duration-300 hover:scale-110;
  @apply text-gray-600 dark:text-gray-300;
  @apply bg-transparent dark:bg-transparent;
  @apply border-gray-200 dark:border-gray-600;
  
  &:hover {
    @apply shadow-lg;
    @apply text-primary-600 dark:text-primary-400;
    @apply bg-primary-50 dark:bg-primary-900/20;
    @apply border-primary-300 dark:border-primary-500;
  }
  
  &:focus {
    @apply text-primary-600 dark:text-primary-400;
    @apply bg-primary-50 dark:bg-primary-900/20;
    @apply border-primary-300 dark:border-primary-500;
  }
}
</style>
