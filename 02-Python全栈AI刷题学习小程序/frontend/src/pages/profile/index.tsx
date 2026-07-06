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
import { ChallengeHistoryItem, getChallengeHistory, Report } from '../../services/quizService'
import './index.css'

export default function ProfilePage() {
  const [reports, setReports] = useState<Report[]>([])
  const [auth, setAuth] = useState<AuthSession | null>(null)
  const [profile, setProfile] = useState<CurrentUserProfile | null>(null)
  const [profileLoading, setProfileLoading] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [challengeHistory, setChallengeHistory] = useState<ChallengeHistoryItem[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')
  const [loggingIn, setLoggingIn] = useState(false)
  const [loginError, setLoginError] = useState('')

  useDidShow(() => {
    setReports(Taro.getStorageSync<Report[]>('learningReports') || [])
    const storedAuth = getStoredAuth()
    setAuth(storedAuth)
    if (storedAuth) {
      loadProfile()
      loadChallengeHistory()
    } else {
      setProfile(null)
      setProfileError('')
      setChallengeHistory([])
      setHistoryError('')
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
      await loadChallengeHistory()
    } catch (error) {
      const message = error instanceof Error ? error.message : '微信登录失败，请稍后重试'
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

  async function loadChallengeHistory() {
    setHistoryLoading(true)
    setHistoryError('')
    try {
      const nextHistory = await getChallengeHistory()
      setChallengeHistory(nextHistory)
    } catch (error) {
      const message = error instanceof Error ? error.message : '闯关历史暂时无法加载'
      setHistoryError(message)
    } finally {
      setHistoryLoading(false)
    }
  }

  function openChallengeReport(quizId: string) {
    Taro.setStorageSync('historyReportQuizId', quizId)
    Taro.switchTab({ url: '/pages/report/index' })
  }

  return (
    <View className='profile-page'>
      <View className='profile-hero'>
        <View className='hero-copy'>
          <Text className='profile-kicker'>Jelly Log</Text>
          <Text className='profile-title'>学习记录</Text>
          <Text className='profile-subtitle'>你的水母复盘、闯关历史和成长数据都会保存到这里。</Text>
        </View>
        <View className='profile-jelly' />
        <Button className='profile-action' onClick={startNew}>新练习</Button>
      </View>

      <View className='login-card'>
        <View className='login-avatar'>水</View>
        <View className='login-copy'>
          <Text className='login-title'>{auth ? auth.user.displayName : '水母学员'}</Text>
          <Text className='login-subtitle'>
            {auth ? '已登录，后续学习记录会归档到你的水母身份。' : '登录后保存你的水母学习记录，游客数据会自动绑定。'}
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
            微信登录
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

      {auth && (
        <View className='growth-card'>
          <View className='growth-header'>
            <View>
              <Text className='growth-title'>水母成长值</Text>
              <Text className='growth-copy'>连续学习、答题和满分闯关都会推动成长。</Text>
            </View>
            <Text className='growth-level'>Lv.{profile?.level ?? 1}</Text>
          </View>
          <View className='growth-track'>
            <View
              className='growth-progress'
              style={{
                width: `${Math.min(100, Math.round(((profile?.exp ?? 0) % 100) / 100 * 100))}%`
              }}
            />
          </View>
          <Text className='growth-copy'>当前 {profile?.exp ?? 0} EXP，下一等级需要 {profile?.nextLevelExp ?? 100} EXP。</Text>

          <View className='badge-list'>
            {(profile?.badges || []).map((badge) => (
              <View key={badge.id} className={`badge-item ${badge.unlocked ? 'badge-unlocked' : 'badge-locked'}`}>
                <Text className='badge-name'>{badge.name}</Text>
                <Text className='badge-desc'>{badge.description}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      <View className='history-section-header'>
        <Text className='history-section-title'>闯关历史</Text>
        <Text className='history-section-status'>{historyLoading ? '同步中' : auth ? '账号记录' : '本地记录'}</Text>
      </View>

      {auth && historyError && <Text className='history-error'>{historyError}</Text>}

      {auth && challengeHistory.length === 0 && !historyLoading && (
        <View className='empty-card'>
          <Text className='empty-title'>还没有闯关历史</Text>
          <Text className='empty-copy'>完成一次闯关并查看报告后，这里会出现账号级历史记录。</Text>
        </View>
      )}

      {auth && challengeHistory.length > 0 && (
        <View className='report-list'>
          {challengeHistory.map((item) => (
            <View
              key={item.quizId}
              className='history-card'
              onClick={() => openChallengeReport(item.quizId)}
            >
              <Text className='history-title'>{item.title}</Text>
              <Text className='history-summary'>完成时间：{item.completedAt.slice(0, 10) || '刚刚完成'}</Text>
              <View className='history-meta'>
                <Text className='history-pill score-pill'>{item.score}/{item.total} 得分</Text>
                <Text className='history-pill mastery-pill'>{item.mastery}% 掌握度</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {!auth && reports.length === 0 && (
        <View className='empty-card'>
          <Text className='empty-title'>还没有本地报告</Text>
          <Text className='empty-copy'>完成一次闯关后，这里会先保存本地复盘结果；登录后会绑定到账号。</Text>
        </View>
      )}

      {!auth && (
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
      )}
    </View>
  )
}
