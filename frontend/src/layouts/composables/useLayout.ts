import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useLayoutStore } from '@/stores/layout'

const MOBILE_WIDTH = 768

export function useLayout() {
  const layoutStore = useLayoutStore()
  
  const isMobile = ref(false)
  
  const checkDevice = () => {
    const width = window.innerWidth
    const wasMobile = isMobile.value
    isMobile.value = width < MOBILE_WIDTH
    layoutStore.setDevice(isMobile.value ? 'mobile' : 'desktop')
    
    // 从桌面端切换到移动端时自动收起侧边栏
    if (isMobile.value && !wasMobile) {
      layoutStore.closeSidebar(true)
    }
    // 从移动端切换到桌面端时恢复侧边栏状态
    else if (!isMobile.value && wasMobile) {
      // 可以选择恢复之前的状态或保持当前状态
    }
  }
  
  const handleResize = () => {
    checkDevice()
  }
  
  onMounted(() => {
    checkDevice()
    window.addEventListener('resize', handleResize)
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
  
  return {
    isMobile: computed(() => isMobile.value),
    sidebar: computed(() => layoutStore.sidebar),
    toggleSidebar: layoutStore.toggleSidebar,
    closeSidebar: layoutStore.closeSidebar,
  }
}
