from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class AdminInlineKeyboard:

    def __init__(self):
        self.home_button = InlineKeyboardButton(text="🏡 Главное меню", callback_data="home")

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="📝 Редактура текстов", callback_data="edit")],
            [InlineKeyboardButton(text="🕺 Войти как клиент", callback_data="as_client")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class AdminEditInline(AdminInlineKeyboard):

    def home_kb(self):
        keyboard = [[self.home_button]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def edit_menu_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="Текст на старте", callback_data="edition:start")],
            [InlineKeyboardButton(text="Цепочка вопросов", callback_data="edition:requests")],
            [InlineKeyboardButton(text="Слишком маленькие значения", callback_data="edition:too_low")],
            [InlineKeyboardButton(text="Низкий ROIm", callback_data="edition:low_roim")],
            [InlineKeyboardButton(text="Нормальный ROIm", callback_data="edition:normal_roim")],
            [InlineKeyboardButton(text="Справка", callback_data="edition:info")],
            [InlineKeyboardButton(text="Ввели не число", callback_data="edition:not_number")],
            [self.home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def edit_types_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="Прогноз", callback_data="requests:forecast")],
            [InlineKeyboardButton(text="По факту", callback_data="requests:in_fact")],
            [self.home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def edit_step_kb(self, type_text: int):
        keyboard = [
            [InlineKeyboardButton(text="Бюджет", callback_data=f"step:budget:{type_text}")],
            [InlineKeyboardButton(text="Число показов", callback_data=f"step:impressions_counter:{type_text}")],
            [InlineKeyboardButton(text="CTR", callback_data=f"step:ctr:{type_text}")],
            [InlineKeyboardButton(text="Конверсия в заявку", callback_data=f"step:application_conversion:{type_text}")],
            [InlineKeyboardButton(text="Конверсия в продажу", callback_data=f"step:sell_conversion:{type_text}")],
            [InlineKeyboardButton(text="Средний чек", callback_data=f"step:aov:{type_text}")],
            [self.home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
