import { useState } from 'react'
import Taro from '@tarojs/taro'
import { Button, Text, Textarea, View } from '@tarojs/components'
import { generateQuiz } from '../../services/quizService'
import './index.css'

const defaultPrompt = '例如：我想学习 HTTP 请求、端口、数据库和 Redis 的基础概念'

interface LocalFile {
  name: string
  path: string
}

export default function CreatePage() {
  const [content, setContent] = useState('')
  const [files, setFiles] = useState<LocalFile[]>([])
  const [images, setImages] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  async function chooseFiles() {
    try {
      const result = await Taro.chooseMessageFile({
        count: 3,
        type: 'file',
        extension: ['txt', 'md', 'csv', 'json']
      })
      setFiles((result.tempFiles || []).slice(0, 3).map((file) => ({
        name: file.name,
        path: file.path
      })))
    } catch {
      Taro.showToast({ title: '暂未选择文件', icon: 'none' })
    }
  }

  async function chooseImages() {
    try {
      const result = await Taro.chooseImage({
        count: 10,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera']
      })
      setImages((result.tempFilePaths || []).slice(0, 10))
    } catch {
      Taro.showToast({ title: '暂未选择图片', icon: 'none' })
    }
  }

  function buildLearningContent(trimmed: string) {
    const parts = [trimmed]
    if (files.length > 0) {
      const fs = Taro.getFileSystemManager()
      files.forEach((file) => {
        try {
          const text = fs.readFileSync(file.path, 'utf8')
          parts.push(`\n\n【上传文件：${file.name}】\n${String(text).slice(0, 2000)}`)
        } catch {
          parts.push(`\n\n【上传文件：${file.name}】文件已选择，但小程序本地读取失败，请根据文件名辅助出题。`)
        }
      })
    }
    if (images.length > 0) {
      parts.push(`\n\n【上传图片】用户选择了 ${images.length} 张图片。当前版本先记录图片数量；如果图片里有关键知识，请用户在文本里补充说明。`)
    }
    return parts.filter(Boolean).join('')
  }

  async function handleGenerate() {
    const trimmed = content.trim()
    if (!trimmed && files.length === 0 && images.length === 0) {
      Taro.showToast({ title: '先输入主题或选择素材', icon: 'none' })
      return
    }

    setLoading(true)
    try {
      const quiz = await generateQuiz(buildLearningContent(trimmed))
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
    <View className='create-page'>
      <View className='brand-hero'>
        <View className='brand-row'>
          <View className='brand-icon'>
            <Text>J</Text>
          </View>
          <Text className='brand-name'>Jelly Quest</Text>
          <Text className='top-mark'>AI</Text>
        </View>

        <Text className='hero-title'>
          <Text className='cyan-word'>水母</Text>
          <Text> DIY </Text>
          <Text className='yellow-word'>学习</Text>
        </Text>
        <Text className='hero-subtitle'>把零散知识变成 5 道闯关题，答完马上看到讲解和报告。</Text>

        <View className='challenge-card'>
          <Text className='challenge-title'>今日水母挑战已准备</Text>
          <View className='challenge-stats'>
            <View className='stat-pill'><Text className='stat-dot'>5</Text><Text>闯关题</Text></View>
            <View className='stat-pill'><Text className='stat-dot blue'>AI</Text><Text>即时讲解</Text></View>
          </View>
        </View>

        <View className='ocean-stage'>
          <View className='ocean-bubble bubble-one' />
          <View className='ocean-bubble bubble-two' />
          <View className='ocean-bubble bubble-three' />
          <View className='jellyfish'>
            <View className='jelly-body'>
              <View className='jelly-highlight' />
              <View className='jelly-smile' />
              <View className='jelly-cheek jelly-cheek-left' />
              <View className='jelly-cheek jelly-cheek-right' />
            </View>
            <View className='jelly-arm jelly-arm-left' />
            <View className='jelly-arm jelly-arm-right' />
            <View className='tentacle tentacle-1' />
            <View className='tentacle tentacle-2' />
            <View className='tentacle tentacle-3' />
            <View className='tentacle tentacle-4' />
          </View>
          <Text className='jelly-label'>今日水母挑战</Text>
        </View>
      </View>

      <View className='input-panel'>
        <Text className='section-title'>今天想学什么？</Text>
        <Textarea
          className='learning-input'
          value={content}
          placeholder={defaultPrompt}
          maxlength={1000}
          showConfirmBar={false}
          onInput={(event) => setContent(event.detail.value)}
        />
        <View className='upload-row'>
          <Button className='upload-button' onClick={chooseFiles}>文件 {files.length}/3</Button>
          <Button className='upload-button upload-image' onClick={chooseImages}>图片 {images.length}/10</Button>
        </View>
        <Button className='main-button' loading={loading} onClick={handleGenerate}>
          让水母生成题目
        </Button>
      </View>

      {loading && (
        <View className='loading-overlay'>
          <View className='loading-panel'>
            <View className='loading-jelly'>
              <View className='loading-jelly-body' />
              <View className='loading-tentacle loading-tentacle-1' />
              <View className='loading-tentacle loading-tentacle-2' />
              <View className='loading-tentacle loading-tentacle-3' />
            </View>
            <Text className='loading-title'>水母正在解析素材...</Text>
            <Text className='loading-copy'>正在生成适合闯关的 5 道题。</Text>
            <View className='loading-track'><View className='loading-fill' /></View>
          </View>
        </View>
      )}
    </View>
  )
}
