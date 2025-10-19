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

  // TMDB 元数据提供商配置（使用通用接口）
  getTmdbConfig: async (): Promise<TmdbConfigOut | null> => {
    const overview: OverviewResponse = await request({
      url: '/config/',
      method: 'get',
      params: { service_name: 'tmdb' },
    })
    const tmdbService = overview.services.find(s => s.service_name === 'tmdb')
    if (!tmdbService) {
      return null
    }
    // 转换为 TmdbConfigOut 格式
    return {
      id: tmdbService.id,
      language: tmdbService.extra_config?.language || 'zh-CN',
      region: tmdbService.extra_config?.region || 'CN',
      include_adult: tmdbService.extra_config?.include_adult || false,
      use_proxy: tmdbService.extra_config?.use_proxy || false,
      api_key_masked: tmdbService.api_key_masked,
      created_at: tmdbService.created_at,
      updated_at: tmdbService.updated_at,
    }
  },

  createTmdbConfig: (payload: TmdbConfigUpdate): Promise<{ id: number }> => {
    return request({
      url: '/config/',
      method: 'post',
      data: {
        type: 'service',
        service_name: 'tmdb',
        service_type: 'metadata',
        name: '默认TMDB',
        url: 'https://api.themoviedb.org/3',
        api_key: payload.api_key,
        extra_config: {
          language: payload.language,
          region: payload.region,
          include_adult: payload.include_adult,
          use_proxy: payload.use_proxy,
        },
        is_active: true,
      } as ServiceConfigCreate,
    })
  },

  updateTmdbConfig: (id: number, payload: TmdbConfigUpdate): Promise<{ id: number }> => {
    return request({
      url: `/config/${id}`,
      method: 'put',
      data: {
        api_key: payload.api_key,
        extra_config: {
          language: payload.language,
          region: payload.region,
          include_adult: payload.include_adult,
          use_proxy: payload.use_proxy,
        },
      } as ServiceConfigUpdate,
    })
  },

  getTmdbOptions: (): Promise<TmdbOptions> => {
    return request({
      url: '/config/tmdb/options',
      method: 'get',
    })
  },
}
