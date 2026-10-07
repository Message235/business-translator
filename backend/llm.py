import os

import openai

from prompts import Direction, Intensity, build_system_prompt, build_user_message

BASE_URL = "https://openrouter.ai/api/v1"
MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4.1-flash")
TIMEOUT_SECONDS = 30.0


class LLMError(Exception):
    """LLM-Anbieter lieferte einen Fehler oder keine brauchbare Antwort."""


class LLMTimeout(LLMError):
    """LLM-Anbieter hat nicht rechtzeitig geantwortet."""


_client: openai.OpenAI | None = None


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(
            base_url=BASE_URL,
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            timeout=TIMEOUT_SECONDS,
        )
    return _client


def translate(text: str, direction: Direction, intensity: Intensity) -> tuple[str, int | None]:
    try:
        response = _get_client().chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": build_system_prompt(direction, intensity)},
                {"role": "user", "content": build_user_message(text)},
            ],
        )
    except openai.APITimeoutError as exc:
        raise LLMTimeout("Der LLM-Anbieter hat nicht rechtzeitig geantwortet.") from exc
    except openai.OpenAIError as exc:
        raise LLMError("Der LLM-Anbieter ist nicht erreichbar oder hat einen Fehler gemeldet.") from exc

    choice = response.choices[0] if response.choices else None
    result = ((choice.message.content or "") if choice else "").strip()
    if not result:
        raise LLMError("Der LLM-Anbieter lieferte keine Übersetzung.")
    tokens = response.usage.total_tokens if response.usage else None
    return result, tokens
