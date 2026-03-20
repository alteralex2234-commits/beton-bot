from __future__ import annotations

from dataclasses import dataclass

from app.services.consultation_service import ConsultationService


@dataclass
class InboundMessage:
    user_id: str
    text: str
    source: str


class InboundMessageService:
    """Unified entry point for Telegram/Meta/WhatsApp messages."""

    def __init__(self, consultation_service: ConsultationService) -> None:
        self._consultation_service = consultation_service

    async def process(self, message: InboundMessage) -> str:
        # TODO: Extend routing logic for channel-specific behavior and AI fallback.
        # Здесь пока нет FSM-контекста, поэтому отвечаем безопасным "вступлением".
        faq_answer = self._consultation_service.answer_faq_by_text(message.text)
        if faq_answer:
            return faq_answer

        if not self._consultation_service.should_start_consultation(message.text):
            return "Могу помочь подобрать бетон — напишите, для чего он нужен."

        # Запускаем диалог в реальном Telegram-боте через FSM.
        # Для интеграций без FSM — коротко просим задачу и объем.
        return (
            "Подскажите, для чего нужен бетон (фундамент/стяжка/дорожки/отмостка/частный дом/мелкие работы/раствор) "
            "и какой примерно объем в кубах."
        )
