import re
import phonenumbers
from datetime import datetime
from typing import Optional

class PhoneUtils:
    """Утилиты для работы с телефонами"""
    
    @staticmethod
    def standardize_phone(phone_input: str) -> Optional[str]:
        """Стандартизация номера телефона в формат +79991234567"""
        if not phone_input:
            return None
        
        try:
            # Убираем все нецифровые символы, кроме +
            cleaned = re.sub(r'[^\d+]', '', phone_input)
            
            # Если номер начинается с 8 или 7, добавляем +
            if cleaned.startswith('8'):
                cleaned = '+7' + cleaned[1:]
            elif cleaned.startswith('7') and not cleaned.startswith('+7'):
                cleaned = '+' + cleaned
            
            # Если номер не начинается с +, добавляем +7
            if not cleaned.startswith('+'):
                # Если номер из 10 цифр, добавляем +7
                if len(cleaned) == 10:
                    cleaned = '+7' + cleaned
                else:
                    cleaned = '+7' + cleaned
            
            # Парсим номер с помощью phonenumbers
            parsed = phonenumbers.parse(cleaned, None)
            
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            else:
                return None
                
        except Exception:
            return None
    
    @staticmethod
    def format_phone_display(phone: str) -> str:
        """Форматирование номера для отображения +7 (999) 123-45-67"""
        if not phone or len(phone) != 12:
            return phone
        
        # +79991234567 -> +7 (999) 123-45-67
        return f"+7 ({phone[2:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:]}"
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Проверка валидности номера телефона"""
        standardized = PhoneUtils.standardize_phone(phone)
        return bool(standardized)


class MessageUtils:
    """Утилиты для работы с сообщениями"""
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Экранирование специальных символов для MarkdownV2"""
        if not text:
            return ""
        
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    @staticmethod
    def format_datetime(dt_str: str) -> str:
        """Форматирование даты для отображения"""
        if not dt_str:
            return "Не указано"
        
        try:
            # Парсим дату из строки
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y %H:%M')
        except:
            return dt_str


class TextUtils:
    """Утилиты для работы с текстом"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Обрезать текст до максимальной длины"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)].rstrip() + suffix
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Нормализация имени (удаление лишних пробелов)"""
        if not name:
            return ""
        
        # Удаляем лишние пробелы
        name = ' '.join(name.strip().split())
        # Делаем первую букву заглавной
        return ' '.join([word.capitalize() for word in name.split()])
