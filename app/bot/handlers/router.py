from __future__ import annotations

from aiogram import Router

from app.bot.handlers.consultation import router as consultation_router
from app.bot.handlers.faq import router as faq_router
from app.bot.handlers.lead import router as lead_router
from app.bot.handlers.start import router as start_router


def get_main_router() -> Router:
    router = Router(name="main_router")

    # Важно:
    # сначала подключаем lead_router, чтобы кнопка "Оставить заявку"
    # и шаги FSM не перехватывались другими текстовыми обработчиками
    router.include_router(lead_router)

    # Потом остальные роутеры
    router.include_router(start_router)
    router.include_router(faq_router)
    router.include_router(consultation_router)

    return router