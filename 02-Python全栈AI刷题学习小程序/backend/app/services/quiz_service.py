from fastapi import HTTPException

from app.schemas import AnswerResult, Quiz, Report
from app.services.mock_ai_service import generate_mock_quiz
from app.storage.memory_store import store


def create_quiz(session_id: str, content: str) -> Quiz:
    if not content.strip():
        raise HTTPException(status_code=422, detail="content is required")

    quiz = generate_mock_quiz(content)
    store.save_quiz(session_id, quiz)
    return quiz


def submit_answer(
    session_id: str,
    quiz_id: str,
    question_id: str,
    answer: list[str],
) -> AnswerResult:
    quiz = store.get_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="quiz not found")

    question = next((item for item in quiz.questions if item.id == question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="question not found")

    normalized_answer = sorted(answer)
    correct_answer = sorted(question.answer)
    result = AnswerResult(
        questionId=question.id,
        isCorrect=normalized_answer == correct_answer,
        correctAnswer=question.answer,
        explanation=question.explanation,
        knowledge_point=question.knowledge_point,
    )
    store.save_answer(session_id, quiz_id, result)
    return result


def generate_report(session_id: str, quiz_id: str) -> Report:
    quiz = store.get_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="quiz not found")

    answers = store.get_answers(session_id, quiz_id)
    score = sum(1 for answer in answers if answer.isCorrect)
    total = len(quiz.questions)
    mastery = round(score / total * 100) if total else 0
    weak_points = [
        answer.knowledge_point for answer in answers if not answer.isCorrect
    ] or ["暂无明显薄弱点"]

    return Report(
        quizId=quiz.quizId,
        title=quiz.title,
        score=score,
        total=total,
        mastery=mastery,
        summary=f"本轮围绕“{quiz.title}”完成 {total} 道题，答对 {score} 道。",
        weakPoints=weak_points,
        nextSteps=[
            "复习错题对应的知识点。",
            "用自己的话重新解释本轮主题。",
            "再生成一组题巩固薄弱点。",
        ],
    )
