from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from sqlalchemy.exc import IntegrityError

from create_bot import bot
from tgbot.handlers.admin.filters import AdminFilter
from tgbot.handlers.admin.inline import AdminEditInline
from tgbot.misc.states import AdminFSM
from tgbot.models.sql_connector import TextsDAO

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = AdminEditInline()


@router.callback_query(F.data == "edit")
async def edit_block(callback: CallbackQuery):
    text = "Укажите объект редактирования"
    kb = inline.edit_menu_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "edition")
async def edit_block(callback: CallbackQuery, state: FSMContext):
    title = callback.data.split(":")[1]
    if title == "requests":
        text = "Укажите тип расчёта"
        kb = inline.edit_types_kb()
    else:
        text = await TextsDAO.get_one_or_none(title=title)
        if text:
            await callback.message.answer("👇 Сейчас текст такой\nВведите новый текст (форматирование будет сохранено")
            text = text["text"]
        else:
            text = "ТЕКСТ НЕ ЗАДАН\nВведите новый текст (форматирование будет сохранено"
        kb = inline.home_kb()
        await state.update_data(title=title)
        await state.set_state(AdminFSM.text)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "requests")
async def edit_block(callback: CallbackQuery):
    title = callback.data.split(":")[1]
    text = "Укажите шаг опроса"
    kb = inline.edit_step_kb(type_text=title)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "step")
async def edit_block(callback: CallbackQuery, state: FSMContext):
    type_text = callback.data.split(":")[2]
    step = callback.data.split(":")[1]
    title = f"requests:{type_text}:{step}"
    text = await TextsDAO.get_one_or_none(title=title)
    if text:
        await callback.message.answer("👇 Сейчас текст такой\nВведите новый текст (форматирование будет сохранено")
        text = text["text"]
    else:
        text = "ТЕКСТ НЕ ЗАДАН\nВведите новый текст (форматирование будет сохранено"
    kb = inline.home_kb()
    await state.update_data(title=title)
    await state.set_state(AdminFSM.text)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.text)
async def edit_block(message: Message, state: FSMContext):
    text = "Текст сообщения обновлен"
    kb = inline.home_kb()
    state_data = await state.get_data()
    title = state_data["title"]
    try:
        await TextsDAO.create(title=title, text=message.html_text)
    except IntegrityError:
        await TextsDAO.update(title=title, text=message.html_text)
    await message.answer(text, reply_markup=kb)
