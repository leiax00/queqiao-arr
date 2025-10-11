<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">仪表板</h1>
      <p class="page-subtitle">欢迎使用 Queqiao-arr 中文内容自动化下载代理服务</p>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.successCount }}</div>
          <div class="stat-label">成功下载</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.pendingCount }}</div>
          <div class="stat-label">等待处理</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon error">
          <el-icon><Close /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.failedCount }}</div>
          <div class="stat-label">失败任务</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon info">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalCount }}</div>
          <div class="stat-label">总任务数</div>
        </div>
      </div>
    </div>
    
    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="actions-grid">
        <el-card class="action-card" @click="$router.push('/config/sonarr')">
          <div class="action-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="action-title">配置 Sonarr</div>
          <div class="action-desc">设置 Sonarr 连接参数</div>
        </el-card>
        
        <el-card class="action-card" @click="$router.push('/config/prowlarr')">
          <div class="action-icon">
            <el-icon><Search /></el-icon>
          </div>
          <div class="action-title">配置 Prowlarr</div>
          <div class="action-desc">设置 Prowlarr 索引器</div>
        </el-card>
        
        <el-card class="action-card" @click="$router.push('/config/proxy')">
          <div class="action-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="action-title">代理设置</div>
          <div class="action-desc">配置网络代理参数</div>
        </el-card>
        
        <el-card class="action-card" @click="$router.push('/logs')">
          <div class="action-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="action-title">查看日志</div>
          <div class="action-desc">查看系统运行日志</div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Check, 
  Clock, 
  Close, 
  DataAnalysis, 
  Monitor, 
  Search, 
  Connection, 
  Document 
} from '@element-plus/icons-vue'

const stats = ref({
  successCount: 0,
  pendingCount: 0,
  failedCount: 0,
  totalCount: 0,
})

onMounted(() => {
  // 模拟数据，实际应该从API获取
  stats.value = {
    successCount: 128,
    pendingCount: 5,
    failedCount: 3,
    totalCount: 136,
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  .page-header {
    @apply mb-8;
    
    .page-title {
      @apply text-3xl font-bold text-gray-900 dark:text-white mb-2;
    }
    
    .page-subtitle {
      @apply text-gray-600 dark:text-gray-400;
    }
  }
  
  .stats-grid {
    @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8;
    
    .stat-card {
      @apply macaron-card p-6 flex items-center space-x-4;
      
      .stat-icon {
        @apply w-12 h-12 rounded-lg flex items-center justify-center text-white text-xl;
        
        &.success {
          @apply bg-gradient-to-r from-success-500 to-success-600;
        }
        
        &.warning {
          @apply bg-gradient-to-r from-warning-500 to-warning-600;
        }
        
        &.error {
          @apply bg-gradient-to-r from-error-500 to-error-600;
        }
        
        &.info {
          @apply bg-gradient-to-r from-primary-500 to-secondary-500;
        }
      }
      
      .stat-content {
        .stat-number {
          @apply text-2xl font-bold text-gray-900 dark:text-white;
        }
        
        .stat-label {
          @apply text-sm text-gray-600 dark:text-gray-400;
        }
      }
    }
  }
  
  .quick-actions {
    .section-title {
      @apply text-xl font-semibold text-gray-900 dark:text-white mb-4;
    }
    
    .actions-grid {
      @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6;
      
      .action-card {
        @apply cursor-pointer transition-all duration-200 hover:shadow-soft-lg hover:scale-105;
        @apply text-center p-6;
        @apply bg-white dark:bg-dark-card border border-light-border dark:border-dark-border;
        @apply hover:bg-gray-50 dark:hover:bg-gray-800/50;
        
        .action-icon {
          @apply text-3xl text-primary-600 dark:text-primary-400 mb-3;
          @apply transition-colors duration-200;
        }
        
        .action-title {
          @apply font-semibold text-gray-900 dark:text-gray-100 mb-2;
          @apply transition-colors duration-200;
        }
        
        .action-desc {
          @apply text-sm text-gray-600 dark:text-gray-400;
          @apply transition-colors duration-200;
        }
        
        &:hover {
          .action-icon {
            @apply text-primary-700 dark:text-primary-300;
          }
          
          .action-title {
            @apply text-gray-900 dark:text-white;
          }
          
          .action-desc {
            @apply text-gray-700 dark:text-gray-300;
          }
        }
      }
    }
  }
}
</style>
