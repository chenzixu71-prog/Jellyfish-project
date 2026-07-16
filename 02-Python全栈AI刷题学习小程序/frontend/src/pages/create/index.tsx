import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Image, Switch, Text, Textarea, View } from '@tarojs/components'
import {
  createKnowledgeBaseFromAssets,
  getKnowledgeBases,
  KnowledgeBaseSummary,
  UploadProgress
} from '../../services/knowledgeBaseService'
import { elapsedMilliseconds, trackEvent } from '../../services/analyticsService'
import jellyIcon from '../../assets/jelly-gpt/jelly-icon.png'
import jellyStudy from '../../assets/jelly-gpt/jelly-study.png'
import './index.css'

interface LocalFile { name: string; path: string }


export default function CreatePage() {
  const [content, setContent] = useState('')
  const [files, setFiles] = useState<LocalFile[]>([])
  const [images, setImages] = useState<string[]>([])
  const [webSearchEnabled, setWebSearchEnabled] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseSummary[]>([])

  useDidShow(() => { void loadKnowledgeBases() })


  async function loadKnowledgeBases() {
    try { setKnowledgeBases(await getKnowledgeBases()) } catch (error) {
      setKnowledgeBases([])
    }
  }

  async function chooseFiles() {
    try {
      const result = await Taro.chooseMessageFile({ count: 3, type: 'file', extension: ['txt', 'md', 'csv', 'json'] })
      const nextFiles = (result.tempFiles || []).slice(0, 3).map((file) => ({ name: file.name, path: file.path }))
      setFiles(nextFiles)
      trackEvent('asset_select', { asset_type: 'file', asset_count: nextFiles.length })
    } catch { Taro.showToast({ title: '暂未选择文件', icon: 'none' }) }
  }

  async function chooseImages() {
    try {
      const result = await Taro.chooseImage({ count: 10, sizeType: ['compressed'], sourceType: ['album', 'camera'] })
      const nextImages = (result.tempFilePaths || []).slice(0, 10)
      setImages(nextImages)
      trackEvent('asset_select', { asset_type: 'image', asset_count: nextImages.length })
    } catch { Taro.showToast({ title: '暂未选择图片', icon: 'none' }) }
  }

  function handleSearchToggle(enabled: boolean) {
    setWebSearchEnabled(enabled)
    trackEvent('search_toggle', { enabled, scene: 'knowledge_create' })
  }

  function buildTitle(trimmed: string) {
    const firstLine = trimmed.split('\n').find((line) => line.trim())?.trim()
    if (firstLine) return firstLine.slice(0, 18)
    if (files[0]?.name) return files[0].name.replace(/\.[^.]+$/, '').slice(0, 18)
    return '水母知识库'
  }

  async function handleCreateKnowledgeBase() {
    const trimmed = content.trim()
    if (!trimmed && files.length === 0 && images.length === 0) {
      Taro.showToast({ title: '先输入主题或选择素材', icon: 'none' }); return
    }
    if (knowledgeBases.length >= 5) {
      Taro.showToast({ title: '最多创建 5 个知识库', icon: 'none' }); return
    }
    const startedAt = Date.now()
    const inputType = files.length > 0 ? 'file' : images.length > 0 ? 'image' : 'text'
    trackEvent('knowledge_create', {
      status: 'start',
      input_type: inputType,
      search_enabled: webSearchEnabled,
      file_count: files.length,
      image_count: images.length
    })
    setLoading(true)
    setUploadProgress(null)
    try {
      const assets = [
        ...files.map((file) => ({ path: file.path, type: 'file' as const, name: file.name })),
        ...images.map((path) => ({ path, type: 'image' as const }))
      ]
      const knowledgeBase = await createKnowledgeBaseFromAssets(
        buildTitle(trimmed), trimmed, webSearchEnabled, assets, setUploadProgress
      )
      trackEvent('knowledge_create', {
        status: 'success',
        input_type: inputType,
        search_enabled: webSearchEnabled,
        duration_ms: elapsedMilliseconds(startedAt),
        material_count: knowledgeBase.materials.length,
        source_count: knowledgeBase.sourceMeta?.sourceCount || 0
      })
      setContent(''); setFiles([]); setImages([])
      await loadKnowledgeBases()
      Taro.navigateTo({ url: `/pages/knowledge-base/index?id=${knowledgeBase.id}` })
    } catch (error) {
      trackEvent('knowledge_create', {
        status: 'fail',
        input_type: inputType,
        search_enabled: webSearchEnabled,
        duration_ms: elapsedMilliseconds(startedAt)
      })
      Taro.showToast({ title: error instanceof Error ? error.message : '生成失败', icon: 'none' })
    } finally { setLoading(false); setUploadProgress(null) }
  }

  return (
    <View className='create-page'>
      <View className='hero'>
        <View className='brand-pill'>
          <Image className='brand-icon' src={jellyIcon} mode='aspectFit' />
          <Text className='brand-name'>Jelly</Text><Text className='brand-tag'>Quest</Text>
        </View>
        <View className='hero-main'>
          <View className='hero-copy'>
            <Text className='hero-kicker'>AI 学习闯关</Text>
            <Text className='hero-title'>把知识变成水母关卡</Text>
            <Text className='hero-desc'>输入主题、上传资料或联网搜索，先沉淀知识库，再到闯关页开始学习。</Text>
          </View>
          <View className='hero-mascot'>
            <View className='hero-bubble bubble-a' /><View className='hero-bubble bubble-b' />
            <Image className='hero-jelly' src={jellyStudy} mode='aspectFit' />
          </View>
        </View>
      </View>

      <View className='content-shell'>
        <View className='input-card'>
          <Text className='input-title'>今天想学什么？</Text>
          <Text className='input-helper'>一句话、一个网址或一份资料都可以</Text>
          <Textarea className='learning-input' value={content} placeholder='例如：我想学习英语' maxlength={1000} showConfirmBar={false} onInput={(event) => setContent(event.detail.value)} />
          <View className='asset-row'>
            <Button className='asset-button asset-yellow' onClick={chooseFiles}>文件 {files.length}/3</Button>
            <Button className='asset-button asset-blue' onClick={chooseImages}>图片 {images.length}/10</Button>
          </View>
          <View className={`search-card ${webSearchEnabled ? 'search-enabled' : ''}`}>
            <View className='search-copy'><Text className='search-title'>联网搜索资料</Text><Text className='search-desc'>{webSearchEnabled ? '将调用外部搜索补充最新资料和网页内容' : '仅解析输入和上传资料，不调用联网搜索'}</Text></View>
            <Switch color='#6D5DF6' checked={webSearchEnabled} onChange={(event) => handleSearchToggle(event.detail.value)} />
          </View>
          <Button className='primary-cta' disabled={loading} onClick={handleCreateKnowledgeBase}>{webSearchEnabled ? '搜索并生成知识库' : '生成水母知识库'}</Button>
        </View>

      </View>

      {loading && (
        <View className='loading-mask'><View className='loading-card'>
          <Image className='loading-jelly' src={jellyStudy} mode='aspectFit' />
          <Text className='loading-title'>{uploadProgress ? `正在处理素材 ${uploadProgress.completed}/${uploadProgress.total}` : '正在生成知识库'}</Text>
          <Text className='loading-desc'>{uploadProgress ? '每份素材处理成功后会更新进度' : '水母正在整理成可闯关的知识结构'}</Text>
        </View></View>
      )}
    </View>
  )
}
