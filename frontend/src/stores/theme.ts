import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: false,
    systemPreference: 'light' as 'light' | 'dark' | 'auto'
  }),
  
  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      this.applyTheme()
    },
    
    setTheme(theme: 'light' | 'dark' | 'auto') {
      this.systemPreference = theme
      if (theme === 'auto') {
        this.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      } else {
        this.isDark = theme === 'dark'
      }
      this.applyTheme()
    },
    
    applyTheme() {
      if (this.isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      localStorage.setItem('theme-preference', this.systemPreference)
    },

    initTheme() {
      const stored = localStorage.getItem('theme-preference') as 'light' | 'dark' | 'auto' | null
      if (stored) {
        this.setTheme(stored)
      } else {
        this.setTheme('auto')
      }
    }
  },

  persist: {
    key: 'theme-settings',
    storage: localStorage,
  },
})
