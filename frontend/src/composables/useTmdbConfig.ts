import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { configAPI } from '@/api/config'
import type { ServiceConfigOut, TestConnectionRequest, TmdbOptions } from '@/api/types'

interface TmdbConfig {
  apiUrl: string
  apiKey: string
  language: string
  region: string
  includeAdult: boolean
  useProxy: boolean
}

export function useTmdbConfig() {
  const tmdbFormRef = ref<FormInstance>()
  const tmdb = reactive<TmdbConfig>({
    apiUrl: 'https://api.themoviedb.org/3',
    apiKey: '',
    language: 'zh-CN',
    region: 'CN',
    includeAdult: false,
    useProxy: false,
  })
  const tmdbInitial = reactive<TmdbConfig>({ ...tmdb })
  const tmdbHint = ref<string>('已保存的密钥不会回显明文')
  const tmdbId = ref<number | null>(null)
  const tmdbSaving = ref(false)
  const tmdbTesting = ref(false)
  const tmdbTestStatus = ref<'success' | 'error' | null>(null)

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

  const loadTmdbConfig = (tmdbSvc: ServiceConfigOut | null) => {
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
  }

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

  const saveTmdb = async (onSuccess?: () => Promise<void>) => {
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
      if (onSuccess) {
        await onSuccess()
      }
      
      ElMessage.success('TMDB 配置保存成功')
    } catch (e: any) {
      ElMessage.error(e.message || 'TMDB 配置保存失败')
    } finally {
      tmdbSaving.value = false
    }
  }

  const testTmdb = async (proxyAddress?: string) => {
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
        if (tmdb.useProxy && proxyAddress) {
          ;(body as any).proxy = { http: proxyAddress, https: proxyAddress }
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

  return {
    // 数据
    tmdbFormRef,
    tmdb,
    tmdbInitial,
    tmdbHint,
    tmdbId,
    tmdbSaving,
    tmdbTesting,
    tmdbTestStatus,
    tmdbLanguages,
    tmdbRegions,
    tmdbOptionsLoading,
    tmdbRules,
    isTmdbValid,
    tmdbChanged,
    // 方法
    loadTmdbConfig,
    loadTmdbOptions,
    saveTmdb,
    testTmdb,
    resetTmdb,
  }
}

