<template>
  <div class="navbar">
    <!-- 左侧区域 -->
    <div class="navbar-left">
      <!-- 菜单折叠按钮 -->
      <el-button
        :icon="Fold"
        circle
        @click="$emit('toggle')"
        class="toggle-btn"
        :title="collapsed ? '展开菜单' : '收起菜单'"
      />
      
      <!-- 面包屑导航 -->
      <Breadcrumb v-if="!isMobile" class="ml-4" />
    </div>

    <!-- 右侧区域 -->
    <div class="navbar-right">
      <!-- 主题切换 -->
      <ThemeToggle />
      
      <!-- 全屏切换 -->
      <el-button
        :icon="isFullscreen ? FullScreen : FullScreen"
        circle
        @click="toggleFullscreen"
        class="ml-2"
        :title="isFullscreen ? '退出全屏' : '全屏显示'"
      />
      
      <!-- 用户下拉菜单 -->
      <UserDropdown class="ml-2" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Fold, FullScreen } from '@element-plus/icons-vue'
import Breadcrumb from '../components/Breadcrumb.vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import UserDropdown from '../components/UserDropdown.vue'
import {useLayout} from "@/layouts/composables/useLayout";

interface Props {
  collapsed: boolean
}

defineProps<Props>()
defineEmits<{
  toggle: []
}>()

const { isMobile } = useLayout()

const isFullscreen = ref(false)

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style lang="scss" scoped>
.navbar {
  @apply flex items-center justify-between px-4 bg-white dark:bg-dark-card;
  @apply border-b border-light-border dark:border-dark-border;
  height: 60px;

  .navbar-left {
    @apply flex items-center;

    .toggle-btn {
      @apply hover:bg-primary-50 dark:hover:bg-primary-900/20;
      @apply text-gray-600 dark:text-gray-300;
      @apply border-gray-200 dark:border-gray-600;
      
      &:hover {
        @apply text-primary-600 dark:text-primary-400;
        @apply border-primary-300 dark:border-primary-500;
      }
    }
  }

  .navbar-right {
    @apply flex items-center;
    
    // Element Plus 按钮全局样式覆盖
    :deep(.el-button) {
      @apply text-gray-600 dark:text-gray-300;
      @apply bg-transparent dark:bg-transparent;
      @apply border-gray-200 dark:border-gray-600;
      
      &:hover {
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
  }
}
</style>
