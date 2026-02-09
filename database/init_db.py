import sqlite3
import os

def init_database(db_path: str):
    """Инициализация базы данных"""
    
    print(f"🔧 Начинаю инициализацию базы данных...")
    print(f"   Путь к БД: {db_path}")
    
    try:
        # Создаем папку если её нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"   ✅ Папка создана/существует")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Таблица менеджеров
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            industry_custom TEXT,
            phone TEXT NOT NULL,
            terms_accepted BOOLEAN DEFAULT FALSE,
            terms_accepted_at TIMESTAMP,
            is_active BOOLEAN DEFAULT FALSE,
            registration_complete BOOLEAN DEFAULT FALSE,
            registration_step INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица клиентов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            notes TEXT,
            interest_model TEXT,
            last_contact TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES managers(id),
            UNIQUE(manager_id, phone)
        )
        ''')
        
        # Таблица шаблонов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            variables TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES managers(id)
        )
        ''')
        
        # Таблица напоминаний
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER NOT NULL,
            client_id INTEGER,
            type TEXT NOT NULL,
            text TEXT NOT NULL,
            due_date TIMESTAMP NOT NULL,
            is_done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES managers(id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
        ''')
        
        # Таблица для хранения ID последних сообщений бота
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_messages (
            telegram_id INTEGER PRIMARY KEY,
            last_message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Создаем индексы для ускорения запросов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_manager_phone ON clients(manager_id, phone)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_due_date ON reminders(due_date, is_done)')
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Все таблицы созданы успешно")
        print(f"🎉 База данных инициализирована: {db_path}")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
        raise

if __name__ == '__main__':
    # Тестируем локально
    init_database('sales_assistant.db')
