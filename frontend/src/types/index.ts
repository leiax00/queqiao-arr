// 全局类型定义

// 菜单项类型
export interface MenuItem {
  id: string
  title: string
  icon?: string
  path?: string
  children?: MenuItem[]
}

// 用户类型
export interface User {
  id: number
  username: string
  email: string
  avatar?: string
  role: string
  created_at: string
  updated_at: string
}

// 配置类型
export interface Config {
  id: number
  type: 'sonarr' | 'prowlarr' | 'proxy'
  name: string
  config: Record<string, any>
  enabled: boolean
  created_at: string
  updated_at: string
}

// 任务状态
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

// 任务类型
export interface Task {
  id: number
  title: string
  status: TaskStatus
  progress: number
  message?: string
  created_at: string
  updated_at: string
}

// 系统统计
export interface SystemStats {
  tasks: {
    total: number
    pending: number
    processing: number
    completed: number
    failed: number
  }
  system: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    uptime: number
  }
}

// 日志级别
export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'

// 日志条目
export interface LogEntry {
  id: number
  level: LogLevel
  message: string
  module?: string
  timestamp: string
}

// 分页参数
export interface PaginationParams {
  page: number
  size: number
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// API响应
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  success: boolean
}

// 表单验证规则
export interface FormRule {
  required?: boolean
  message?: string
  trigger?: string | string[]
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}
