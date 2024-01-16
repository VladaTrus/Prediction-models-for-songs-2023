from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import pandas as pd
import random

df = pd.DataFrame({'genre': ['pop', 'rap', 'hop', 'rap', 'pop'], 
                   'artist': ['Lana', 'Mana', 'Zhana', 'Hanna', 'Moana'], 
                   'title': ['pu', 'pupu', 'pupupu', 'pupupupu', 'pupup']})

router = Router()

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
async def genre_command(message: types.Message):
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


@router.message(lambda message: not message.text.isdigit(), state="*")
async def handle_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'selected_genre' in data:
            genre = data['selected_genre']
            try:
                num_songs = int(message.text)
                await send_random_songs_by_genre(message, genre, num_songs)
            except ValueError:
                await message.reply('Пожалуйста, введите число')
        else:
            await message.reply('Пожалуйста, выберите жанр сначала')

