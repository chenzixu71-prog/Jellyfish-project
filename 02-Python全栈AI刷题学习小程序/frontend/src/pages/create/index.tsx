import { useState } from 'react'
import Taro from '@tarojs/taro'
import { Button, Text, Textarea, View } from '@tarojs/components'
import { generateQuiz } from '../../services/quizService'
import './index.css'

const defaultPrompt = '例如：我想学习 HTTP 请求、端口、数据库和 Redis 的基础概念'

export default function CreatePage() {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleGenerate() {
    const trimmed = content.trim()
    if (!trimmed) {
      Taro.showToast({ title: '先输入一个学习主题', icon: 'none' })
      return
    }

    setLoading(true)
    try {
      const quiz = await generateQuiz(trimmed)
      Taro.setStorageSync('currentQuiz', quiz)
      Taro.navigateTo({ url: '/pages/quiz/index' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '生成失败',
        icon: 'none'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className='page create-page'>
      <View className='hero'>
        <View className='bubble bubble-small' />
        <View className='bubble bubble-soft' />
        <View className='brand-row'>
          <Text className='hand-logo'>Jelly Quest</Text>
          <Text className='status-pill'>今日挑战 5 题</Text>
        </View>
        <Text className='hero-title'>水母 DIY 学习助手</Text>
        <Text className='hero-subtitle'>把一段知识变成闯关练习，答完马上看到讲解和学习报告。</Text>
        <View className='jellyfish-hero'>
          <View className='jelly-head'>
            <View className='jelly-eye jelly-eye-left' />
            <View className='jelly-eye jelly-eye-right' />
            <View className='jelly-mouth' />
          </View>
          <View className='tentacle tentacle-1' />
          <View className='tentacle tentacle-2' />
          <View className='tentacle tentacle-3' />
          <View className='tentacle tentacle-4' />
          <View className='front-bubble front-bubble-1' />
          <View className='front-bubble front-bubble-2' />
        </View>
      </View>

      <View className='card input-card'>
        <Text className='section-title'>今天想学什么？</Text>
        <Textarea
          className='learning-input'
          value={content}
          placeholder={defaultPrompt}
          maxlength={1000}
          showConfirmBar={false}
          onInput={(event) => setContent(event.detail.value)}
        />
        <Button className='primary-button generate-button' loading={loading} onClick={handleGenerate}>
          让水母生成题目
        </Button>
      </View>
    </View>
  )
}
