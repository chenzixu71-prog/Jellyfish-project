import { useEffect, useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Image, Switch, Text, Textarea, View } from '@tarojs/components'
import { createKnowledgeBase, getKnowledgeBases, KnowledgeBaseSummary } from '../../services/knowledgeBaseService'
import { elapsedMilliseconds, trackEvent } from '../../services/analyticsService'
import jellyIcon from '../../assets/jelly-gpt/jelly-icon.png'
import jellyStudy from '../../assets/jelly-gpt/jelly-study.png'
import './index.css'

interface LocalFile { name: string; path: string }

const loadingSteps = {
  local: ['读取素材', '拆解重点', '生成知识库'],
  search: ['联网搜索', '筛选资料', '生成知识库']
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

  useDidShow(() => { void loadKnowledgeBases() })

  useEffect(() => {
    if (!loading) { setLoadingStep(0); return undefined }
    const timer = setInterval(() => setLoadingStep((step) => (step + 1) % 3), 1100)
    return () => clearInterval(timer)
  }, [loading])

  async function loadKnowledgeBases() {
    setListLoading(true)
    try { setKnowledgeBases(await getKnowledgeBases()) } catch { setKnowledgeBases([]) }
    finally { setListLoading(false) }
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

  function buildLearningContent(trimmed: string) {
    const parts = [trimmed]
    if (files.length > 0) {
      const fs = Taro.getFileSystemManager()
      files.forEach((file) => {
        try {
          const text = fs.readFileSync(file.path, 'utf8')
          parts.push(`\n\n[上传文件：${file.name}]\n${String(text).slice(0, 2000)}`)
        } catch { parts.push(`\n\n[上传文件：${file.name}] 文件已选择，但本地读取失败。`) }
      })
    }
    if (images.length > 0) parts.push(`\n\n[上传图片] 用户选择了 ${images.length} 张图片，请结合用户文本辅助理解。`)
    return parts.filter(Boolean).join('')
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
    try {
      const knowledgeBase = await createKnowledgeBase(buildTitle(trimmed), buildLearningContent(trimmed), webSearchEnabled)
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
    } finally { setLoading(false) }
  }

  const steps = webSearchEnabled ? loadingSteps.search : loadingSteps.local

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
            <Text className='hero-desc'>输入主题、上传资料或联网搜索，先沉淀知识库，再开始 5 题闯关。</Text>
          </View>
          <View className='hero-mascot'>
            <View className='hero-bubble bubble-a' /><View className='hero-bubble bubble-b' />
            <Image className='hero-jelly' src={jellyStudy} mode='aspectFit' />
          </View>
        </View>
      </View>

      <View className='content-shell'>
        <View className='challenge-card'>
          <View className='challenge-head'>
            <View><Text className='section-kicker'>TODAY</Text><Text className='challenge-title'>今日水母挑战</Text></View>
            <Text className='challenge-count'>5 / 20</Text>
          </View>
          <View className='challenge-track'><View className='challenge-fill' /></View>
          <Text className='challenge-copy'>先完成当前 5 题，再根据报告复盘薄弱点。</Text>
        </View>

        <View className='input-card'>
          <Text className='input-title'>今天想学什么？</Text>
          <Text className='input-helper'>一句话、一个网址或一份资料都可以</Text>
          <Textarea className='learning-input' value={content} placeholder='例如：我想学习英语' maxlength={1000} showConfirmBar={false} onInput={(event) => setContent(event.detail.value)} />
          <View className='asset-row'>
            <Button className='asset-button asset-yellow' onClick={chooseFiles}>文件 {files.length}/3</Button>
            <Button className='asset-button asset-blue' onClick={chooseImages}>图片 {images.length}/10</Button>
          </View>
          <View className={`search-card ${webSearchEnabled ? 'search-enabled' : ''}`}>
            <View className='search-copy'><Text className='search-title'>联网搜索资料</Text><Text className='search-desc'>适合最新知识、网页链接和产品文档</Text></View>
            <Switch color='#6D5DF6' checked={webSearchEnabled} onChange={(event) => handleSearchToggle(event.detail.value)} />
          </View>
          <Button className='primary-cta' disabled={loading} onClick={handleCreateKnowledgeBase}>{webSearchEnabled ? '搜索并生成知识库' : '生成水母知识库'}</Button>
        </View>

        <View className='kb-card'>
          <View className='kb-head'><Text className='kb-title'>我的知识库</Text><Text className='kb-count'>{knowledgeBases.length}/5</Text></View>
          {listLoading && <Text className='empty-text'>正在同步知识库...</Text>}
          {!listLoading && knowledgeBases.length === 0 && <Text className='empty-text'>还没有知识库。输入一个主题，让水母帮你整理。</Text>}
          {!listLoading && knowledgeBases.map((item) => (
            <View key={item.id} className='kb-item' onClick={() => Taro.navigateTo({ url: `/pages/knowledge-base/index?id=${item.id}` })}>
              <Text className='kb-item-title'>{item.title}</Text><Text className='kb-item-summary'>{item.summary}</Text>
              <View className='kb-meta-row'><Text className='mini-chip'>{item.materialCount} 素材</Text><Text className='mini-chip chip-blue'>{item.quizCount} 闯关</Text></View>
            </View>
          ))}
        </View>
      </View>

      {loading && (
        <View className='loading-mask'><View className='loading-card'>
          <Image className='loading-jelly' src={jellyStudy} mode='aspectFit' />
          <Text className='loading-title'>{steps[loadingStep]}</Text><Text className='loading-desc'>水母正在整理成可闯关的知识结构</Text>
          <View className='loading-steps'>{steps.map((step, index) => <Text key={step} className={`step-dot ${index <= loadingStep ? 'step-active' : ''}`}>{index + 1}</Text>)}</View>
        </View></View>
      )}
    </View>
  )
}
