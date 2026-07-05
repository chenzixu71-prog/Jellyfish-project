from app.schemas import AnswerResult, Quiz


class MemoryStore:
    def __init__(self) -> None:
        self.quizzes: dict[str, Quiz] = {}
        self.answers: dict[tuple[str, str], list[AnswerResult]] = {}

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


store = MemoryStore()
