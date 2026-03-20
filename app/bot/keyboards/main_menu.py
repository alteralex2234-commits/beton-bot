from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Марки бетона"), KeyboardButton(text="Помощь в выборе")],
            [KeyboardButton(text="Оставить заявку"), KeyboardButton(text="Частые вопросы")],
            [KeyboardButton(text="Связаться с менеджером")],
        ],
        resize_keyboard=True,
    )
