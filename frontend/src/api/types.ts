// 通用响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 认证相关类型
export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface RegisterResponse {
  user: UserInfo
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserInfo {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

// 配置相关类型
export interface ConfigData {
  url: string
  api_key: string
  enabled: boolean
}

export interface ProxyConfigData {
  http_proxy?: string
  https_proxy?: string
  enabled: boolean
}

export interface ConfigResponse {
  id: number
  type: 'sonarr' | 'prowlarr' | 'proxy'
  config: ConfigData | ProxyConfigData
  updated_at: string
}

// 系统相关类型
export interface HealthCheck {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  version: string
}

export interface SystemStats {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  uptime: number
}

// 日志相关类型
export interface LogEntry {
  id: number
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'
  message: string
  timestamp: string
  module?: string
}
