from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import logging

# Настройка логирования ПЕРЕД импортами
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорты из текущей директории src (БЕЗ префикса src.)
try:
    from database import Database
    logger.info("✅ Database импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта Database: {e}")
    raise

try:
    from keyboards import Keyboards
    from messages import Messages
    from utils import PhoneUtils, MessageUtils, TextUtils
    from states import RegistrationStates, ClientStates
    from config import Config
    logger.info("✅ Все модули импортированы успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта модулей: {e}")
    raise

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
    @router.message(RegistrationStates.waiting_for_phone, F.text)
    async def process_phone_invalid_text(message: Message, state: FSMContext):
        """Обработка текстового ввода вместо контакта"""
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
        
        logger.info(f"📱 Получен контакт: {contact.phone_number}")
        
        # Стандартизируем номер телефона
        phone = PhoneUtils.standardize_phone(contact.phone_number)
        if not phone:
            await message.answer("⚠️ Не удалось обработать номер телефона. Попробуйте ещё раз.")
            return
        
        logger.info(f"✅ Номер стандартизирован: {phone}")
        
        await state.update_data(phone=phone)
        
        # Получаем данные из состояния
        data = await state.get_data()
        logger.info(f"📋 Данные состояния: {data}")
        
        # Создаем менеджера в базе данных
        manager_id = db.create_manager(
            telegram_id=message.from_user.id,
            full_name=data['full_name'],
            industry=data['industry'],
            phone=phone,
            industry_custom=data.get('industry_custom')
        )
        
        logger.info(f"✅ Менеджер создан с ID: {manager_id}")
        
        # Создаем шаблоны по умолчанию
        db.create_default_templates(manager_id, data['full_name'], data['industry_display'])
        
        # Переходим к правилам
        await handler._send_and_save_message(
            message.chat.id,
            Messages.STEP_4_TERMS,
            Keyboards.get_terms_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_terms)
    
    @staticmethod
    @router.callback_query(F.data == "terms_accept")
    async def process_terms_accept(callback: CallbackQuery, state: FSMContext):
        """Обработка принятия правил"""
        handler = BotHandler(callback.bot)
        
        # Завершаем регистрацию
        db.complete_registration(callback.from_user.id)
        
        # Получаем данные менеджера
        manager = db.get_manager(callback.from_user.id)
        
        # Показываем главное меню
        await handler._send_and_save_message(
            callback.message.chat.id,
            Messages.MAIN_MENU.format(name=manager['full_name']),
            Keyboards.get_main_menu()
        )
        
        await state.clear()
        await callback.answer("✅ Регистрация завершена!")
    
    @staticmethod
    @router.callback_query(F.data == "terms_reject")
    async def process_terms_reject(callback: CallbackQuery, state: FSMContext):
        """Обработка отказа от правил"""
        handler = BotHandler(callback.bot)
        
        # Обновляем статус менеджера
        db.update_manager_step(callback.from_user.id, 0)
        
        # Показываем сообщение об отмене
        await handler._send_and_save_message(
            callback.message.chat.id,
            Messages.REGISTRATION_CANCELLED,
            Keyboards.remove_keyboard()
        )
        
        await state.clear()
        await callback.answer("❌ Регистрация отменена")


class ClientHandlers:
    """Обработчики работы с клиентами"""
    
    @staticmethod
    @router.message(F.text)
    async def process_phone_input(message: Message, state: FSMContext):
        """Обработка ввода номера телефона клиента"""
        handler = BotHandler(message.bot)
        
        # Проверяем, зарегистрирован ли пользователь
        manager = db.get_manager(message.from_user.id)
        if not manager or not manager['terms_accepted']:
            await message.answer("ℹ️ Пожалуйста, сначала завершите регистрацию. Нажмите /start")
            return
        
        # Проверяем, не в процессе ли мы регистрации
        current_state = await state.get_state()
        if current_state:
            # Если есть активное состояние, игнорируем ввод телефона
            return
        
        # Стандартизируем номер телефона
        phone = PhoneUtils.standardize_phone(message.text)
        if not phone:
            await handler._send_and_save_message(
                message.chat.id,
                Messages.INVALID_PHONE,
                Keyboards.get_back_button("main_menu")
            )
            return
        
        # Проверяем, есть ли такой клиент
        client = db.get_client(manager['id'], phone)
        
        if client:
            # Клиент уже существует - показываем карточку
            await handler._send_and_save_message(
                message.chat.id,
                Messages.CLIENT_CARD.format(
                    name=client['name'],
                    phone=PhoneUtils.format_phone_display(client['phone']),
                    last_contact=MessageUtils.format_datetime(client['last_contact']),
                    status=client['status'],
                    notes=client['notes'] or "Нет заметок"
                ),
                Keyboards.get_client_actions()
            )
        else:
            # Новый клиент - запрашиваем имя
            await state.update_data(client_phone=phone)
            await handler._send_and_save_message(
                message.chat.id,
                Messages.NEW_CLIENT.format(phone=PhoneUtils.format_phone_display(phone)),
                Keyboards.get_back_button("main_menu")
            )
            await state.set_state(ClientStates.waiting_for_client_name)
    
    @staticmethod
    @router.message(ClientStates.waiting_for_client_name)
    async def process_client_name(message: Message, state: FSMContext):
        """Обработка ввода имени клиента"""
        handler = BotHandler(message.bot)
        
        client_name = TextUtils.normalize_name(message.text)
        if not client_name or len(client_name) < 2:
            await message.answer("⚠️ Пожалуйста, введите корректное имя клиента (минимум 2 символа)")
            return
        
        # Получаем данные из состояния
        data = await state.get_data()
        client_phone = data['client_phone']
        
        # Получаем менеджера
        manager = db.get_manager(message.from_user.id)
        
        # Создаем клиента
        client_id = db.create_client(manager['id'], client_name, client_phone)
        
        # Показываем сообщение об успешном создании
        await handler._send_and_save_message(
            message.chat.id,
            Messages.CLIENT_SAVED.format(name=client_name),
            Keyboards.get_new_client_actions()
        )
        
        # Сохраняем ID клиента для дальнейших действий
        await state.update_data(client_id=client_id, client_name=client_name)
        await state.clear()


