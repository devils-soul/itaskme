import asyncio
import os
import sys
import logging

# Добавляем текущую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем наши модули
from config import Config
from handlers import router
from database.init_db import init_database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция бота"""
    
    # Проверяем конфигурацию
    try:
        Config.validate()
        logger.info("✅ Конфигурация загружена успешно")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Инициализируем базу данных
    try:
        init_database(Config.DB_PATH)
        logger.info(f"✅ База данных инициализирована: {Config.DB_PATH}")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Создаем бота и диспетчер
    try:
        bot = Bot(token=Config.BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Регистрируем роутер
        dp.include_router(router)
        
        # Запускаем бота
        logger.info("🚀 Бот запущен и готов к работе!")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
        return

if __name__ == '__main__':
    asyncio.run(main())
