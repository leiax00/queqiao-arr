import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { configAPI } from '@/api/config'
import type { ServiceConfigOut } from '@/api/types'

export function useProxyConfig() {
  const proxyFormRef = ref<FormInstance>()
  const proxy = reactive({
    address: '',
    testUrl: '',
    timeout: 5000,
  })
  const proxyInitial = reactive({ ...proxy })
  const proxyId = ref<number | null>(null)

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

  const loadProxyConfig = (proxySvc: ServiceConfigOut | null) => {
    if (proxySvc) {
      proxyId.value = proxySvc.id
      proxy.address = proxySvc.url || ''
      if (proxySvc.extra_config) {
        if (typeof proxySvc.extra_config.test_url === 'string') proxy.testUrl = proxySvc.extra_config.test_url
        if (typeof proxySvc.extra_config.timeout_ms === 'number') proxy.timeout = proxySvc.extra_config.timeout_ms
      }
      Object.assign(proxyInitial, proxy)
    }
  }

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

  return {
    // 数据
    proxyFormRef,
    proxy,
    proxyId,
    proxyRules,
    proxySaving,
    proxyTesting,
    proxyTestStatus,
    proxyChanged,
    // 方法
    loadProxyConfig,
    saveProxy,
    testProxy,
    resetProxy,
  }
}

