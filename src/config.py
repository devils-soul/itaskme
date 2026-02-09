import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Путь к базе данных
    # Для bothost.ru используем /app/data/
    DB_PATH = os.getenv('DB_PATH', '/app/data/sales_assistant.db')
    
    # ID администратора
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
    
    # Настройки
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')
    
    # Проверка конфигурации
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен. Добавьте его в переменные окружения на bothost.ru")
        
        print(f"✅ Конфигурация проверена:")
        print(f"   • BOT_TOKEN: {'установлен' if cls.BOT_TOKEN else 'НЕТ!'}")
        print(f"   • DB_PATH: {cls.DB_PATH}")
        print(f"   • ADMIN_ID: {cls.ADMIN_ID}")
