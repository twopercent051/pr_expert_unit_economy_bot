from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot
from .filters import AdminFilter
from .inline import AdminInlineKeyboard
from ...misc.states import AdminFSM

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = AdminInlineKeyboard()


async def start_render(user_id: str | int):
    text = "Вы вошли как админ.\nГЛАВНОЕ МЕНЮ"
    kb = inline.main_menu_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render(user_id=message.from_user.id)
    await state.set_state(AdminFSM.home)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render(user_id=callback.from_user.id)
    await state.set_state(AdminFSM.home)
    await bot.answer_callback_query(callback.id)
