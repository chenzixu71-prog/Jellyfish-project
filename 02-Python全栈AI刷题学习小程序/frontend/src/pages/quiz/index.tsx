import { useMemo, useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { Button, Image, ScrollView, Text, Textarea, View } from '@tarojs/components'
import { AnswerResult, Question, Quiz, submitAnswer } from '../../services/quizService'
import { trackEvent } from '../../services/analyticsService'
import jellyCelebrate from '../../assets/jelly-gpt/jelly-celebrate.png'
import './index.css'

function answerText(question: Question, answer: string[]) {
  return answer.map((key) => {
    const option = question.options.find((item) => item.key === key)
    return option ? `${option.key}. ${option.text}` : key
  }).join('、')
}

function typeText(question: Question) {
  if (question.type === 'multiple') return '多选题'
  if (question.type === 'judge') return '判断题'
  if (question.type === 'short_answer') return '问答题'
  return '单选题'
}

function difficultyText(difficulty: Question['difficulty']) {
  if (difficulty === 'hard') return '进阶'
  if (difficulty === 'medium') return '适中'
  return '入门'
}

export default function QuizPage() {
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selected, setSelected] = useState<string[]>([])
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [correctCount, setCorrectCount] = useState(0)
  const [shortAnswer, setShortAnswer] = useState('')

  useDidShow(() => {
    const storedQuiz = Taro.getStorageSync<Quiz>('currentQuiz')
    if (!storedQuiz) return
    if (!quiz || quiz.quizId !== storedQuiz.quizId) {
      setQuiz(storedQuiz)
      setCurrentIndex(0)
      setSelected([])
      setResult(null)
      setCompleted(false)
      setSheetOpen(false)
      setCorrectCount(0)
      setShortAnswer('')
      trackEvent('quiz_start', {
        question_count: storedQuiz.questions.length,
        search_enabled: Boolean(storedQuiz.sourceMeta?.enabled)
      })
    }
  })

  const question = quiz?.questions[currentIndex]
  const progress = useMemo(() => {
    if (!quiz) return 0
    return Math.round(((currentIndex + 1) / quiz.questions.length) * 100)
  }, [currentIndex, quiz])

  function toggleOption(key: string) {
    if (!question || result) return
    if (question.type === 'multiple') {
      setSelected((previous) => previous.includes(key)
        ? previous.filter((item) => item !== key)
        : [...previous, key].sort())
      return
    }
    setSelected([key])
  }

  async function handleSubmit() {
    if (!quiz || !question) return
    const isShortAnswer = question.type === 'short_answer'
    const answer = isShortAnswer ? [shortAnswer.trim()] : selected
    if (!answer[0]) {
      Taro.showToast({ title: isShortAnswer ? '先写下你的回答' : '先选择答案', icon: 'none' })
      return
    }

    let selfAssessment: 'correct' | 'incorrect' | undefined
    if (isShortAnswer) {
      const assessment = await Taro.showModal({
        title: '自评这道题',
        content: '回想题目要求，你认为自己的回答是否掌握了关键点？选择后会显示参考答案。',
        confirmText: '我答对了',
        cancelText: '还没掌握'
      })
      selfAssessment = assessment.confirm ? 'correct' : 'incorrect'
    }

    setSubmitting(true)
    try {
      const answerResult = await submitAnswer(
        quiz.quizId,
        question.id,
        answer,
        selfAssessment
      )
      setResult(answerResult)
      if (answerResult.isCorrect) setCorrectCount((count) => count + 1)
      trackEvent('answer_submit', {
        question_index: currentIndex + 1,
        question_type: question.type,
        difficulty: question.difficulty,
        is_correct: answerResult.isCorrect
      })
    } catch (error) {
      Taro.showToast({ title: error instanceof Error ? error.message : '提交失败', icon: 'none' })
    } finally {
      setSubmitting(false)
    }
  }

  function goNext() {
    if (!quiz) return
    if (currentIndex >= quiz.questions.length - 1) {
      trackEvent('quiz_complete', {
        question_count: quiz.questions.length,
        correct_count: correctCount,
        search_enabled: Boolean(quiz.sourceMeta?.enabled)
      })
      setCompleted(true)
      return
    }
    setCurrentIndex((index) => index + 1)
    setSelected([])
    setResult(null)
    setSheetOpen(false)
    setShortAnswer('')
  }

  if (!quiz || !question) {
    return (
      <View className='quiz-page quiz-empty'>
        <Text className='empty-title'>还没有关卡</Text>
        <Text className='empty-copy'>先选择一个知识库，再开始闯关。</Text>
        <Button className='empty-button' onClick={() => Taro.switchTab({ url: '/pages/challenge/index' })}>选择知识库</Button>
      </View>
    )
  }

  if (completed) {
    return (
      <View className='complete-page'>
        <View className='complete-bubble complete-bubble-one' />
        <View className='complete-bubble complete-bubble-two' />
        <View className='complete-card'>
          <Image className='complete-jelly' src={jellyCelebrate} mode='aspectFit' />
          <Text className='complete-kicker'>QUEST COMPLETE</Text>
          <Text className='complete-title'>恭喜通关！</Text>
          <Text className='complete-desc'>{quiz.questions.length} 道题已经完成，水母正在帮你整理复盘报告。</Text>
          <Button className='complete-button' onClick={() => Taro.switchTab({ url: '/pages/report/index' })}>查看水母报告</Button>
        </View>
      </View>
    )
  }

  return (
    <View className={`quiz-page ${result ? 'has-feedback' : ''}`}>
      <View className='quiz-hero'>
        <Text className='quiz-kicker'>QUIZ STAGE</Text>
        <Text className='quiz-title'>{quiz.title}</Text>
        <View className='progress-top'>
          <View className='progress-bar'><View className='progress-inner' style={{ width: `${progress}%` }} /></View>
          <Text className='progress-text'>{currentIndex + 1}/{quiz.questions.length}</Text>
        </View>
      </View>

      <View className='question-card'>
        <View className='question-meta'>
          <Text className='type-pill'>{typeText(question)}</Text>
          <Text className='type-pill soft'>{difficultyText(question.difficulty)}</Text>
        </View>
        <Text className='question-stem'>{question.stem}</Text>
        {question.type === 'short_answer' ? (
          <View className='short-answer-wrap'>
            <Textarea
              className='short-answer-input'
              value={shortAnswer}
              maxlength={600}
              disabled={Boolean(result)}
              placeholder='用自己的话写下答案，不用和参考答案一字不差'
              onInput={(event) => setShortAnswer(event.detail.value)}
            />
            <Text className='short-answer-count'>{shortAnswer.length}/600</Text>
          </View>
        ) : (
          <View className='option-list'>
            {question.options.map((option) => {
            const active = selected.includes(option.key)
            const isCorrect = Boolean(result?.correctAnswer.includes(option.key))
            const isWrong = Boolean(result && active && !isCorrect)
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
        )}
        {!result && (
          <Button className={`submit-button ${(selected.length || shortAnswer.trim()) ? 'ready' : ''}`} disabled={submitting} onClick={handleSubmit}>{question.type === 'short_answer' ? '完成回答' : '提交答案'}</Button>
        )}
      </View>

      {result && (
        <View className={`feedback-bar ${result.isCorrect ? 'right' : 'wrong'}`}>
          <View className='feedback-copy-wrap'>
            <Text className='feedback-title'>{result.evaluationMode === 'self_assessment' ? (result.isCorrect ? '已记录：我掌握了' : '已加入重点复习') : (result.isCorrect ? '答对了，漂亮！' : '差一点，马上弄懂')}</Text>
            <Text className='feedback-copy'>{question.type === 'short_answer' ? '参考答案' : '正确答案'}：{answerText(question, result.correctAnswer)}</Text>
          </View>
          <View className='feedback-actions'>
            <Button className='feedback-secondary' onClick={() => setSheetOpen(true)}>展开讲解</Button>
            <Button className='feedback-primary' onClick={goNext}>{currentIndex >= quiz.questions.length - 1 ? '完成闯关' : '下一题'}</Button>
          </View>
        </View>
      )}

      {sheetOpen && result && (
        <View className='sheet-mask' onClick={() => setSheetOpen(false)}>
          <View className='knowledge-sheet' onClick={(event) => event.stopPropagation()}>
            <View className='sheet-handle' />
            <Text className='sheet-eyebrow'>KNOWLEDGE NOTE</Text>
            <Text className='sheet-title'>{result.knowledge_point}</Text>
            <ScrollView className='sheet-scroll' scrollY>
              <View className='sheet-block'>
                <Text className='sheet-label'>为什么这样选</Text>
                <Text className='sheet-copy'>{result.explanation}</Text>
              </View>
              <View className='sheet-block'>
                <Text className='sheet-label'>{question.type === 'short_answer' ? '参考答案' : '正确答案'}</Text>
                <Text className='sheet-copy'>{answerText(question, result.correctAnswer)}</Text>
              </View>
              <View className='sheet-block'>
                <Text className='sheet-label'>记忆动作</Text>
                <Text className='sheet-copy'>用自己的话复述一次原因，再进入下一题。主动回忆会比只看答案记得更牢。</Text>
              </View>
            </ScrollView>
          </View>
        </View>
      )}
    </View>
  )
}
