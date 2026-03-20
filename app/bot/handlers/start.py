from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main_menu import main_menu_keyboard
from app.core.container import ServiceContainer


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    text = (
        "Здравствуйте! Я консультант компании 'Бетон Семей'.\n"
        "Помогу подобрать бетон или пескобетон под вашу задачу, "
        "а также передам контакт менеджеру."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(F.text == "Связаться с менеджером")
async def manager_contact_handler(message: Message, services: ServiceContainer) -> None:
    await message.answer(
        "Оставьте заявку через меню, и менеджер свяжется с вами.\n"
        f"График работы: {services.settings.business_hours}."
    )
