from __future__ import annotations

from openai import OpenAI


class LLMAdvisor:
    def __init__(self, api_key: str | None):
        self.client = OpenAI(api_key=api_key) if api_key else None

    def suggest(self, prompt: str) -> str:
        if not self.client:
            return "OPENAI_API_KEY가 없어 로컬 기본 추천만 제공합니다: 정확도 우선은 접근 B, 빠른 스케치는 접근 A를 선택하세요."

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": "You are a music transcription workflow assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text
