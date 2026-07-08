from app.schemas import (
    AnswerResult,
    KnowledgeBase,
    KnowledgeBaseMaterial,
    Option,
    Question,
    Quiz,
    Report,
    WrongQuestion,
)
from app.storage.sql_store import SqlStore


def make_store(tmp_path):
    return SqlStore(f"sqlite:///{tmp_path / 'jelly_store.db'}")


def make_quiz() -> Quiz:
    return Quiz(
        quizId="quiz-sql-1",
        title="SQL Store Quiz",
        summary="Validate persisted quiz data.",
        questions=[
            Question(
                id="q1",
                type="single",
                stem="Which storage mode writes data to a database?",
                options=[
                    Option(key="A", text="memory"),
                    Option(key="B", text="mysql"),
                ],
                answer=["B"],
                explanation="MySQL mode writes aggregates into SQL records.",
                knowledge_point="storage backend",
                difficulty="easy",
            )
        ],
    )


def test_sql_store_persists_core_learning_data(tmp_path):
    store = make_store(tmp_path)
    user = store.get_or_create_wechat_user("openid-sql")
    token = store.create_auth_token(user.id)

    quiz = make_quiz()
    store.save_quiz(user.id, quiz)
    store.save_answer(
        user.id,
        quiz.quizId,
        AnswerResult(
            questionId="q1",
            isCorrect=True,
            correctAnswer=["B"],
            explanation="MySQL mode is persistent.",
            knowledge_point="storage backend",
        ),
    )
    store.record_answer_stat(user.id, True)
    store.save_wrong_question(
        user.id,
        WrongQuestion(
            quizId=quiz.quizId,
            questionId="q2",
            stem="Wrong question",
            selectedAnswer=["A"],
            correctAnswer=["B"],
            explanation="Explanation",
            knowledge_point="storage backend",
        ),
    )
    store.save_report(
        user.id,
        Report(
            quizId=quiz.quizId,
            title=quiz.title,
            score=1,
            total=1,
            mastery=100,
            summary="Good progress.",
            weakPoints=[],
            nextSteps=["Keep reviewing."],
        ),
    )
    store.save_knowledge_base(
        user.id,
        KnowledgeBase(
            id="kb-sql-1",
            title="SQL Knowledge Base",
            summary="Persist knowledge base data.",
            content="SQLAlchemy persists this content.",
            materials=[
                KnowledgeBaseMaterial(
                    id="mat-1",
                    type="text",
                    name="note",
                    summary="note summary",
                    contentHash="hash-1",
                    createdAt="2026-01-01T00:00:00+00:00",
                )
            ],
            chunks=[],
            quizIds=[quiz.quizId],
            createdAt="2026-01-01T00:00:00+00:00",
            updatedAt="2026-01-01T00:00:00+00:00",
        ),
    )

    reloaded = make_store(tmp_path)

    assert reloaded.get_user_by_token(token).id == user.id
    assert reloaded.get_quiz(quiz.quizId).title == quiz.title
    assert reloaded.get_answers(user.id, quiz.quizId)[0].isCorrect is True
    assert reloaded.get_wrong_questions(user.id)[0].questionId == "q2"
    assert reloaded.get_reports(user.id)[0].mastery == 100
    assert reloaded.get_profile(user.id).totalAnswered == 1
    assert reloaded.get_knowledge_base(user.id, "kb-sql-1").title == "SQL Knowledge Base"
