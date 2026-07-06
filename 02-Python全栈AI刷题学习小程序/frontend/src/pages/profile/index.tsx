import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Text, View } from '@tarojs/components'
import { Report } from '../../services/quizService'
import './index.css'

export default function ProfilePage() {
  const [reports, setReports] = useState<Report[]>([])

  useDidShow(() => {
    setReports(Taro.getStorageSync<Report[]>('learningReports') || [])
  })

  function startNew() {
    Taro.switchTab({ url: '/pages/create/index' })
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
