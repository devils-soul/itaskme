from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from .database import Database
from .keyboards import Keyboards
from .messages import Messages
from .utils import PhoneUtils, MessageUtils, TextUtils
from .states import RegistrationStates, ClientStates
from .config import Config

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
db = Database(Config.DB_PATH)

class BotHandler:
    """Основной обработчик бота"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def _safe_delete_message(self, chat_id: int, message_id: int):
        """Безопасное удаление сообщения"""
        try:
            await self.bot.delete_message(chat_id, message_id)
            return True
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение {message_id}: {e}")
            return False
    
    async def _send_and_save_message(self, chat_id: int, text: str, 
                                   reply_markup=None, parse_mode="Markdown"):
        """Отправить сообщение и сохранить его ID"""
        # Пытаемся удалить предыдущее сообщение
        last_msg_id = db.get_last_bot_message(chat_id)
        if last_msg_id:
            await self._safe_delete_message(chat_id, last_msg_id)
        
        # Отправляем новое сообщение
        msg = await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        
        # Сохраняем ID нового сообщения
        db.save_last_bot_message(chat_id, msg.message_id)
        return msg

class RegistrationHandlers:
    """Обработчики регистрации"""
    
    @staticmethod
    @router.message(Command("start"))
    async def cmd_start(message: Message, state: FSMContext):
        """Обработчик команды /start"""
        handler = BotHandler(message.bot)
        
        # Проверяем, есть ли пользователь в базе
        manager = db.get_manager(message.from_user.id)
        
        if manager:
            if manager['terms_accepted']:
                # Пользователь уже зарегистрирован
                await handler._send_and_save_message(
                    message.chat.id,
                    Messages.MAIN_MENU.format(name=manager['full_name']),
                    Keyboards.get_main_menu()
                )
                await state.clear()
            else:
                # Пользователь есть, но не принял правила
                await handler._send_and_save_message(
                    message.chat.id,
                    Messages.STEP_4_TERMS,
                    Keyboards.get_terms_keyboard()
                )
                await state.set_state(RegistrationStates.waiting_for_terms)
        else:
            # Новый пользователь - начинаем регистрацию
            await handler._send_and_save_message(
                message.chat.id,
                Messages.STEP_1_NAME,
                Keyboards.remove_keyboard()
            )
            await state.set_state(RegistrationStates.waiting_for_name)
    
    @staticmethod
    @router.message(RegistrationStates.waiting_for_name)
    async def process_name(message: Message, state: FSMContext):
        """Обработка ввода имени"""
        handler = BotHandler(message.bot)
        
        name = TextUtils.normalize_name(message.text)
        if not name or len(name) < 2:
            await message.answer("⚠️ Пожалуйста, введите корректное имя (минимум 2 символа)")
            return
        
        # Сохраняем имя в состоянии
        await state.update_data(full_name=name)
        
        # Переходим к следующему шагу
        await handler._send_and_save_message(
            message.chat.id,
            Messages.STEP_2_INDUSTRY.format(name=name),
            Keyboards.get_industry_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_industry)
    
    @staticmethod
    @router.callback_query(F.data.startswith("industry_"))
    async def process_industry(callback: CallbackQuery, state: FSMContext):
        """Обработка выбора сферы деятельности"""
        handler = BotHandler(callback.bot)
        industry = callback.data.split("_")[1]
        
        if industry == "other":
            # Запрашиваем уточнение для "Другого"
            await handler._send_and_save_message(
                callback.message.chat.id,
                Messages.STEP_2_OTHER,
                Keyboards.remove_keyboard()
            )
            await state.set_state(RegistrationStates.waiting_for_industry_other)
        else:
            # Сохраняем выбранную сферу
            industry_map = {
                "auto": "Автосалон",
                "real_estate": "Недвижимость"
            }
            await state.update_data(industry=industry, industry_display=industry_map.get(industry, "Другое"))
            
            # Переходим к следующему шагу
            await handler._send_and_save_message(
                callback.message.chat.id,
                Messages.STEP_3_PHONE,
                Keyboards.get_phone_keyboard()
            )
            await state.set_state(RegistrationStates.waiting_for_phone)
        
        await callback.answer()
    
    @staticmethod
    @router.message(RegistrationStates.waiting_for_industry_other)
    async def process_industry_other(message: Message, state: FSMContext):
        """Обработка ввода другой сферы деятельности"""
        handler = BotHandler(message.bot)
        
        industry_custom = message.text.strip()
        if not industry_custom or len(industry_custom) < 2:
            await message.answer("⚠️ Пожалуйста, введите корректное название сферы деятельности")
            return
        
        await state.update_data(industry="other", industry_display=industry_custom, industry_custom=industry_custom)
        
        # Переходим к следующему шагу
        await handler._send_and_save_message(
            message.chat.id,
            Messages.STEP_3_PHONE,
            Keyboards.get_phone_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_phone)
    
    @staticmethod
    @router.message(RegistrationStates.waiting_for_phone)
    async def process_phone_invalid(message: Message, state: FSMContext):
        """Обработка невалидного ввода телефона (не контакт)"""
        handler = BotHandler(message.bot)
        
        await handler._send_and_save_message(
            message.chat.id,
            Messages.STEP_3_INVALID,
            Keyboards.get_phone_keyboard()
        )
    
    @staticmethod
    @router.message(RegistrationStates.waiting_for_phone, F.contact)
    async def process_phone_valid(message: Message, state: FSMContext):
        """Обработка валидного телефона (контакт)"""
        handler = BotHandler(message.bot)
        contact = message.contact
        
        # Стандартизируем номер телефона
        phone = PhoneUtils.standardize_phone(contact.phone_number)
        if not phone:
            await message.answer("⚠️ Не удалось обработать номер телефона. Попробуйте ещё раз.")
            return
        
        await state.update_data(phone=phone)
        
        # Получаем
