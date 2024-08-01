import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from handlers import comands

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
# bot = Bot(token="*")
dp = Dispatcher()


async def delete_webhook():
    await bot.delete_webhook()


dp.include_router(comands.router)


async def main():
    await delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
