import request from './request'
import type {
  OverviewResponse,
  ServiceConfigCreate,
  ServiceConfigUpdate,
  TestConnectionRequest,
  TestConnectionResponse,
} from './types'

export const configAPI = {
  // 获取配置概览（服务 + KV）
  getOverview: (): Promise<OverviewResponse> => {
    return request({
      url: '/config/',
      method: 'get',
    })
  },

  // 创建配置（服务或KV）
  createConfig: (payload: ServiceConfigCreate | any): Promise<{ id: number }> => {
    return request({
      url: '/config/',
      method: 'post',
      data: payload,
    })
  },

  // 更新配置（服务或KV）
  updateConfig: (id: number, payload: ServiceConfigUpdate | any): Promise<{ id: number }> => {
    return request({
      url: `/config/${id}`,
      method: 'put',
      data: payload,
    })
  },

  // 删除配置（服务或KV）
  deleteConfig: (id: number): Promise<{ deleted: boolean }> => {
    return request({
      url: `/config/${id}`,
      method: 'delete',
    })
  },

  // 测试服务连接（Sonarr/Prowlarr）
  testConnection: (body: TestConnectionRequest): Promise<TestConnectionResponse> => {
    return request({
      url: '/config/test-connection',
      method: 'post',
      data: body,
    })
  },
}
