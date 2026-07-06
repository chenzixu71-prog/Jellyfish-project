from datetime import date

from fastapi import HTTPException

from app.schemas import (
    AnswerResult,
    ChallengeHistoryItem,
    DailyChallenge,
    LearningProfile,
    Quiz,
    Report,
    ReportHistoryItem,
    WrongQuestion,
)
from app.services.ai_service import generate_quiz
from app.storage.memory_store import store


def create_quiz(session_id: str, content: str) -> Quiz:
    if not content.strip():
        raise HTTPException(status_code=422, detail="content is required")

    quiz = generate_quiz(content)
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
    store.record_answer_stat(session_id, result.isCorrect)
    if result.isCorrect:
        store.remove_wrong_question(session_id, quiz_id, question.id)
    else:
        store.save_wrong_question(
            session_id,
            WrongQuestion(
                quizId=quiz_id,
                questionId=question.id,
                stem=question.stem,
                selectedAnswer=answer,
                correctAnswer=question.answer,
                explanation=question.explanation,
                knowledge_point=question.knowledge_point,
            ),
        )
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

    report = Report(
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
    store.save_report(session_id, report)
    return report


def get_wrong_questions(session_id: str) -> list[WrongQuestion]:
    return store.get_wrong_questions(session_id)


def get_report_history(session_id: str) -> list[ReportHistoryItem]:
    return [
        ReportHistoryItem(
            quizId=report.quizId,
            title=report.title,
            score=report.score,
            total=report.total,
            mastery=report.mastery,
            weakPoints=report.weakPoints,
        )
        for report in store.get_reports(session_id)
    ]


def get_challenge_history(session_id: str) -> list[ChallengeHistoryItem]:
    return [
        ChallengeHistoryItem(
            quizId=report.quizId,
            title=report.title,
            score=report.score,
            total=report.total,
            mastery=report.mastery,
            completedAt=store.get_report_time(session_id, report.quizId),
        )
        for report in store.get_reports(session_id)
    ]


def get_daily_challenge(session_id: str) -> DailyChallenge:
    today = date.today().isoformat()
    reports = store.get_reports(session_id)
    today_quiz_ids = {report.quizId for report in reports}
    answered = sum(
        len(store.get_answers(session_id, quiz_id)) for quiz_id in today_quiz_ids
    )
    correct = sum(
        sum(1 for answer in store.get_answers(session_id, quiz_id) if answer.isCorrect)
        for quiz_id in today_quiz_ids
    )
    target = 5
    capped_answered = min(answered, target)
    return DailyChallenge(
        date=today,
        target=target,
        answered=capped_answered,
        correct=correct,
        completed=answered >= target,
        progress=round(capped_answered / target * 100),
    )


def get_learning_profile(session_id: str) -> LearningProfile:
    return store.get_profile(session_id)


def regenerate_weak_quiz(session_id: str, quiz_id: str) -> Quiz:
    quiz = store.get_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="quiz not found")

    wrong_questions = [
        item for item in store.get_wrong_questions(session_id) if item.quizId == quiz_id
    ]
    weak_points = [item.knowledge_point for item in wrong_questions]
    if not weak_points:
        weak_points = [
            answer.knowledge_point
            for answer in store.get_answers(session_id, quiz_id)
        ]
    weak_text = "、".join(dict.fromkeys(weak_points)) or quiz.title
    content = (
        f"请围绕这些薄弱点重新生成一组复习题：{weak_text}。"
        "题目要适合初学者，并重点检查用户是否真的理解。"
    )
    next_quiz = generate_quiz(content)
    store.save_quiz(session_id, next_quiz)
    return next_quiz
