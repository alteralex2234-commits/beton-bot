from __future__ import annotations

import asyncio
import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states.lead import LeadForm
from app.core.container import ServiceContainer
from app.models.lead import LeadCreate
from app.utils.validators import is_valid_phone

router = Router(name="lead_router")
logger = logging.getLogger(__name__)


@router.message(F.text.casefold() == "оставить заявку")
async def lead_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LeadForm.name)
    await message.answer("Как вас зовут?")


@router.message(LeadForm.name, F.text)
async def lead_name_handler(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()

    if not name:
        await message.answer("Пожалуйста, укажите имя.")
        return

    await state.update_data(name=name)
    await state.set_state(LeadForm.phone)
    await message.answer("Укажите номер телефона для связи:")


@router.message(LeadForm.phone, F.text)
async def lead_phone_handler(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()

    if not is_valid_phone(phone):
        await message.answer("Пожалуйста, укажите корректный номер телефона.")
        return

    await state.update_data(phone=phone)
    await state.set_state(LeadForm.volume)
    await message.answer("Какой объем вас интересует? Например: 3 куба")


@router.message(LeadForm.volume, F.text)
async def lead_volume_handler(message: Message, state: FSMContext) -> None:
    volume = (message.text or "").strip()

    if not volume:
        await message.answer("Пожалуйста, укажите объем.")
        return

    await state.update_data(volume=volume)
    await state.set_state(LeadForm.desired_product)
    await message.answer("Какой продукт или марка вас интересует?")


@router.message(LeadForm.desired_product, F.text)
async def lead_product_handler(message: Message, state: FSMContext) -> None:
    product = (message.text or "").strip()

    if not product:
        await message.answer("Пожалуйста, укажите марку или продукт.")
        return

    await state.update_data(desired_product=product)
    await state.set_state(LeadForm.comment)
    await message.answer("Комментарий к заявке? Если не нужен, напишите: пропустить")


@router.message(LeadForm.comment, F.text)
async def lead_comment_handler(
    message: Message,
    state: FSMContext,
    services: ServiceContainer,
) -> None:
    data = await state.get_data()

    raw_comment = (message.text or "").strip()
    comment = None if raw_comment.casefold() == "пропустить" else raw_comment

    lead = LeadCreate(
        name=data.get("name", ""),
        phone=data.get("phone", ""),
        volume=data.get("volume", ""),
        desired_product=data.get("desired_product", ""),
        comment=comment,
        source="telegram",
    )

    logger.info("Final lead payload before save: %s", lead.model_dump())

    try:
        saved_lead = await asyncio.wait_for(
            services.lead_service.create_lead(lead),
            timeout=15,
        )
        logger.info("Lead saved successfully: %s", saved_lead)
    except asyncio.TimeoutError:
        logger.exception("Timeout while saving lead to database")
        await state.clear()
        await message.answer(
            "Заявка не сохранилась вовремя. Пожалуйста, попробуйте ещё раз через минуту."
        )
        return
    except Exception as e:
        logger.exception("Failed to save lead")
        await state.clear()
        await message.answer(
            f"Не удалось сохранить заявку в базу. Ошибка: {str(e)}"
        )
        return

    await state.clear()

    # Сначала подтверждаем клиенту, чтобы он не ждал молча
    await message.answer(
        "Спасибо! Заявка принята.\n"
        "Менеджер свяжется с вами в рабочее время."
    )

    # Потом отдельно пытаемся уведомить менеджера
    try:
        await asyncio.wait_for(
            services.notification_service.notify_new_lead(message.bot, lead),
            timeout=10,
        )
        logger.info("Manager notification sent successfully")
    except asyncio.TimeoutError:
        logger.exception("Timeout while sending manager notification")
    except Exception:
        logger.exception("Failed to notify manager")


@router.message(StateFilter(LeadForm))
async def lead_fallback_handler(message: Message) -> None:
    await message.answer("Пожалуйста, ответьте текстом на текущий вопрос.")