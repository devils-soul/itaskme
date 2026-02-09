import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self):
        """Получение соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ========== Менеджеры ==========
    
    def get_manager(self, telegram_id: int) -> Optional[Dict]:
        """Получить менеджера по telegram_id"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM managers WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def create_manager(self, telegram_id: int, full_name: str, industry: str, 
                      phone: str, industry_custom: str = None) -> int:
        """Создать нового менеджера"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO managers (telegram_id, full_name, industry, industry_custom, phone)
        VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, full_name, industry, industry_custom, phone))
        
        manager_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return manager_id
    
    def update_manager_step(self, telegram_id: int, step: int):
        """Обновить шаг регистрации менеджера"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE managers 
        SET registration_step = ?, updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = ?
        ''', (step, telegram_id))
        
        conn.commit()
        conn.close()
    
    def complete_registration(self, telegram_id: int):
        """Завершить регистрацию менеджера"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE managers 
        SET terms_accepted = TRUE,
            terms_accepted_at = CURRENT_TIMESTAMP,
            is_active = TRUE,
            registration_complete = TRUE,
            registration_step = 5,
            updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = ?
        ''', (telegram_id,))
        
        conn.commit()
        conn.close()
    
    # ========== Сообщения бота ==========
    
    def save_last_bot_message(self, telegram_id: int, message_id: int):
        """Сохранить ID последнего сообщения бота"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO bot_messages (telegram_id, last_message_id, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (telegram_id, message_id))
        
        conn.commit()
        conn.close()
    
    def get_last_bot_message(self, telegram_id: int) -> Optional[int]:
        """Получить ID последнего сообщения бота"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT last_message_id FROM bot_messages WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()
        
        conn.close()
        return row['last_message_id'] if row else None
    
    # ========== Клиенты ==========
    
    def get_client(self, manager_id: int, phone: str) -> Optional[Dict]:
        """Получить клиента по номеру телефона"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM clients 
        WHERE manager_id = ? AND phone = ?
        ''', (manager_id, phone))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def create_client(self, manager_id: int, name: str, phone: str) -> int:
        """Создать нового клиента"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO clients (manager_id, name, phone, last_contact)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (manager_id, name, phone))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return client_id
    
    def get_clients(self, manager_id: int, limit: int = 100) -> List[Dict]:
        """Получить список клиентов менеджера"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM clients 
        WHERE manager_id = ?
        ORDER BY last_contact DESC
        LIMIT ?
        ''', (manager_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ========== Шаблоны ==========
    
    def get_templates(self, manager_id: int) -> List[Dict]:
        """Получить шаблоны менеджера"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM templates 
        WHERE manager_id = ? AND is_active = TRUE
        ORDER BY name
        ''', (manager_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def create_default_templates(self, manager_id: int, full_name: str, industry: str):
        """Создать шаблоны по умолчанию для нового менеджера"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        templates = [
            {
                'name': 'Первичный контакт',
                'content': f"👋 Добрый день, {{имя_клиента}}!\n\nМеня зовут {full_name}, я менеджер по продажам. Отправляю вам контакты.\n\n📍 Адрес: укажите адрес\n📞 Телефон: укажите телефон\n🌐 Сайт: укажите сайт\n\nС уважением, {full_name}",
                'variables': '["имя_клиента", "ваше_имя", "ваша_компания"]'
            }
        ]
        
        for template in templates:
            cursor.execute('''
            INSERT INTO templates (manager_id, name, content, variables)
            VALUES (?, ?, ?, ?)
            ''', (manager_id, template['name'], template['content'], template['variables']))
        
        conn.commit()
        conn.close()
