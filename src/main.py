import asyncio
import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Основная функция бота"""
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК SALES ASSISTANT BOT")
    logger.info("=" * 60)
    
    try:
        # Импортируем aiogram
        from aiogram import Bot, Dispatcher
        from aiogram.fsm.storage.memory import MemoryStorage
        logger.info("✅ aiogram импортирован")
        
        # Импортируем наши модули
        from config import Config
        logger.info("✅ config импортирован")
        
        from handlers import router
        logger.info("✅ handlers импортирован")
        
        # Импортируем init_database - ВАЖНО: из папки database
        # Добавляем путь к папке database
        database_path = os.path.join(os.path.dirname(__file__), '..', 'database')
        sys.path.insert(0, database_path)
        
        try:
            from init_db import init_database
            logger.info("✅ init_db импортирован из database/")
        except ImportError:
            # Пробуем альтернативный путь
            logger.warning("⚠️ Не удалось импортировать через database/, пробуем прямой путь...")
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "init_db", 
                os.path.join(database_path, "init_db.py")
            )
            init_db_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(init_db_module)
            init_database = init_db_module.init_database
            logger.info("✅ init_db импортирован через importlib")
        
        # Проверяем конфигурацию
        logger.info("🔍 Проверка конфигурации...")
        try:
            Config.validate()
            logger.info(f"✅ Конфигурация OK. DB_PATH: {Config.DB_PATH}")
        except ValueError as e:
            logger.error(f"❌ Ошибка конфигурации: {e}")
            logger.error("💡 Проверьте переменные окружения на bothost.ru:")
            logger.error("   - BOT_TOKEN (токен от @BotFather)")
            logger.error("   - ADMIN_ID (ваш Telegram ID)")
            logger.error("   - DB_PATH (/app/data/sales_assistant.db)")
            return
        
        # Инициализируем базу данных
        logger.info(f"🗄️  Инициализация базы данных: {Config.DB_PATH}")
        try:
            init_database(Config.DB_PATH)
            logger.info("✅ База данных инициализирована")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            return
        
        # Создаем бота
        logger.info("🤖 Создание экземпляра бота...")
        try:
            bot = Bot(token=Config.BOT_TOKEN)
            logger.info("✅ Бот создан")
        except Exception as e:
            logger.error(f"❌ Ошибка создания бота: {e}")
            return
        
        # Настраиваем диспетчер
        logger.info("⚙️  Настройка диспетчера...")
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        dp.include_router(router)
        
        # Запускаем бота
        logger.info("=" * 60)
        logger.info("🎉 БОТ УСПЕШНО ЗАПУЩЕН!")
        logger.info("📱 Отправьте /start в Telegram вашему боту")
        logger.info("=" * 60)
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}", exc_info=True)
        return

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"💥 Непредвиденная ошибка: {e}", exc_info=True)
