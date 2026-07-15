import { useState } from 'react'
import Taro, { useDidShow, useRouter } from '@tarojs/taro'
import { Button, Switch, Text, Textarea, View } from '@tarojs/components'
import {
  getKnowledgeBase,
  KnowledgeBase,
  startKnowledgeBaseQuiz,
  supplementKnowledgeBaseFromAssets,
  UploadProgress
} from '../../services/knowledgeBaseService'
import { elapsedMilliseconds, trackEvent } from '../../services/analyticsService'
import './index.css'

interface LocalFile {
  name: string
  path: string
}

export default function KnowledgeBasePage() {
  const router = useRouter()
  const knowledgeBaseId = String(router.params.id || '')
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null)
  const [content, setContent] = useState('')
  const [files, setFiles] = useState<LocalFile[]>([])
  const [images, setImages] = useState<string[]>([])
  const [webSearchEnabled, setWebSearchEnabled] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [saving, setSaving] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
  const [starting, setStarting] = useState(false)

  useDidShow(() => {
    loadKnowledgeBase()
  })

  async function loadKnowledgeBase() {
    if (!knowledgeBaseId) {
      setLoading(false)
      return
    }
    setLoading(true)
    setLoadError('')
    try {
      const next = await getKnowledgeBase(knowledgeBaseId)
      setKnowledgeBase(next)
    } catch (error) {
      setKnowledgeBase(null)
      setLoadError(error instanceof Error ? error.message : '知识库加载失败')
    } finally {
      setLoading(false)
    }
  }

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

  async function saveSupplement() {
    const nextContent = content.trim()
    if (!nextContent && files.length === 0 && images.length === 0) {
      Taro.showToast({ title: '先输入或选择补充资料', icon: 'none' })
      return
    }
    const startedAt = Date.now()
    trackEvent('knowledge_supplement', {
      status: 'start',
      search_enabled: webSearchEnabled,
      file_count: files.length,
      image_count: images.length
    })
    setSaving(true)
    setUploadProgress(null)
    try {
      const assets = [
        ...files.map((file) => ({ path: file.path, type: 'file' as const, name: file.name })),
        ...images.map((path) => ({ path, type: 'image' as const }))
      ]
      const next = await supplementKnowledgeBaseFromAssets(
        knowledgeBaseId, nextContent, webSearchEnabled, assets, setUploadProgress
      )
      trackEvent('knowledge_supplement', {
        status: 'success',
        search_enabled: webSearchEnabled,
        duration_ms: elapsedMilliseconds(startedAt),
        material_count: next.materials.length
      })
      setKnowledgeBase(next)
      setContent('')
      setFiles([])
      setImages([])
      Taro.showToast({ title: '已补充知识库', icon: 'none' })
    } catch (error) {
      trackEvent('knowledge_supplement', {
        status: 'fail',
        search_enabled: webSearchEnabled,
        duration_ms: elapsedMilliseconds(startedAt)
      })
      Taro.showToast({
        title: error instanceof Error ? error.message : '补充失败',
        icon: 'none'
      })
    } finally {
      setSaving(false)
      setUploadProgress(null)
    }
  }

  async function startQuiz() {
    if (!knowledgeBase) return
    setStarting(true)
    try {
      const quiz = await startKnowledgeBaseQuiz(knowledgeBase.id)
      Taro.setStorageSync('currentQuiz', quiz)
      Taro.switchTab({ url: '/pages/quiz/index' })
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '生成闯关失败',
        icon: 'none'
      })
    } finally {
      setStarting(false)
    }
  }

  if (loading) {
    return (
      <View className='kb-detail-page'>
        <View className='kb-hero'>
          <Text className='kb-kicker'>Knowledge Dock</Text>
          <Text className='kb-hero-title'>水母正在整理知识库</Text>
        </View>
        <View className='kb-detail-card'>
          <Text className='kb-muted'>loading......</Text>
        </View>
      </View>
    )
  }

  if (loadError) {
    return (
      <View className='kb-detail-page'>
        <View className='kb-hero'><Text className='kb-kicker'>Knowledge Dock</Text><Text className='kb-hero-title'>知识库加载失败</Text></View>
        <View className='kb-detail-card kb-state-card'><Text className='kb-muted kb-error-text'>{loadError}</Text><Button className='kb-retry-button' onClick={loadKnowledgeBase}>重新加载</Button></View>
      </View>
    )
  }

  if (!knowledgeBase) {
    return (
      <View className='kb-detail-page'>
        <View className='kb-hero'>
          <Text className='kb-kicker'>Knowledge Dock</Text>
          <Text className='kb-hero-title'>知识库不存在</Text>
        </View>
        <View className='kb-detail-card'>
          <Text className='kb-muted'>请回到首页重新选择知识库。</Text>
        </View>
      </View>
    )
  }

  return (
    <View className='kb-detail-page'>
      <View className='kb-hero'>
        <View className='kb-hero-copy'>
          <Text className='kb-kicker'>Knowledge Dock</Text>
          <Text className='kb-hero-title'>{knowledgeBase.title}</Text>
          <Text className='kb-hero-subtitle'>{knowledgeBase.summary}</Text>
        </View>
        <View className='kb-jelly'>
          <View className='kb-jelly-body'>
            <View className='kb-jelly-mouth' />
          </View>
          <View className='kb-tentacle kb-tentacle-one' />
          <View className='kb-tentacle kb-tentacle-two' />
          <View className='kb-tentacle kb-tentacle-three' />
        </View>
      </View>

      <View className='kb-detail-card kb-actions-card'>
        <View className='kb-stat-row'>
          <View className='kb-stat'>
            <Text className='kb-stat-value'>{knowledgeBase.materials.length}</Text>
            <Text className='kb-stat-label'>素材</Text>
          </View>
          <View className='kb-stat kb-stat-blue'>
            <Text className='kb-stat-value'>{knowledgeBase.sourceMeta?.sourceCount || 0}</Text>
            <Text className='kb-stat-label'>来源</Text>
          </View>
          <View className='kb-stat kb-stat-yellow'>
            <Text className='kb-stat-value'>{knowledgeBase.quizIds.length}</Text>
            <Text className='kb-stat-label'>闯关</Text>
          </View>
        </View>
        <Button className='kb-primary-button' loading={starting} onClick={startQuiz}>
          从知识库开始闯关
        </Button>
      </View>

      <View className='kb-detail-card'>
        <Text className='kb-section-title'>补充知识</Text>
        <Textarea
          className='kb-textarea'
          value={content}
          placeholder='补充新的知识点、网页链接、课堂笔记，水母会更新知识库。'
          maxlength={1000}
          showConfirmBar={false}
          onInput={(event) => setContent(event.detail.value)}
        />
        <View className='kb-upload-row'>
          <Button className='kb-secondary-button' onClick={chooseFiles}>文件 {files.length}/3</Button>
          <Button className='kb-secondary-button kb-secondary-blue' onClick={chooseImages}>图片 {images.length}/10</Button>
        </View>
        <View className='kb-search-row'>
          <View>
            <Text className='kb-search-title'>联网补充</Text>
            <Text className='kb-search-copy'>适合最新知识、网页链接、产品文档。</Text>
          </View>
          <Switch
            color='#6246f2'
            checked={webSearchEnabled}
            onChange={(event) => {
              setWebSearchEnabled(event.detail.value)
              trackEvent('search_toggle', { enabled: event.detail.value, scene: 'knowledge_supplement' })
            }}
          />
        </View>
        <Button className='kb-save-button' loading={saving} onClick={saveSupplement}>
          {uploadProgress ? `处理素材 ${uploadProgress.completed}/${uploadProgress.total}` : '补充到知识库'}
        </Button>
        {saving && uploadProgress && <Text className='kb-progress-copy'>每份素材处理成功后会更新进度，失败时将停止后续上传。</Text>}
      </View>

      {knowledgeBase.sourceMeta?.enabled && (
        <View className='kb-detail-card'>
          <Text className='kb-section-title'>联网资料来源</Text>
          {knowledgeBase.sourceMeta.sources.length === 0 && (
            <Text className='kb-muted'>本次没有可展示来源，已按普通资料整理。</Text>
          )}
          {knowledgeBase.sourceMeta.sources.map((source, index) => (
            <View key={`${source.url}-${index}`} className='kb-source-card'>
              <Text className='kb-source-title'>{index + 1}. {source.title}</Text>
              <Text className='kb-source-summary'>{source.summary}</Text>
            </View>
          ))}
        </View>
      )}

      <View className='kb-detail-card'>
        <Text className='kb-section-title'>素材记录</Text>
        {knowledgeBase.materials.map((material) => (
          <View key={material.id} className='kb-material-card'>
            <Text className='kb-material-title'>{material.name}</Text>
            <Text className='kb-material-summary'>{material.summary}</Text>
          </View>
        ))}
      </View>
    </View>
  )
}
