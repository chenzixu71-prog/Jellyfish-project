import {
  getOrCreateSessionId,
  Quiz,
  request,
  SourceMeta
} from './quizService'

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

export function startKnowledgeBaseQuiz(id: string): Promise<Quiz> {
  return request<Quiz>(`/api/knowledge-bases/${id}/quiz`, 'POST', {
    sessionId: getOrCreateSessionId()
  })
}
