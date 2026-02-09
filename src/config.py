import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Путь к базе данных
    DB_PATH = os.getenv('DB_PATH', 'database/sales_assistant.db')
    
    # ID администратора
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
    
    # Настройки
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')
    
    # Проверка конфигурации
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
