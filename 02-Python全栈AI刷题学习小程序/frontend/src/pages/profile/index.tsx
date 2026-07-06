import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Text, View } from '@tarojs/components'
import { AuthSession, getStoredAuth, loginWithWechat } from '../../services/authService'
import { Report } from '../../services/quizService'
import './index.css'

export default function ProfilePage() {
  const [reports, setReports] = useState<Report[]>([])
  const [auth, setAuth] = useState<AuthSession | null>(null)
  const [loggingIn, setLoggingIn] = useState(false)
  const [loginError, setLoginError] = useState('')

  useDidShow(() => {
    setReports(Taro.getStorageSync<Report[]>('learningReports') || [])
    setAuth(getStoredAuth())
  })

  function startNew() {
    Taro.switchTab({ url: '/pages/create/index' })
  }

  async function handleLogin() {
    if (loggingIn) return

    setLoggingIn(true)
    setLoginError('')
    try {
      const nextAuth = await loginWithWechat()
      setAuth(nextAuth)
    } catch (error) {
      const message = error instanceof Error ? error.message : '登录失败，请稍后重试'
      setLoginError(message)
    } finally {
      setLoggingIn(false)
    }
  }

  return (
    <View className='profile-page'>
      <View className='profile-hero'>
        <View className='hero-copy'>
          <Text className='profile-kicker'>Jelly Log</Text>
          <Text className='profile-title'>学习记录</Text>
          <Text className='profile-subtitle'>你的水母复盘都会保存在这里</Text>
        </View>
        <View className='profile-jelly' />
        <Button className='profile-action' onClick={startNew}>新练习</Button>
      </View>

      <View className='login-card'>
        <View className='login-avatar'>水</View>
        <View className='login-copy'>
          <Text className='login-title'>{auth ? auth.user.displayName : '水母学员'}</Text>
          <Text className='login-subtitle'>
            {auth ? '已登录，后续学习记录会归档到你的水母身份。' : '登录后保存你的水母学习记录。'}
          </Text>
          {loginError && <Text className='login-error'>{loginError}</Text>}
        </View>
        {!auth && (
          <Button
            className='login-button'
            loading={loggingIn}
            disabled={loggingIn}
            onClick={handleLogin}
          >
            微信一键登录
          </Button>
        )}
      </View>

      {reports.length === 0 && (
        <View className='empty-card'>
          <Text className='empty-title'>还没有报告</Text>
          <Text className='empty-copy'>完成一次闯关后，这里会保存你的复盘结果。</Text>
        </View>
      )}

      <View className='report-list'>
        {reports.map((report) => (
          <View key={report.quizId} className='history-card'>
            <Text className='history-title'>{report.title}</Text>
            <Text className='history-summary'>{report.summary}</Text>
            <View className='history-meta'>
              <Text className='history-pill score-pill'>{report.score}/{report.total} 得分</Text>
              <Text className='history-pill mastery-pill'>{report.mastery}% 掌握度</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  )
}
