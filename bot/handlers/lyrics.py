import pandas as pd
from aiogram import Router, types

df = pd.DataFrame(
    {
        "genre": ["pop", "rap", "hop", "rap", "pop"],
        "artist": ["Lana", "Mana", "Zhana", "Hanna", "Moana"],
        "title_name": ["pu", "pupu", "pupupu", "pupupupu", "pupup"],
    }
)

# 'title', 'lyrics'
router = Router()


async def search_song(message: types.Message):
    user_message = message.text
    results = df[df["title_name"].str.contains(user_message, case=False)]

    if len(results) == 0:
        await message.reply("К сожалению, я не знаю такого трека. Попробуйте снова.")
    elif len(results) == 1:
        song = results.iloc[0]
        reply_message = f"Слова найдены, вот результат:\nИсполнитель: {song['artist']}, Песня: {song['title']}\nТекст песни: {song['lyrics']}"
        await message.reply(reply_message, reply=False)
    else:
        pass
        # keyboard = types.InlineKeyboardMarkup(row_width=1)
        # for index, song in results.iterrows():
        # button_text = f"Исполнитель: {song['artist']}, Песня: {song['title']}"
        # callback_data = f"select_song_{index}"
        # keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))

        # await message.reply(
        #     "Найдено несколько вариантов, выберите подходящий:",
        #     reply_markup=keyboard,
        #     reply=False,
        # )


# @router.callback_query_handler(lambda c: c.data.startswith('select_song_'))
# async def process_callback(callback_query: types.CallbackQuery):
#     index = int(callback_query.data.split('_')[-1])
#     song = df.iloc[index]
#     reply_message = f"Слова найдены, вот результат:\nИсполнитель: {song['artist']}, Песня: {song['title']}\nТекст песни: {song['lyrics']}"
#     await bot.send_message(callback_query.from_user.id, reply_message, reply=False)
