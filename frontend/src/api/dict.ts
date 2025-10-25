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
}): Promise<DictTypeListResponse> {
  return request.get('/dict/types', { params }) as Promise<DictTypeListResponse>
}

/**
 * 创建字典类型
 */
export function createDictType(data: DictTypeCreate): Promise<DictType> {
  return request.post('/dict/types', data) as Promise<DictType>
}

/**
 * 更新字典类型
 */
export function updateDictType(typeId: number, data: DictTypeUpdate): Promise<DictType> {
  return request.put(`/dict/types/${typeId}`, data) as Promise<DictType>
}

/**
 * 删除字典类型
 */
export function deleteDictType(typeId: number): Promise<{ deleted: boolean }> {
  return request.delete(`/dict/types/${typeId}`) as Promise<{ deleted: boolean }>
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
}): Promise<DictItemListResponse> {
  return request.get('/dict/items', { params }) as Promise<DictItemListResponse>
}

/**
 * 获取字典项详情
 */
export function getDictItem(itemId: number): Promise<DictItem> {
  return request.get(`/dict/items/${itemId}`) as Promise<DictItem>
}

/**
 * 创建字典项
 */
export function createDictItem(data: DictItemCreate): Promise<DictItem> {
  return request.post('/dict/items', data) as Promise<DictItem>
}

/**
 * 更新字典项
 */
export function updateDictItem(itemId: number, data: DictItemUpdate): Promise<DictItem> {
  return request.put(`/dict/items/${itemId}`, data) as Promise<DictItem>
}

/**
 * 删除字典项
 */
export function deleteDictItem(itemId: number): Promise<{ deleted: boolean }> {
  return request.delete(`/dict/items/${itemId}`) as Promise<{ deleted: boolean }>
}

// ----------------------- 统一选项查询 -----------------------

/**
 * 获取字典选项（用于下拉列表）
 */
export function getDictOptions(dictTypeCode: string, params?: { parent_id?: number }): Promise<DictOptionsResponse> {
  return request.get(`/dict/options/${dictTypeCode}`, { params }) as Promise<DictOptionsResponse>
}

