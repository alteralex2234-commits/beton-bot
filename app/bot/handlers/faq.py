from aiogram import F, Router
from aiogram.types import Message

from app.core.container import ServiceContainer


router = Router()


@router.message(F.text == "Частые вопросы")
async def faq_list_handler(message: Message, services: ServiceContainer) -> None:
    await message.answer(services.consultation_service.list_faq_text())
