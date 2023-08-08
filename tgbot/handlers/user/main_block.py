from typing import Literal

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from create_bot import bot
from tgbot.handlers.user.inline import InlineKeyboard
from tgbot.misc.states import UserFSM
from tgbot.models.sql_connector import UsersDAO, TextsDAO

router = Router()
inline = InlineKeyboard()


async def text_render(title: str) -> str:
    text = await TextsDAO.get_one_or_none(title=title)
    text = text["text"] if text else "ТЕКСТ НЕ ЗАДАН"
    return text


async def start_render(user_id: str | int, username: str):
    try:
        username = f"@{username}" if username else "---"
        await UsersDAO.create(user_id=str(user_id), username=username)
    except IntegrityError:
        pass
    text = await text_render(title="start")
    kb = inline.main_menu_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render(user_id=message.from_user.id, username=message.from_user.username)
    await state.set_state(UserFSM.home)


@router.callback_query(F.data == "restart")
@router.callback_query(F.data == "as_client")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render(user_id=callback.from_user.id, username=callback.from_user.username)
    await state.set_state(UserFSM.home)
    await bot.answer_callback_query(callback.id)


async def total_render_text(data: dict, type_text: Literal["forecast", "in_fact"]):
    try:
        budget = int(data["budget"])
        impressions_counter = int(data["impressions_counter"])
        cpm = round(budget / (impressions_counter / 1000), 2)
        ctr = int(data["ctr"])
        clicks = int(impressions_counter * ctr / 100)
        cpc = round(budget / clicks, 2)
        application_conversion = int(data["application_conversion"])
        application_counter = int(clicks * application_conversion / 100)
        cpa = round(budget / application_counter, 2)
        sell_conversion = int(data["sell_conversion"])
        sell_counter = int(clicks * sell_conversion / 1000)
        cps = round(budget / sell_counter, 2)
        aov = int(data["aov"])
        sales_revenue = int(sell_counter * aov)
        sae = round(budget * 100 / sales_revenue, 2)
        roim = int((sales_revenue - budget) * 100 / budget)
        text_dict = dict(forecast="Примерный", in_fact="Фактический")
    except (ZeroDivisionError, Exception):
        text = await text_render(title="too_low")
        return text
    text = [
        f"{text_dict[type_text]} бюджет <b>{'{0:,}'.format(budget).replace(',', ' ')} ₽</b>",
        f"Число показов объявлений в кампании <b>{'{0:,}'.format(impressions_counter).replace(',', ' ')}</b>\n",
        f"Стоимость тысячи показов, CPM <b>{'{0:,}'.format(cpm).replace(',', ' ')} ₽</b>",
        f"Показатель кликабельности, CTR <b>{'{0:,}'.format(ctr).replace(',', ' ')} %</b>",
        f"Клики (Посещаемость) <b>{'{0:,}'.format(clicks).replace(',', ' ')}</b>",
        f"Стоимость клика, CPC <b>{'{0:,}'.format(cpc).replace(',', ' ')} ₽\n</b>",
        f"Конверсия в заявку <b>{'{0:,}'.format(application_conversion).replace(',', ' ')} %</b>",
        f"Число заявок <b>{'{0:,}'.format(application_counter).replace(',', ' ')}</b>",
        f"Стоимость заявки, CPA <b>{'{0:,}'.format(cpa).replace(',', ' ')} ₽</b>",
        f"Конверсия в продажу <b>{'{0:,}'.format(sell_conversion).replace(',', ' ')} %</b>",
        f"Число продаж <b>{'{0:,}'.format(sell_counter).replace(',', ' ')}</b>",
        f"Стоимость продажи, CPS <b>{'{0:,}'.format(cps).replace(',', ' ')} ₽\n</b>",
        f"Средний чек с продажи, AOV <b>{'{0:,}'.format(aov).replace(',', ' ')} ₽</b>",
        f"Выручка с продаж <b>{'{0:,}'.format(sales_revenue).replace(',', ' ')} ₽\n</b>",
        f"Доля рекламных расходов, ДРР <b>{'{0:,}'.format(sae).replace(',', ' ')} %</b>",
        f"Возврат маркетинговых инвестиций, ROIм <b>{'{0:,}'.format(roim).replace(',', ' ')} %</b>\n",
    ]
    if roim <= 100:
        added_text = await text_render(title="low_roim")
    else:
        added_text = await text_render(title="normal_roim")
    text.append(added_text)
    return "\n".join(text)


@router.callback_query(F.data == "forecast")
@router.callback_query(F.data == "in_fact")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = await text_render(title=f"requests:{callback.data}:budget")
    await state.set_state(UserFSM.impressions_counter)
    await state.update_data(type_text=callback.data, result_data={})
    await callback.message.answer(text)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.impressions_counter)
@router.message(F.text, UserFSM.ctr)
@router.message(F.text, UserFSM.application_conversion)
@router.message(F.text, UserFSM.sell_conversion)
@router.message(F.text, UserFSM.aov)
async def main_block(message: Message, state: FSMContext):
    if not message.text.isdigit():
        text = await text_render(title="not_number")
        await message.answer(text)
        return
    current_state = await state.get_state()
    state_data = await state.get_data()
    current_state = current_state.split(":")[1]
    type_text = state_data["type_text"]
    result_data = state_data["result_data"]
    if current_state == "impressions_counter":
        await state.set_state(UserFSM.ctr)
        result_data["budget"] = float(message.text.replace(",", "."))
    if current_state == "ctr":
        await state.set_state(UserFSM.application_conversion)
        result_data["impressions_counter"] = float(message.text.replace(",", "."))
    if current_state == "application_conversion":
        await state.set_state(UserFSM.sell_conversion)
        result_data["ctr"] = float(message.text.replace(",", "."))
    if current_state == "sell_conversion":
        await state.set_state(UserFSM.aov)
        result_data["application_conversion"] = float(message.text.replace(",", "."))
    if current_state == "aov":
        await state.set_state(UserFSM.result)
        result_data["sell_conversion"] = float(message.text.replace(",", "."))
    text = await text_render(title=f"requests:{type_text}:{current_state}")
    await message.answer(text)


@router.message(F.text, UserFSM.result)
async def main_block(message: Message, state: FSMContext):
    if not message.text.isdigit():
        text = await text_render(title="not_number")
        await message.answer(text)
        return
    state_data = await state.get_data()
    type_text = state_data["type_text"]
    result_data = state_data["result_data"]
    result_data["aov"] = float(message.text.replace(",", "."))
    text = total_render_text(data=result_data, type_text=type_text)
    kb = inline.finish_text_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "info")
async def main_block(callback: CallbackQuery):
    text = await text_render(title="info")
    kb = inline.info_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)
