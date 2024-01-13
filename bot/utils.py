from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from utils import generate_prediction, batch_prediction, get_usage_statistics, get_average_rating, request_feedback

async def start_handler(message: types.Message):
    await message.reply("Привет! Я бот для предсказаний песен. Отправь мне текст песни.")

async def predict_handler(message: types.Message):
    prediction = generate_prediction(message.text)
    await message.reply(f"Предсказание: {prediction}")

async def batch_predict_handler(message: types.Message):
    # Обработка загруженного файла с текстами песен
    pass

async def usage_statistics_handler(message: types.Message):
    stats = get_usage_statistics()
    await message.reply(f"Статистика использования: {stats
