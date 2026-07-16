import httpx
import pytest
from fastapi import HTTPException

from app.services.ai_service import (
    DeepSeekClient,
    build_quiz_prompt,
    normalize_quiz_payload,
    parse_json_object,
)
from app.services.mock_ai_service import generate_mock_quiz
from app.services.search_service import SourceContext, SourceDocument


def test_parse_json_object_accepts_plain_json():
    payload = parse_json_object('{"title":"Git","summary":"s","questions":[]}')

    assert payload["title"] == "Git"


def test_parse_json_object_accepts_fenced_json():
    payload = parse_json_object(
        """```json
{"title":"端口","summary":"s","questions":[]}
```"""
    )

    assert payload["title"] == "端口"


def test_deepseek_client_builds_chat_completion_request():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat/completions"
        assert request.headers["authorization"] == "Bearer test-key"
        body = request.read().decode("utf-8")
        assert "deepseek-v4-flash" in body
        assert "Git" in body
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": """
{
  "quizId": "quiz-git",
  "title": "Git",
  "summary": "Git 基础",
  "questions": [
    {
      "id": "q1",
      "type": "single",
      "stem": "什么是 commit？",
      "options": [
        {"key": "A", "text": "保存一次本地版本"},
        {"key": "B", "text": "删除仓库"},
        {"key": "C", "text": "打开网页"},
        {"key": "D", "text": "关闭电脑"}
      ],
      "answer": ["A"],
      "explanation": "commit 是一次本地版本记录。",
      "knowledge_point": "Git commit",
      "difficulty": "easy"
    },
    {
      "id": "q2",
      "type": "single",
      "stem": "什么是 push？",
      "options": [
        {"key": "A", "text": "推送到远端"},
        {"key": "B", "text": "创建文件"},
        {"key": "C", "text": "格式化磁盘"},
        {"key": "D", "text": "退出登录"}
      ],
      "answer": ["A"],
      "explanation": "push 会把本地提交推送到远端。",
      "knowledge_point": "Git push",
      "difficulty": "easy"
    },
    {
      "id": "q3",
      "type": "single",
      "stem": "什么是 pull？",
      "options": [
        {"key": "A", "text": "拉取远端更新"},
        {"key": "B", "text": "截图"},
        {"key": "C", "text": "改密码"},
        {"key": "D", "text": "关机"}
      ],
      "answer": ["A"],
      "explanation": "pull 会获取并合并远端更新。",
      "knowledge_point": "Git pull",
      "difficulty": "easy"
    },
    {
      "id": "q4",
      "type": "multiple",
      "stem": "哪些命令和远端协作有关？",
      "options": [
        {"key": "A", "text": "push"},
        {"key": "B", "text": "pull"},
        {"key": "C", "text": "fetch"},
        {"key": "D", "text": "status"}
      ],
      "answer": ["A", "B", "C"],
      "explanation": "push、pull、fetch 都和远端同步有关。",
      "knowledge_point": "远端协作",
      "difficulty": "medium"
    },
    {
      "id": "q5",
      "type": "judge",
      "stem": "commit 会直接上传到 GitHub。",
      "options": [
        {"key": "true", "text": "正确"},
        {"key": "false", "text": "错误"}
      ],
      "answer": ["false"],
      "explanation": "commit 只是本地版本记录，push 才上传。",
      "knowledge_point": "Git 工作流",
      "difficulty": "easy"
    }
  ]
}
"""
                        }
                    }
                ]
            },
        )

    client = DeepSeekClient(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    quiz = client.generate_quiz("Git")

    assert quiz.title == "Git"
    assert len(quiz.questions) == 5


def test_deepseek_client_generates_unpredictable_quiz_id_and_normalizes_truefalse():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": """
{
  "title": "Python",
  "summary": "Python basics",
  "questions": [
    {
      "id": "q1",
      "type": "truefalse",
      "stem": "Python uses indentation to define code blocks.",
      "options": [
        {"key": "true", "text": "True"},
        {"key": "false", "text": "False"}
      ],
      "answer": ["true"],
      "explanation": "Indentation is syntactically significant in Python.",
      "knowledge_point": "Python indentation",
      "difficulty": "easy"
    }
  ]
}
"""
                        }
                    }
                ]
            },
        )

    client = DeepSeekClient(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    first_quiz = client.generate_quiz("Python")
    second_quiz = client.generate_quiz("Python")

    assert first_quiz.quizId.startswith("quiz-")
    assert first_quiz.quizId != second_quiz.quizId
    assert first_quiz.questions[0].type == "judge"


@pytest.mark.parametrize("question_type", ["truefalse", "boolean", "true_false"])
def test_normalize_quiz_payload_maps_common_judge_aliases(question_type):
    payload = {
        "title": "Python",
        "summary": "Python basics",
        "questions": [{"type": question_type}],
    }

    normalized = normalize_quiz_payload(payload)

    assert normalized["questions"][0]["type"] == "judge"


def test_build_quiz_prompt_includes_reference_sources():
    prompt = build_quiz_prompt(
        "Harness Engineering",
        SourceContext(
            documents=[
                SourceDocument(
                    title="Harness docs",
                    url="https://developer.harness.io/docs",
                    content="Harness is a software delivery platform.",
                    source_type="search",
                )
            ]
        ),
    )

    assert "Harness Engineering" in prompt
    assert "Reference sources" in prompt
    assert "Harness is a software delivery platform." in prompt


def test_build_quiz_prompt_rejects_generic_learning_questions():
    prompt = build_quiz_prompt("Harness Engineering is a software delivery platform.")

    assert "Questions must test the actual domain knowledge" in prompt
    assert "Do not create generic stems" in prompt
    assert "Each question stem must contain a concrete term" in prompt
    assert "knowledge_point must be a specific domain point" in prompt


def test_build_quiz_prompt_reserves_quiz_id_and_limits_question_types():
    prompt = build_quiz_prompt("Python")

    assert "quizId is generated by the server" in prompt
    assert "single, multiple, judge, or short_answer" in prompt


def test_build_quiz_prompt_supports_twenty_question_batches():
    prompt = build_quiz_prompt("Redis persistence", question_count=20)

    assert "Generate exactly 20 questions" in prompt
    assert "10 single-choice questions" in prompt
    assert "4 multiple-choice questions" in prompt
    assert "3 true/false questions" in prompt
    assert "3 short-answer questions" in prompt


def test_mock_quiz_supports_twenty_unique_questions():
    quiz = generate_mock_quiz("Redis persistence", question_count=20)

    assert len(quiz.questions) == 20
    assert len({question.id for question in quiz.questions}) == 20
    assert [question.type for question in quiz.questions].count("single") == 10
    assert [question.type for question in quiz.questions].count("multiple") == 4
    assert [question.type for question in quiz.questions].count("judge") == 3
    assert [question.type for question in quiz.questions].count("short_answer") == 3


def test_deepseek_client_maps_payment_required_to_readable_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(402, json={"error": {"message": "Payment Required"}})

    client = DeepSeekClient(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(HTTPException) as exc_info:
        client.generate_quiz("Git")

    assert exc_info.value.status_code == 502
    assert "DeepSeek API" in exc_info.value.detail
    assert "余额不足" in exc_info.value.detail
