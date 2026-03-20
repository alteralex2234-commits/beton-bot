from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.models.lead import LeadCreate


class WebhookAck(BaseModel):
    status: str
    detail: str


def build_api_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/api/leads/test")
    async def create_test_lead(lead: LeadCreate, request: Request) -> dict:
        services = request.app.state.services
        stored = await services.lead_service.create_lead(lead)
        return {"status": "saved", "lead_id": stored.id}

    @router.post("/webhooks/meta", response_model=WebhookAck)
    async def meta_webhook_stub() -> WebhookAck:
        # TODO: Parse Instagram/Meta payload and map into unified inbound message model.
        return WebhookAck(status="accepted", detail="Meta webhook stub is ready for future integration")

    @router.post("/webhooks/whatsapp", response_model=WebhookAck)
    async def whatsapp_webhook_stub() -> WebhookAck:
        # TODO: Parse WhatsApp payload and map into unified inbound message model.
        return WebhookAck(status="accepted", detail="WhatsApp webhook stub is ready for future integration")

    return router
