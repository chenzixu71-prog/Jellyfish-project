import json
import re

import httpx

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
