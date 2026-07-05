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
        <View className='hand-logo'>Jellyfish</View>
        <Text className='hero-title'>水母diy学习助手</Text>
        <Text className='hero-subtitle'>把一段知识变成 5 题闯关练习，答完立刻生成复盘报告。</Text>
      </View>

      <View className='card input-card'>
        <View className='boy-illustration'>
          <View className='face face-boy'>
            <View className='eye left-eye' />
            <View className='eye right-eye' />
            <View className='smile' />
          </View>
          <View className='speech-bubble'>Let&apos;s learn</View>
        </View>

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
          生成闯关题
        </Button>
      </View>
    </View>
  )
}
