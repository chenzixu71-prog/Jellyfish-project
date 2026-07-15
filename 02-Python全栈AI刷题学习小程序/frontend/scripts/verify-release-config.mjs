import fs from 'node:fs'
import path from 'node:path'

function loadLocalProductionEnv() {
  const filePath = path.resolve('.env.production.local')
  if (!fs.existsSync(filePath)) return

  for (const line of fs.readFileSync(filePath, 'utf8').split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/)
    if (!match || match[0].trimStart().startsWith('#')) continue
    if (!(match[1] in process.env)) process.env[match[1]] = match[2]
  }
}

loadLocalProductionEnv()

const apiBaseUrl = process.env.TARO_APP_API_BASE_URL || ''
const appId = process.env.TARO_APP_ID || ''
const errors = []

if (!apiBaseUrl.startsWith('https://')) {
  errors.push('TARO_APP_API_BASE_URL must be a public HTTPS origin')
}
if (apiBaseUrl.includes('localhost') || apiBaseUrl.includes('127.0.0.1')) {
  errors.push('TARO_APP_API_BASE_URL cannot point to localhost')
}
if (!/^wx[a-zA-Z0-9]{16}$/.test(appId)) {
  errors.push('TARO_APP_ID must be a valid WeChat mini-program AppID')
}

if (errors.length > 0) {
  console.error(`Release configuration failed:\n- ${errors.join('\n- ')}`)
  process.exit(1)
}

console.log('Release configuration is valid.')
