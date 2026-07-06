import { useMemo, useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, ScrollView, Text, View } from '@tarojs/components'
import { AnswerResult, Question, Quiz, submitAnswer } from '../../services/quizService'
import './index.css'

function answerText(question: Question, answer: string[]) {
  return answer
    .map((key) => {
      const option = question.options.find((item) => item.key === key)
      return option ? `${option.key}. ${option.text}` : key
    })
    .join('、')
}

function typeText(question: Question) {
  if (question.type === 'multiple') return '多选题'
  if (question.type === 'judge') return '判断题'
  return '单选题'
}

export default function QuizPage() {
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selected, setSelected] = useState<string[]>([])
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [sheetOpen, setSheetOpen] = useState(false)

  useDidShow(() => {
    const storedQuiz = Taro.getStorageSync<Quiz>('currentQuiz')
    if (!storedQuiz) {
      Taro.switchTab({ url: '/pages/create/index' })
      return
    }
    if (quiz?.quizId !== storedQuiz.quizId) {
      setQuiz(storedQuiz)
      setCurrentIndex(0)
      setSelected([])
      setResult(null)
      setCompleted(false)
      setSheetOpen(false)
    } else if (!quiz) {
      setQuiz(storedQuiz)
    }
  })

  const question = quiz?.questions[currentIndex]
  const progressText = useMemo(() => {
    if (!quiz) return ''
    return `${currentIndex + 1}/${quiz.questions.length}`
  }, [currentIndex, quiz])

  function toggleOption(key: string) {
    if (!question || result) return
    if (question.type === 'multiple') {
      setSelected((previous) => (
        previous.includes(key)
          ? previous.filter((item) => item !== key)
          : [...previous, key].sort()
      ))
      return
    }
    setSelected([key])
  }

  async function handleSubmit() {
    if (!quiz || !question || selected.length === 0) {
      Taro.showToast({ title: '先选择答案', icon: 'none' })
      return
    }

    setSubmitting(true)
    try {
      const answerResult = await submitAnswer(quiz.quizId, question.id, selected)
      setResult(answerResult)
    } catch (error) {
      Taro.showToast({
        title: error instanceof Error ? error.message : '提交失败',
        icon: 'none'
      })
    } finally {
      setSubmitting(false)
    }
  }

  function goNext() {
    if (!quiz) return
    if (currentIndex >= quiz.questions.length - 1) {
      setCompleted(true)
      return
    }

    setCurrentIndex((index) => index + 1)
    setSelected([])
    setResult(null)
    setSheetOpen(false)
  }

  function goReport() {
    if (!quiz) return
    Taro.switchTab({ url: '/pages/report/index' })
  }

  if (!quiz || !question) {
    return (
      <View className='quiz-page'>
        <Text className='muted'>正在读取题目...</Text>
      </View>
    )
  }

  if (completed) {
    return (
      <View className='complete-page'>
        <View className='bubble-celebrate bubble-one' />
        <View className='bubble-celebrate bubble-two' />
        <View className='bubble-celebrate bubble-three' />
        <View className='complete-card'>
          <View className='complete-jellyfish'>
            <View className='complete-jelly-body'>
              <View className='complete-smile' />
            </View>
            <View className='complete-tentacle complete-tentacle-1' />
            <View className='complete-tentacle complete-tentacle-2' />
            <View className='complete-tentacle complete-tentacle-3' />
            <View className='complete-tentacle complete-tentacle-4' />
          </View>
          <Text className='complete-title'>恭喜通关！</Text>
          <Text className='complete-subtitle'>水母已经整理好答题结果，下一步生成完整学习报告。</Text>
          <Button className='primary-button' onClick={goReport}>查看学习报告</Button>
        </View>
      </View>
    )
  }

  return (
    <View className='quiz-page'>
      <View className='quiz-hero'>
        <Text className='stage-title'>Quiz Stage</Text>
        <View className='quiz-progress-row'>
          <Text className='pill'>{progressText}</Text>
          <Text className='pill'>{typeText(question)}</Text>
        </View>
        <Text className='quiz-title'>{quiz.title}</Text>
      </View>

      <View className='question-card'>
        <Text className='question-stem'>{question.stem}</Text>

        <View className='option-list'>
          {question.options.map((option) => {
            const active = selected.includes(option.key)
            const isCorrect = result?.correctAnswer.includes(option.key)
            const isWrong = result && active && !isCorrect
            return (
              <View
                key={option.key}
                className={`option-item ${active ? 'option-active' : ''} ${isCorrect ? 'option-correct' : ''} ${isWrong ? 'option-wrong' : ''}`}
                onClick={() => toggleOption(option.key)}
              >
                <Text className='option-key'>{option.key}</Text>
                <Text className='option-text'>{option.text}</Text>
              </View>
            )
          })}
        </View>

        {!result && (
          <Button className='primary-button submit-button' loading={submitting} onClick={handleSubmit}>
            提交答案
          </Button>
        )}

        {result && (
          <View className={`feedback ${result.isCorrect ? 'feedback-right' : 'feedback-wrong'}`}>
            <Text className='feedback-title'>{result.isCorrect ? '答对了，水母点头！' : '答错了，水母帮你补一补'}</Text>
            <Text className='feedback-line'>正确答案：{answerText(question, result.correctAnswer)}</Text>
            <Text className='feedback-explanation'>{result.explanation}</Text>
            <View className='feedback-actions'>
              <Button className='secondary-button action-button' onClick={() => setSheetOpen(true)}>展开知识详情</Button>
              <Button className='secondary-button action-button' onClick={goNext}>
                {currentIndex >= quiz.questions.length - 1 ? '完成闯关' : '下一题'}
              </Button>
            </View>
          </View>
        )}
      </View>

      {sheetOpen && result && (
        <View className='sheet-mask' onClick={() => setSheetOpen(false)}>
          <View className='knowledge-sheet' onClick={(event) => event.stopPropagation()}>
            <Text className='sheet-title'>{result.knowledge_point} 拆解</Text>
            <ScrollView className='sheet-scroll' scrollY>
              <View className={`knowledge-block ${result.isCorrect ? 'correct' : 'wrong'}`}>
                <Text className='knowledge-label'>{result.isCorrect ? '答对时看这里' : '答错时看这里'}</Text>
                <Text className='knowledge-copy'>{result.explanation}</Text>
              </View>
              <View className='knowledge-block'>
                <Text className='knowledge-label'>正确答案</Text>
                <Text className='knowledge-copy'>{answerText(question, result.correctAnswer)}</Text>
              </View>
              <View className='knowledge-block'>
                <Text className='knowledge-label'>知识点标签</Text>
                <Text className='knowledge-copy'>{result.knowledge_point}</Text>
              </View>
              <View className='knowledge-block'>
                <Text className='knowledge-label'>下一步练习</Text>
                <Text className='knowledge-copy'>用自己的话复述这道题为什么选这个答案，再进入下一题。</Text>
              </View>
            </ScrollView>
          </View>
        </View>
      )}
    </View>
  )
}
