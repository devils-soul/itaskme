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

# Добавляем путь к корню проекта
sys.path.insert(0, '/app')

logger.info("=" * 50)
logger.info("🚀 ЗАПУСК БОТА SALES ASSISTANT")
logger.info("=" * 50)

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

# ПРЯМОЙ ИМПОРТ БЕЗ src. префикса
try:
    from database.init_db import init_database
    logger.info("✅ database.init_db импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта database.init_db: {e}")
    logger.error("Пробую альтернативный импорт...")
    try:
        # Альтернативный способ
        import importlib.util
        spec = importlib.util.spec_from_file_location("init_db", "/app/database/init_db.py")
        init_db_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(init_db_module)
        init_database = init_db_module.init_database
        logger.info("✅ database импортирован через importlib")
    except Exception as e2:
        logger.error(f"❌ Альтернативный импорт также не удался: {e2}")
        sys.exit(1)

async def main():
    """Основная функция бота"""
    logger.info("🔧 Начинаем инициализацию бота...")
    
    # Проверяем конфигурацию
    try:
        Config.validate()
        logger.info(f"✅ Конфигурация загружена")
        logger.info(f"   • DB_PATH: {Config.DB_PATH}")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        logger.error("💡 Проверьте переменные окружения на bothost.ru")
        return
    
    # Инициализируем базу данных
    try:
        logger.info(f"🔧 Инициализация БД по пути: {Config.DB_PATH}")
        init_database(Config.DB_PATH)
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}", exc_info=True)
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
        logger.info("=" * 50)
        logger.info("🎉 БОТ УСПЕШНО ЗАПУЩЕН!")
        logger.info("📱 Отправьте /start в Telegram вашему боту")
        logger.info("=" * 50)
        
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
