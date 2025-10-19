<template>
  <div class="config-page">
    <div class="page-header">
      <h1 class="page-title">配置中心</h1>
      <p class="page-subtitle">快速配置 Sonarr、Prowlarr 与网络代理</p>
      <div class="page-actions">
        <el-button :loading="refreshing" @click="refreshConfigs">
          <el-icon style="margin-right: 4px"><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="config-layout">
      <!-- 服务配置 - 两列 -->
      <div class="services-grid">
        <!-- Sonarr -->
        <ConfigFormCard title="📺 Sonarr 配置" subtitle="配置 Sonarr 服务连接">
          <el-form ref="sonarrFormRef" :model="sonarr.config" :rules="sonarr.serviceRules" label-width="100px">
            <el-form-item label="服务地址" prop="url">
              <el-input v-model="sonarr.config.url" placeholder="http://127.0.0.1:8989" />
            </el-form-item>
            <el-form-item label="API 密钥" prop="apiKey">
              <SecretInput v-model="sonarr.config.apiKey" placeholder="请输入 API Key" :hint="sonarr.hint.value" />
            </el-form-item>
            <el-form-item label="启用代理">
              <el-switch v-model="sonarr.config.useProxy" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="sonarr.reset">重置</el-button>
            <el-button 
              type="info" 
              :loading="sonarr.testing.value" 
              :disabled="!sonarr.isValid.value" 
              @click="sonarr.test(proxyConfig.proxy.address)"
            >
              <el-icon v-if="sonarr.testStatus.value === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
              <el-icon v-else-if="sonarr.testStatus.value === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
              测试连接
            </el-button>
            <el-button type="primary" :loading="sonarr.saving.value" :disabled="!sonarr.changed.value || !sonarr.isValid.value" @click="sonarr.save">保存</el-button>
          </template>
        </ConfigFormCard>

        <!-- Prowlarr -->
        <ConfigFormCard title="🔍 Prowlarr 配置" subtitle="配置 Prowlarr 索引器连接">
          <el-form ref="prowlarrFormRef" :model="prowlarr.config" :rules="prowlarr.serviceRules" label-width="100px">
            <el-form-item label="服务地址" prop="url">
              <el-input v-model="prowlarr.config.url" placeholder="http://127.0.0.1:9696" />
            </el-form-item>
            <el-form-item label="API 密钥" prop="apiKey">
              <SecretInput v-model="prowlarr.config.apiKey" placeholder="请输入 API Key" :hint="prowlarr.hint.value" />
            </el-form-item>
            <el-form-item label="启用代理">
              <el-switch v-model="prowlarr.config.useProxy" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="prowlarr.reset">重置</el-button>
            <el-button 
              type="info" 
              :loading="prowlarr.testing.value" 
              :disabled="!prowlarr.isValid.value" 
              @click="prowlarr.test(proxyConfig.proxy.address)"
            >
              <el-icon v-if="prowlarr.testStatus.value === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
              <el-icon v-else-if="prowlarr.testStatus.value === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
              测试连接
            </el-button>
            <el-button type="primary" :loading="prowlarr.saving.value" :disabled="!prowlarr.changed.value || !prowlarr.isValid.value" @click="prowlarr.save">保存</el-button>
          </template>
        </ConfigFormCard>
      </div>

      <!-- TMDB 元数据提供商配置 - 与上方服务配置对齐 -->
      <div class="services-grid">
        <ConfigFormCard title="🎬 TMDB 元数据配置" subtitle="配置 The Movie Database API 用于获取影视元数据">
          <el-form ref="tmdbFormRef" :model="tmdbConfig.tmdb" :rules="tmdbConfig.tmdbRules" label-width="120px" class="tmdb-form">
            <el-form-item label="API 地址" prop="apiUrl">
              <el-input v-model="tmdbConfig.tmdb.apiUrl" placeholder="https://api.themoviedb.org/3" />
            </el-form-item>
            <el-form-item label="API 密钥" prop="apiKey">
              <SecretInput v-model="tmdbConfig.tmdb.apiKey" placeholder="请输入 TMDB API Key" :hint="tmdbConfig.tmdbHint.value" />
            </el-form-item>
            <div class="form-row">
              <el-form-item label="语言" prop="language" class="form-row-item">
                <el-select v-model="tmdbConfig.tmdb.language" placeholder="请选择语言" filterable :loading="tmdbConfig.tmdbOptionsLoading.value">
                  <el-option v-for="lang in tmdbConfig.tmdbLanguages.value" :key="lang.code" :label="lang.label" :value="lang.code" />
                </el-select>
              </el-form-item>
              <el-form-item label="地区" prop="region" class="form-row-item">
                <el-select v-model="tmdbConfig.tmdb.region" placeholder="请选择地区" filterable :loading="tmdbConfig.tmdbOptionsLoading.value">
                  <el-option v-for="reg in tmdbConfig.tmdbRegions.value" :key="reg.code" :label="reg.label" :value="reg.code" />
                </el-select>
              </el-form-item>
            </div>
            <div class="form-row">
              <el-form-item label="包含成人内容" class="form-row-item">
                <el-switch v-model="tmdbConfig.tmdb.includeAdult" />
              </el-form-item>
              <el-form-item label="启用代理" class="form-row-item">
                <el-switch v-model="tmdbConfig.tmdb.useProxy" />
              </el-form-item>
            </div>
          </el-form>
          <template #footer>
            <el-button @click="tmdbConfig.resetTmdb">重置</el-button>
            <el-button 
              type="info" 
              :loading="tmdbConfig.tmdbTesting.value" 
              :disabled="!tmdbConfig.isTmdbValid.value" 
              @click="tmdbConfig.testTmdb(proxyConfig.proxy.address)"
            >
              <el-icon v-if="tmdbConfig.tmdbTestStatus.value === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
              <el-icon v-else-if="tmdbConfig.tmdbTestStatus.value === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
              测试连接
            </el-button>
            <el-button type="primary" :loading="tmdbConfig.tmdbSaving.value" :disabled="!tmdbConfig.tmdbChanged.value || !tmdbConfig.isTmdbValid.value" @click="tmdbConfig.saveTmdb(loadOverview)">保存</el-button>
          </template>
        </ConfigFormCard>
      </div>

      <!-- 代理配置 - 单行 -->
      <ConfigFormCard class="proxy-card" title="🌐 网络代理配置" subtitle="配置全局代理服务器，服务配置可选择是否使用">
        <el-form ref="proxyFormRef" :model="proxyConfig.proxy" :rules="proxyConfig.proxyRules" label-width="100px" class="proxy-form">
          <div class="proxy-form-grid">
            <el-form-item label="代理地址" prop="address" class="proxy-address">
              <el-input v-model="proxyConfig.proxy.address" placeholder="http://127.0.0.1:7890" />
            </el-form-item>
            
            <el-form-item label="测试地址" prop="testUrl" class="proxy-test-url">
              <el-input v-model="proxyConfig.proxy.testUrl" placeholder="https://www.google.com/generate_204" />
            </el-form-item>

            <el-form-item label="超时时间" prop="timeout" class="proxy-timeout">
              <el-input-number v-model="proxyConfig.proxy.timeout" :min="1000" :max="30000" :step="1000" controls-position="right" />
              <span class="unit-hint">毫秒</span>
            </el-form-item>
            
            <div class="proxy-hint">
              <el-icon><InfoFilled /></el-icon>
              <span>代理将用于 TMDB 元数据获取、索引器搜索等外网访问。留空则直连。</span>
            </div>
          </div>
        </el-form>
        <template #footer>
          <el-button @click="proxyConfig.resetProxy">重置</el-button>
          <el-button 
            type="info" 
            :loading="proxyConfig.proxyTesting.value" 
            :disabled="!proxyConfig.proxy.address" 
            @click="proxyConfig.testProxy"
          >
            <el-icon v-if="proxyConfig.proxyTestStatus.value === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
            <el-icon v-else-if="proxyConfig.proxyTestStatus.value === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
            测试连接
          </el-button>
          <el-button type="primary" :loading="proxyConfig.proxySaving.value" :disabled="!proxyConfig.proxyChanged.value" @click="proxyConfig.saveProxy">保存配置</el-button>
        </template>
      </ConfigFormCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, CircleCheck, CircleClose, Refresh } from '@element-plus/icons-vue'
