import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Auth 路由（使用 auth layout）
    {
      path: '/login',
      component: () => import('@/layouts/auth/index.vue'),
      children: [
        {
          path: '',
          name: 'Login',
          component: () => import('@/views/auth/Login.vue'),
          meta: {
            title: '登录',
            requiresAuth: false,
          },
        },
      ],
    },
    {
      path: '/register',
      component: () => import('@/layouts/auth/index.vue'),
      children: [
        {
          path: '',
          name: 'Register',
          component: () => import('@/views/auth/Register.vue'),
          meta: {
            title: '注册',
            requiresAuth: false,
          },
        },
      ],
    },
    // 默认布局路由
    {
      path: '/',
      redirect: '/dashboard',
      component: () => import('@/layouts/default/index.vue'),
      meta: {
        requiresAuth: true,
      },
      children: [
        {
          path: '/dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/index.vue'),
          meta: {
            title: '仪表板',
            requiresAuth: true,
          },
        },
        {
          path: '/config',
          name: 'Config',
          component: () => import('@/views/config/index.vue'),
          meta: {
            title: '配置中心',
            requiresAuth: true,
          },
        },
        {
          path: '/system',
          name: 'System',
          component: () => import('@/views/system/index.vue'),
          meta: {
            title: '系统监控',
            requiresAuth: true,
          },
        },
        {
          path: '/logs',
          name: 'Logs',
          component: () => import('@/views/system/Logs.vue'),
          meta: {
            title: '日志管理',
            requiresAuth: true,
          },
        },
        {
          path: '/system/dict',
          name: 'SystemDict',
          component: () => import('@/views/system/dict/index.vue'),
          meta: {
            title: '字典管理',
            requiresAuth: true,
          },
        },
        {
          path: '/profile',
          name: 'Profile',
          component: () => import('@/views/auth/Profile.vue'),
          meta: {
            title: '个人资料',
            requiresAuth: true,
          },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/error/404.vue'),
      meta: {
        title: '页面未找到',
      },
    },
  ],
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 未登录，跳转到登录页
    next('/login')
    return
  }
  
  // 已登录用户访问登录页，跳转到首页
  if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
