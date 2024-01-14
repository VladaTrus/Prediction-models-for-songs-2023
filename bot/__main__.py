import asyncio
import logging 

from aiogram import Bot, Dispatcher, types
from config import config
from handlers import questions, different_types, handlers

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

async def main():
    dp.include_routers(questions.router, different_types.router, handlers.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
