from aiogram.fsm.state import State, StatesGroup


class ConsultationDialogue(StatesGroup):
    # Шаг 1: определяем задачу (что нужно и для чего).
    task = State()
    # Шаг 2: уточняем детали (объем, важность W12 и т.п.).
    details = State()
    # Шаг 3-5: выдаем рекомендацию и предлагаем оставить заявку.
    offer = State()

