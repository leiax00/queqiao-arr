<template>
  <div class="app-wrapper" :class="layoutClasses">
    <!-- 桌面端侧边栏 -->
    <Sidebar 
      v-if="!isMobile" 
      :collapsed="sidebar.collapsed"
    />
    
    <!-- 移动端侧边栏（抽屉式） -->
    <Transition name="sidebar-mobile">
      <Sidebar 
        v-if="isMobile && !sidebar.collapsed" 
        :collapsed="false"
        class="mobile-sidebar"
      />
    </Transition>
    
    <!-- 移动端侧边栏遮罩 -->
    <div 
      v-if="isMobile && !sidebar.collapsed" 
      class="drawer-bg"
      @click="closeSidebar"
    />
    
    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <Navbar 
        :collapsed="sidebar.collapsed"
        @toggle="toggleSidebar"
      />
      
      <!-- 页面内容 -->
      <AppMain />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLayout } from '../composables/useLayout'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import AppMain from './AppMain.vue'

const { isMobile, sidebar, toggleSidebar, closeSidebar } = useLayout()

// 响应式计算属性
const layoutClasses = computed(() => ({
  'hide-sidebar': sidebar.value.collapsed,
  'open-sidebar': !sidebar.value.collapsed,
  'mobile': isMobile.value,
}))
</script>

<style lang="scss" scoped>
.app-wrapper {
  @apply relative h-full w-full flex;
  
  &.mobile {
    .main-container {
      margin-left: 0;
    }
  }
}

.main-container {
  @apply flex-1 flex flex-col min-h-full transition-all duration-300 ease-in-out;
}

.drawer-bg {
  @apply fixed top-0 left-0 w-full h-full bg-black bg-opacity-30 z-40;
}

/* 移动端侧边栏样式 */
.mobile-sidebar {
  @apply fixed top-0 left-0 z-50;
  height: 100vh;
  width: 280px;
}

/* 移动端侧边栏动画 */
.sidebar-mobile-enter-active,
.sidebar-mobile-leave-active {
  transition: transform 0.3s ease;
}

.sidebar-mobile-enter-from,
.sidebar-mobile-leave-to {
  transform: translateX(-100%);
}

.sidebar-mobile-enter-to,
.sidebar-mobile-leave-from {
  transform: translateX(0);
}
</style>
