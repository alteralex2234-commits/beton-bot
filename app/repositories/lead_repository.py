from __future__ import annotations

import logging

from app.models.lead import LeadCreate
from app.repositories.supabase_client import SupabaseClient


logger = logging.getLogger(__name__)


class LeadRepository:
    def __init__(self, supabase_client: SupabaseClient) -> None:
        self._supabase_client = supabase_client

    async def create_lead(self, lead: LeadCreate) -> dict:
        payload = lead.model_dump(mode="json", exclude_none=True)

        try:
            result = await self._supabase_client.insert("leads", payload)
            if result:
                return result[0]
            return payload
        except Exception:
            logger.exception("Failed to create lead in Supabase")
            raise