from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.core.config import Settings


logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, settings: Settings) -> None:
        self._enabled = settings.ai_enabled
        self._api_key = settings.openrouter_api_key.strip()
        self._base_url = settings.openrouter_base_url.rstrip("/")
        self._model = settings.openrouter_model.strip()
        self._system_prompt = settings.ai_system_prompt.strip()

    async def generate_answer(self, user_message: str, context: str) -> Optional[str]:
        if not self._enabled:
            logger.info("AI disabled, fallback used")
            return None

        if not self._api_key or not self._base_url or not self._model:
            logger.warning("AI config is incomplete, fallback used")
            return None

        url = f"{self._base_url}/chat/completions"

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": self._system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Контекст:\n{context}\n\nВопрос клиента:\n{user_message}",
                },
            ],
            "temperature": 0.4,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, headers=headers, json=payload)

            if response.is_error:
                logger.error("AI request failed: %s - %s", response.status_code, response.text)
                return None

            data = response.json()
            answer = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content")
            )

            if not answer:
                logger.warning("AI returned empty answer, fallback used")
                return None

            logger.info("AI used successfully")
            return answer.strip()

        except Exception:
            logger.exception("AI request crashed, fallback used")
            return None