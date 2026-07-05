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


class Report(BaseModel):
    quizId: str
    title: str
    score: int
    total: int
    mastery: int
    summary: str
    weakPoints: list[str]
    nextSteps: list[str]
