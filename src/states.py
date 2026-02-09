from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    """Состояния регистрации"""
    waiting_for_name = State()
    waiting_for_industry = State()
    waiting_for_industry_other = State()
    waiting_for_phone = State()
    waiting_for_terms = State()

class ClientStates(StatesGroup):
    """Состояния работы с клиентами"""
    waiting_for_client_name = State()
    waiting_for_client_phone = State()
    waiting_for_client_note = State()
    waiting_for_client_edit = State()

class TemplateStates(StatesGroup):
    """Состояния работы с шаблонами"""
    waiting_for_template_name = State()
    waiting_for_template_content = State()
    editing_template = State()

class ReminderStates(StatesGroup):
    """Состояния работы с напоминаниями"""
    waiting_for_reminder_type = State()
    waiting_for_reminder_date = State()
    waiting_for_reminder_text = State()