import ConfigFormCard from '@/components/common/ConfigFormCard.vue'
import SecretInput from '@/components/form/SecretInput.vue'
import { configAPI } from '@/api/config'
import type { OverviewResponse } from '@/api/types'
import { useProxyConfig } from '@/composables/useProxyConfig'
import { useServiceConfig } from '@/composables/useServiceConfig'
import { useTmdbConfig } from '@/composables/useTmdbConfig'

// 使用组合式函数管理各个配置模块
const proxyConfig = useProxyConfig()
const sonarr = useServiceConfig('sonarr')
const prowlarr = useServiceConfig('prowlarr')
const tmdbConfig = useTmdbConfig()

// 拉取概览并填充表单
const loadOverview = async () => {
  try {
    const data: OverviewResponse = await configAPI.getOverview()
    // 服务配置
    const svc = (name: 'sonarr' | 'prowlarr' | 'proxy' | 'tmdb') => data.services.find(s => s.service_name === name) || null
    
    const sonarrSvc = svc('sonarr')
    const prowlarrSvc = svc('prowlarr')
    const proxySvc = svc('proxy')
    const tmdbSvc = svc('tmdb')

    // 加载各个配置
    sonarr.loadConfig(sonarrSvc)
    prowlarr.loadConfig(prowlarrSvc)
    proxyConfig.loadProxyConfig(proxySvc)
    tmdbConfig.loadTmdbConfig(tmdbSvc)
  } catch (e) {
    ElMessage.error('加载配置失败')
  }
}

