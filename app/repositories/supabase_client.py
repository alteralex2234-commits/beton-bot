from __future__ import annotations

import logging
from typing import Any

import httpx


logger = logging.getLogger(__name__)


class SupabaseClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/").strip().strip('"').strip("'")
        self._api_key = api_key.strip().strip('"').strip("'")

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self._api_key,
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "return=representation",
        }

    async def insert(self, table: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        url = f"{self._base_url}/rest/v1/{table}"

        logger.info("Supabase request url: %s", url)
        logger.info("Supabase key prefix: %s", self._api_key[:20])
        logger.info("Supabase key length: %s", len(self._api_key))

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                url,
                headers=self._headers,
                json=payload,
            )

        logger.info("Supabase response status: %s", response.status_code)
        logger.info("Supabase response text: %s", response.text)

        if response.is_error:
            logger.error(
                "Supabase insert failed: %s - %s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

        data = response.json()
        if not isinstance(data, list):
            logger.warning("Unexpected Supabase response format: %r", data)
            return []

        return data