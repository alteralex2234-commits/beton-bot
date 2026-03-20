from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states.consultation import ConsultationDialogue
from app.bot.states.lead import LeadForm
from app.core.container import ServiceContainer


router = Router()


def build_ai_context(services: ServiceContainer) -> str:
    settings = services.settings

    delivery_text = "есть" if settings.has_delivery else "нет"
    pickup_text = "есть" if settings.has_pickup else "нет"
    pump_text = "есть" if settings.has_pump else "нет"

    return f"""
Компания: {settings.company_name}
Город: {settings.city}
Время работы: {settings.business_hours}
Доставка: {delivery_text}
Самовывоз: {pickup_text}
Насос: {pump_text}
Минимальный заказ: {settings.min_order_m3} куб

Ассортимент:
{services.consultation_service.list_products_text()}

Подсказки по подбору:
- стяжка: обычно рассматривают М150 или М200
- дорожки: обычно рассматривают М150 или М200
- фундамент частного дома: часто выбирают М250 или М300
- более ответственные конструкции: обычно смотрят М300 или М350
- повышенная водонепроницаемость: варианты W12
- мелкие работы: пескобетон
- если клиенту нужен точный подбор, лучше предложить оставить заявку
""".strip()


@router.message(StateFilter(None), F.text == "Марки бетона")
async def products_handler(
    message: Message,
    services: ServiceContainer,
    state: FSMContext,
) -> None:
    await message.answer(services.consultation_service.list_products_text())


@router.message(StateFilter(None), F.text == "Помощь в выборе")
async def help_choose_handler(
    message: Message,
    services: ServiceContainer,
    state: FSMContext,
) -> None:
    await state.clear()
    await state.set_state(ConsultationDialogue.task)
    await message.answer(
        "Отлично, давайте подберем вариант.\n"
        "Подскажите, для чего нужен бетон:\n"
        "фундамент / стяжка / дорожки / отмостка / частный дом / мелкие работы / раствор."
    )


@router.message(ConsultationDialogue.task, F.text)
async def consultation_task_handler(
    message: Message,
    services: ServiceContainer,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пожалуйста, напишите, для чего нужен бетон.")
        return

    fsm_data = await state.get_data()
    result = await services.consultation_service.task_step(text, fsm_data)

    if result.updates:
        await state.update_data(**result.updates)

    if result.next_state == "details":
        await state.set_state(ConsultationDialogue.details)
    elif result.next_state == "task":
        await state.set_state(ConsultationDialogue.task)
    elif result.next_state == "offer":
        await state.set_state(ConsultationDialogue.offer)

    context = build_ai_context(services)
    ai_answer = await services.ai_service.generate_answer(text, context)

    if ai_answer:
        await message.answer(ai_answer)
    else:
        await message.answer(result.response_text)


@router.message(ConsultationDialogue.details, F.text)
async def consultation_details_handler(
    message: Message,
    services: ServiceContainer,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пожалуйста, напишите ответ текстом.")
        return

    fsm_data = await state.get_data()
    result = await services.consultation_service.details_step(text, fsm_data)

    if result.updates:
        await state.update_data(**result.updates)

    if result.next_state == "offer":
        await state.set_state(ConsultationDialogue.offer)
    else:
        await state.set_state(ConsultationDialogue.details)

    context = build_ai_context(services)
    ai_answer = await services.ai_service.generate_answer(text, context)

    if ai_answer:
        await message.answer(ai_answer)
    else:
        await message.answer(result.response_text)


@router.message(ConsultationDialogue.offer, F.text)
async def consultation_offer_handler(
    message: Message,
    services: ServiceContainer,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пожалуйста, ответьте текстом.")
        return

    fsm_data = await state.get_data()
    result = await services.consultation_service.offer_step(text, fsm_data)

    wants_lead = bool(result.updates.get("wants_lead")) if result.updates else False
    if wants_lead:
        await state.clear()
        await state.set_state(LeadForm.name)
        await message.answer("Как вас зовут?")
        return

    if result.updates:
        await state.update_data(**result.updates)

    context = build_ai_context(services)
    ai_answer = await services.ai_service.generate_answer(text, context)

    if ai_answer:
        await message.answer(ai_answer)
    else:
        await message.answer(result.response_text)


@router.message(StateFilter(None), F.text)
async def free_text_consultation_entry(
    message: Message,
    services: ServiceContainer,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()
    if not text:
        return

    ignored = {
        "Марки бетона",
        "Помощь в выборе",
        "Оставить заявку",
        "Частые вопросы",
        "Связаться с менеджером",
    }
    if text in ignored:
        return

    faq_answer = services.consultation_service.answer_faq_by_text(text)
    if faq_answer:
        await message.answer(faq_answer)
        return

    if not services.consultation_service.should_start_consultation(text):
        context = build_ai_context(services)
        ai_answer = await services.ai_service.generate_answer(text, context)

        if ai_answer:
            await message.answer(ai_answer)
        else:
            await message.answer("Могу помочь подобрать бетон. Напишите, для чего он нужен.")
        return

    await state.set_state(ConsultationDialogue.task)

    fsm_data = await state.get_data()
    result = await services.consultation_service.task_step(text, fsm_data)

    if result.updates:
        await state.update_data(**result.updates)

    if result.next_state == "details":
        await state.set_state(ConsultationDialogue.details)
    elif result.next_state == "offer":
        await state.set_state(ConsultationDialogue.offer)
    else:
        await state.set_state(ConsultationDialogue.task)

    context = build_ai_context(services)
    ai_answer = await services.ai_service.generate_answer(text, context)

    if ai_answer:
        await message.answer(ai_answer)
    else:
        await message.answer(result.response_text)