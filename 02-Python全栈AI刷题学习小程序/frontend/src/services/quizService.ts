import Taro from '@tarojs/taro'

const API_BASE_URLS = ['http://127.0.0.1:8010', 'http://localhost:8010']

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

export interface WrongQuestion {
  quizId: string
  questionId: string
  stem: string
  selectedAnswer: string[]
  correctAnswer: string[]
  explanation: string
  knowledge_point: string
  reviewed: boolean
}

export interface ReportHistoryItem {
  quizId: string
  title: string
  score: number
  total: number
  mastery: number
  weakPoints: string[]
}

export interface ChallengeHistoryItem {
  quizId: string
  title: string
  score: number
  total: number
  mastery: number
  completedAt: string
}

export interface DailyChallenge {
  date: string
  target: number
  answered: number
  correct: number
  completed: boolean
  progress: number
}

export interface Badge {
  id: string
  name: string
  description: string
  unlocked: boolean
}

export interface LearningProfile {
  level: number
  exp: number
  streakDays: number
  totalAnswered: number
  totalCorrect: number
  badges: Badge[]
}

interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export async function request<T>(
  url: string,
  method: 'GET' | 'POST',
  data?: unknown,
  extraHeader: Record<string, string> = {}
): Promise<T> {
  let lastError: unknown
  const token = Taro.getStorageSync<string>('authToken')
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {}

  for (const baseUrl of API_BASE_URLS) {
    try {
      const response = await Taro.request<ApiResponse<T>>({
        url: `${baseUrl}${url}`,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          ...authHeader,
          ...extraHeader
        }
      })

      if (response.statusCode >= 400 || response.data.code !== 0) {
        throw new Error(response.data?.message || `接口返回异常：${response.statusCode}`)
      }

      return response.data.data
    } catch (error) {
      lastError = error
    }
  }

  const detail = lastError instanceof Error ? lastError.message : '未知网络错误'
  throw new Error(`后端接口暂时无法访问，请确认本地后端已启动，并在微信开发者工具勾选“不校验合法域名”。${detail}`)
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

export function getWrongQuestions(): Promise<WrongQuestion[]> {
  return request<WrongQuestion[]>(`/api/wrong-questions?sessionId=${getOrCreateSessionId()}`, 'GET')
}

export function regenerateWeakQuiz(quizId: string): Promise<Quiz> {
  return request<Quiz>('/api/regenerate-weak-quiz', 'POST', {
    sessionId: getOrCreateSessionId(),
    quizId
  })
}

export function getReportHistory(): Promise<ReportHistoryItem[]> {
  return request<ReportHistoryItem[]>(`/api/report-history?sessionId=${getOrCreateSessionId()}`, 'GET')
}

export function getChallengeHistory(): Promise<ChallengeHistoryItem[]> {
  return request<ChallengeHistoryItem[]>(`/api/challenge-history?sessionId=${getOrCreateSessionId()}`, 'GET')
}

export function getDailyChallenge(): Promise<DailyChallenge> {
  return request<DailyChallenge>(`/api/daily-challenge?sessionId=${getOrCreateSessionId()}`, 'GET')
}

export function getLearningProfile(): Promise<LearningProfile> {
  return request<LearningProfile>(`/api/profile?sessionId=${getOrCreateSessionId()}`, 'GET')
}
