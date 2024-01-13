import logging

from aiogram import types
from bot.main import dp, bot

from aiogram import types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ParseMode, Message, ReplyKeyboardRemove
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    """
    Отправляет приветственное сообщение при команде /start
    """
    await message.answer("Привет, <b>{message.from_user.full_name}</b>! Я учебный бот для предсказания жанра песни. Посмотри, что я умею",
                         parse_mode=ParseMode.HTML)


@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode=ParseMode.HTML
    )

@dp.message_handler(Command('help'))
async def on_help(message: types.Message):
    await message.reply("Набери /start , чтобы начать и /help если нужна помощь")


@dp.inline_handler()
async def inline_query(query: types.InlineQuery):
    results = [types.InlineQueryResultArticle(
        id='1',
        title='Echo',
        input_message_content=types.InputTextMessageContent(message_text=query.query)
    )]
    await bot.answer_inline_query(query.id, results, cache_time=0)

# @dp.message_handler(Command('quiz'))
# async def start_quiz(message: types.Message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     item1 = types.KeyboardButton("Да")
#     item2 = types.KeyboardButton("Нет")
#     markup.add(item1, item2)
#     await message.answer("Довольны ли полученным результатом?", reply_markup=markup)
#     await QuizState.question.set()

# @dp.message_handler(lambda message: message.text in ["Option A", "Option B"], state=QuizState.question)
# async def answer_question(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['answer'] = message.text
#     await message.reply(f"You selected: {message.text}. Thanks for participating!")
#     await state.finish()
