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
          <el-form ref="sonarrFormRef" :model="sonarr" :rules="serviceRules" label-width="100px">
            <el-form-item label="服务地址" prop="url">
              <el-input v-model="sonarr.url" placeholder="http://127.0.0.1:8989" />
            </el-form-item>
            <el-form-item label="API 密钥" prop="apiKey">
              <SecretInput v-model="sonarr.apiKey" placeholder="请输入 API Key" :hint="sonarrHint" />
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
              <SecretInput v-model="prowlarr.apiKey" placeholder="请输入 API Key" :hint="prowlarrHint" />
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

      <!-- TMDB 元数据提供商配置 - 与上方服务配置对齐 -->
      <div class="services-grid">
        <ConfigFormCard title="🎬 TMDB 元数据配置" subtitle="配置 The Movie Database API 用于获取影视元数据">
          <el-form ref="tmdbFormRef" :model="tmdb" :rules="tmdbRules" label-width="120px" class="tmdb-form">
            <el-form-item label="API 地址" prop="apiUrl">
              <el-input v-model="tmdb.apiUrl" placeholder="https://api.themoviedb.org/3" />
            </el-form-item>
            <el-form-item label="API 密钥" prop="apiKey">
              <SecretInput v-model="tmdb.apiKey" placeholder="请输入 TMDB API Key" :hint="tmdbHint" />
            </el-form-item>
            <div class="form-row">
              <el-form-item label="语言" prop="language" class="form-row-item">
                <el-select v-model="tmdb.language" placeholder="请选择语言" filterable :loading="tmdbOptionsLoading">
                  <el-option v-for="lang in tmdbLanguages" :key="lang.code" :label="lang.label" :value="lang.code" />
                </el-select>
              </el-form-item>
              <el-form-item label="地区" prop="region" class="form-row-item">
                <el-select v-model="tmdb.region" placeholder="请选择地区" filterable :loading="tmdbOptionsLoading">
                  <el-option v-for="reg in tmdbRegions" :key="reg.code" :label="reg.label" :value="reg.code" />
                </el-select>
              </el-form-item>
            </div>
            <div class="form-row">
              <el-form-item label="包含成人内容" class="form-row-item">
                <el-switch v-model="tmdb.includeAdult" />
              </el-form-item>
              <el-form-item label="启用代理" class="form-row-item">
                <el-switch v-model="tmdb.useProxy" />
              </el-form-item>
            </div>
          </el-form>
          <template #footer>
            <el-button @click="resetTmdb">重置</el-button>
            <el-button 
              type="info" 
              :loading="tmdbTesting" 
              :disabled="!isTmdbValid" 
              @click="testTmdb"
            >
              <el-icon v-if="tmdbTestStatus === 'success'" class="test-status-icon success"><CircleCheck /></el-icon>
              <el-icon v-else-if="tmdbTestStatus === 'error'" class="test-status-icon error"><CircleClose /></el-icon>
              测试连接
            </el-button>
            <el-button type="primary" :loading="tmdbSaving" :disabled="!tmdbChanged || !isTmdbValid" @click="saveTmdb">保存</el-button>
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
            
            <el-form-item label="测试地址" prop="testUrl" class="proxy-test-url">
              <el-input v-model="proxy.testUrl" placeholder="https://www.google.com/generate_204" />
            </el-form-item>

            <el-form-item label="超时时间" prop="timeout" class="proxy-timeout">
              <el-input-number v-model="proxy.timeout" :min="1000" :max="30000" :step="1000" controls-position="right" />
              <span class="unit-hint">毫秒</span>
            </el-form-item>
            
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { InfoFilled, CircleCheck, CircleClose, Refresh } from '@element-plus/icons-vue'
import ConfigFormCard from '@/components/common/ConfigFormCard.vue'
import SecretInput from '@/components/form/SecretInput.vue'
import { configAPI } from '@/api/config'
import type { OverviewResponse, TestConnectionRequest, TmdbOptions } from '@/api/types'

// 代理配置
const proxyFormRef = ref<FormInstance>()
const proxy = reactive({
  address: '',
  testUrl: '',
  timeout: 5000,
})
const proxyInitial = reactive({ ...proxy })