onMounted(() => {
  loadOverview()
  tmdbConfig.loadTmdbOptions()
})

// 刷新配置
const refreshing = ref(false)
const refreshConfigs = async () => {
  try {
    refreshing.value = true
    await loadOverview()
    ElMessage.success('配置已刷新')
  } finally {
    refreshing.value = false
  }
}
</script>

<style lang="scss" scoped>
.config-page {
  .page-header {
    @apply mb-6;
    
    .page-title {
      @apply text-2xl font-bold text-gray-900 dark:text-white mb-2;
    }
    
    .page-subtitle {
      @apply text-gray-600 dark:text-gray-400;
    }
  }

  .config-layout {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .proxy-card {
    width: 100%;

    .proxy-form {
      .proxy-form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr auto;
            gap: 20px 16px;
            align-items: flex-start;

        @media (max-width: 1200px) {
              grid-template-columns: 1fr;
        }

        .proxy-address {
          grid-column: span 1;
        }

        .proxy-meta {
              grid-column: span 1;
        }

            .proxy-test-url { grid-column: span 1; }

            .proxy-timeout {
              grid-column: span 1;
              min-width: 260px;
              :deep(.el-form-item__content) {
                display: flex;
                align-items: center;
                gap: 8px;
              }

              .unit-hint {
                color: #64748b;
                font-size: 14px;
                white-space: nowrap;
              }
            }

        .proxy-hint {
          grid-column: 1 / -1;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          color: #475569;
          font-size: 14px;
          line-height: 1.6;

          .el-icon {
            flex-shrink: 0;
            font-size: 16px;
            color: #64748b;
          }
        }
      }
    }
  }

  .services-grid {
    display: grid;
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 20px;

    @media (min-width: 1024px) {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .tmdb-form {
    .form-row {
      display: grid;
      grid-template-columns: repeat(1, minmax(0, 1fr));
      gap: 0 20px;

      @media (min-width: 768px) {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .form-row-item {
        margin-bottom: 18px;
      }
    }
  }
}

:deep(.el-form-item__label) {
  @apply font-medium;
}

.test-status-icon {
  margin-right: 4px;
  
  &.success {
    color: var(--el-color-success);
  }
  
  &.error {
    color: var(--el-color-danger);
  }
}
</style>

<style lang="scss">
// 深色模式优化（非 scoped，使其生效）
.dark .proxy-hint {
  background: rgba(30, 41, 59, 0.5) !important;
  border-color: rgba(51, 65, 85, 0.6) !important;
  color: #cbd5e1 !important;
  
  .el-icon {
    color: #94a3b8 !important;
  }
}

.dark .unit-hint {
  color: #94a3b8 !important;
}
</style>
