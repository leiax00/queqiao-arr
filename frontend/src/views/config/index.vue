<template>
  <div class="config-page">
    <div class="page-header">
      <h1 class="page-title">配置中心</h1>
      <p class="page-subtitle">快速配置 Sonarr、Prowlarr 与网络代理</p>
    </div>

    <div class="config-layout">
      <!-- 服务配置 - 两列 -->
      <div class="services-grid">
        <!-- Sonarr -->
        <ConfigFormCard title="📺 Sonarr 配置" subtitle="配置 Sonarr 服务连接">
          <el-form ref="sonarrFormRef" :model="sonarr" :rules="serviceRules" label-width="100px">
            <el-form-item label="服务地址" prop="url">
              <el-input v-model="sonarr.url" placeholder="http://127.0.0.1:8989" />
            </el-form-item>
            <el-form-item label="API 密钥" prop="apiKey">
              <SecretInput v-model="sonarr.apiKey" placeholder="请输入 API Key" hint="已保存的密钥不会回显明文" />
            </el-form-item>
            <el-form-item label="启用代理">
              <el-switch v-model="sonarr.useProxy" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="resetSonarr">重置</el-button>
            <el-button 
              type="info" 
              :loading="sonarrTesting" 
              :disabled="!isSonarrValid" 
              @click="testSonarr"
            >
              <el-icon v-if="sonarrTestStatus === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
              <el-icon v-else-if="sonarrTestStatus === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
              测试连接
            </el-button>
            <el-button type="primary" :loading="sonarrSaving" :disabled="!sonarrChanged || !isSonarrValid" @click="saveSonarr">保存</el-button>
          </template>
        </ConfigFormCard>

        <!-- Prowlarr -->
        <ConfigFormCard title="🔍 Prowlarr 配置" subtitle="配置 Prowlarr 索引器连接">
          <el-form ref="prowlarrFormRef" :model="prowlarr" :rules="serviceRules" label-width="100px">
            <el-form-item label="服务地址" prop="url">
              <el-input v-model="prowlarr.url" placeholder="http://127.0.0.1:9696" />
            </el-form-item>
            <el-form-item label="API 密钥" prop="apiKey">
              <SecretInput v-model="prowlarr.apiKey" placeholder="请输入 API Key" hint="已保存的密钥不会回显明文" />
            </el-form-item>
            <el-form-item label="启用代理">
              <el-switch v-model="prowlarr.useProxy" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="resetProwlarr">重置</el-button>
            <el-button 
              type="info" 
              :loading="prowlarrTesting" 
              :disabled="!isProwlarrValid" 
              @click="testProwlarr"
            >
              <el-icon v-if="prowlarrTestStatus === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
              <el-icon v-else-if="prowlarrTestStatus === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
              测试连接
            </el-button>
            <el-button type="primary" :loading="prowlarrSaving" :disabled="!prowlarrChanged || !isProwlarrValid" @click="saveProwlarr">保存</el-button>
          </template>
        </ConfigFormCard>
      </div>

      <!-- 代理配置 - 单行 -->
      <ConfigFormCard class="proxy-card" title="🌐 网络代理配置" subtitle="配置全局代理服务器，服务配置可选择是否使用">
        <el-form ref="proxyFormRef" :model="proxy" :rules="proxyRules" label-width="100px" class="proxy-form">
          <div class="proxy-form-grid">
            <el-form-item label="代理地址" prop="address" class="proxy-address">
              <el-input v-model="proxy.address" placeholder="http://127.0.0.1:7890" />
            </el-form-item>
            
            <div class="proxy-meta">
              <el-form-item label="代理类型" prop="type" class="proxy-type">
                <el-select v-model="proxy.type" placeholder="选择代理协议">
                  <el-option label="HTTP" value="http" />
                  <el-option label="HTTPS" value="https" />
                  <el-option label="SOCKS5" value="socks5" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="超时时间" prop="timeout" class="proxy-timeout">
                <el-input-number v-model="proxy.timeout" :min="1000" :max="30000" :step="1000" controls-position="right" />
                <span class="unit-hint">毫秒</span>
              </el-form-item>
            </div>
            
            <div class="proxy-hint">
              <el-icon><InfoFilled /></el-icon>
              <span>代理将用于 TMDB 元数据获取、索引器搜索等外网访问。留空则直连。</span>
            </div>
          </div>
        </el-form>
        <template #footer>
          <el-button @click="resetProxy">重置</el-button>
          <el-button 
            type="info" 
            :loading="proxyTesting" 
            :disabled="!proxy.address" 
            @click="testProxy"
          >
            <el-icon v-if="proxyTestStatus === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
            <el-icon v-else-if="proxyTestStatus === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
            测试连接
          </el-button>
          <el-button type="primary" :loading="proxySaving" :disabled="!proxyChanged" @click="saveProxy">保存配置</el-button>
        </template>
      </ConfigFormCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Link, InfoFilled, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import ConfigFormCard from '@/components/common/ConfigFormCard.vue'