const proxyRules = reactive<FormRules>({
  address: [
    { pattern: /^(https?|socks5):\/\/.+/, message: '请输入有效的代理地址', trigger: 'blur' },
  ],
  testUrl: [
    { pattern: /^(https?:)\/\/.+/, message: '请输入有效的测试地址', trigger: 'blur' },
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
const sonarrHint = ref<string>('已保存的密钥不会回显明文')
const sonarrSaving = ref(false)
const sonarrTesting = ref(false)
const sonarrTestStatus = ref<'success' | 'error' | null>(null)

// Prowlarr
const prowlarrFormRef = ref<FormInstance>()
const prowlarr = reactive<ServiceConfig>(defaultService())
const prowlarrInitial = reactive<ServiceConfig>({ ...prowlarr })
const prowlarrHint = ref<string>('已保存的密钥不会回显明文')
const prowlarrSaving = ref(false)
const prowlarrTesting = ref(false)
const prowlarrTestStatus = ref<'success' | 'error' | null>(null)

// TMDB 元数据提供商配置
interface TmdbConfig {
  apiUrl: string
  apiKey: string
  language: string
  region: string
  includeAdult: boolean
  useProxy: boolean
}

const tmdbFormRef = ref<FormInstance>()
const tmdb = reactive<TmdbConfig>({
  apiUrl: 'https://api.themoviedb.org',
  apiKey: '',
  language: 'zh-CN',
  region: 'CN',
  includeAdult: false,
  useProxy: false,
})
const tmdbInitial = reactive<TmdbConfig>({ ...tmdb })
const tmdbHint = ref<string>('已保存的密钥不会回显明文')
const tmdbSaving = ref(false)
const tmdbTesting = ref(false)
const tmdbTestStatus = ref<'success' | 'error' | null>(null)
const tmdbId = ref<number | null>(null)

// TMDB 选项
const tmdbLanguages = ref<Array<{ code: string; label: string }>>([])
const tmdbRegions = ref<Array<{ code: string; label: string }>>([])
const tmdbOptionsLoading = ref(false)

// TMDB 校验规则
const tmdbRules = reactive<FormRules<TmdbConfig>>({
  apiUrl: [
    { required: true, message: '请输入 API 地址', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的 URL（http:// 或 https://）', trigger: 'blur' },
  ],
  apiKey: [
    {
      validator: (_rule, value: string, callback) => {
        if (tmdbId.value !== null && (!value || value.length === 0)) return callback()
        if (!value || value.length < 8) return callback(new Error('API 密钥长度至少 8 字符'))
        return callback()
      },
      trigger: 'blur',
    },
  ],
  language: [
    { required: true, message: '请选择语言', trigger: 'change' },
  ],
  region: [
    { required: true, message: '请选择地区', trigger: 'change' },
  ],
})

const isTmdbValid = computed(() => 
  !!tmdb.apiUrl &&
  /^https?:\/\/.+/.test(tmdb.apiUrl) &&
  !!tmdb.language && 
  !!tmdb.region && 
  (tmdb.apiKey.length >= 8 || tmdbId.value !== null)
)
const tmdbChanged = computed(() => JSON.stringify(tmdb) !== JSON.stringify(tmdbInitial))

// 服务校验规则
const serviceRules = reactive<FormRules<ServiceConfig>>({
  url: [
    { required: true, message: '请输入服务地址', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的 URL（http:// 或 https://）', trigger: 'blur' },
  ],
  apiKey: [
    {
      validator: (_rule, value: string, callback) => {
        // 若已存在配置（有ID），apiKey 可为空；否则需 >= 8
        const currentId = _rule?.field?.includes('prowlarr') ? prowlarrId.value : sonarrId.value
        if (currentId !== null && (!value || value.length === 0)) return callback()
        if (!value || value.length < 8) return callback(new Error('API 密钥长度至少 8 字符'))
        return callback()
      },
      trigger: 'blur',
    },
  ],
})


// 已有配置ID（用于判断更新/创建、以及按ID测试）
const sonarrId = ref<number | null>(null)
const prowlarrId = ref<number | null>(null)
const proxyId = ref<number | null>(null)

// 计算属性（允许已存在配置但不输入新 API Key 的场景）
const isSonarrValid = computed(() => !!sonarr.url && /^https?:\/\/.+/.test(sonarr.url) && (sonarr.apiKey.length >= 8 || sonarrId.value !== null))
const isProwlarrValid = computed(() => !!prowlarr.url && /^https?:\/\/.+/.test(prowlarr.url) && (prowlarr.apiKey.length >= 8 || prowlarrId.value !== null))
const sonarrChanged = computed(() => JSON.stringify(sonarr) !== JSON.stringify(sonarrInitial))
const prowlarrChanged = computed(() => JSON.stringify(prowlarr) !== JSON.stringify(prowlarrInitial))

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

    if (sonarrSvc) {
      sonarrId.value = sonarrSvc.id
      sonarr.url = sonarrSvc.url || ''
      sonarr.apiKey = '' // 不回显密钥
      if (sonarrSvc.api_key_masked) {
        sonarrHint.value = `已保存：${sonarrSvc.api_key_masked}`
      } else {
        sonarrHint.value = '已保存的密钥不会回显明文'
      }
      // 回显 useProxy
      if (sonarrSvc.extra_config && typeof sonarrSvc.extra_config.useProxy === 'boolean') {
        sonarr.useProxy = !!sonarrSvc.extra_config.useProxy
      }
      Object.assign(sonarrInitial, sonarr)
    }
    if (prowlarrSvc) {
      prowlarrId.value = prowlarrSvc.id
      prowlarr.url = prowlarrSvc.url || ''
      prowlarr.apiKey = ''
      if (prowlarrSvc.api_key_masked) {
        prowlarrHint.value = `已保存：${prowlarrSvc.api_key_masked}`
      } else {
        prowlarrHint.value = '已保存的密钥不会回显明文'
      }
      if (prowlarrSvc.extra_config && typeof prowlarrSvc.extra_config.useProxy === 'boolean') {
        prowlarr.useProxy = !!prowlarrSvc.extra_config.useProxy
      }
      Object.assign(prowlarrInitial, prowlarr)
    }
    if (proxySvc) {
      proxyId.value = proxySvc.id
      proxy.address = proxySvc.url || ''
      if (proxySvc.extra_config) {
        if (typeof proxySvc.extra_config.test_url === 'string') proxy.testUrl = proxySvc.extra_config.test_url
        if (typeof proxySvc.extra_config.timeout_ms === 'number') proxy.timeout = proxySvc.extra_config.timeout_ms
      }
      Object.assign(proxyInitial, proxy)
    }
    if (tmdbSvc) {
      tmdbId.value = tmdbSvc.id
      tmdb.apiUrl = tmdbSvc.url || 'https://api.themoviedb.org/3'
      tmdb.apiKey = ''  // 不回显密钥
      tmdb.language = tmdbSvc.extra_config?.language || 'zh-CN'
      tmdb.region = tmdbSvc.extra_config?.region || 'CN'
      tmdb.includeAdult = tmdbSvc.extra_config?.include_adult || false
      tmdb.useProxy = tmdbSvc.extra_config?.use_proxy || false
      
      if (tmdbSvc.api_key_masked) {
        tmdbHint.value = `已保存：${tmdbSvc.api_key_masked}`
      } else {
        tmdbHint.value = '已保存的密钥不会回显明文'
      }
      
      Object.assign(tmdbInitial, tmdb)
    }
  } catch (e) {
    ElMessage.error('加载配置失败')
  }
}

onMounted(() => {
  loadOverview()
  loadTmdbOptions()
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

// 代理操作
const saveProxy = async () => {
  try {
    await proxyFormRef.value?.validate()
    proxySaving.value = true
    const payload = {
      type: 'service',
      service_name: 'proxy',
      service_type: 'proxy',
      name: '默认',
      url: proxy.address || '',
      extra_config: {
        test_url: proxy.testUrl || undefined,
        timeout_ms: proxy.timeout,
      },
      is_active: true,
    } as const

    if (proxyId.value != null) {
      await configAPI.updateConfig(proxyId.value, {
        url: payload.url,
        extra_config: payload.extra_config,
        is_active: true,
      })
    } else {
      const res = await configAPI.createConfig(payload)
      proxyId.value = res.id
    }
    Object.assign(proxyInitial, proxy)
    ElMessage.success('代理配置保存成功')
  } catch (e) {
    ElMessage.error('代理配置保存失败')
  } finally {
    proxySaving.value = false
  }
}

const testProxy = async () => {
  try {
    await proxyFormRef.value?.validate()
    proxyTesting.value = true
    proxyTestStatus.value = null
    const url = proxy.testUrl || undefined
    const proxies = proxy.address ? { http: proxy.address, https: proxy.address } : undefined
    const timeout_ms = proxy.timeout
    const res = await configAPI.testProxy({ url, proxy: proxies, timeout_ms })
    if (res.ok) {
      proxyTestStatus.value = 'success'
      const latency = res.latency_ms ? `延迟 ${res.latency_ms}ms` : res.details
      ElMessage.success({ message: `代理连通性测试成功！${latency}`, duration: 3000 })
    } else {
      proxyTestStatus.value = 'error'
      ElMessage.error({ message: `代理连接失败：${res.details}`, duration: 4000 })
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
    const payloadBase = {
      url: sonarr.url,
      extra_config: { useProxy: sonarr.useProxy },
      is_active: true,
    } as any

    if (sonarr.apiKey) payloadBase.api_key = sonarr.apiKey

    if (sonarrId.value != null) {
      await configAPI.updateConfig(sonarrId.value, payloadBase)
    } else {
      const res = await configAPI.createConfig({
        type: 'service',
        service_name: 'sonarr',
        service_type: 'api',
        name: '默认',
        url: sonarr.url,
        api_key: sonarr.apiKey || undefined,
        extra_config: { useProxy: sonarr.useProxy },
        is_active: true,
      })
      sonarrId.value = res.id
    }
    Object.assign(sonarrInitial, sonarr)
    ElMessage.success('Sonarr 配置保存成功')
  } catch (e) {
    ElMessage.error('Sonarr 配置保存失败')
  } finally {
    sonarrSaving.value = false
  }
}

const testSonarr = async () => {
  try {
    await sonarrFormRef.value?.validate()
    sonarrTesting.value = true
    sonarrTestStatus.value = null
    let body: TestConnectionRequest
    if (!sonarr.apiKey && sonarrId.value != null) {
      body = { mode: 'by_id', id: sonarrId.value }
    } else {
      body = {
        mode: 'by_body',
        service_name: 'sonarr',
        url: sonarr.url,
        api_key: sonarr.apiKey || undefined,
      }
      if (sonarr.useProxy && proxy.address) {
        ;(body as any).proxy = { http: proxy.address, https: proxy.address }
      }
    }
    const res = await configAPI.testConnection(body)
    if (res.ok) {
      sonarrTestStatus.value = 'success'
      ElMessage.success({ message: `Sonarr 连接成功！${res.details}`, duration: 3000 })
    } else {
      sonarrTestStatus.value = 'error'
      ElMessage.error({ message: `Sonarr 连接失败：${res.details}`, duration: 4000 })
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
    const payloadBase = {
      url: prowlarr.url,
      extra_config: { useProxy: prowlarr.useProxy },
      is_active: true,
    } as any
    if (prowlarr.apiKey) payloadBase.api_key = prowlarr.apiKey

    if (prowlarrId.value != null) {
      await configAPI.updateConfig(prowlarrId.value, payloadBase)
    } else {
      const res = await configAPI.createConfig({
        type: 'service',
        service_name: 'prowlarr',
        service_type: 'api',
        name: '默认',
        url: prowlarr.url,
        api_key: prowlarr.apiKey || undefined,
        extra_config: { useProxy: prowlarr.useProxy },
        is_active: true,
      })
      prowlarrId.value = res.id
    }
    Object.assign(prowlarrInitial, prowlarr)
    ElMessage.success('Prowlarr 配置保存成功')
  } catch (e) {
    ElMessage.error('Prowlarr 配置保存失败')
  } finally {
    prowlarrSaving.value = false
  }
}

const testProwlarr = async () => {
  try {
    await prowlarrFormRef.value?.validate()
    prowlarrTesting.value = true
    prowlarrTestStatus.value = null
    let body: TestConnectionRequest
    if (!prowlarr.apiKey && prowlarrId.value != null) {
      body = { mode: 'by_id', id: prowlarrId.value }
    } else {
      body = {
        mode: 'by_body',
        service_name: 'prowlarr',
        url: prowlarr.url,
        api_key: prowlarr.apiKey || undefined,
      }
      if (prowlarr.useProxy && proxy.address) {
        ;(body as any).proxy = { http: proxy.address, https: proxy.address }
      }
    }
    const res = await configAPI.testConnection(body)
    if (res.ok) {
      prowlarrTestStatus.value = 'success'
      ElMessage.success({ message: `Prowlarr 连接成功！${res.details}`, duration: 3000 })
    } else {
      prowlarrTestStatus.value = 'error'
      ElMessage.error({ message: `Prowlarr 连接失败：${res.details}`, duration: 4000 })
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

// TMDB 操作
const loadTmdbOptions = async () => {
  try {
    tmdbOptionsLoading.value = true
    const options: TmdbOptions = await configAPI.getTmdbOptions()
    tmdbLanguages.value = options.languages
    tmdbRegions.value = options.regions
  } catch (e) {
    ElMessage.error('加载 TMDB 选项失败')
  } finally {
    tmdbOptionsLoading.value = false
  }
}


const saveTmdb = async () => {
  try {
    await tmdbFormRef.value?.validate()
    tmdbSaving.value = true
    
    const payload: any = {
      url: tmdb.apiUrl,
      language: tmdb.language,
      region: tmdb.region,
      include_adult: tmdb.includeAdult,
      use_proxy: tmdb.useProxy,
    }
    
    // 只有在用户修改了 API Key 时才提交
    if (tmdb.apiKey) {
      payload.api_key = tmdb.apiKey
    }
    
    let res: { id: number }
    if (tmdbId.value === null) {
      // 创建新配置
      res = await configAPI.createTmdbConfig(payload)
      tmdbId.value = res.id
    } else {
      // 更新已有配置
      res = await configAPI.updateTmdbConfig(tmdbId.value, payload)
    }
    
    // 保存成功后重新加载配置以获取最新的掩码
    await loadOverview()
    
    ElMessage.success('TMDB 配置保存成功')
  } catch (e: any) {
    ElMessage.error(e.message || 'TMDB 配置保存失败')
  } finally {
    tmdbSaving.value = false
  }
}

const testTmdb = async () => {
  try {
    await tmdbFormRef.value?.validate()
    tmdbTesting.value = true
    tmdbTestStatus.value = null
    
    let body: TestConnectionRequest
    
    // 如果已有配置且用户未输入新密钥，使用 by_id 模式（后端会自动从数据库读取密钥）
    if (tmdbId.value !== null && !tmdb.apiKey) {
      body = { 
        mode: 'by_id', 
        id: tmdbId.value 
      }
    } else {
      // 否则使用 by_body 模式（新配置或用户重新输入了密钥）
      body = {
        mode: 'by_body',
        service_name: 'tmdb',
        url: tmdb.apiUrl,
        api_key: tmdb.apiKey || undefined,
      }
      
      // 如果启用代理且代理地址存在，添加代理配置
      if (tmdb.useProxy && proxy.address) {
        ;(body as any).proxy = { http: proxy.address, https: proxy.address }
      }
    }
    
    const res = await configAPI.testConnection(body)
    if (res.ok) {
      tmdbTestStatus.value = 'success'
      const latency = (res as any).latency_ms ? `延迟 ${(res as any).latency_ms}ms` : ''
      ElMessage.success({ 
        message: `TMDB 连接成功！${res.details} ${latency}`, 
        duration: 3000 
      })
    } else {
      tmdbTestStatus.value = 'error'
      ElMessage.error({ 
        message: `TMDB 连接失败：${res.details}`, 
        duration: 4000 
      })
    }
  } catch (e: any) {
    tmdbTestStatus.value = 'error'
    ElMessage.error(e.message || '请先完善 TMDB 配置')
  } finally {
    tmdbTesting.value = false
  }
}

const resetTmdb = () => {
  Object.assign(tmdb, tmdbInitial)
  tmdbFormRef.value?.clearValidate()
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

