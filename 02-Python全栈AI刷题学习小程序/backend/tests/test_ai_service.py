import httpx

from app.services.ai_service import DeepSeekClient, build_quiz_prompt, parse_json_object
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
