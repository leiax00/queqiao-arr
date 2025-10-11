<template>
  <div class="sidebar-container">
    <el-scrollbar>
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :unique-opened="true"
        :collapse-transition="false"
        mode="vertical"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <!-- Logo区域 -->
        <div class="logo-container" :class="{ collapsed }">
          <img src="/logo.svg" alt="Queqiao-arr" class="logo-image" />
          <h1 v-show="!collapsed" class="logo-text">Queqiao-arr</h1>
        </div>

        <!-- 菜单项 -->
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>

        <el-sub-menu index="config">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>配置管理</span>
          </template>
          <el-menu-item index="/config/sonarr">
            <el-icon><Monitor /></el-icon>
            <template #title>Sonarr配置</template>
          </el-menu-item>
          <el-menu-item index="/config/prowlarr">
            <el-icon><Search /></el-icon>
            <template #title>Prowlarr配置</template>
          </el-menu-item>
          <el-menu-item index="/config/proxy">
            <el-icon><Connection /></el-icon>
            <template #title>代理设置</template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/system">
          <el-icon><Monitor /></el-icon>
          <template #title>系统监控</template>
        </el-menu-item>

        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <template #title>日志管理</template>
        </el-menu-item>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  DataAnalysis, 
  Setting, 
  Monitor, 
  Document, 
  Search, 
  Connection 
} from '@element-plus/icons-vue'

interface Props {
  collapsed: boolean
}

const props = defineProps<Props>()
const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => {
  const { path } = route
  if (path.startsWith('/config')) {
    return path
  }
  return path
})

const handleMenuSelect = (index: string) => {
  if (index !== route.path) {
    router.push(index)
  }
}
</script>

<style lang="scss" scoped>
.sidebar-container {
  @apply h-full bg-white dark:bg-dark-card border-r border-light-border dark:border-dark-border;
  width: v-bind('props.collapsed ? "64px" : "210px"');
  transition: width 0.3s ease;
  
  /* 移动端样式优化 */
  @media (max-width: 768px) {
    width: 280px !important;
    @apply shadow-2xl;
  }

  .logo-container {
    @apply flex items-center justify-center py-4 px-4 border-none border-light-border dark:border-dark-border;
    height: 60px;
    
    &.collapsed {
      @apply px-2;
    }

    .logo-image {
      @apply w-8 h-8 flex-shrink-0;
    }

    .logo-text {
      @apply ml-3 text-lg font-bold text-primary-600 dark:text-primary-400 whitespace-nowrap;
    }
  }

  .sidebar-menu {
    @apply border-none bg-transparent;
    
    // Element Plus 菜单项样式覆盖
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      @apply text-gray-700 dark:text-gray-300;
      @apply bg-transparent;
      @apply hover:bg-primary-50 dark:hover:bg-primary-900/20;
      @apply hover:text-primary-600 dark:hover:text-primary-400;
      @apply border-none;
      
      .el-icon {
        @apply text-gray-600 dark:text-gray-400;
      }
      
      &:hover .el-icon {
        @apply text-primary-600 dark:text-primary-400;
      }
      
      &.is-active {
        @apply bg-gradient-to-r from-primary-500 to-secondary-500 text-white;
        
        .el-icon {
          @apply text-white;
        }
      }
    }

    :deep(.el-sub-menu .el-menu-item) {
      @apply pl-12;
      @apply text-gray-600 dark:text-gray-400;
      @apply bg-transparent;
      @apply hover:bg-primary-50 dark:hover:bg-primary-900/20;
      @apply hover:text-primary-600 dark:hover:text-primary-400;
      
      &.is-active {
        @apply bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400;
        @apply border-r-2 border-primary-500;
      }
    }
    
    // 子菜单展开面板样式
    :deep(.el-sub-menu__icon-arrow) {
      @apply text-gray-500 dark:text-gray-400;
    }
    
    // 子菜单内容区域
    :deep(.el-menu) {
      @apply bg-transparent;
    }
  }
}
</style>
