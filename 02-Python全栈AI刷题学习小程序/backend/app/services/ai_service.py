import json
import re

import httpx
from fastapi import HTTPException

from app import config
from app.schemas import Quiz
from app.services.mock_ai_service import generate_mock_quiz
from app.services.search_service import SourceContext, format_source_context


QUIZ_SYSTEM_PROMPT = """You are a professional AI learning coach.
Generate a mini-program quiz from the learner's content.

Output rules:
1. Output valid JSON only. Do not output any text outside JSON.
2. Generate exactly 5 questions.
3. Include 3 single-choice questions, 1 multiple-choice question, and 1 true/false question.
4. Every question must include: id, type, stem, options, answer, explanation, knowledge_point, difficulty.
5. Explanations must be beginner-friendly.
6. If reference sources are provided, prioritize them over your training data. Do not invent facts that conflict with the sources.
7. If sources are missing or weak, stay close to the user's topic and say only what can be reasonably inferred.
8. Questions must test the actual domain knowledge in the learner content, not generic learning methods.
9. Do not create generic stems like "What should you do first when learning X?", "Why review after answering?", or "What is useful for revision?".
10. Do not use generic options like "understand the core concept first", "memorize all details", "skip basics", or "guess randomly".
11. Each question stem must contain a concrete term, fact, concept, API, tool name, rule, process, or example from the learner content or reference sources.
12. Every wrong option must be a plausible domain-related misconception. Avoid options about UI, page color, study attitude, or app workflow unless the learner content is specifically about those topics.
13. knowledge_point must be a specific domain point, not labels such as "learning start", "instant feedback", "review", or "question structure".
14. If the content is too short, infer only the minimum needed from reliable sources/context and make the limitation clear in the summary.

JSON shape:
{{
  "title": "learning topic",
  "summary": "short topic summary",
  "questions": [
    {{
      "id": "q1",
      "type": "single",
      "stem": "question",
      "options": [
        {{"key": "A", "text": "option A"}},
        {{"key": "B", "text": "option B"}}
      ],
      "answer": ["A"],
      "explanation": "explanation",
      "knowledge_point": "knowledge point",
      "difficulty": "easy"
    }}
  ]
}}

Learner content:
{user_input}

Reference sources:
{source_context}
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

    def generate_quiz(
        self,
        content: str,
        source_context: SourceContext | None = None,
    ) -> Quiz:
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required when AI_PROVIDER=deepseek")

        try:
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
                            "content": build_quiz_prompt(content, source_context),
                        }
                    ],
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 402:
                raise HTTPException(
                    status_code=502,
                    detail="DeepSeek API 余额不足或账号未开通计费，请充值后重试。",
                ) from exc
            raise HTTPException(
                status_code=502,
                detail=f"DeepSeek API 调用失败：HTTP {exc.response.status_code}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail="DeepSeek API 网络请求失败，请稍后重试。",
            ) from exc
        payload = response.json()
        raw_content = payload["choices"][0]["message"]["content"]
        quiz_payload = parse_json_object(raw_content)
        return Quiz.model_validate(quiz_payload)


def build_quiz_prompt(
    content: str,
    source_context: SourceContext | None = None,
) -> str:
    formatted_context = format_source_context(source_context or SourceContext())
    if not formatted_context:
        formatted_context = "No external sources provided."
    return QUIZ_SYSTEM_PROMPT.format(
        user_input=content,
        source_context=formatted_context,
    )


def parse_json_object(raw_content: str) -> dict:
    cleaned = raw_content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()
    return json.loads(cleaned)


def generate_quiz(content: str, source_context: SourceContext | None = None) -> Quiz:
    if config.AI_PROVIDER != "deepseek":
        return generate_mock_quiz(content)

    client = DeepSeekClient(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
        model=config.AI_MODEL,
    )
    return client.generate_quiz(content, source_context)
