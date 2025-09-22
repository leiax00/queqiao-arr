import { defineStore } from 'pinia'
import { authAPI } from '@/api'
import type { LoginData, UserInfo } from '@/api/types'
import router from '@/router'

interface AuthState {
  token: string | null
  user: UserInfo | null
  isLoggedIn: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null,
    isLoggedIn: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && state.isLoggedIn,
    username: (state) => state.user?.username || '',
  },

  actions: {
    async login(loginData: LoginData) {
      try {
        const response = await authAPI.login(loginData)
        this.token = response.access_token
        this.isLoggedIn = true
        
        // 获取用户信息
        await this.fetchUserInfo()
        
        // 跳转到首页
        router.push('/')
        
        return { success: true }
      } catch (error: any) {
        return { success: false, message: error.message || '登录失败' }
      }
    },

    async fetchUserInfo() {
      try {
        const userInfo = await authAPI.getUserInfo()
        this.user = userInfo
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
      }
    },

    async logout() {
      try {
        if (this.token) {
          await authAPI.logout()
        }
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        this.token = null
        this.user = null
        this.isLoggedIn = false
        router.push('/login')
      }
    },

    async refreshToken() {
      try {
        const response = await authAPI.refreshToken()
        this.token = response.access_token
        return true
      } catch (error) {
        console.error('刷新Token失败:', error)
        this.logout()
        return false
      }
    },

    // 检查登录状态
    checkAuth() {
      if (this.token && this.isLoggedIn) {
        this.fetchUserInfo()
      }
    },
  },

  persist: {
    key: 'auth-storage',
    storage: localStorage,
    paths: ['token', 'isLoggedIn'],
  },
})
