import Taro from '@tarojs/taro'

const API_BASE_URL = 'http://127.0.0.1:8000'

export type QuestionType = 'single' | 'multiple' | 'judge'
export type Difficulty = 'easy' | 'medium' | 'hard'

export interface Option {
  key: string
  text: string
}

export interface Question {
  id: string
  type: QuestionType
  stem: string
  options: Option[]
  answer: string[]
  explanation: string
  knowledge_point: string
  difficulty: Difficulty
}

export interface Quiz {
  quizId: string
  title: string
  summary: string
  questions: Question[]
}

export interface AnswerResult {
  questionId: string
  isCorrect: boolean
  correctAnswer: string[]
  explanation: string
  knowledge_point: string
}

export interface Report {
  quizId: string
  title: string
  score: number
  total: number
  mastery: number
  summary: string
  weakPoints: string[]
  nextSteps: string[]
}

interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

async function request<T>(url: string, method: 'GET' | 'POST', data?: unknown): Promise<T> {
  const response = await Taro.request<ApiResponse<T>>({
    url: `${API_BASE_URL}${url}`,
    method,
    data,
    header: {
      'Content-Type': 'application/json'
    }
  })

  if (response.statusCode >= 400 || response.data.code !== 0) {
    throw new Error(response.data?.message || '请求失败')
  }

  return response.data.data
}

export function getOrCreateSessionId(): string {
  const existing = Taro.getStorageSync<string>('sessionId')
  if (existing) return existing

  const sessionId = `session-${Date.now()}-${Math.random().toString(16).slice(2)}`
  Taro.setStorageSync('sessionId', sessionId)
  return sessionId
}

export function generateQuiz(content: string): Promise<Quiz> {
  return request<Quiz>('/api/generate-quiz', 'POST', {
    sessionId: getOrCreateSessionId(),
    inputType: 'text',
    content,
    questionCount: 5
  })
}

export function submitAnswer(quizId: string, questionId: string, answer: string[]): Promise<AnswerResult> {
  return request<AnswerResult>('/api/submit-answer', 'POST', {
    sessionId: getOrCreateSessionId(),
    quizId,
    questionId,
    answer
  })
}

export function generateReport(quizId: string): Promise<Report> {
  return request<Report>('/api/generate-report', 'POST', {
    sessionId: getOrCreateSessionId(),
    quizId
  })
}
