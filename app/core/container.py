from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.repositories.lead_repository import LeadRepository
from app.repositories.supabase_client import SupabaseClient
from app.services.ai_service import AIService
from app.services.consultation_service import ConsultationService
from app.services.lead_service import LeadService
from app.services.notification_service import NotificationService


@dataclass
class ServiceContainer:
    settings: Settings
    consultation_service: ConsultationService
    lead_service: LeadService
    notification_service: NotificationService
    ai_service: AIService


def build_service_container(settings: Settings) -> ServiceContainer:
    supabase_client = SupabaseClient(
        base_url=settings.supabase_url,
        api_key=settings.supabase_key,
    )

    lead_repository = LeadRepository(supabase_client)
    consultation_service = ConsultationService()
    lead_service = LeadService(lead_repository)
    notification_service = NotificationService(settings)
    ai_service = AIService(settings)

    return ServiceContainer(
        settings=settings,
        consultation_service=consultation_service,
        lead_service=lead_service,
        notification_service=notification_service,
        ai_service=ai_service,
    )