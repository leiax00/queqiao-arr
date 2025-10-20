/**
 * 系统字典管理 API
 */

import request from './request'
import type {
  DictType,
  DictTypeCreate,
  DictTypeUpdate,
  DictTypeListResponse,
  DictItem,
  DictItemCreate,
  DictItemUpdate,
  DictItemListResponse,
  DictOptionsResponse,
} from './types'

// ----------------------- 字典类型管理 -----------------------

/**
 * 获取字典类型列表
 */
export function getDictTypes(params?: {
  is_active?: boolean
  page?: number
  page_size?: number
}) {
  return request.get<DictTypeListResponse>('/dict/types', { params })
}

/**
 * 创建字典类型
 */
export function createDictType(data: DictTypeCreate) {
  return request.post<DictType>('/dict/types', data)
}

/**
 * 更新字典类型
 */
export function updateDictType(typeId: number, data: DictTypeUpdate) {
  return request.put<DictType>(`/dict/types/${typeId}`, data)
}

/**
 * 删除字典类型
 */
export function deleteDictType(typeId: number) {
  return request.delete<{ deleted: boolean }>(`/dict/types/${typeId}`)
}

// ----------------------- 字典项管理 -----------------------

/**
 * 获取字典项列表
 */
export function getDictItems(params: {
  dict_type_code: string
  is_active?: boolean
  parent_id?: number
  page?: number
  page_size?: number
}) {
  return request.get<DictItemListResponse>('/dict/items', { params })
}

/**
 * 获取字典项详情
 */
export function getDictItem(itemId: number) {
  return request.get<DictItem>(`/dict/items/${itemId}`)
}

/**
 * 创建字典项
 */
export function createDictItem(data: DictItemCreate) {
  return request.post<DictItem>('/dict/items', data)
}

/**
 * 更新字典项
 */
export function updateDictItem(itemId: number, data: DictItemUpdate) {
  return request.put<DictItem>(`/dict/items/${itemId}`, data)
}

/**
 * 删除字典项
 */
export function deleteDictItem(itemId: number) {
  return request.delete<{ deleted: boolean }>(`/dict/items/${itemId}`)
}

// ----------------------- 统一选项查询 -----------------------

/**
 * 获取字典选项（用于下拉列表）
 */
export function getDictOptions(dictTypeCode: string, params?: { parent_id?: number }) {
  return request.get<DictOptionsResponse>(`/dict/options/${dictTypeCode}`, { params })
}

