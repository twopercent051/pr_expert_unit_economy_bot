from typing import Literal

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.handlers.user.inline import InlineKeyboard
from tgbot.misc.states import UserFSM

router = Router()
inline = InlineKeyboard()


async def start_render(user_id: str | int):
    text = "С помощью этого бота вы можете спрогнозировать рекламный бюджет или, имея фактические показатели, " \
           "увидеть экономический результат рекламных кампаний."
    kb = inline.main_menu_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render(user_id=message.from_user.id)
    await state.set_state(UserFSM.home)


@router.callback_query(F.data == "restart")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render(user_id=callback.from_user.id)
    await state.set_state(UserFSM.home)
    await bot.answer_callback_query(callback.id)


def text_render(type_text: Literal["forecast", "in_fact"], step: str) -> str:
    forecast = dict(budget="Введите <i>примерный</i> рекламный бюджет",
                    impressions_counter="Введите число показов объявлений в кампаниях",
                    ctr="Введите CTR (показатель кликабельности — отношение кликов к показам)",
                    application_conversion="Введите показатель конверсии в заявку (%, сколько посетителей сайта с "
                                           "рекламы оставили заявку). <i>Можно взять примерные данные с вашего сайта "
                                           "по другим источникам (SEO, соцсети и т.д.)</i>",
                    sell_conversion="Введите показатель конверсии в продажу (%, сколько посетителей оставили заявку, "
                                    "совершили продажу) <i>Можно взять примерные данные в вашем бизнесе, которые были "
                                    "без участия интернет-маркетинга</i>",
                    aov="Введите средний чек с продажи (₽)")

    in_fact = dict(budget="Введите <i>фактический</i> рекламный бюджет",
                   impressions_counter="Введите число показов объявлений в кампаниях",
                   ctr="Введите CTR (показатель кликабельности — отношение кликов к показам)",
                   application_conversion="Введите показатель конверсии в заявку (%, сколько посетителей сайта с "
                                          "рекламы оставили заявку)",
                   sell_conversion="Введите показатель конверсии в продажу (%, сколько посетителей оставили заявку, "
                                   "совершили продажу)",
                   aov="Введите средний чек с продажи (₽)")

    result = dict(forecast=forecast, in_fact=in_fact)
    return result[type_text][step]


def total_render_text(data: dict, type_text: Literal["forecast", "in_fact"]):
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
        return "Значения, которые вы ввели слишком малы. Пожалуйста, начните сначала"
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
        text.append("У вас низкий показатель возврата инвестиций. Напишите нам, расскажем, как его улучшить.")
    else:
        text.append("Если какой-то из показателей вызывает у вас затруднения — обратитесь к нам. Поможем разобраться "
                    "и дадим бесплатную консультацию по юнит-экономике интернет-рекламы.")
    return "\n".join(text)


@router.callback_query(F.data == "forecast")
@router.callback_query(F.data == "in_fact")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = text_render(type_text=callback.data, step="budget")
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
        await message.answer("⚠️ Введите пожалуйста число")
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
    text = text_render(type_text=type_text, step=current_state)
    await message.answer(text)


