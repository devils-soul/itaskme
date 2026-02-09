from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

class Keyboards:
    """Клавиатуры для бота"""
    
    @staticmethod
    def remove_keyboard():
        """Удалить клавиатуру - ПРАВИЛЬНО для aiogram 3.0"""
        return ReplyKeyboardMarkup(
            keyboard=[],  # Пустой список кнопок
            resize_keyboard=True,
            one_time_keyboard=True,
            remove_keyboard=True  # Это устаревший параметр, но оставим
        )
    
    @staticmethod
    def get_phone_keyboard():
        """Клавиатура для получения номера телефона"""
        builder = ReplyKeyboardBuilder()
        
        builder.add(
            KeyboardButton(text="📱 Поделиться номером телефона", request_contact=True)
        )
        
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    @staticmethod
    def get_industry_keyboard():
        """Клавиатура для выбора сферы деятельности"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(text="🚗 Автосалон", callback_data="industry_auto"),
            InlineKeyboardButton(text="🏠 Недвижимость", callback_data="industry_real_estate"),
            InlineKeyboardButton(text="⚙️ Другое", callback_data="industry_other")
        )
        
        builder.adjust(2, 1)
        return builder.as_markup()
    
    @staticmethod
    def get_terms_keyboard():
        """Клавиатура для принятия правил"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(text="✅ Я принимаю правила", callback_data="terms_accept"),
            InlineKeyboardButton(text="❌ Отказаться", callback_data="terms_reject")
        )
        
        builder.adjust(1, 1)
        return builder.as_markup()
    
    @staticmethod
    def get_main_menu():
        """Главное меню"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(text="👥 Мои клиенты", callback_data="menu_clients"),
            InlineKeyboardButton(text="📋 Шаблоны сообщений", callback_data="menu_templates"),
            InlineKeyboardButton(text="🔔 Мои напоминания", callback_data="menu_reminders"),
            InlineKeyboardButton(text="⚙️ Настройки профиля", callback_data="menu_settings")
        )
        
        builder.adjust(2, 2)
        return builder.as_markup()
    
    @staticmethod
    def get_client_actions():
        """Действия с клиентом"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(text="📝 Добавить заметку", callback_data="client_add_note"),
            InlineKeyboardButton(text="🔔 Создать напоминание", callback_data="client_add_reminder"),
            InlineKeyboardButton(text="📨 Отправить сообщение", callback_data="client_send_message"),
            InlineKeyboardButton(text="✏️ Редактировать данные", callback_data="client_edit"),
            InlineKeyboardButton(text="🗑️ Удалить клиента", callback_data="client_delete"),
            InlineKeyboardButton(text="↩️ Назад к списку", callback_data="menu_clients")
        )
        
        builder.adjust(2, 2, 2)
        return builder.as_markup()
    
    @staticmethod
    def get_new_client_actions():
        """Действия для нового клиента"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(text="✅ Да, отправить визитку", callback_data="new_client_send_card"),
            InlineKeyboardButton(text="📝 Нет, добавить заметку", callback_data="client_add_note"),
            InlineKeyboardButton(text="🔔 Создать напоминание", callback_data="client_add_reminder"),
            InlineKeyboardButton(text="↩️ Пропустить", callback_data="menu_clients")
        )
        
        builder.adjust(1, 2, 1)
        return builder.as_markup()
    
    @staticmethod
    def get_back_button(callback_data: str = "main_menu"):
        """Кнопка Назад"""
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data=callback_data))
        return builder.as_markup()
    
    @staticmethod
    def get_business_card_actions():
        """Действия с визиткой"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(text="📋 Копировать текст визитки", callback_data="card_copy"),
            InlineKeyboardButton(text="👤 Вернуться к карточке клиента", callback_data="client_card"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        )
        
        builder.adjust(1, 2)
        return builder.as_markup()
