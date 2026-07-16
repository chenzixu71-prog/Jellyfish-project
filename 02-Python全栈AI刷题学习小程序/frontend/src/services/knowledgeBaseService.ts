import Taro from '@tarojs/taro'
import { requireApiBaseUrls } from '../config/api'
import {
  getOrCreateSessionId,
  request,
  SourceMeta
} from './quizService'

const API_BASE_URLS = requireApiBaseUrls()

interface ApiResponse<T> {
  code: number
  message: string
  data: T
  detail?: string
}

export interface KnowledgeBaseUploadAsset {
  path: string
  type: 'file' | 'image'
  name?: string
}

export interface UploadProgress {
  completed: number
  total: number
}

export interface KnowledgeBaseMaterial {
  id: string
  type: 'text' | 'file' | 'image' | 'search'
  name: string
  summary: string
  createdAt: string
}

export interface KnowledgeBaseSummary {
  id: string
  title: string
  summary: string
  materialCount: number
  sourceCount: number
  quizCount: number
  questionCount: number
  completedQuestionCount: number
  maxQuestions: number
  updatedAt: string
}

export interface KnowledgeBase {
  id: string
  title: string
  summary: string
  content: string
  materials: KnowledgeBaseMaterial[]
  sourceMeta?: SourceMeta
  quizIds: string[]
  questionCount: number
  completedQuestionCount: number
  maxQuestions: number
  createdAt: string
  updatedAt: string
}

export function createKnowledgeBase(
  title: string,
  content: string,
  webSearchEnabled = false
): Promise<KnowledgeBase> {
  return request<KnowledgeBase>('/api/knowledge-bases', 'POST', {
    sessionId: getOrCreateSessionId(),
    title,
    content,
    webSearchEnabled
  })
}

export function getKnowledgeBases(): Promise<KnowledgeBaseSummary[]> {
  return request<KnowledgeBaseSummary[]>(
    `/api/knowledge-bases?sessionId=${getOrCreateSessionId()}`,
    'GET'
  )
}

export function getKnowledgeBase(id: string): Promise<KnowledgeBase> {
  return request<KnowledgeBase>(
    `/api/knowledge-bases/${id}?sessionId=${getOrCreateSessionId()}`,
    'GET'
  )
}

export function supplementKnowledgeBase(
  id: string,
  content: string,
  webSearchEnabled = false
): Promise<KnowledgeBase> {
  return request<KnowledgeBase>(`/api/knowledge-bases/${id}/supplements`, 'POST', {
    sessionId: getOrCreateSessionId(),
    content,
    webSearchEnabled
  })
}

function parseUploadResponse<T>(rawData: string, statusCode: number): T {
  let body: ApiResponse<T>
  try {
    body = JSON.parse(rawData) as ApiResponse<T>
  } catch {
    throw new Error('素材上传返回格式异常，请稍后重试')
  }

  if (statusCode >= 400 || body.code !== 0 || !body.data) {
    throw new Error(body.detail || body.message || `素材上传失败（${statusCode}）`)
  }
  return body.data
}

async function uploadAsset<T>(url: string, asset: KnowledgeBaseUploadAsset, formData: Record<string, string>): Promise<T> {
  const token = Taro.getStorageSync<string>('authToken')
  const header = token ? { Authorization: `Bearer ${token}` } : undefined
  let transportError: unknown

  for (const baseUrl of API_BASE_URLS) {
    let response
    try {
      response = await Taro.uploadFile({
        url: `${baseUrl}${url}`,
        filePath: asset.path,
        name: asset.type === 'file' ? 'files' : 'images',
        formData,
        header
      })
    } catch (error) {
      transportError = error
      continue
    }
    if (response.statusCode === 401) {
      Taro.removeStorageSync('authToken')
      Taro.removeStorageSync('authUser')
    }
    return parseUploadResponse<T>(response.data, response.statusCode)
  }

  const detail = transportError instanceof Error ? transportError.message : '未知网络错误'
  throw new Error(`素材上传失败，请确认后端已启动且小程序允许访问本地域名。${detail}`)
}

async function uploadAssetAt<T>(
  url: string,
  asset: KnowledgeBaseUploadAsset,
  formData: Record<string, string>,
  index: number,
  total: number
): Promise<T> {
  try {
    return await uploadAsset<T>(url, asset, formData)
  } catch (error) {
    const detail = error instanceof Error ? error.message : '未知错误'
    throw new Error(`第 ${index}/${total} 份素材处理失败：${detail}`)
  }
}

export async function createKnowledgeBaseFromAssets(
  title: string,
  content: string,
  webSearchEnabled: boolean,
  assets: KnowledgeBaseUploadAsset[],
  onProgress?: (progress: UploadProgress) => void
): Promise<KnowledgeBase> {
  if (assets.length === 0) return createKnowledgeBase(title, content, webSearchEnabled)

  const sessionId = getOrCreateSessionId()
  const total = assets.length
  onProgress?.({ completed: 0, total })
  let knowledgeBase = await uploadAssetAt<KnowledgeBase>('/api/knowledge-bases/from-assets', assets[0], {
    sessionId, title, content, webSearchEnabled: String(webSearchEnabled), originalName: assets[0].name || ''
  }, 1, total)
  onProgress?.({ completed: 1, total })

  for (let index = 1; index < total; index += 1) {
    knowledgeBase = await uploadAssetAt<KnowledgeBase>(
      `/api/knowledge-bases/${knowledgeBase.id}/supplements/from-assets`, assets[index],
      { sessionId, content: '', webSearchEnabled: 'false', originalName: assets[index].name || '' }, index + 1, total
    )
    onProgress?.({ completed: index + 1, total })
  }
  return knowledgeBase
}

export async function supplementKnowledgeBaseFromAssets(
  id: string,
  content: string,
  webSearchEnabled: boolean,
  assets: KnowledgeBaseUploadAsset[],
  onProgress?: (progress: UploadProgress) => void
): Promise<KnowledgeBase> {
  if (assets.length === 0) return supplementKnowledgeBase(id, content, webSearchEnabled)

  const sessionId = getOrCreateSessionId()
  const total = assets.length
  onProgress?.({ completed: 0, total })
  let knowledgeBase: KnowledgeBase | null = null
  for (let index = 0; index < total; index += 1) {
    knowledgeBase = await uploadAssetAt<KnowledgeBase>(
      `/api/knowledge-bases/${id}/supplements/from-assets`, assets[index], {
        sessionId,
        content: index === 0 ? content : '',
        webSearchEnabled: index === 0 ? String(webSearchEnabled) : 'false',
        originalName: assets[index].name || ''
      }, index + 1, total
    )
    onProgress?.({ completed: index + 1, total })
  }
  return knowledgeBase as KnowledgeBase
}
export function startKnowledgeBaseQuiz(id: string): Promise<Quiz> {
  return request<Quiz>(`/api/knowledge-bases/${id}/quiz`, 'POST', {
    sessionId: getOrCreateSessionId()
  })
}
