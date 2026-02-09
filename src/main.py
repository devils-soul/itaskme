import asyncio
import os
import sys
import logging

# Настройка логирования ПЕРЕД всеми импортами
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Добавляем пути для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

logger.info(f"📁 Текущая директория: {current_dir}")
logger.info(f"📁 Корень проекта: {project_root}")

try:
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    logger.info("✅ aiogram импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта aiogram: {e}")
    sys.exit(1)

try:
    from src.config import Config
    logger.info("✅ config импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта config: {e}")
    sys.exit(1)

try:
    from src.handlers import router
    logger.info("✅ handlers импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта handlers: {e}")
    sys.exit(1)

try:
    from src.database.init_db import init_database
    logger.info("✅ database импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта database: {e}")
    sys.exit(1)

async def main():
    """Основная функция бота"""
    logger.info("🚀 Запуск бота Sales Assistant...")
    
    # Проверяем конфигурацию
    try:
        Config.validate()
        logger.info(f"✅ Конфигурация загружена. BOT_TOKEN: {'есть' if Config.BOT_TOKEN else 'НЕТ'}")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        logger.error("💡 Проверьте переменные окружения на bothost.ru:")
        logger.error("   1. BOT_TOKEN - токен от @BotFather")
        logger.error("   2. ADMIN_ID - ваш Telegram ID")
        logger.error("   3. DB_PATH - /app/data/sales_assistant.db")
        return
    
    # Инициализируем базу данных
    try:
        logger.info(f"🔧 Инициализация БД по пути: {Config.DB_PATH}")
        init_database(Config.DB_PATH)
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Создаем бота и диспетчер
    try:
        logger.info("🤖 Создаем экземпляр бота...")
        bot = Bot(token=Config.BOT_TOKEN)
        
        logger.info("🔄 Настройка диспетчера...")
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Регистрируем роутер
        dp.include_router(router)
        
        # Запускаем бота
        logger.info("🎉 Бот запущен! Ожидаем сообщения...")
        logger.info("📱 Перейдите в Telegram и отправьте /start вашему боту")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}", exc_info=True)
        return

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Непредвиденная ошибка: {e}", exc_info=True)
