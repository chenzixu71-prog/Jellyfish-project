import secrets
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic import model_validator


QuestionType = Literal["single", "multiple", "judge", "short_answer"]
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
    sourceChunkIds: list[str] = Field(default_factory=list)

    @field_validator("type", mode="before")
    @classmethod
    def normalize_question_type(cls, value):
        normalized = str(value).lower()
        if normalized in {"truefalse", "true_false", "true-false", "boolean"}:
            return "judge"
        return value


class SourceItem(BaseModel):
    title: str
    url: str = ""
    sourceType: str
    summary: str


class SourceMeta(BaseModel):
    enabled: bool = False
    sourceCount: int = 0
    toolCalls: list[str] = []
    warnings: list[str] = []
    sources: list[SourceItem] = []


class GenerateQuizRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    inputType: Literal["text"] = "text"
    content: str = Field(min_length=1)
    questionCount: int = Field(default=5, ge=5, le=5)
    webSearchEnabled: bool = False


class KnowledgeBaseCreateRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    title: str = ""
    content: str = Field(min_length=1)
    webSearchEnabled: bool = False


class KnowledgeBaseSupplementRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    content: str = Field(min_length=1)
    webSearchEnabled: bool = False


class KnowledgeBaseQuizRequest(BaseModel):
    sessionId: str = Field(min_length=1)


class WechatLoginRequest(BaseModel):
    code: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)


class LoginUser(BaseModel):
    id: str
    displayName: str
    avatarUrl: str = ""
    loginType: Literal["wechat"] = "wechat"


class MergedGuestData(BaseModel):
    answers: int = 0
    wrongQuestions: int = 0
    reports: int = 0
    profileStats: bool = False
    knowledgeBases: int = 0


class WechatLoginResponse(BaseModel):
    token: str
    user: LoginUser
    merged: MergedGuestData | None = None


class CurrentUserProfile(LoginUser):
    level: int
    exp: int
    nextLevelExp: int
    streakDays: int
    totalAnswered: int
    totalCorrect: int
    totalSessions: int
    accuracy: int
    badges: list["Badge"]


class Quiz(BaseModel):
    quizId: str
    title: str
    summary: str
    questions: list[Question]
    sourceMeta: SourceMeta | None = None
    knowledgeBaseId: str = ""


    @model_validator(mode="before")
    @classmethod
    def ensure_quiz_id(cls, value):
        normalized = dict(value)
        normalized.setdefault("quizId", f"quiz-{secrets.token_hex(8)}")
        return normalized

class KnowledgeBaseMaterial(BaseModel):
    id: str
    type: Literal["text", "file", "image", "search"]
    name: str
    summary: str
    contentHash: str = ""
    createdAt: str = ""


class KnowledgeBaseChunk(BaseModel):
    id: str
    text: str
    keywords: list[str] = []
    source: str = ""


class KnowledgeBaseSummary(BaseModel):
    id: str
    title: str
    summary: str
    materialCount: int
    sourceCount: int
    quizCount: int = 0
    questionCount: int = 0
    completedQuestionCount: int = 0
    maxQuestions: int = Field(default=200, ge=1, le=200)
    updatedAt: str = ""


class KnowledgeBase(BaseModel):
    id: str
    title: str
    summary: str
    content: str
    materials: list[KnowledgeBaseMaterial]
    chunks: list[KnowledgeBaseChunk] = []
    sourceMeta: SourceMeta | None = None
    quizIds: list[str] = []
    questions: list[Question] = Field(default_factory=list)
    completedQuestionIds: list[str] = Field(default_factory=list)
    maxQuestions: int = Field(default=200, ge=1, le=200)
    createdAt: str = ""
    updatedAt: str = ""


class SubmitAnswerRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    quizId: str = Field(min_length=1)
    questionId: str = Field(min_length=1)
    answer: list[str] = Field(min_length=1)
    selfAssessment: Literal["correct", "incorrect"] | None = None

    @field_validator("answer", mode="before")
    @classmethod
    def normalize_single_answer(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class AnswerResult(BaseModel):
    questionId: str
    isCorrect: bool
    correctAnswer: list[str]
    explanation: str
    knowledge_point: str
    evaluationMode: Literal["objective", "self_assessment"] = "objective"


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
    completedAt: str = ""
    sourceMeta: SourceMeta | None = None


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
    completedAt: str = ""


class ChallengeHistoryItem(BaseModel):
    quizId: str
    title: str
    score: int
    total: int
    mastery: int
    completedAt: str


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
