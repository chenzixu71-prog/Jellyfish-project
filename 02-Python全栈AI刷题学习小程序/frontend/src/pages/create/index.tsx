import { useEffect, useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Image, Switch, Text, Textarea, View } from '@tarojs/components'
import {
  createKnowledgeBase,
  getKnowledgeBases,
  KnowledgeBaseSummary
} from '../../services/knowledgeBaseService'
import jellyLogo from '../../assets/jelly-logo.jpg'
import './index.css'

const defaultPrompt = '例如我想学习英语'

interface LocalFile {
  name: string
  path: string
}

export default function CreatePage() {
  const [content, setContent] = useState('')
  const [files, setFiles] = useState<LocalFile[]>([])
  const [images, setImages] = useState<string[]>([])
  const [webSearchEnabled, setWebSearchEnabled] = useState(false)
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseSummary[]>([])
  const [listLoading, setListLoading] = useState(false)

  useDidShow(() => {
    loadKnowledgeBases()
  })

  useEffect(() => {
    if (!loading) {
      setLoadingStep(0)
      return undefined
    }

    const timer = setInterval(() => {
      setLoadingStep((step) => Math.min(step + 1, 2))
    }, 1200)
    return () => clearInterval(timer)
  }, [loading])

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
          parts.push(`\n\n[上传文件：${file.name}]\n${String(text).slice(0, 2000)}`)
        } catch {
          parts.push(`\n\n[上传文件：${file.name}] 文件已选择，但小程序本地读取失败，请根据文件名辅助出题。`)
        }
      })
    }
    if (images.length > 0) {
      parts.push(`\n\n[上传图片] 用户选择了 ${images.length} 张图片。当前小程序端先记录图片数量；如果图片里有关键知识，请用户在文本里补充说明。`)
    }
    return parts.filter(Boolean).join('')
  }

  async function loadKnowledgeBases() {
    setListLoading(true)
    try {
      const list = await getKnowledgeBases()
      setKnowledgeBases(list)
    } catch {
      setKnowledgeBases([])
    } finally {
      setListLoading(false)
    }
  }

  async function handleCreateKnowledgeBase() {
    const trimmed = content.trim()
    if (!trimmed && files.length === 0 && images.length === 0) {
      Taro.showToast({ title: '先输入主题或选择素材', icon: 'none' })
      return
    }

    setLoading(true)
    setLoadingStep(0)
    try {
      const knowledgeBase = await createKnowledgeBase(
        buildTitle(trimmed),
        buildLearningContent(trimmed),
        webSearchEnabled
      )
      if (knowledgeBase.sourceMeta?.enabled) {
        Taro.showToast({
          title: knowledgeBase.sourceMeta.sourceCount > 0 ? `已参考 ${knowledgeBase.sourceMeta.sourceCount} 条资料` : '联网搜索已降级',
          icon: 'none'
        })
      }
      setContent('')
      setFiles([])
      setImages([])
      await loadKnowledgeBases()
      Taro.navigateTo({ url: `/pages/knowledge-base/index?id=${knowledgeBase.id}` })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '生成失败',
        icon: 'none'
      })
    } finally {
      setLoading(false)
    }
  }

  const loadingSteps = webSearchEnabled
    ? ['联网检索新资料', '整理可信来源', '沉淀知识库']
    : ['读取学习素材', '拆解知识重点', '沉淀知识库']

  function buildTitle(trimmed: string) {
    const firstLine = trimmed.split('\n').find((line) => line.trim())?.trim()
    if (firstLine) {
      return firstLine.slice(0, 18)
    }
    if (files[0]?.name) {
      return files[0].name.replace(/\.[^.]+$/, '').slice(0, 18)
    }
    return '水母知识库'
  }

  function openKnowledgeBase(id: string) {
    Taro.navigateTo({ url: `/pages/knowledge-base/index?id=${id}` })
  }

  return (
    <View className='create-page'>
      <View className='brand-hero'>
        <View className='brand-row'>
          <Image className='brand-logo-image' src={jellyLogo} mode='aspectFill' />
          <Text className='brand-main'>Jelly</Text>
          <Text className='brand-quest'>Quest</Text>
          <Text className='top-mark'>AI</Text>
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

      <View className='home-board'>
        <View className='challenge-card'>
          <Text className='challenge-title'>今日水母知识库已准备</Text>
          <Text className='challenge-copy'>先把学习资料沉淀成知识库，再从知识库里进入 5 题闯关。</Text>
          <View className='tag-row'>
            <Text className='topic-tag'>知识点</Text>
            <Text className='topic-tag'>AI 讲解</Text>
            <Text className='topic-tag'>复盘报告</Text>
          </View>
          <View className='progress-card'>
            <View className='progress-head'>
              <Text className='progress-title'>今日题目</Text>
              <Text className='progress-count'>5 / 20</Text>
            </View>
            <View className='progress-track'>
              <View className='progress-fill' />
            </View>
            <Text className='progress-copy'>每个人最多保留 5 个知识库，适合持续补充和复习。</Text>
          </View>
        </View>

        <View className='kb-panel'>
          <View className='kb-panel-head'>
            <Text className='kb-title'>我的知识库</Text>
            <Text className='kb-count'>{knowledgeBases.length}/5</Text>
          </View>
          {listLoading && <Text className='kb-empty'>同步知识库中...</Text>}
          {!listLoading && knowledgeBases.length === 0 && (
            <Text className='kb-empty'>还没有知识库。先输入一个主题，水母会帮你整理。</Text>
          )}
          {!listLoading && knowledgeBases.map((item) => (
            <View key={item.id} className='kb-card' onClick={() => openKnowledgeBase(item.id)}>
              <View className='kb-card-main'>
                <Text className='kb-card-title'>{item.title}</Text>
                <Text className='kb-card-summary'>{item.summary}</Text>
              </View>
              <View className='kb-card-meta'>
                <Text className='kb-pill'>{item.materialCount} 份素材</Text>
                <Text className='kb-pill kb-pill-blue'>{item.sourceCount} 条来源</Text>
              </View>
            </View>
          ))}
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
          <View className='search-toggle-card'>
            <View className='search-toggle-copy'>
              <Text className='search-toggle-title'>联网搜索资料</Text>
              <Text className='search-toggle-desc'>适合最新知识、网页链接、产品文档，会先搜索再出题。</Text>
            </View>
            <Switch
              color='#6246f2'
              checked={webSearchEnabled}
              onChange={(event) => setWebSearchEnabled(event.detail.value)}
            />
          </View>
          <Button className='main-button' loading={loading} onClick={handleCreateKnowledgeBase}>
            {webSearchEnabled ? '搜索资料并生成知识库' : '让水母生成知识库'}
          </Button>
        </View>
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
            <Text className='loading-title'>{loadingSteps[loadingStep]}</Text>
            <Text className='loading-copy'>
              {webSearchEnabled ? '打开联网搜索后，会先参考搜索结果和网页内容再沉淀。' : '正在整理成可复习的知识库。'}
            </Text>
            <View className='loading-step-row'>
              {loadingSteps.map((step, index) => (
                <Text key={step} className={`loading-step ${index <= loadingStep ? 'loading-step-active' : ''}`}>
                  {index + 1}
                </Text>
              ))}
            </View>
            <View className='loading-track'><View className='loading-fill' /></View>
          </View>
        </View>
      )}
    </View>
  )
}
