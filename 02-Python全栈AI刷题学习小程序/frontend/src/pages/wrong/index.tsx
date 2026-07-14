import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Image, Text, View } from '@tarojs/components'
import { getWrongQuestions, regenerateWeakQuiz, WrongQuestion } from '../../services/quizService'
import jellyReviewSprite from '../../assets/jelly-gpt/jelly-review-sprite.png'
import './index.css'

function answerCopy(answer: string[]) {
  return answer.length > 0 ? answer.join('、') : '暂无'
}

export default function WrongPage() {
  const [wrongQuestions, setWrongQuestions] = useState<WrongQuestion[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useDidShow(() => {
    loadWrongQuestions()
  })

  async function loadWrongQuestions() {
    setLoading(true)
    try {
      const list = await getWrongQuestions()
      setWrongQuestions(list)
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '错题读取失败',
        icon: 'none'
      })
    } finally {
      setLoading(false)
    }
  }

  async function startWeakQuiz() {
    const first = wrongQuestions[0]
    if (!first) {
      Taro.showToast({ title: '还没有可复习的错题', icon: 'none' })
      return
    }

    setGenerating(true)
    try {
      const quiz = await regenerateWeakQuiz(first.quizId)
      Taro.setStorageSync('currentQuiz', quiz)
      Taro.switchTab({ url: '/pages/quiz/index' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '复习题生成失败',
        icon: 'none'
      })
    } finally {
      setGenerating(false)
    }
  }

  return (
    <View className='wrong-page'>
      <View className='wrong-hero'>
        <View className='wrong-ambient-bubble wrong-ambient-bubble-one' />
        <View className='wrong-ambient-bubble wrong-ambient-bubble-two' />
        <View className='wrong-copy'>
          <Text className='wrong-kicker'>Review Dock</Text>
          <Text className='wrong-title'>错题水母舱</Text>
          <Text className='wrong-subtitle'>把答错的知识点收集起来，下一轮专门练薄弱处。</Text>
        </View>
        <View className='wrong-mascot-stage' aria-label='会思考的水母学习伙伴'>
          <View className='wrong-mascot-bubble wrong-mascot-bubble-one' />
          <View className='wrong-mascot-bubble wrong-mascot-bubble-two' />
          <View className='wrong-sprite-window'>
            <Image className='wrong-sprite-strip' src={jellyReviewSprite} mode='scaleToFill' />
          </View>
        </View>
      </View>

      <View className='wrong-panel'>
        <View className='wrong-panel-head'>
          <View>
            <Text className='panel-title'>待复习错题</Text>
            <Text className='panel-copy'>共 {wrongQuestions.length} 道需要回看</Text>
          </View>
          <Button className='weak-button' loading={generating} onClick={startWeakQuiz}>
            生成复习闯关
          </Button>
        </View>

        {loading && (
          <View className='empty-card'>
            <Text className='empty-title'>正在打捞错题...</Text>
            <Text className='empty-copy'>水母正在打捞你的错题。</Text>
          </View>
        )}

        {!loading && wrongQuestions.length === 0 && (
          <View className='empty-card'>
            <Text className='empty-title'>还没有错题</Text>
            <Text className='empty-copy'>完成一次闯关后，答错的题会自动出现在这里。</Text>
          </View>
        )}

        {!loading && wrongQuestions.map((item, index) => (
          <View key={`${item.quizId}-${item.questionId}`} className='wrong-card'>
            <View className='wrong-card-top'>
              <Text className='wrong-index'>#{index + 1}</Text>
              <Text className='knowledge-pill'>{item.knowledge_point}</Text>
            </View>
            <Text className='wrong-stem'>{item.stem}</Text>
            <View className='answer-grid'>
              <View className='answer-box answer-box-soft'>
                <Text className='answer-label'>你的答案</Text>
                <Text className='answer-value'>{answerCopy(item.selectedAnswer)}</Text>
              </View>
              <View className='answer-box answer-box-yellow'>
                <Text className='answer-label'>正确答案</Text>
                <Text className='answer-value'>{answerCopy(item.correctAnswer)}</Text>
              </View>
            </View>
            <View className='explain-box'>
              <Text className='explain-label'>水母讲解</Text>
              <Text className='explain-copy'>{item.explanation}</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  )
}
