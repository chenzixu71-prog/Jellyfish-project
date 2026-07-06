from typing import Literal

from pydantic import BaseModel, Field


QuestionType = Literal["single", "multiple", "judge"]
Difficulty = Literal["easy", "medium", "hard"]


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: object | None = None


class Option(BaseModel):
    key: str
    text: str


class Question(BaseModel):
    id: str
    type: QuestionType
    stem: str
    options: list[Option]
    answer: list[str]
    explanation: str
    knowledge_point: str
    difficulty: Difficulty


class GenerateQuizRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    inputType: Literal["text"] = "text"
    content: str = Field(min_length=1)
    questionCount: int = Field(default=5, ge=5, le=5)


class WechatLoginRequest(BaseModel):
    code: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)


class LoginUser(BaseModel):
    id: str
    displayName: str
    avatarUrl: str = ""
    loginType: Literal["wechat"] = "wechat"


class WechatLoginResponse(BaseModel):
    token: str
    user: LoginUser


class Quiz(BaseModel):
    quizId: str
    title: str
    summary: str
    questions: list[Question]


class SubmitAnswerRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    quizId: str = Field(min_length=1)
    questionId: str = Field(min_length=1)
    answer: list[str] = Field(min_length=1)


class AnswerResult(BaseModel):
    questionId: str
    isCorrect: bool
    correctAnswer: list[str]
    explanation: str
    knowledge_point: str


class GenerateReportRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    quizId: str = Field(min_length=1)


class RegenerateWeakQuizRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    quizId: str = Field(min_length=1)


class Report(BaseModel):
    quizId: str
    title: str
    score: int
    total: int
    mastery: int
    summary: str
    weakPoints: list[str]
    nextSteps: list[str]


class WrongQuestion(BaseModel):
    quizId: str
    questionId: str
    stem: str
    selectedAnswer: list[str]
    correctAnswer: list[str]
    explanation: str
    knowledge_point: str
    reviewed: bool = False


class ReportHistoryItem(BaseModel):
    quizId: str
    title: str
    score: int
    total: int
    mastery: int
    weakPoints: list[str]


class DailyChallenge(BaseModel):
    date: str
    target: int
    answered: int
    correct: int
    completed: bool
    progress: int


class Badge(BaseModel):
    id: str
    name: str
    description: str
    unlocked: bool


class LearningProfile(BaseModel):
    level: int
    exp: int
    streakDays: int
    totalAnswered: int
    totalCorrect: int
    badges: list[Badge]
