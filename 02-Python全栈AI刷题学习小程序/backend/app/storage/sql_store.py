import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import AUTH_TOKEN_TTL_DAYS
from app.schemas import (
    AnswerResult,
    CurrentUserProfile,
    KnowledgeBase,
    LearningProfile,
    LoginUser,
    MergedGuestData,
    Quiz,
    Report,
    WrongQuestion,
)


try:
    from sqlalchemy import DateTime, JSON, String, create_engine, select
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
except ImportError as exc:  # pragma: no cover - only hit when mysql mode is enabled
    raise RuntimeError(
        "STORAGE_BACKEND=mysql requires SQLAlchemy and PyMySQL. "
        "Install backend requirements before starting the service."
    ) from exc


GLOBAL_OWNER = "global"
LIST_ITEM = "list"
STATS_ITEM = "stats"
OPENID_OWNER = "openid"
TOKEN_OWNER = "token"


class Base(DeclarativeBase):
    pass


class StoreRecord(Base):
    __tablename__ = "jelly_store_records"

    namespace: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(191), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(191), primary_key=True)
    payload: Mapped[Any] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SqlStore:
    """MySQL-backed store with the same public methods as MemoryStore.

    The first persistence iteration stores business aggregates as JSON records.
    This keeps the current product flow stable while moving data out of process
    memory. High-frequency queries can be normalized into relational tables in a
    later migration.
    """

    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise RuntimeError("DATABASE_URL is required when STORAGE_BACKEND=mysql.")
        self.engine = create_engine(database_url, pool_pre_ping=True, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            future=True,
        )
        Base.metadata.create_all(self.engine)

    def _now(self) -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def _upsert(self, namespace: str, owner_id: str, item_id: str, payload: Any) -> None:
        now = self._now()
        with self.SessionLocal() as db:
            row = db.get(StoreRecord, (namespace, owner_id, item_id))
            if row:
                row.payload = payload
                row.updated_at = now
            else:
                row = StoreRecord(
                    namespace=namespace,
                    owner_id=owner_id,
                    item_id=item_id,
                    payload=payload,
                    created_at=now,
                    updated_at=now,
                )
                db.add(row)
            db.commit()

    def _get(self, namespace: str, owner_id: str, item_id: str) -> Any | None:
        with self.SessionLocal() as db:
            row = db.get(StoreRecord, (namespace, owner_id, item_id))
            return row.payload if row else None

    def _list(self, namespace: str, owner_id: str) -> list[Any]:
        with self.SessionLocal() as db:
            rows = db.execute(
                select(StoreRecord)
                .where(
                    StoreRecord.namespace == namespace,
                    StoreRecord.owner_id == owner_id,
                )
                .order_by(StoreRecord.updated_at.desc())
            ).scalars()
            return [row.payload for row in rows]

    def _delete(self, namespace: str, owner_id: str, item_id: str) -> None:
        with self.SessionLocal() as db:
            row = db.get(StoreRecord, (namespace, owner_id, item_id))
            if row:
                db.delete(row)
                db.commit()

    def get_or_create_wechat_user(self, openid: str) -> LoginUser:
        item_id = self._hash(openid)
        existing = self._get("wechat_user", OPENID_OWNER, item_id)
        if existing:
            return LoginUser.model_validate(existing)

        user = LoginUser(
            id=f"user-{hashlib.sha256(openid.encode('utf-8')).hexdigest()[:16]}",
            displayName="水母学员",
            avatarUrl="",
            loginType="wechat",
        )
        self._upsert("wechat_user", OPENID_OWNER, item_id, user.model_dump(mode="json"))
        return user

    def create_auth_token(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        token_hash = self._hash(token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=AUTH_TOKEN_TTL_DAYS)
        self._upsert(
            "auth_session",
            TOKEN_OWNER,
            token_hash,
            {"user_id": user_id, "expires_at": expires_at.isoformat()},
        )
        return token

    def get_user_by_id(self, user_id: str) -> LoginUser | None:
        users = self._list("wechat_user", OPENID_OWNER)
        for payload in users:
            user = LoginUser.model_validate(payload)
            if user.id == user_id:
                return user
        return None

    def get_user_by_token(self, token: str) -> LoginUser | None:
        token_hash = self._hash(token)
        session = self._get("auth_session", TOKEN_OWNER, token_hash)
        if not session:
            return None
        expires_at_value = session.get("expires_at")
        if not isinstance(expires_at_value, str):
            return None
        expires_at = datetime.fromisoformat(expires_at_value)
        if expires_at <= datetime.now(timezone.utc):
            self._delete("auth_session", TOKEN_OWNER, token_hash)
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
            nextLevelExp=profile.level * 100,
            streakDays=profile.streakDays,
            totalAnswered=profile.totalAnswered,
            totalCorrect=profile.totalCorrect,
            totalSessions=len(reports),
            accuracy=accuracy,
            badges=profile.badges,
        )

    def merge_guest_session_into_user(self, session_id: str, user_id: str) -> MergedGuestData:
        if not session_id or session_id == user_id:
            return MergedGuestData()

        merge_key = self._get("merged_guest", user_id, session_id)
        if merge_key:
            return MergedGuestData()

        copied_answers = 0
        for quiz_payload in self._list("quiz", GLOBAL_OWNER):
            quiz = Quiz.model_validate(quiz_payload)
            guest_answers = self.get_answers(session_id, quiz.quizId)
            if not guest_answers:
                continue
            target_answers = self.get_answers(user_id, quiz.quizId)
            existing_question_ids = {item.questionId for item in target_answers}
            for answer in guest_answers:
                if answer.questionId not in existing_question_ids:
                    target_answers.append(answer)
                    existing_question_ids.add(answer.questionId)
                    copied_answers += 1
            self._save_answers(user_id, quiz.quizId, target_answers)

        copied_wrong_questions = 0
        user_wrong_questions = self.get_wrong_questions(user_id)
        existing_wrong_keys = {
            (item.quizId, item.questionId) for item in user_wrong_questions
        }
        for item in self.get_wrong_questions(session_id):
            key = (item.quizId, item.questionId)
            if key not in existing_wrong_keys:
                user_wrong_questions.append(item)
                existing_wrong_keys.add(key)
                copied_wrong_questions += 1
        self._save_wrong_questions(user_id, user_wrong_questions[:50])

        copied_reports = 0
        user_reports = self.get_reports(user_id)
        existing_report_ids = {item.quizId for item in user_reports}
        for report in self.get_reports(session_id):
            if report.quizId not in existing_report_ids:
                user_reports.append(report)
                guest_time = self.get_report_time(session_id, report.quizId)
                if guest_time and not self.get_report_time(user_id, report.quizId):
                    self._save_report_time(user_id, report.quizId, guest_time)
                existing_report_ids.add(report.quizId)
                copied_reports += 1
        self._save_reports(user_id, user_reports[:10])

        copied_knowledge_bases = 0
        user_knowledge_bases = self.get_knowledge_bases(user_id)
        existing_kb_ids = {item.id for item in user_knowledge_bases}
        for knowledge_base in self.get_knowledge_bases(session_id):
            if knowledge_base.id not in existing_kb_ids and len(user_knowledge_bases) < 5:
                self.save_knowledge_base(user_id, knowledge_base)
                user_knowledge_bases.append(knowledge_base)
                existing_kb_ids.add(knowledge_base.id)
                copied_knowledge_bases += 1

        copied_profile_stats = False
        guest_stats = self._get("profile_stats", session_id, STATS_ITEM)
        if guest_stats:
            user_stats = self._profile_stats(user_id)
            user_stats["exp"] = int(user_stats["exp"]) + int(guest_stats.get("exp", 0))
            user_stats["streak_days"] = max(
                int(user_stats["streak_days"]),
                int(guest_stats.get("streak_days", 1)),
            )
            user_stats["total_answered"] = int(user_stats["total_answered"]) + int(
                guest_stats.get("total_answered", 0)
            )
            user_stats["total_correct"] = int(user_stats["total_correct"]) + int(
                guest_stats.get("total_correct", 0)
            )
            self._save_profile_stats(user_id, user_stats)
            copied_profile_stats = True

        self._upsert("merged_guest", user_id, session_id, {"merged": True})
        return MergedGuestData(
            answers=copied_answers,
            wrongQuestions=copied_wrong_questions,
            reports=copied_reports,
            profileStats=copied_profile_stats,
            knowledgeBases=copied_knowledge_bases,
        )

    def save_knowledge_base(self, owner_id: str, knowledge_base: KnowledgeBase) -> None:
        self._upsert(
            "knowledge_base",
            owner_id,
            knowledge_base.id,
            knowledge_base.model_dump(mode="json"),
        )
        items = self.get_knowledge_bases(owner_id)
        for extra in items[5:]:
            self._delete("knowledge_base", owner_id, extra.id)

    def count_knowledge_bases(self, owner_id: str) -> int:
        return len(self.get_knowledge_bases(owner_id))

    def get_knowledge_bases(self, owner_id: str) -> list[KnowledgeBase]:
        return [
            KnowledgeBase.model_validate(payload)
            for payload in self._list("knowledge_base", owner_id)
        ]

    def get_knowledge_base(self, owner_id: str, knowledge_base_id: str) -> KnowledgeBase | None:
        payload = self._get("knowledge_base", owner_id, knowledge_base_id)
        return KnowledgeBase.model_validate(payload) if payload else None

    def save_quiz(self, session_id: str, quiz: Quiz) -> None:
        self._upsert("quiz", GLOBAL_OWNER, quiz.quizId, quiz.model_dump(mode="json"))
        self._save_answers(session_id, quiz.quizId, [])

    def get_quiz(self, quiz_id: str) -> Quiz | None:
        payload = self._get("quiz", GLOBAL_OWNER, quiz_id)
        return Quiz.model_validate(payload) if payload else None

    def save_answer(self, session_id: str, quiz_id: str, result: AnswerResult) -> None:
        existing = [
            item for item in self.get_answers(session_id, quiz_id) if item.questionId != result.questionId
        ]
        existing.append(result)
        self._save_answers(session_id, quiz_id, existing)

    def get_answers(self, session_id: str, quiz_id: str) -> list[AnswerResult]:
        payload = self._get("answers", session_id, quiz_id) or []
        return [AnswerResult.model_validate(item) for item in payload]

    def save_wrong_question(self, session_id: str, wrong_question: WrongQuestion) -> None:
        existing = [
            item
            for item in self.get_wrong_questions(session_id)
            if not (
                item.quizId == wrong_question.quizId
                and item.questionId == wrong_question.questionId
            )
        ]
        existing.insert(0, wrong_question)
        self._save_wrong_questions(session_id, existing[:50])

    def remove_wrong_question(self, session_id: str, quiz_id: str, question_id: str) -> None:
        self._save_wrong_questions(
            session_id,
            [
                item
                for item in self.get_wrong_questions(session_id)
                if not (item.quizId == quiz_id and item.questionId == question_id)
            ],
        )

    def get_wrong_questions(self, session_id: str) -> list[WrongQuestion]:
        payload = self._get("wrong_questions", session_id, LIST_ITEM) or []
        return [WrongQuestion.model_validate(item) for item in payload]

    def save_report(self, session_id: str, report: Report) -> None:
        completed_at = datetime.now(timezone.utc).isoformat()
        report.completedAt = completed_at
        existing = [
            item for item in self.get_reports(session_id) if item.quizId != report.quizId
        ]
        existing.insert(0, report)
        self._save_reports(session_id, existing[:10])
        self._save_report_time(session_id, report.quizId, completed_at)

    def get_reports(self, session_id: str) -> list[Report]:
        payload = self._get("reports", session_id, LIST_ITEM) or []
        return [Report.model_validate(item) for item in payload]

    def get_report(self, session_id: str, quiz_id: str) -> Report | None:
        return next(
            (item for item in self.get_reports(session_id) if item.quizId == quiz_id),
            None,
        )

    def get_report_time(self, session_id: str, quiz_id: str) -> str:
        payload = self._get("report_time", session_id, quiz_id) or {}
        return str(payload.get("completed_at", ""))

    def record_answer_stat(self, session_id: str, is_correct: bool) -> None:
        stats = self._profile_stats(session_id)
        stats["total_answered"] = int(stats["total_answered"]) + 1
        stats["total_correct"] = int(stats["total_correct"]) + (1 if is_correct else 0)
        stats["exp"] = int(stats["exp"]) + (12 if is_correct else 5)
        self._save_profile_stats(session_id, stats)

    def get_profile(self, session_id: str) -> LearningProfile:
        stats = self._profile_stats(session_id)
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

    def _save_answers(self, session_id: str, quiz_id: str, answers: list[AnswerResult]) -> None:
        self._upsert(
            "answers",
            session_id,
            quiz_id,
            [item.model_dump(mode="json") for item in answers],
        )

    def _save_wrong_questions(
        self, session_id: str, wrong_questions: list[WrongQuestion]
    ) -> None:
        self._upsert(
            "wrong_questions",
            session_id,
            LIST_ITEM,
            [item.model_dump(mode="json") for item in wrong_questions],
        )

    def _save_reports(self, session_id: str, reports: list[Report]) -> None:
        self._upsert(
            "reports",
            session_id,
            LIST_ITEM,
            [item.model_dump(mode="json") for item in reports],
        )

    def _save_report_time(self, session_id: str, quiz_id: str, completed_at: str) -> None:
        self._upsert("report_time", session_id, quiz_id, {"completed_at": completed_at})

    def _profile_stats(self, session_id: str) -> dict[str, int]:
        payload = self._get("profile_stats", session_id, STATS_ITEM)
        if payload:
            return {
                "exp": int(payload.get("exp", 0)),
                "streak_days": int(payload.get("streak_days", 1)),
                "total_answered": int(payload.get("total_answered", 0)),
                "total_correct": int(payload.get("total_correct", 0)),
            }
        stats = {
            "exp": 0,
            "streak_days": 1,
            "total_answered": 0,
            "total_correct": 0,
        }
        self._save_profile_stats(session_id, stats)
        return stats

    def _save_profile_stats(self, session_id: str, stats: dict[str, int]) -> None:
        self._upsert("profile_stats", session_id, STATS_ITEM, stats)

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
