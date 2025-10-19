import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { configAPI } from '@/api/config'
import type { ServiceConfigOut, TestConnectionRequest } from '@/api/types'

interface ServiceConfig {
  url: string
  apiKey: string
  useProxy: boolean
}

export function useServiceConfig(serviceName: 'sonarr' | 'prowlarr') {
  const formRef = ref<FormInstance>()
  const config = reactive<ServiceConfig>({
    url: '',
    apiKey: '',
    useProxy: false,
  })
  const initialConfig = reactive<ServiceConfig>({ ...config })
  const hint = ref<string>('已保存的密钥不会回显明文')
  const configId = ref<number | null>(null)
  const saving = ref(false)
  const testing = ref(false)
  const testStatus = ref<'success' | 'error' | null>(null)

  const serviceRules = reactive<FormRules<ServiceConfig>>({
    url: [
      { required: true, message: '请输入服务地址', trigger: 'blur' },
      { pattern: /^https?:\/\/.+/, message: '请输入有效的 URL（http:// 或 https://）', trigger: 'blur' },
    ],
    apiKey: [
      {
        validator: (_rule, value: string, callback) => {
          if (configId.value !== null && (!value || value.length === 0)) return callback()
          if (!value || value.length < 8) return callback(new Error('API 密钥长度至少 8 字符'))
          return callback()
        },
        trigger: 'blur',
      },
    ],
  })

  const isValid = computed(() => 
    !!config.url && 
    /^https?:\/\/.+/.test(config.url) && 
    (config.apiKey.length >= 8 || configId.value !== null)
  )
  const changed = computed(() => JSON.stringify(config) !== JSON.stringify(initialConfig))

  const loadConfig = (svc: ServiceConfigOut | null) => {
    if (svc) {
      configId.value = svc.id
      config.url = svc.url || ''
      config.apiKey = ''
      if (svc.api_key_masked) {
        hint.value = `已保存：${svc.api_key_masked}`
      } else {
        hint.value = '已保存的密钥不会回显明文'
      }
      if (svc.extra_config && typeof svc.extra_config.useProxy === 'boolean') {
        config.useProxy = !!svc.extra_config.useProxy
      }
      Object.assign(initialConfig, config)
    }
  }

  const save = async () => {
    try {
      await formRef.value?.validate()
      saving.value = true
      const payloadBase = {
        url: config.url,
        extra_config: { useProxy: config.useProxy },
        is_active: true,
      } as any

      if (config.apiKey) payloadBase.api_key = config.apiKey

      if (configId.value != null) {
        await configAPI.updateConfig(configId.value, payloadBase)
      } else {
        const res = await configAPI.createConfig({
          type: 'service',
          service_name: serviceName,
          service_type: 'api',
          name: '默认',
          url: config.url,
          api_key: config.apiKey || undefined,
          extra_config: { useProxy: config.useProxy },
          is_active: true,
        })
        configId.value = res.id
      }
      Object.assign(initialConfig, config)
      ElMessage.success(`${serviceName === 'sonarr' ? 'Sonarr' : 'Prowlarr'} 配置保存成功`)
    } catch (e) {
      ElMessage.error(`${serviceName === 'sonarr' ? 'Sonarr' : 'Prowlarr'} 配置保存失败`)
    } finally {
      saving.value = false
    }
  }

  const test = async (proxyAddress?: string) => {
    try {
      await formRef.value?.validate()
      testing.value = true
      testStatus.value = null
      let body: TestConnectionRequest
      if (!config.apiKey && configId.value != null) {
        body = { mode: 'by_id', id: configId.value }
      } else {
        body = {
          mode: 'by_body',
          service_name: serviceName,
          url: config.url,
          api_key: config.apiKey || undefined,
        }
        if (config.useProxy && proxyAddress) {
          ;(body as any).proxy = { http: proxyAddress, https: proxyAddress }
        }
      }
      const res = await configAPI.testConnection(body)
      if (res.ok) {
        testStatus.value = 'success'
        ElMessage.success({ 
          message: `${serviceName === 'sonarr' ? 'Sonarr' : 'Prowlarr'} 连接成功！${res.details}`, 
          duration: 3000 
        })
      } else {
        testStatus.value = 'error'
        ElMessage.error({ 
          message: `${serviceName === 'sonarr' ? 'Sonarr' : 'Prowlarr'} 连接失败：${res.details}`, 
          duration: 4000 
        })
      }
    } catch (e) {
      testStatus.value = 'error'
      ElMessage.error(`请先完善 ${serviceName === 'sonarr' ? 'Sonarr' : 'Prowlarr'} 配置`)
    } finally {
      testing.value = false
    }
  }

  const reset = () => {
    Object.assign(config, initialConfig)
    formRef.value?.clearValidate()
  }

  return {
    formRef,
    config,
    hint,
    configId,
    serviceRules,
    saving,
    testing,
    testStatus,
    isValid,
    changed,
    loadConfig,
    save,
    test,
    reset,
  }
}

