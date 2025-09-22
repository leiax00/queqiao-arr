import request from './request'
import type { HealthCheck, SystemStats, LogEntry, PaginatedResponse } from './types'

export const systemAPI = {
  // 健康检查
  healthCheck: (): Promise<HealthCheck> => {
    return request({
      url: '/health',
      method: 'get',
    })
  },

  // 获取系统统计信息
  getSystemStats: (): Promise<SystemStats> => {
    return request({
      url: '/system/stats',
      method: 'get',
    })
  },

  // 获取日志列表
  getLogs: (params: {
    page?: number
    size?: number
    level?: string
    start_time?: string
    end_time?: string
  }): Promise<PaginatedResponse<LogEntry>> => {
    return request({
      url: '/system/logs',
      method: 'get',
      params,
    })
  },

  // 清空日志
  clearLogs: (): Promise<void> => {
    return request({
      url: '/system/logs',
      method: 'delete',
    })
  },
}