import SecretInput from '@/components/form/SecretInput.vue'

// 代理配置
const proxyFormRef = ref<FormInstance>()
const proxy = reactive({
  address: '',
  type: 'http' as 'http' | 'https' | 'socks5',
  timeout: 5000,
})
const proxyInitial = reactive({ ...proxy })

const proxyRules = reactive<FormRules>({
  address: [
    { pattern: /^(https?|socks5):\/\/.+/, message: '请输入有效的代理地址', trigger: 'blur' },
  ],
  timeout: [
    { type: 'number', min: 1000, max: 30000, message: '超时时间应在 1-30 秒之间', trigger: 'change' },
  ],
})

const proxySaving = ref(false)
const proxyTesting = ref(false)
const proxyTestStatus = ref<'success' | 'error' | null>(null)
const proxyChanged = computed(() => JSON.stringify(proxy) !== JSON.stringify(proxyInitial))

// 服务配置通用结构
interface ServiceConfig {
  url: string
  apiKey: string
  useProxy: boolean
}

const defaultService = (): ServiceConfig => ({
  url: '',
  apiKey: '',
  useProxy: false,
})

// Sonarr
const sonarrFormRef = ref<FormInstance>()
const sonarr = reactive<ServiceConfig>(defaultService())
const sonarrInitial = reactive<ServiceConfig>({ ...sonarr })
const sonarrSaving = ref(false)
const sonarrTesting = ref(false)
const sonarrTestStatus = ref<'success' | 'error' | null>(null)

// Prowlarr
const prowlarrFormRef = ref<FormInstance>()
const prowlarr = reactive<ServiceConfig>(defaultService())
const prowlarrInitial = reactive<ServiceConfig>({ ...prowlarr })
const prowlarrSaving = ref(false)
const prowlarrTesting = ref(false)
const prowlarrTestStatus = ref<'success' | 'error' | null>(null)

