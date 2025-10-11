import request from './request'
import type { ConfigData, ConfigResponse, ProxyConfigData } from './types'

export const configAPI = {
  // 获取所有配置
  getConfigs: (): Promise<ConfigResponse[]> => {
    return request({
      url: '/config',
      method: 'get',
    })
  },

  // 更新Sonarr配置
  updateSonarrConfig: (data: ConfigData): Promise<void> => {
    return request({
      url: '/config/sonarr',
      method: 'put',
      data,
    })
  },

  // 更新Prowlarr配置
  updateProwlarrConfig: (data: ConfigData): Promise<void> => {
    return request({
      url: '/config/prowlarr',
      method: 'put',
      data,
    })
  },

  // 更新代理配置
  updateProxyConfig: (data: ProxyConfigData): Promise<void> => {
    return request({
      url: '/config/proxy',
      method: 'put',
      data,
    })
  },

  // 测试配置连接
  testConnection: (type: 'sonarr' | 'prowlarr', data: ConfigData): Promise<{ success: boolean; message: string }> => {
    return request({
      url: `/config/${type}/test`,
      method: 'post',
      data,
    })
  },
}
