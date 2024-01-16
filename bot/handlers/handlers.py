import logging

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.filters.state import State, StatesGroup
from keyboards.kb import menu_kb, exit_kb, iexit_kb
from keyboards.for_questions import get_yes_no_kb
import pandas as pd

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
    user_full_name = message.from_user.full_name
    greeting_message = f"Привет, <b>{user_full_name}</b>! Я бот для предсказания жанра песни. Посмотри, что я умею"
    
    await message.answer(
        text=greeting_message,
        parse_mode=ParseMode.HTML,
        reply_markup=menu_kb
    )

@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer("Главное меню:", reply_markup=menu_kb)

# stats
    
@router.callback_query(Command("stats"))
async def get_stats(clbck: CallbackQuery, message: types.Message):
    stats_info = "Bot usage stats: ...\nAverage rating: ..."
    await message.answer(stats_info)
    await clbck.message.answer(exit_phrase, reply_markup=exit_kb)

# review
# review
reviews = []

class ReviewState(StatesGroup):
    # waiting_for_review = FSMContext(storage="memory") 
    waiting_for_review = State() 

@router.callback_query(lambda query: query.data == "review")
async def get_review(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Оставьте свой отзыв об использовании бота. Что понравилось и чего не хватило в функционале?"
    )
    await state.set(ReviewState.waiting_for_review)

# Обработчик текстового сообщения при ожидании отзыва
@router.message(state=ReviewState.waiting_for_review)
async def save_review(message: Message, state: FSMContext):
    review = message.text
    reviews.append(review)

    # Сохраняем отзывы в файл
    with open("reviews.txt", "a", encoding="utf-8") as file:
        file.write(review + "\n")

    await message.answer("Спасибо за ваш отзыв!", reply_markup=exit_kb)
    await state.finish()

# /get_reviews
@router.message(Command("/get_reviews"))
async def get_reviews(message: Message):
    try:
        with open("reviews.txt", "r", encoding="utf-8") as file:
            saved_reviews = file.readlines()
        if saved_reviews:
            await message.answer("Вот недавние отзывы:\n\n" + "".join(saved_reviews))
        else:
            await message.answer("Пока нет отзывов")
    except FileNotFoundError:
        await message.answer("Пока нет отзывов")

# genre
    
df = pd.DataFrame({'genre': ['pop', 'rap', 'hop', 'rap', 'pop'], 
                   'artist': ['Lana', 'Mana', 'Zhana', 'Hanna', 'Moana'], 
                   'title': ['pu', 'pupu', 'pupupu', 'pupupupu', 'pupup']})

async def send_random_songs_by_genre(message: types.Message, genre: str, num_songs: int):
    genre_songs = df[df['genre'].str.lower() == genre]

    if len(genre_songs) == 0:
        await message.reply(f'Извините, нет песен в жанре "{genre}"')
    else:
        random_songs = genre_songs.sample(min(num_songs, len(genre_songs)))
        song_list = []
        for _, song in random_songs.iterrows():
            song_info = f"{song['artist']} -- {song['title']}\n"
            song_list.append(song_info)

        await message.reply('\n'.join(song_list), reply=False)

@router.message(Command('genre'))
async def genre_playlist(message: types.Message):
    await message.reply('Введите жанр:', reply=False)

@router.message(lambda message: message.text.isdigit())
async def handle_number(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        genre = message.text
        if genre.lower() not in [genre.lower() for genre in df['genre'].unique()]:
            await message.reply('Пожалуйста, выберите жанр из списка кнопок выше.')
        else:
            await message.answer('Конечно, сколько песен хотите получить? (Введите число)', reply=False)
            await state.update_data(selected_genre=genre)
    except Exception as e:
        await message.reply('Произошла ошибка при обработке вашего запроса')


@router.message(lambda message: not message.text.isdigit())
async def handle_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'selected_genre' in data:
            genre = data['selected_genre']
            try:
                num_songs = int(message.text)
                await send_random_songs_by_genre(message, genre, num_songs)
            except ValueError:
                await message.reply('Пожалуйста, введите число больше 0')
        else:
            await message.reply('Пожалуйста, выберите жанр сначала')

# questions + predict


@router.message(Command("/predict"))
async def predict_genre(message: Message):
    await message.answer(
        "Предсказание для вашей песни:"
    )

@router.message(Command("/survey"))
async def survey(message: Message):
    await message.answer(
        "Вы довольны результатом предсказания модели?",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.lower() == "да")
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "нет")
async def answer_no(message: Message):
    await message.answer(
        "Жаль",
        reply_markup=ReplyKeyboardRemove()
    )

# help 
@router.message(lambda message: message.text.startswith('/'))
async def show_command_hints(clbck: CallbackQuery, message: types.Message):
    command_hints = '\n'.join([f"{command}: {description}" for command, description in command_descriptions.items()])
    await message.reply(f'Доступные команды:\n{command_hints}', reply=False)
    await clbck.message.answer(exit_phrase, reply_markup=exit_kb)
# menu

@router.callback_query(lambda query: query.data == "review")
async def process_review_callback(query: CallbackQuery):
    await query.answer()
    await get_review(query.message)

@router.callback_query(lambda query: query.data == "genre")
async def process_genre_callback(query: CallbackQuery):
    await query.answer()
    await genre_playlist(query.message)

@router.callback_query(lambda query: query.data == "predict")
async def process_predict_callback(query: CallbackQuery):
    await query.answer()
    await predict_genre(query.message)

# @router.callback_query(lambda query: query.data == "stats")
# async def process_stats_callback(query: CallbackQuery):
#     await query.answer()
#     await get_stats(query.message)

# @router.callback_query(lambda query: query.data == "help")
# async def process_help_(query: CallbackQuery):
#     await query.answer()
#     await show_command_hints(query.message)

# @dp.inline_handler()
# async def inline_query(query: types.InlineQuery):
#     results = [types.InlineQueryResultArticle(
#         id='1',
#         title='Echo',
#         input_message_content=types.InputTextMessageContent(message_text=query.query)
#     )]
#     await bot.answer_inline_query(query.id, results, cache_time=0)
