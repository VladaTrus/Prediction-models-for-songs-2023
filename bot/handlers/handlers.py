import logging

from aiogram import types, Router, F
from aiogram.dispatcher.filters import Command
from aiogram.types import ParseMode, Message, ReplyKeyboardRemove

logging.basicConfig(level=logging.INFO)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Отправляет приветственное сообщение при команде /start
    """
    await message.answer(f"Привет, <b>{message.from_user.full_name}</b>! Я учебный бот для предсказания жанра песни. Посмотри, что я умею",
                         parse_mode=ParseMode.HTML)


@router.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode=ParseMode.HTML
    )

@router.message(Command('help'))
async def on_help(message: types.Message):
    help_message = "Available commands:\n"
    help_message += "/start - Begin using the bot\n"
    help_message += "/help - Get assistance\n"
    help_message += "/stats - View bot statistics\n"
    help_message += "/predict - Make a single prediction\n"
    help_message += "/predict_multiple - Make multiple predictions\n"
    help_message += "/review - Provide a review\n"
    help_message += "/suggestions - List available commands\n"

    await message.reply(help_message)


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    # You would replace the following with actual logic to retrieve stats
    stats_info = "Bot usage stats: ...\nAverage rating: ..."
    await message.answer(stats_info)

# @dp.inline_handler()
# async def inline_query(query: types.InlineQuery):
#     results = [types.InlineQueryResultArticle(
#         id='1',
#         title='Echo',
#         input_message_content=types.InputTextMessageContent(message_text=query.query)
#     )]
#     await bot.answer_inline_query(query.id, results, cache_time=0)

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
