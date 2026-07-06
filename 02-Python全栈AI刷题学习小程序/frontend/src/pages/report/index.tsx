import { useState } from 'react'
import Taro, { useDidShow, useRouter, useShareAppMessage } from '@tarojs/taro'
import { Button, Text, View } from '@tarojs/components'
import {
  generateReport,
  getReportDetail,
  getReportHistory,
  Quiz,
  Report,
  ReportHistoryItem
} from '../../services/quizService'
import './index.css'

export default function ReportPage() {
  const router = useRouter()
  const [report, setReport] = useState<Report | null>(null)
  const [reportHistory, setReportHistory] = useState<ReportHistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useShareAppMessage(() => ({
    title: report ? `我的学习报告：${report.title}` : '水母 DIY 学习助手',
    path: '/pages/create/index'
  }))

  useDidShow(async () => {
    const storedQuiz = Taro.getStorageSync<Quiz>('currentQuiz')
    const historyQuizId = Taro.getStorageSync<string>('historyReportQuizId')
    const quizId = router.params.quizId || historyQuizId || storedQuiz?.quizId

    if (historyQuizId) {
      Taro.removeStorageSync('historyReportQuizId')
    }

    if (!quizId) {
      setReport(null)
      await loadReportHistory()
      setLoading(false)
      return
    }

    setLoading(true)
    try {
      const nextReport = historyQuizId ? await getReportDetail(quizId) : await generateReport(quizId)
      setReport(nextReport)
      const history = Taro.getStorageSync<Report[]>('learningReports') || []
      Taro.setStorageSync('learningReports', [nextReport, ...history.filter((item) => item.quizId !== quizId)].slice(0, 10))
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '报告加载失败',
        icon: 'none'
      })
      setReport(null)
      await loadReportHistory()
    } finally {
      setLoading(false)
    }
  })

  async function loadReportHistory() {
    try {
      const list = await getReportHistory()
      setReportHistory(list)
    } catch (error) {
      setReportHistory([])
    }
  }

  function openSavedReport(quizId: string) {
    Taro.setStorageSync('historyReportQuizId', quizId)
    Taro.switchTab({ url: '/pages/report/index' })
  }

  function shareToQQ() {
    Taro.showToast({ title: 'QQ 分享入口已保留', icon: 'none' })
  }

  if (loading) {
    return (
      <View className='report-page loading-page'>
        <View className='loading-card'>
          <View className='mini-jelly'>
            <View className='mini-jelly-body'>
              <View className='mini-mouth' />
            </View>
          </View>
          <View className='loading-dot-group'>
            <View className='loading-dot' />
            <View className='loading-dot loading-dot-delay-1' />
            <View className='loading-dot loading-dot-delay-2' />
          </View>
          <Text className='loading-title'>loading......</Text>
          <Text className='muted'>水母正在整理你的学习报告</Text>
        </View>
      </View>
    )
  }

  if (!report) {
    return (
      <View className='report-page'>
        <View className='report-cover'>
          <Text className='cover-label'>REPORT HISTORY</Text>
          <View className='cover-bubble' />
        </View>

        <View className='report-card'>
          <Text className='report-title'>报告历史</Text>
          <Text className='report-summary'>完成闯关并生成报告后，可以在这里重新打开最近的学习报告。</Text>

          {reportHistory.length === 0 && (
            <View className='report-section'>
              <Text className='block-title'>暂无报告</Text>
              <Text className='list-line'>- 先完成一组水母闯关，再回来查看报告。</Text>
            </View>
          )}

          {reportHistory.map((item) => (
            <View key={item.quizId} className='report-history-card' onClick={() => openSavedReport(item.quizId)}>
              <Text className='report-history-title'>{item.title}</Text>
              <Text className='report-history-meta'>{item.score}/{item.total} 得分 · {item.mastery}% 掌握度</Text>
              <Text className='report-history-time'>{item.completedAt?.slice(0, 10) || '刚刚完成'}</Text>
            </View>
          ))}
        </View>
      </View>
    )
  }

  return (
    <View className='report-page'>
      <View className='report-cover'>
        <Text className='cover-label'>REPORT CENTER</Text>
        <View className='cover-bubble' />
      </View>

      <View className='report-card'>
        <Text className='report-title'>水母学习报告</Text>
        <Text className='report-summary'>{report.summary}</Text>

        <View className='score-row'>
          <View className='score-box score-box-yellow'>
            <Text className='score-number'>{report.score}/{report.total}</Text>
            <Text className='score-label'>答题得分</Text>
          </View>
          <View className='score-box score-box-blue'>
            <Text className='score-number'>{report.mastery}%</Text>
            <Text className='score-label'>掌握度</Text>
          </View>
        </View>

        <View className='report-section yellow'>
          <Text className='block-title'>本次总览</Text>
          <Text className='list-line'>- 完成 {report.total} 道题，答对 {report.score} 道。</Text>
          <Text className='list-line'>- 掌握度：{report.mastery}%。</Text>
          <Text className='list-line'>- 主题：{report.title}</Text>
        </View>

        <View className='report-section'>
          <Text className='block-title'>薄弱点</Text>
          {report.weakPoints.map((item) => (
            <Text key={item} className='list-line'>- {item}</Text>
          ))}
        </View>

        <View className='report-section blue'>
          <Text className='block-title'>知识拆解</Text>
          <Text className='list-line'>- 先复盘错题对应的概念。</Text>
          <Text className='list-line'>- 再用自己的话解释正确答案。</Text>
          <Text className='list-line'>- 最后重新生成一组薄弱点练习。</Text>
        </View>

        <View className='report-section'>
          <Text className='block-title'>下一步建议</Text>
          {report.nextSteps.map((item) => (
            <Text key={item} className='list-line'>- {item}</Text>
          ))}
        </View>

        <View className='share-row'>
          <Button className='share-button share-button-wechat' openType='share'>分享到微信</Button>
          <Button className='share-button share-button-qq' onClick={shareToQQ}>分享到 QQ</Button>
        </View>
      </View>
    </View>
  )
}
