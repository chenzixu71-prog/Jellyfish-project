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
    <View className='page profile-page'>
      <View className='profile-header'>
        <View>
          <Text className='profile-title'>学习记录</Text>
          <Text className='profile-subtitle'>你的水母复盘都会保存在这里</Text>
        </View>
        <Button className='primary-button compact-button' onClick={startNew}>新练习</Button>
      </View>

      {reports.length === 0 && (
        <View className='card empty-card'>
          <Text className='empty-title'>还没有报告</Text>
          <Text className='muted'>完成一次闯关后，这里会保存你的复盘结果。</Text>
        </View>
      )}

      <View className='report-list'>
        {reports.map((report) => (
          <View key={report.quizId} className='card history-card'>
            <Text className='history-title'>{report.title}</Text>
            <Text className='history-summary'>{report.summary}</Text>
            <View className='history-meta'>
              <Text className='tag'>{report.score}/{report.total}</Text>
              <Text className='tag'>{report.mastery}% 掌握度</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  )
}
