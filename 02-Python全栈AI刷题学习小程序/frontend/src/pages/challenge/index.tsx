import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Image, Text, View } from '@tarojs/components'
import {
  getKnowledgeBases,
  KnowledgeBaseSummary
} from '../../services/knowledgeBaseService'
import jellyStudy from '../../assets/jelly-gpt/jelly-study.png'
import './index.css'

function progressPercent(item: KnowledgeBaseSummary) {
  if (item.questionCount <= 0) return 0
  return Math.min(100, Math.round(item.completedQuestionCount / item.questionCount * 100))
}

export default function ChallengePage() {
  const [items, setItems] = useState<KnowledgeBaseSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useDidShow(() => { void loadKnowledgeBases() })

  async function loadKnowledgeBases() {
    setLoading(true)
    setError('')
    try {
      setItems(await getKnowledgeBases())
    } catch (nextError) {
      setItems([])
      setError(nextError instanceof Error ? nextError.message : '闯关知识库加载失败')
    } finally {
      setLoading(false)
    }
  }

  function openKnowledgeBase(id: string) {
    Taro.navigateTo({ url: `/pages/knowledge-base/index?id=${id}` })
  }

  return (
    <View className='challenge-page'>
      <View className='challenge-hero'>
        <View className='challenge-hero-copy'>
          <Text className='challenge-kicker'>JELLY QUEST</Text>
          <Text className='challenge-title'>选择知识库开始闯关</Text>
          <Text className='challenge-subtitle'>每次完成一小轮，累计进度会保存到对应知识库。</Text>
        </View>
        <View className='challenge-mascot-wrap'>
          <View className='challenge-bubble bubble-one' />
          <View className='challenge-bubble bubble-two' />
          <Image className='challenge-mascot' src={jellyStudy} mode='aspectFit' />
        </View>
      </View>

      <View className='challenge-content'>
        <View className='challenge-section-head'>
          <View>
            <Text className='challenge-section-kicker'>MY KNOWLEDGE</Text>
            <Text className='challenge-section-title'>我的闯关题库</Text>
          </View>
          <Text className='challenge-limit'>{items.length}/5</Text>
        </View>

        {loading && (
          <View className='challenge-state-card'>
            <View className='challenge-loading-dot' />
            <Text className='challenge-state-title'>正在同步学习进度</Text>
            <Text className='challenge-state-copy'>水母正在整理你的知识库。</Text>
          </View>
        )}

        {!loading && error && (
          <View className='challenge-state-card'>
            <Text className='challenge-state-title'>暂时无法读取题库</Text>
            <Text className='challenge-state-copy'>{error}</Text>
            <Button className='challenge-state-button' onClick={loadKnowledgeBases}>重新加载</Button>
          </View>
        )}

        {!loading && !error && items.length === 0 && (
          <View className='challenge-state-card'>
            <Text className='challenge-state-title'>还没有可以闯关的知识库</Text>
            <Text className='challenge-state-copy'>先在首页输入主题或上传资料，创建你的第一个知识库。</Text>
            <Button className='challenge-state-button' onClick={() => Taro.switchTab({ url: '/pages/create/index' })}>去首页创建</Button>
          </View>
        )}

        {!loading && !error && items.map((item) => {
          const progress = progressPercent(item)
          const hasQuestions = item.questionCount > 0
          const completed = hasQuestions && item.completedQuestionCount >= item.questionCount
          return (
            <View key={item.id} className='challenge-library-card' onClick={() => openKnowledgeBase(item.id)}>
              <View className='challenge-card-head'>
                <View className='challenge-card-copy'>
                  <Text className='challenge-library-title'>{item.title}</Text>
                  <Text className='challenge-library-summary'>{item.summary}</Text>
                </View>
                <Text className={`challenge-status ${completed ? 'is-complete' : ''}`}>
                  {completed ? '已学完' : hasQuestions ? '继续' : '待出题'}
                </Text>
              </View>

              <View className='challenge-progress-head'>
                <Text className='challenge-progress-label'>知识库进度</Text>
                <Text className='challenge-progress-value'>{item.completedQuestionCount}/{item.questionCount}</Text>
              </View>
              <View className='challenge-progress-track'>
                <View className='challenge-progress-fill' style={{ width: `${progress}%` }} />
              </View>
              <View className='challenge-meta-row'>
                <Text className='challenge-meta-chip'>{item.materialCount} 份素材</Text>
                <Text className='challenge-meta-chip is-blue'>{item.sourceCount} 条联网来源</Text>
                <Text className='challenge-open-copy'>{hasQuestions ? '进入题库' : '生成首轮题目'} ›</Text>
              </View>
            </View>
          )
        })}
      </View>
    </View>
  )
}
