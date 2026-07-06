import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Text, View } from '@tarojs/components'
import {
  AuthSession,
  CurrentUserProfile,
  getCurrentUser,
  getStoredAuth,
  loginWithWechat
} from '../../services/authService'
import { Report } from '../../services/quizService'
import './index.css'

export default function ProfilePage() {
  const [reports, setReports] = useState<Report[]>([])
  const [auth, setAuth] = useState<AuthSession | null>(null)
  const [profile, setProfile] = useState<CurrentUserProfile | null>(null)
  const [profileLoading, setProfileLoading] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [loggingIn, setLoggingIn] = useState(false)
  const [loginError, setLoginError] = useState('')

  useDidShow(() => {
    setReports(Taro.getStorageSync<Report[]>('learningReports') || [])
    const storedAuth = getStoredAuth()
    setAuth(storedAuth)
    if (storedAuth) {
      loadProfile()
    } else {
      setProfile(null)
      setProfileError('')
    }
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
      await loadProfile()
    } catch (error) {
      const message = error instanceof Error ? error.message : '登录失败，请稍后重试'
      setLoginError(message)
    } finally {
      setLoggingIn(false)
    }
  }

  async function loadProfile() {
    setProfileLoading(true)
    setProfileError('')
    try {
      const nextProfile = await getCurrentUser()
      setProfile(nextProfile)
    } catch (error) {
      const message = error instanceof Error ? error.message : '用户信息暂时无法加载'
      setProfileError(message)
    } finally {
      setProfileLoading(false)
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
          {profileError && <Text className='login-error'>{profileError}</Text>}
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

      {auth && (
        <View className='stats-card'>
          <View className='stats-header'>
            <Text className='stats-title'>水母学习概览</Text>
            <Text className='stats-status'>{profileLoading ? '同步中' : '已同步'}</Text>
          </View>
          <View className='stats-grid'>
            <View className='stat-cell stat-yellow'>
              <Text className='stat-value'>Lv.{profile?.level ?? 1}</Text>
              <Text className='stat-label'>等级</Text>
            </View>
            <View className='stat-cell stat-blue'>
              <Text className='stat-value'>{profile?.exp ?? 0}</Text>
              <Text className='stat-label'>经验值</Text>
            </View>
            <View className='stat-cell stat-soft'>
              <Text className='stat-value'>{profile?.totalAnswered ?? 0}</Text>
              <Text className='stat-label'>累计答题</Text>
            </View>
            <View className='stat-cell stat-soft'>
              <Text className='stat-value'>{profile?.accuracy ?? 0}%</Text>
              <Text className='stat-label'>正确率</Text>
            </View>
            <View className='stat-cell stat-soft'>
              <Text className='stat-value'>{profile?.streakDays ?? 1}</Text>
              <Text className='stat-label'>连续学习</Text>
            </View>
            <View className='stat-cell stat-soft'>
              <Text className='stat-value'>{profile?.totalSessions ?? 0}</Text>
              <Text className='stat-label'>学习次数</Text>
            </View>
          </View>
        </View>
      )}

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
