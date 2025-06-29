import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BotConfig
from datetime import datetime, timedelta

from bot_instance import bot
from handlers import user
from errors import handlers
from database.models import async_main


def register_routers(dp: Dispatcher) -> None:
    """Registers routers"""
    dp.include_routers(handlers.router, user.router)


async def main() -> None:
    """Entry point of the program."""

    await async_main()

    config = BotConfig(
        admin_ids=[],
        welcome_message=""
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["config"] = config

    register_routers(dp)

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as _ex:
        print(f'Exception: {_ex}')


if __name__ == '__main__':
    asyncio.run(main())
