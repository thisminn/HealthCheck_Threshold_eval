import json
from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, TEMPERATURE
from src.schemas import LLMOutput


class LLMClient:
    def __init__(self) -> None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is missing in .env")

        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
        self.model = OPENAI_MODEL

    def generate_structured_answer(self, system_prompt: str, user_question: str) -> LLMOutput:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
        )

        raw = completion.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Model output is not valid JSON.\nRaw output:\n{raw}") from e

        return LLMOutput(**parsed)