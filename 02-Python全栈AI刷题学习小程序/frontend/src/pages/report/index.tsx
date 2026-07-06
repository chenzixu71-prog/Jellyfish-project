import { useState } from 'react'
import Taro, { useLoad, useRouter, useShareAppMessage } from '@tarojs/taro'
import { Button, Text, View } from '@tarojs/components'
import { generateReport, Quiz, Report } from '../../services/quizService'
import './index.css'

export default function ReportPage() {
  const router = useRouter()
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)

  useShareAppMessage(() => ({
    title: report ? `我的学习报告：${report.title}` : '水母diy学习助手',
    path: '/pages/create/index'
  }))

  useLoad(async () => {
    const storedQuiz = Taro.getStorageSync<Quiz>('currentQuiz')
    const quizId = router.params.quizId || storedQuiz?.quizId
    if (!quizId) {
      Taro.redirectTo({ url: '/pages/create/index' })
      return
    }

    setLoading(true)
    try {
      const nextReport = await generateReport(quizId)
      setReport(nextReport)
      const history = Taro.getStorageSync<Report[]>('learningReports') || []
      Taro.setStorageSync('learningReports', [nextReport, ...history.filter((item) => item.quizId !== quizId)].slice(0, 10))
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '报告生成失败',
        icon: 'none'
      })
    } finally {
      setLoading(false)
    }
  })

  function shareToQQ() {
    Taro.showToast({ title: 'QQ 分享入口已保留', icon: 'none' })
  }

  if (loading) {
    return (
      <View className='page report-page'>
        <View className='card loading-card'>
          <View className='loading-dot-group'>
            <View className='loading-dot' />
            <View className='loading-dot loading-dot-delay-1' />
            <View className='loading-dot loading-dot-delay-2' />
          </View>
          <Text className='loading-title'>loading......</Text>
          <Text className='muted'>AI 正在生成你的学习报告</Text>
        </View>
      </View>
    )
  }

  if (!report) {
    return (
      <View className='page report-page'>
        <Text className='muted'>暂时没有报告。</Text>
      </View>
    )
  }

  return (
    <View className='page report-page'>
      <View className='card report-card'>
        <Text className='report-title'>{report.title}</Text>
        <Text className='report-summary'>{report.summary}</Text>

        <View className='score-row'>
          <View className='score-box'>
            <Text className='score-number'>{report.score}/{report.total}</Text>
            <Text className='score-label'>答题得分</Text>
          </View>
          <View className='score-box yellow-box'>
            <Text className='score-number'>{report.mastery}%</Text>
            <Text className='score-label'>掌握度</Text>
          </View>
        </View>

        <Text className='block-title'>薄弱点</Text>
        {report.weakPoints.map((item) => (
          <Text key={item} className='list-line'>- {item}</Text>
        ))}

        <Text className='block-title'>下一步建议</Text>
        {report.nextSteps.map((item) => (
          <Text key={item} className='list-line'>- {item}</Text>
        ))}

        <View className='share-row'>
          <Button className='share-button share-button-wechat' openType='share'>分享到微信</Button>
          <Button className='share-button share-button-qq' onClick={shareToQQ}>分享到QQ</Button>
        </View>
      </View>
    </View>
  )
}
