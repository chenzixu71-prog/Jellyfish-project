import json
import re

import httpx

from app import config
from app.schemas import Quiz
from app.services.mock_ai_service import generate_mock_quiz


QUIZ_SYSTEM_PROMPT = """你是一名专业的 AI 学习教练，请根据用户提供的学习内容生成一组用于小程序闯关答题的题目。

要求：
1. 输出必须是合法 JSON，不要输出任何 JSON 之外的内容。
2. 题目总数为 5 题。
3. 题型包含：3 道单选题、1 道多选题、1 道判断题。
4. 每道题必须包含：题目编号、题型、题干、选项、正确答案、详细讲解、知识点标签、难度。
5. 讲解必须适合初学者阅读，避免过度学术化。
6. 如果用户输入内容过短，可以基于常识进行合理补充，但不要偏离主题。

用户学习内容如下：
{user_input}
"""


class DeepSeekClient:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.http_client = http_client or httpx.Client(timeout=30)

    def generate_quiz(self, content: str) -> Quiz:
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required when AI_PROVIDER=deepseek")

        response = self.http_client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": QUIZ_SYSTEM_PROMPT.format(user_input=content),
                    }
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        payload = response.json()
        raw_content = payload["choices"][0]["message"]["content"]
        quiz_payload = parse_json_object(raw_content)
        return Quiz.model_validate(quiz_payload)


def parse_json_object(raw_content: str) -> dict:
    cleaned = raw_content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()
    return json.loads(cleaned)


def generate_quiz(content: str) -> Quiz:
    if config.AI_PROVIDER != "deepseek":
        return generate_mock_quiz(content)

    client = DeepSeekClient(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
        model=config.AI_MODEL,
    )
    return client.generate_quiz(content)