class MenuHandlers:
    """Обработчики меню"""
    
    @staticmethod
    @router.callback_query(F.data == "main_menu")
    async def process_main_menu(callback: CallbackQuery, state: FSMContext):
        """Обработка перехода в главное меню"""
        handler = BotHandler(callback.bot)
        
        # Очищаем состояние
        await state.clear()
        
        # Получаем данные менеджера
        manager = db.get_manager(callback.from_user.id)
        if not manager:
            await callback.answer("❌ Ошибка: пользователь не найден")
            return
        
        # Показываем главное меню
        await handler._send_and_save_message(
            callback.message.chat.id,
            Messages.MAIN_MENU.format(name=manager['full_name']),
            Keyboards.get_main_menu()
        )
        
        await callback.answer()
class MainMenuHandlers:
    """Обработчики главного меню"""
    
    @staticmethod
    @router.callback_query(F.data == "menu_clients")
    async def menu_clients(callback: CallbackQuery, state: FSMContext):
        """Меню 'Мои клиенты'"""
        handler = BotHandler(callback.bot)
        
        # Получаем данные менеджера
        manager = db.get_manager(callback.from_user.id)
        if not manager:
            await callback.answer("❌ Ошибка: пользователь не найден")
            return
        
        # Получаем список клиентов
        clients = db.get_clients(manager['id'], limit=10)
        
        if not clients:
            message_text = "👥 *Мои клиенты*\n\nУ вас пока нет клиентов.\n\n📱 Отправьте номер телефона клиента, чтобы добавить его."
        else:
            clients_list = []
            for i, client in enumerate(clients[:10], 1):
                clients_list.append(f"{i}. {client['name']} - {PhoneUtils.format_phone_display(client['phone'])}")
            
            message_text = f"👥 *Мои клиенты* (последние 10)\n\n" + "\n".join(clients_list) + "\n\n📱 Отправьте номер телефона клиента, чтобы добавить или найти."
        
        await handler._send_and_save_message(
            callback.message.chat.id,
            message_text,
            Keyboards.get_back_button("main_menu")
        )
        await callback.answer()
    
    @staticmethod
    @router.callback_query(F.data == "menu_templates")
    async def menu_templates(callback: CallbackQuery, state: FSMContext):
        """Меню 'Шаблоны сообщений'"""
        handler = BotHandler(callback.bot)
        
        # Получаем данные менеджера
        manager = db.get_manager(callback.from_user.id)
        if not manager:
            await callback.answer("❌ Ошибка: пользователь не найден")
            return
        
        # Получаем шаблоны
        templates = db.get_templates(manager['id'])
        
        if not templates:
            message_text = "📋 *Шаблоны сообщений*\n\nУ вас пока нет шаблонов."
        else:
            templates_list = []
            for i, template in enumerate(templates, 1):
                templates_list.append(f"{i}. {template['name']}")
            
            message_text = f"📋 *Шаблоны сообщений*\n\n" + "\n".join(templates_list) + "\n\n⚡ Эта функция находится в разработке."
        
        await handler._send_and_save_message(
            callback.message.chat.id,
            message_text,
            Keyboards.get_back_button("main_menu")
        )
        await callback.answer()
    
    @staticmethod
    @router.callback_query(F.data == "menu_reminders")
    async def menu_reminders(callback: CallbackQuery, state: FSMContext):
        """Меню 'Мои напоминания'"""
        handler = BotHandler(callback.bot)
        
        message_text = "🔔 *Мои напоминания*\n\n⚡ Эта функция находится в разработке.\n\nСкоро вы сможете создавать напоминания для звонков и встреч с клиентами."
        
        await handler._send_and_save_message(
            callback.message.chat.id,
            message_text,
            Keyboards.get_back_button("main_menu")
        )
        await callback.answer()
    
    @staticmethod
    @router.callback_query(F.data == "menu_settings")
    async def menu_settings(callback: CallbackQuery, state: FSMContext):
        """Меню 'Настройки профиля'"""
        handler = BotHandler(callback.bot)
        
        # Получаем данные менеджера
        manager = db.get_manager(callback.from_user.id)
        if not manager:
            await callback.answer("❌ Ошибка: пользователь не найден")
            return
        
        message_text = f"⚙️ *Настройки профиля*\n\n👤 Имя: {manager['full_name']}\n🏢 Сфера: {manager['industry_custom'] or manager['industry']}\n📱 Телефон: {PhoneUtils.format_phone_display(manager['phone'])}\n\n⚡ Редактирование профиля в разработке."
        
        await handler._send_and_save_message(
            callback.message.chat.id,
            message_text,
            Keyboards.get_back_button("main_menu")
        )
        await callback.answer()

# Регистрируем обработчики
registration_handlers = RegistrationHandlers()
client_handlers = ClientHandlers()
menu_handlers = MenuHandlers()
main_menu_handlers = MainMenuHandlers()  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