@router.message(F.text, UserFSM.result)
async def main_block(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Введите пожалуйста число")
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
    text = [
        "<b>Раздел справка:</b>\n",
        "<b>Ниже вы найдете определения показателей юнит-экономики и информацию, где их можно найти. Указывайте "
        "данные за одинаковый период. Например, за 1 календарный месяц.</b>",
        "<b>Если у вас есть подрядчик, маркетолог или специалист по рекламе, то данные вы можете запросить у "
        "них.</b>\n",
        "1. <b>Бюджет</b> — сумма денег, потраченная на рекламу. Вы можете указывать как общий бюджет по всем "
        "инструментам, так и вести расчет по конкретному инструменту. Например, рассчитать показатели с инструментов "
        "«Реклама на поиске», «Реклама в сетях», «Медийная реклама» или только по одному из них.",
        "Если ведете рекламу через подрядчика, нужно учитывать и цену работы исполнителей, и прямой бюджет рекламной "
        "площадки с НДС",
        "<b>Где взять:</b> уточнить у вашего специалиста или посмотреть в рекламном кабинете. Примерный бюджет "
        "можете рассчитать в "
        "<a href='https://direct.yandex.ru/registered/main.pl?cmd=advancedForecast'>прогнозаторе</a> Яндекса "
        "или взять планируемый. \n",
        "2. <b>Число показов объявлений в кампании</b> — число, показывающее, сколько раз ваше объявление было "
        "показано пользователям. Аналогично с «Бюджетом», можно брать показатель по всем инструментам или "
        "только по одному.",
        "<b>Где взять:</b> уточнить у вашего специалиста или посмотреть в рекламном кабинете. Если нужны примерные "
        "данные, можно взять в "
        "<a href='https://direct.yandex.ru/registered/main.pl?cmd=advancedForecast'>прогнозаторе</a> Яндекса.\n",
        "3. <b>CPM (Cost Per Mille)</b> — стоимость тысячи показов, т.е. показа объявления одной тысяче посетителей.\n",
        "4. <b>CTR (Click-Through Rate)</b> — процент-показатель кликабельности, т.е. отношение кликов по вашим "
        "объявлениям к их показам. По этому показателю можно оценивать привлекательность, «продающесть» рекламного "
        "объявления.",
        "<b>Где взять:</b> уточнить у вашего специалиста или посмотреть в кабинете рекламной системы. Если нужны "
        "примерные данные, можно взять в "
        "<a href='https://direct.yandex.ru/registered/main.pl?cmd=advancedForecast'>прогнозаторе</a> Яндекса.\n",
        "5. <b>Клики (Посещаемость)</b> — число, показывающее, сколько раз пользователи кликнули по вашему "
        "объявлению и перешли на сайт.\n",
        "6. <b>CPC (Cost Per Click)</b> — стоимость клика, т.е. рекламный бюджет делённый на количество кликов. "
        "Во сколько рублей вам обходится переход на сайт.\n",
        "7. <b>Конверсия в заявку</b> — процент переходов (писем, звонков) на сайт с рекламы, которые "
        "сконвертировались в заявку. То есть сколько людей, которые перешли по рекламе на сайт, оставили заявку. "
        "По этому показателю можно оценивать эффективность сайта или посадочной страницы.",
        "<b>Где взять:</b> уточнить у вашего специалиста или посмотреть в системе аналитики Яндекс Метрика или "
        "Google Analytics.\n",
        "8. <b>Число заявок</b> — общее количество заявок, которые вы получили благодаря рекламе.\n",
        "9. <b>CPA (Cost Per Action)</b> — стоимость заявки, т.е. сколько для вас стоит получение одной заявки "
        "(письма, звонка) с рекламы.\n",
        "10. <b>Конверсия в продажу</b> — процент, указывающий сколько оставленных заявок (или заполненных корзин) "
        "закончились продажей. По этому показателю можно оценивать эффективность отдела продаж.",
        "<b>Где взять:</b> уточнить у вашего специалиста, в отделе продаж или в CRM-системе компании.\n",
        "11. <b>Число продаж</b> — общее количество состоявшихся продаж с рекламы.\n",
        "12. <b>CPS (Cost Per Sale)</b> — стоимость продажи, во сколько рублей вам обходится одна продажа.\n",
        "13. <b>AOV (Average Order Value)</b> — средний чек с продажи, т.е. средняя стоимость товаров/услуг, "
        "которые вы продаете с использованием рекламы, на одного пользователя.",
        "<b>Где взять:</b> уточнить у вашего специалиста, в отделе продаж или в CRM-системе компании.\n",
        "14. <b>Выручка с продаж</b> — произведение среднего чека с продажи на число продаж с рекламы.\n",
        "15. <b>ДРР</b> — доля рекламных расходов, соотношение рекламного бюджета к полученной выручке с этой "
        "рекламы.\n",
        "16. <b>ROIм (Return Of Investments)</b> — возврат маркетинговых инвестиций, т.е. сколько процентов вложенных "
        "в рекламу денег вам вернулось."
    ]
    kb = inline.info_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)
