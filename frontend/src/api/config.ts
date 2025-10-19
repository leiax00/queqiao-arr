import request from './request'
import type {
  OverviewResponse,
  ServiceConfigCreate,
  ServiceConfigUpdate,
  TestConnectionRequest,
  TestConnectionResponse,
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

  // TMDB 元数据提供商配置（使用通用接口）
  // 注：TMDB 配置通过 getOverview() 统一加载，无需单独的 getTmdbConfig 方法
  
  createTmdbConfig: (payload: TmdbConfigUpdate): Promise<{ id: number }> => {
    return request({
      url: '/config/',
      method: 'post',
      data: {
        type: 'service',
        service_name: 'tmdb',
        service_type: 'metadata',
        name: '默认TMDB',
        url: payload.url || 'https://api.themoviedb.org/3',
        api_key: payload.api_key,
        extra_config: {
          language: payload.language,
          region: payload.region,
          include_adult: payload.include_adult,
          use_proxy: payload.use_proxy,
        },
        is_active: true,
      },
    })
  },

  updateTmdbConfig: (id: number, payload: TmdbConfigUpdate): Promise<{ id: number }> => {
    return request({
      url: `/config/${id}`,
      method: 'put',
      data: {
        url: payload.url,
        api_key: payload.api_key,
        extra_config: {
          language: payload.language,
          region: payload.region,
          include_adult: payload.include_adult,
          use_proxy: payload.use_proxy,
        },
      },
    })
  },

  getTmdbOptions: (): Promise<TmdbOptions> => {
    return request({
      url: '/config/tmdb/options',
      method: 'get',
    })
  },
}
