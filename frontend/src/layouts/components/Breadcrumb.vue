<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item
      v-for="(item, index) in breadcrumbs"
      :key="item.path"
      :to="index === breadcrumbs.length - 1 ? undefined : item.path"
    >
      <el-icon v-if="item.icon" class="mr-1">
        <component :is="item.icon" />
      </el-icon>
      {{ item.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  HomeFilled, 
  Setting, 
  Monitor, 
  Document, 
  User,
  DataAnalysis 
} from '@element-plus/icons-vue'

interface BreadcrumbItem {
  title: string
  path: string
  icon?: any
}

const route = useRoute()

// 路由到图标的映射
const routeIcons: Record<string, any> = {
  '/': HomeFilled,
  '/dashboard': DataAnalysis,
  '/config': Setting,
  '/system': Monitor,
  '/logs': Document,
  '/profile': User,
}

// 路由到标题的映射
const routeTitles: Record<string, string> = {
  '/': '首页',
  '/dashboard': '仪表板',
  '/config': '配置中心',
  '/system': '系统管理',
  '/logs': '日志管理',
  '/profile': '个人资料',
}

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  const breadcrumbItems: BreadcrumbItem[] = []

  // 如果不是首页，添加首页链接
  if (route.path !== '/') {
    breadcrumbItems.push({
      title: '首页',
      path: '/',
      icon: HomeFilled
    })
  }

  // 根据当前路由生成面包屑
  const pathSegments = route.path.split('/').filter(Boolean)
  let currentPath = ''

  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const title = routeTitles[currentPath] || segment
    const icon = routeIcons[currentPath]

    breadcrumbItems.push({
      title,
      path: currentPath,
      icon
    })
  })

  return breadcrumbItems
})
</script>

<style lang="scss" scoped>
:deep(.el-breadcrumb__item) {
  .el-breadcrumb__inner {
    @apply flex items-center;
    @apply text-gray-700 dark:text-gray-300;
    
    &:hover {
      @apply text-primary-600 dark:text-primary-400;
    }
  }
  
  .el-breadcrumb__separator {
    @apply text-gray-500 dark:text-gray-400;
  }
  
  // 最后一个面包屑项（当前页面）
  &:last-child .el-breadcrumb__inner {
    @apply text-gray-900 dark:text-gray-100 font-medium;
    cursor: default;
    
    &:hover {
      @apply text-gray-900 dark:text-gray-100;
    }
  }
  
  // 图标颜色
  .el-icon {
    @apply text-gray-600 dark:text-gray-400 mr-1;
  }
  
  &:hover .el-icon {
    @apply text-primary-600 dark:text-primary-400;
  }
  
  &:last-child .el-icon {
    @apply text-gray-700 dark:text-gray-300;
  }
  
  &:last-child:hover .el-icon {
    @apply text-gray-700 dark:text-gray-300;
  }
}
</style>
