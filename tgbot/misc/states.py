from aiogram.fsm.state import State, StatesGroup


class UserFSM(StatesGroup):
    home = State()
    impressions_counter = State()
    ctr = State()
    application_conversion = State()
    sell_conversion = State()
    aov = State()
    result = State()
