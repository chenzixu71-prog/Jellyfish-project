import Taro from '@tarojs/taro'
import { getOrCreateSessionId, request } from './quizService'

const AUTH_TOKEN_KEY = 'authToken'
const AUTH_USER_KEY = 'authUser'

export interface LoginUser {
  id: string
  displayName: string
  avatarUrl: string
  loginType: 'wechat'
}

export interface CurrentUserProfile extends LoginUser {
  level: number
  exp: number
  nextLevelExp: number
  streakDays: number
  totalAnswered: number
  totalCorrect: number
  totalSessions: number
  accuracy: number
  badges: Array<{
    id: string
    name: string
    description: string
    unlocked: boolean
  }>
}

export interface AuthSession {
  token: string
  user: LoginUser
}

export function getStoredAuth(): AuthSession | null {
  const token = Taro.getStorageSync<string>(AUTH_TOKEN_KEY)
  const user = Taro.getStorageSync<LoginUser>(AUTH_USER_KEY)

  if (!token || !user?.id) return null
  return { token, user }
}

export function saveAuth(auth: AuthSession): void {
  Taro.setStorageSync(AUTH_TOKEN_KEY, auth.token)
  Taro.setStorageSync(AUTH_USER_KEY, auth.user)
}

export async function loginWithWechat(): Promise<AuthSession> {
  const loginResult = await Taro.login()
  if (!loginResult.code) {
    throw new Error('微信登录失败，请稍后重试')
  }

  const auth = await request<AuthSession>('/api/auth/wechat-login', 'POST', {
    code: loginResult.code,
    sessionId: getOrCreateSessionId()
  })
  saveAuth(auth)
  return auth
}

export async function getCurrentUser(): Promise<CurrentUserProfile> {
  const auth = getStoredAuth()
  if (!auth) {
    throw new Error('请先登录')
  }

  return request<CurrentUserProfile>('/api/me', 'GET', undefined, {
    Authorization: `Bearer ${auth.token}`
  })
}
