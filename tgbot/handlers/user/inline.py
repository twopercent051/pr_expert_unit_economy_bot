from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboard:

    def __init__(self):
        self.forecast = InlineKeyboardButton(text="Прогноз", callback_data="forecast")
        self.in_fact = InlineKeyboardButton(text="По факту", callback_data="in_fact")
        self.info = InlineKeyboardButton(text="Справка", callback_data="info")
        self.restart = InlineKeyboardButton(text="Начать сначала", callback_data="restart")
        self.feedback = InlineKeyboardButton(text="Написать нам", url="https://promoexpert.pro/")

    def main_menu_kb(self):
        keyboard = [
            [
                self.forecast,
                self.in_fact
            ],
            [self.info]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def finish_text_kb(self):
        keyboard = [
            [
                self.restart,
                self.info
            ],
            [self.feedback]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def info_kb(self):
        keyboard = [
            [
                self.restart,
                self.feedback
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)