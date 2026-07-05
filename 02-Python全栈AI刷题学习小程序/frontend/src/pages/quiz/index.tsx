import { useMemo, useState } from 'react'
import Taro, { useLoad } from '@tarojs/taro'
import { Button, Text, View } from '@tarojs/components'
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

export default function QuizPage() {
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selected, setSelected] = useState<string[]>([])
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [completed, setCompleted] = useState(false)

  useLoad(() => {
    const storedQuiz = Taro.getStorageSync<Quiz>('currentQuiz')
    if (!storedQuiz) {
      Taro.redirectTo({ url: '/pages/create/index' })
      return
    }
    setQuiz(storedQuiz)
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
  }

  function goReport() {
    if (!quiz) return
    Taro.navigateTo({ url: `/pages/report/index?quizId=${quiz.quizId}` })
  }

  if (!quiz || !question) {
    return (
      <View className='page quiz-page'>
        <Text className='muted'>正在读取题目...</Text>
      </View>
    )
  }

  if (completed) {
    return (
      <View className='page complete-page'>
        <View className='confetti-layer'>
          {Array.from({ length: 20 }).map((_, index) => (
            <View key={index} className={`confetti confetti-${index % 5}`} />
          ))}
        </View>
        <View className='card complete-card'>
          <View className='girl-illustration'>
            <View className='girl-face'>
              <View className='eye left-eye' />
              <View className='eye right-eye' />
              <View className='smile' />
            </View>
          </View>
          <Text className='complete-title'>恭喜通关！</Text>
          <Text className='complete-subtitle'>你的答题记录已经保存，可以生成一份学习复盘报告。</Text>
          <Button className='primary-button' onClick={goReport}>查看学习报告</Button>
        </View>
      </View>
    )
  }

  return (
    <View className='page quiz-page'>
      <View className='quiz-header'>
        <Text className='tag'>{progressText}</Text>
        <Text className='quiz-title'>{quiz.title}</Text>
      </View>

      <View className='card question-card'>
        <View className='question-meta'>
          <Text className='tag'>{question.type === 'multiple' ? '多选题' : question.type === 'judge' ? '判断题' : '单选题'}</Text>
          <Text className='muted'>{question.difficulty}</Text>
        </View>
        <Text className='question-stem'>{question.stem}</Text>

        <View className='option-list'>
          {question.options.map((option) => {
            const active = selected.includes(option.key)
            return (
              <View
                key={option.key}
                className={`option-item ${active ? 'option-active' : ''}`}
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
            <Text className='feedback-title'>{result.isCorrect ? '答对了' : '再想想'}</Text>
            <Text className='feedback-line'>你的答案：{answerText(question, selected)}</Text>
            <Text className='feedback-line'>正确答案：{answerText(question, result.correctAnswer)}</Text>
            <Text className='feedback-explanation'>{result.explanation}</Text>
            <Button className='secondary-button next-button' onClick={goNext}>
              {currentIndex >= quiz.questions.length - 1 ? '完成闯关' : '下一题'}
            </Button>
          </View>
        )}
      </View>
    </View>
  )
}
