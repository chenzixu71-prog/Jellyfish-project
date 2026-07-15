import Taro from '@tarojs/taro'

export type AnalyticsEventName =
  | 'login_result'
  | 'search_toggle'
  | 'asset_select'
  | 'knowledge_create'
  | 'knowledge_supplement'
  | 'quiz_start'
  | 'answer_submit'
  | 'quiz_complete'
  | 'report_view'
  | 'report_share'

type AnalyticsValue = string | number | boolean | null | undefined
type AnalyticsData = Record<string, AnalyticsValue>

const MAX_STRING_LENGTH = 100

export function sanitizeAnalyticsData(data: AnalyticsData): Record<string, string | number> {
  return Object.entries(data).reduce<Record<string, string | number>>((result, [key, value]) => {
    if (value === null || value === undefined) return result
    if (typeof value === 'boolean') {
      result[key] = value ? 1 : 0
      return result
    }
    result[key] = typeof value === 'string' ? value.slice(0, MAX_STRING_LENGTH) : value
    return result
  }, {})
}

export function trackEvent(eventName: AnalyticsEventName, data: AnalyticsData = {}): boolean {
  const payload = sanitizeAnalyticsData(data)

  if (process.env.NODE_ENV !== 'production') {
    console.info(`[analytics] ${eventName}`, payload)
  }

  if (Taro.getEnv() !== Taro.ENV_TYPE.WEAPP) return false

  try {
    Taro.reportEvent(eventName, payload)
    return true
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn(`[analytics] ${eventName} report failed`, error)
    }
    return false
  }
}

export function elapsedMilliseconds(startedAt: number): number {
  return Math.max(0, Date.now() - startedAt)
}
