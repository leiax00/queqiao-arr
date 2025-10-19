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
export type ProxyMode = 'inherit' | 'custom' | 'direct'

export interface ServiceConfigData {
  name: string
  url: string
  apiKey: string
  username?: string
  password?: string
  timeoutMs?: number
  isActive: boolean
  proxyMode: ProxyMode
  httpProxy?: string
  httpsProxy?: string
  socks5Proxy?: string
  noProxy?: string
}

export interface ProxyConfigData {
  enabled: boolean
  httpProxy?: string
  httpsProxy?: string
  socks5Proxy?: string
  noProxy?: string
  scope?: string[]
}

export interface ConfigData {
  url: string
  api_key: string
  enabled: boolean
}

export interface ConfigResponse {
  id: number
  type: 'sonarr' | 'prowlarr' | 'proxy'
  config: ConfigData | ProxyConfigData
  updated_at: string
}

export interface ConnectionTestResult {
  ok: boolean
  latency_ms?: number
  details: string
}

// ---- B-02 配置模块契约（FE-05 使用） ----

export type ServiceName = 'sonarr' | 'prowlarr' | 'proxy' | 'tmdb'

export interface ServiceConfigOut {
  id: number
  service_name: ServiceName
  service_type: 'api' | 'proxy'
  name: string
  url: string
  api_key_masked?: string | null
  username?: string | null
  is_active: boolean
  extra_config?: Record<string, any> | null
  created_at?: string | null
  updated_at?: string | null
}

export interface KVConfigOut {
  id: number
  key: string
  value?: string | null
  has_value?: boolean | null
  is_encrypted: boolean
  is_active: boolean
  created_at?: string | null
  updated_at?: string | null
}

export interface OverviewResponse {
  services: ServiceConfigOut[]
  kv: KVConfigOut[]
}

export interface ServiceConfigCreate {
  type: 'service'
  service_name: ServiceName
  service_type: 'api' | 'proxy'
  name: string
  url: string
  api_key?: string | null
  username?: string | null
  password?: string | null
  extra_config?: Record<string, any> | null
  is_active?: boolean
}

export interface KVConfigCreate {
  type: 'kv'
  key: string
  value?: string | null
  description?: string | null
  is_encrypted?: boolean
  is_active?: boolean
}

export type ServiceConfigUpdate = Partial<Omit<ServiceConfigCreate, 'type'>>
export type KVConfigUpdate = Partial<Omit<KVConfigCreate, 'type'>>

export interface TestConnectionByBody {
  mode: 'by_body'
  service_name: Exclude<ServiceName, 'proxy'>
  url: string
  api_key?: string | null
  username?: string | null
  password?: string | null
  proxy?: Record<string, string> | null
}

export interface TestConnectionById {
  mode: 'by_id'
  id: number
}

export type TestConnectionRequest = TestConnectionByBody | TestConnectionById

export interface TestConnectionResponse {
  ok: boolean
  details: string
}

// TMDB 元数据提供商配置类型
export interface TmdbConfigOut {
  id?: number
  api_key_masked?: string | null
  language: string
  region: string
  include_adult: boolean
  use_proxy: boolean
  created_at?: string | null
  updated_at?: string | null
}

export interface TmdbConfigUpdate {
  url?: string
  api_key?: string | null
  language?: string
  region?: string
  include_adult?: boolean
  use_proxy?: boolean
}

export interface TmdbOptions {
  languages: Array<{ code: string; label: string }>
  regions: Array<{ code: string; label: string }>
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