// 服务校验规则
const serviceRules = reactive<FormRules<ServiceConfig>>({
  url: [
    { required: true, message: '请输入服务地址', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的 URL（http:// 或 https://）', trigger: 'blur' },
  ],
  apiKey: [
    { required: true, message: '请输入 API 密钥', trigger: 'blur' },
    { min: 8, message: 'API 密钥长度至少 8 字符', trigger: 'blur' },
  ],
})


// 计算属性
const isSonarrValid = computed(() => !!sonarr.url && /^https?:\/\/.+/.test(sonarr.url) && sonarr.apiKey.length >= 8)
const isProwlarrValid = computed(() => !!prowlarr.url && /^https?:\/\/.+/.test(prowlarr.url) && prowlarr.apiKey.length >= 8)
const sonarrChanged = computed(() => JSON.stringify(sonarr) !== JSON.stringify(sonarrInitial))
const prowlarrChanged = computed(() => JSON.stringify(prowlarr) !== JSON.stringify(prowlarrInitial))

// 代理操作
const saveProxy = async () => {
  try {
    await proxyFormRef.value?.validate()
    proxySaving.value = true
    await new Promise(r => setTimeout(r, 800))
    Object.assign(proxyInitial, proxy)
    ElMessage.success('代理配置保存成功')
  } finally {
    proxySaving.value = false
  }
}

const testProxy = async () => {
  try {
    await proxyFormRef.value?.validate()
    proxyTesting.value = true
    proxyTestStatus.value = null
    await new Promise(r => setTimeout(r, 1500))
    // 模拟随机成功/失败
    const success = Math.random() > 0.3
    if (success) {
      proxyTestStatus.value = 'success'
      ElMessage.success({
        message: '代理连通性测试成功！延迟 210ms',
        duration: 3000,
      })
    } else {
      proxyTestStatus.value = 'error'
      ElMessage.error({
        message: '代理连接失败，请检查代理地址和网络连接',
        duration: 4000,
      })
    }
  } catch (e) {
    proxyTestStatus.value = 'error'
    ElMessage.error('请先完善代理配置')
  } finally {
    proxyTesting.value = false
  }
}

const resetProxy = () => {
  Object.assign(proxy, proxyInitial)
  proxyFormRef.value?.clearValidate()
}

// Sonarr 操作
const saveSonarr = async () => {
  try {
    await sonarrFormRef.value?.validate()
    sonarrSaving.value = true
    await new Promise(r => setTimeout(r, 800))
    Object.assign(sonarrInitial, sonarr)
    ElMessage.success('Sonarr 配置保存成功')
  } finally {
    sonarrSaving.value = false
  }
}

const testSonarr = async () => {
  try {
    await sonarrFormRef.value?.validate()
    sonarrTesting.value = true
    sonarrTestStatus.value = null
    await new Promise(r => setTimeout(r, 1200))
    // 模拟随机成功/失败
    const success = Math.random() > 0.2
    if (success) {
      sonarrTestStatus.value = 'success'
      ElMessage.success({
        message: 'Sonarr 连接成功！版本 v3.0.10，延迟 123ms',
        duration: 3000,
      })
    } else {
      sonarrTestStatus.value = 'error'
      ElMessage.error({
        message: 'Sonarr 连接失败，请检查服务地址和 API 密钥',
        duration: 4000,
      })
    }
  } catch (e) {
    sonarrTestStatus.value = 'error'
    ElMessage.error('请先完善 Sonarr 配置')
  } finally {
    sonarrTesting.value = false
  }
}

const resetSonarr = () => {
  Object.assign(sonarr, sonarrInitial)
  sonarrFormRef.value?.clearValidate()
}

// Prowlarr 操作
const saveProwlarr = async () => {
  try {
    await prowlarrFormRef.value?.validate()
    prowlarrSaving.value = true
    await new Promise(r => setTimeout(r, 800))
    Object.assign(prowlarrInitial, prowlarr)
    ElMessage.success('Prowlarr 配置保存成功')
  } finally {
    prowlarrSaving.value = false
  }
}

const testProwlarr = async () => {
  try {
    await prowlarrFormRef.value?.validate()
    prowlarrTesting.value = true
    prowlarrTestStatus.value = null
    await new Promise(r => setTimeout(r, 1200))
    // 模拟随机成功/失败
    const success = Math.random() > 0.2
    if (success) {
      prowlarrTestStatus.value = 'success'
      ElMessage.success({
        message: 'Prowlarr 连接成功！版本 v1.10.5，延迟 156ms',
        duration: 3000,
      })
    } else {
      prowlarrTestStatus.value = 'error'
      ElMessage.error({
        message: 'Prowlarr 连接失败，请检查服务地址和 API 密钥',
        duration: 4000,
      })
    }
  } catch (e) {
    prowlarrTestStatus.value = 'error'
    ElMessage.error('请先完善 Prowlarr 配置')
  } finally {
    prowlarrTesting.value = false
  }
}

const resetProwlarr = () => {
  Object.assign(prowlarr, prowlarrInitial)
  prowlarrFormRef.value?.clearValidate()
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
        grid-template-columns: 1fr 1fr;
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
          display: flex;
          gap: 12px;

          @media (max-width: 1200px) {
            flex-direction: column;
            gap: 0;
          }

          .proxy-type,
          .proxy-timeout {
            flex: 1;
            min-width: 0;
          }

          .proxy-timeout {
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

