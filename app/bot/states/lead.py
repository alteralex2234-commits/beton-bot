from aiogram.fsm.state import State, StatesGroup


class LeadForm(StatesGroup):
    name = State()
    phone = State()
    volume = State()
    desired_product = State()
    comment = State()
