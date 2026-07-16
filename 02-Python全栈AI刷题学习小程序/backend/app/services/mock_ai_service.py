import hashlib

from app.schemas import Option, Question, Quiz


def generate_mock_quiz(content: str, question_count: int = 5) -> Quiz:
    topic = content.strip()
    safe_topic = topic[:40] if topic else "Custom topic"
    batch_seed = hashlib.sha256(topic.encode("utf-8")).hexdigest()[:6]
    single_count, multiple_count, judge_count = question_type_counts(question_count)
    question_types = (
        ["single"] * single_count
        + ["multiple"] * multiple_count
        + ["judge"] * judge_count
    )
    questions = [
        build_mock_question(index + 1, question_type, safe_topic, batch_seed)
        for index, question_type in enumerate(question_types)
    ]
    return Quiz(
        title=safe_topic,
        summary=f"A {question_count}-question development quiz about {safe_topic}.",
        questions=questions,
    )


def question_type_counts(question_count: int) -> tuple[int, int, int]:
    if not 1 <= question_count <= 200:
        raise ValueError("question_count must be between 1 and 200")
    if question_count == 1:
        return 1, 0, 0

    multiple_count = max(1, round(question_count * 0.2))
    judge_count = max(1, round(question_count * 0.2))
    single_count = question_count - multiple_count - judge_count
    return single_count, multiple_count, judge_count

def build_mock_question(
    index: int,
    question_type: str,
    topic: str,
    batch_seed: str,
) -> Question:
    if question_type == "judge":
        return Question(
            id=f"q{index}",
            type="judge",
            stem=f"Mock statement {batch_seed}-{index} about {topic} is marked as correct.",
            options=[
                Option(key="true", text="Correct"),
                Option(key="false", text="Incorrect"),
            ],
            answer=["true"],
            explanation=f"Development-mode explanation {index} for {topic}.",
            knowledge_point=f"{topic} point {index}",
            difficulty="easy",
        )

    answer = ["A", "B"] if question_type == "multiple" else ["A"]
    return Question(
        id=f"q{index}",
        type=question_type,
        stem=f"Development question {batch_seed}-{index}: which option describes {topic} point {index}?",
        options=[
            Option(key="A", text=f"Correct detail {index}A"),
            Option(key="B", text=f"Related detail {index}B"),
            Option(key="C", text=f"Misconception {index}C"),
            Option(key="D", text=f"Misconception {index}D"),
        ],
        answer=answer,
        explanation=f"Development-mode explanation {index} for {topic}.",
        knowledge_point=f"{topic} point {index}",
        difficulty="medium" if question_type == "multiple" else "easy",
    )
