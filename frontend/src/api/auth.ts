import request from './request'
import type { LoginData, LoginResponse, UserInfo, RegisterData, RegisterResponse } from './types'

export const authAPI = {
  // 用户登录
  login: (data: LoginData): Promise<LoginResponse> => {
    return request({
      url: '/auth/login',
      method: 'post',
      data,
    })
  },

  // 用户注册
  register: (data: Omit<RegisterData, 'confirmPassword'>): Promise<RegisterResponse> => {
    return request({
      url: '/auth/register',
      method: 'post',
      data,
    })
  },

  // 获取用户信息
  getUserInfo: (): Promise<UserInfo> => {
    return request({
      url: '/auth/me',
      method: 'get',
    })
  },

  // 刷新Token
  refreshToken: (): Promise<{ access_token: string }> => {
    return request({
      url: '/auth/refresh',
      method: 'post',
    })
  },

  // 用户登出
  logout: (): Promise<void> => {
    return request({
      url: '/auth/logout',
      method: 'post',
    })
  },
}
