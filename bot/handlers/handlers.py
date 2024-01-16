import logging

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from keyboards.kb import menu_kb, exit_kb, iexit_kb

logging.basicConfig(level=logging.INFO)

router = Router()

command_descriptions = {
    '/start': 'Начать диалог с ботом',
    '/genre': 'Выбрать жанр и желаемое количество треков для подборки',
    '/predict': 'Определить жанр песни по характеристикам (csv-файл)',
    '/review': 'Оставить отзыв на бота',
    '/stats': 'Посмотреть количество ...',
    '/lyrics': 'Найти текст песни (в разработке)'
}

exit_phrase = "Чтобы вернуться в главное меню, нажмите кнопку ниже:"

@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет, <b>{message.from_user.full_name}</b>! Я учебный бот для предсказания жанра песни. Посмотри, что я умею",
                         parse_mode=ParseMode.HTML, 
                         reply_markup=menu)

@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer("Главное меню:", reply_markup=menu_kb)

@router.message(lambda message: message.text.startswith('/'))
async def show_command_hints(clbck: CallbackQuery, message: types.Message):
    command_hints = '\n'.join([f"{command}: {description}" for command, description in command_descriptions.items()])
    await message.reply(f'Доступные команды:\n{command_hints}', reply=False)
    await clbck.message.answer(exit_phrase, reply_markup=exit_kb)

@router.message(Command("stats"))
async def cmd_stats(clbck: CallbackQuery, message: types.Message):
    stats_info = "Bot usage stats: ...\nAverage rating: ..."
    await message.answer(stats_info)
    await clbck.message.answer(exit_phrase, reply_markup=exit_kb)

# @dp.inline_handler()
# async def inline_query(query: types.InlineQuery):
#     results = [types.InlineQueryResultArticle(
#         id='1',
#         title='Echo',
#         input_message_content=types.InputTextMessageContent(message_text=query.query)
#     )]
#     await bot.answer_inline_query(query.id, results, cache_time=0)
