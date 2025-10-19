import request from './request'
import type {
  OverviewResponse,
  ServiceConfigCreate,
  ServiceConfigUpdate,
  TestConnectionRequest,
  TestConnectionResponse,
  TmdbConfigOut,
  TmdbConfigUpdate,
  TmdbOptions,
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

  // 测试代理连通性
  testProxy: (body: { url?: string; proxy?: Record<string, string>; timeout_ms?: number }): Promise<{ ok: boolean; latency_ms?: number; details: string }> => {
    return request({
      url: '/config/test-proxy',
      method: 'post',
      data: body,
    })
  },

  // TMDB 元数据提供商配置
  getTmdbConfig: (): Promise<TmdbConfigOut> => {
    return request({
      url: '/config/tmdb',
      method: 'get',
    })
  },

  updateTmdbConfig: (payload: TmdbConfigUpdate): Promise<TmdbConfigOut> => {
    return request({
      url: '/config/tmdb',
      method: 'put',
      data: payload,
    })
  },

  getTmdbOptions: (): Promise<TmdbOptions> => {
    return request({
      url: '/config/tmdb/options',
      method: 'get',
    })
  },
}
