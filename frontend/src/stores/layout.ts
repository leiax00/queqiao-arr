import { defineStore } from 'pinia'

interface LayoutState {
  sidebar: {
    collapsed: boolean
    withoutAnimation: boolean
  }
  device: 'desktop' | 'mobile'
  size: 'small' | 'medium' | 'large'
}

export const useLayoutStore = defineStore('layout', {
  state: (): LayoutState => ({
    sidebar: {
      collapsed: false,
      withoutAnimation: false,
    },
    device: 'desktop',
    size: 'medium',
  }),

  getters: {
    sidebarCollapsed: (state) => state.sidebar.collapsed,
    isMobile: (state) => state.device === 'mobile',
  },

  actions: {
    toggleSidebar(withoutAnimation = false) {
      this.sidebar.collapsed = !this.sidebar.collapsed
      this.sidebar.withoutAnimation = withoutAnimation
    },

    closeSidebar(withoutAnimation = false) {
      this.sidebar.collapsed = true
      this.sidebar.withoutAnimation = withoutAnimation
    },

    openSidebar(withoutAnimation = false) {
      this.sidebar.collapsed = false
      this.sidebar.withoutAnimation = withoutAnimation
    },

    setDevice(device: 'desktop' | 'mobile') {
      this.device = device
    },

    setSize(size: 'small' | 'medium' | 'large') {
      this.size = size
    },
  },

  persist: {
    key: 'layout-settings',
    storage: localStorage,
    paths: ['sidebar.collapsed', 'size'],
  },
})
