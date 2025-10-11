<template>
  <el-dropdown trigger="click" @command="handleCommand">
    <div class="user-dropdown">
      <el-avatar :size="32" :src="userAvatar">
        <el-icon><User /></el-icon>
      </el-avatar>
      <span class="username">{{ username }}</span>
      <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="profile">
          <el-icon><User /></el-icon>
          个人资料
        </el-dropdown-item>
        <el-dropdown-item command="settings">
          <el-icon><Setting /></el-icon>
          系统设置
        </el-dropdown-item>
        <el-dropdown-item divided command="logout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { User, ArrowDown, Setting, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const username = computed(() => authStore.username || 'Guest')
const userAvatar = computed(() => {
  // 可以根据用户信息生成头像URL
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${username.value}`
})

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      try {
        await authStore.logout()
        ElMessage.success('退出登录成功')
      } catch (error) {
        ElMessage.error('退出登录失败')
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.user-dropdown {
  @apply flex items-center space-x-2 px-3 py-2 rounded-lg cursor-pointer;
  @apply hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors;

  .username {
    @apply text-sm font-medium text-gray-700 dark:text-gray-300;
  }

  .dropdown-icon {
    @apply text-xs text-gray-500 dark:text-gray-400 transition-transform;
  }

  &:hover .dropdown-icon {
    @apply transform rotate-180;
  }
}
</style>
