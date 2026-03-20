from __future__ import annotations

import logging
from typing import Any

from app.models.lead import LeadCreate
from app.repositories.lead_repository import LeadRepository


logger = logging.getLogger(__name__)


class LeadService:
    def __init__(self, lead_repository: LeadRepository) -> None:
        self._lead_repository = lead_repository

    async def create_lead(self, lead: LeadCreate) -> dict[str, Any]:
        saved = await self._lead_repository.create_lead(lead)

        lead_id = None
        if isinstance(saved, dict):
            lead_id = saved.get("id")
        else:
            lead_id = getattr(saved, "id", None)

        logger.info("Lead created successfully. id=%s payload=%s", lead_id, saved)
        return saved