#!/usr/bin/env python
import asyncio
import logging
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from handlers.menu import register_menu_handlers
from handlers.numbers import register_numbers_handlers
from handlers.info import register_info_handlers
from handlers.admin import register_admin_handlers
from storage_db import initialize_db_storage

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main function to start the bot"""
    API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not API_TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        return

    start_time = time.time()
    logging.info("Запуск Telegram бота Narkoz Team...")
    
    try:
        # Initialize database first
        initialize_db_storage()
        
        # Initialize bot and dispatcher
        bot = Bot(token=API_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Register handlers
        register_menu_handlers(dp)
        register_numbers_handlers(dp)
        register_info_handlers(dp)
        register_admin_handlers(dp)
        
        # Set bot commands
        await bot.set_my_commands([
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="info", description="Полезная информация"),
            BotCommand(command="work", description="Панель админа")
        ])
        
        init_time = time.time() - start_time
        logging.info(f"Бот запущен! Время инициализации: {init_time:.2f} сек.")
        
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при инициализации бота: {e}")
        raise
    
def run_bot():
    """Function to start the bot from external modules"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен!")
        print("\nБот остановлен!")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    run_bot()