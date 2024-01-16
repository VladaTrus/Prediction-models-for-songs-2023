import asyncio
import logging 

from aiogram import Bot, Dispatcher, types
from config import config
from handlers import handlers

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

async def main():
    dp.include_routers(handlers.router) #questions.router, genres.router
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
