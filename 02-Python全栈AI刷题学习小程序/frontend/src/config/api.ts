const configuredBaseUrl = (process.env.TARO_APP_API_BASE_URL || '').replace(/\/$/, '')

export function getApiBaseUrls(): string[] {
  if (configuredBaseUrl) return [configuredBaseUrl]
  return []
}

export function requireApiBaseUrls(): string[] {
  const urls = getApiBaseUrls()
  if (urls.length === 0) {
    throw new Error('生产版本未配置 TARO_APP_API_BASE_URL')
  }
  return urls
}
