from __future__ import annotations

import logging

from aiogram import Bot

from app.core.config import Settings
from app.models.lead import LeadCreate


logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, settings: Settings) -> None:
        self._manager_chat_id = settings.telegram_manager_chat_id

    async def notify_new_lead(self, bot: Bot, lead: LeadCreate) -> None:
        text = self._build_lead_message(lead)
        await bot.send_message(chat_id=self._manager_chat_id, text=text)
        logger.info("Manager notification sent to chat_id=%s", self._manager_chat_id)

    def _build_lead_message(self, lead: LeadCreate) -> str:
        comment = lead.comment if lead.comment else "—"

        return (
            "📥 Новая заявка\n\n"
            f"👤 Имя: {lead.name}\n"
            f"📞 Телефон: {lead.phone}\n"
            f"📦 Объем: {lead.volume}\n"
            f"🧱 Продукт: {lead.desired_product}\n"
            f"💬 Комментарий: {comment}\n"
            f"📍 Источник: {lead.source}"
        )