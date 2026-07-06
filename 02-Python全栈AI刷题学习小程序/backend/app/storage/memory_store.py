import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.config import AUTH_TOKEN_TTL_DAYS
from app.schemas import (
    AnswerResult,
    CurrentUserProfile,
    LearningProfile,
    LoginUser,
    Quiz,
    Report,
    WrongQuestion,
)


class MemoryStore:
    def __init__(self) -> None:
        self.quizzes: dict[str, Quiz] = {}
        self.answers: dict[tuple[str, str], list[AnswerResult]] = {}
        self.wrong_questions: dict[str, list[WrongQuestion]] = {}
        self.reports: dict[str, list[Report]] = {}
        self.profile_stats: dict[str, dict[str, object]] = {}
        self.wechat_users: dict[str, LoginUser] = {}
        self.auth_sessions: dict[str, dict[str, object]] = {}

    def get_or_create_wechat_user(self, openid: str) -> LoginUser:
        existing = self.wechat_users.get(openid)
        if existing:
            return existing

        user = LoginUser(
            id=f"user-{hashlib.sha256(openid.encode('utf-8')).hexdigest()[:16]}",
            displayName="水母学员",
            avatarUrl="",
            loginType="wechat",
        )
        self.wechat_users[openid] = user
        return user

    def create_auth_token(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.auth_sessions[token_hash] = {
            "user_id": user_id,
            "expires_at": datetime.now(timezone.utc)
            + timedelta(days=AUTH_TOKEN_TTL_DAYS),
        }
        return token

    def get_user_by_id(self, user_id: str) -> LoginUser | None:
        return next(
            (user for user in self.wechat_users.values() if user.id == user_id),
            None,
        )

    def get_user_by_token(self, token: str) -> LoginUser | None:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        session = self.auth_sessions.get(token_hash)
        if not session:
            return None
        expires_at = session.get("expires_at")
        if not isinstance(expires_at, datetime) or expires_at <= datetime.now(timezone.utc):
            return None
        user_id = session.get("user_id")
        if not isinstance(user_id, str):
            return None
        return self.get_user_by_id(user_id)

    def get_current_user_profile(self, user: LoginUser) -> CurrentUserProfile:
        profile = self.get_profile(user.id)
        reports = self.get_reports(user.id)
        accuracy = (
            round(profile.totalCorrect / profile.totalAnswered * 100)
            if profile.totalAnswered
            else 0
        )
        return CurrentUserProfile(
            id=user.id,
            displayName=user.displayName,
            avatarUrl=user.avatarUrl,
            loginType=user.loginType,
            level=profile.level,
            exp=profile.exp,
            streakDays=profile.streakDays,
            totalAnswered=profile.totalAnswered,
            totalCorrect=profile.totalCorrect,
            totalSessions=len(reports),
            accuracy=accuracy,
        )

    def save_quiz(self, session_id: str, quiz: Quiz) -> None:
        self.quizzes[quiz.quizId] = quiz
        self.answers[(session_id, quiz.quizId)] = []

    def get_quiz(self, quiz_id: str) -> Quiz | None:
        return self.quizzes.get(quiz_id)

    def save_answer(self, session_id: str, quiz_id: str, result: AnswerResult) -> None:
        self.answers.setdefault((session_id, quiz_id), [])
        existing = [
            item
            for item in self.answers[(session_id, quiz_id)]
            if item.questionId != result.questionId
        ]
        existing.append(result)
        self.answers[(session_id, quiz_id)] = existing

    def get_answers(self, session_id: str, quiz_id: str) -> list[AnswerResult]:
        return self.answers.get((session_id, quiz_id), [])

    def save_wrong_question(self, session_id: str, wrong_question: WrongQuestion) -> None:
        existing = [
            item
            for item in self.wrong_questions.get(session_id, [])
            if not (
                item.quizId == wrong_question.quizId
                and item.questionId == wrong_question.questionId
            )
        ]
        existing.insert(0, wrong_question)
        self.wrong_questions[session_id] = existing[:50]

    def remove_wrong_question(self, session_id: str, quiz_id: str, question_id: str) -> None:
        self.wrong_questions[session_id] = [
            item
            for item in self.wrong_questions.get(session_id, [])
            if not (item.quizId == quiz_id and item.questionId == question_id)
        ]

    def get_wrong_questions(self, session_id: str) -> list[WrongQuestion]:
        return self.wrong_questions.get(session_id, [])

    def save_report(self, session_id: str, report: Report) -> None:
        existing = [
            item for item in self.reports.get(session_id, []) if item.quizId != report.quizId
        ]
        existing.insert(0, report)
        self.reports[session_id] = existing[:10]

    def get_reports(self, session_id: str) -> list[Report]:
        return self.reports.get(session_id, [])

    def record_answer_stat(self, session_id: str, is_correct: bool) -> None:
        stats = self.profile_stats.setdefault(
            session_id,
            {
                "exp": 0,
                "streak_days": 1,
                "total_answered": 0,
                "total_correct": 0,
            },
        )
        stats["total_answered"] = int(stats["total_answered"]) + 1
        stats["total_correct"] = int(stats["total_correct"]) + (1 if is_correct else 0)
        stats["exp"] = int(stats["exp"]) + (12 if is_correct else 5)

    def get_profile(self, session_id: str) -> LearningProfile:
        stats = self.profile_stats.setdefault(
            session_id,
            {
                "exp": 0,
                "streak_days": 1,
                "total_answered": 0,
                "total_correct": 0,
            },
        )
        exp = int(stats["exp"])
        total_answered = int(stats["total_answered"])
        total_correct = int(stats["total_correct"])
        streak_days = int(stats["streak_days"])
        reports = self.get_reports(session_id)
        wrong_questions = self.get_wrong_questions(session_id)

        return LearningProfile(
            level=exp // 100 + 1,
            exp=exp,
            streakDays=streak_days,
            totalAnswered=total_answered,
            totalCorrect=total_correct,
            badges=[
                {
                    "id": "first-quiz",
                    "name": "首次闯关",
                    "description": "完成第一轮水母问答",
                    "unlocked": total_answered >= 5,
                },
                {
                    "id": "perfect-run",
                    "name": "满分水母",
                    "description": "任意一次报告达到 100% 掌握度",
                    "unlocked": any(report.mastery == 100 for report in reports),
                },
                {
                    "id": "mistake-cleaner",
                    "name": "错题清理员",
                    "description": "答题后暂无待复习错题",
                    "unlocked": total_answered > 0 and len(wrong_questions) == 0,
                },
            ],
        )


store = MemoryStore()
