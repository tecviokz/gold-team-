from aiogram import Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from keyboards import get_main_menu_keyboard, get_back_keyboard
from storage_db import get_work_status, get_queue_count, get_user_queue_count, get_moderator_status
from utils import get_moscow_time

async def start_command(message: types.Message):
    """Handler for /start command that shows the main menu"""
    await show_main_menu(message)

async def show_main_menu(message: types.Message):
    """Display the main menu with status information"""
    # Get current statuses
    work_status = get_work_status()
    work_emoji = "✅" if work_status else "🚫"
    
    queue_count = get_queue_count()
    user_queue_count = get_user_queue_count(message.from_user.id)
    
    moderator_status = get_moderator_status()
    moderator_emoji = "🟢" if moderator_status else "🔴"
    
    # Получаем текущее время в московском часовом поясе
    moscow_time = get_moscow_time()
    
    # Format the welcome message with improved design
    text = (
        "👋 *Добро пожаловать в GOLD TEAM*\n\n"
        "⏰ *Время сервера: " + Moscow_time + "*\n\n"
        "*О сервисе:*\n"
        "Narkoz Team - команда, которая берёт WhatsApp аккаунты в аренду.\n\n"
        "📊 *Информация:*\n"
        f"└ Статус работы: {work_emoji}\n"
        f"└ Общая очередь: {queue_count} номеров\n"
        f"└ Ваши номера: {user_queue_count} номеров\n\n"
        f"👥 *Модерация:*\n"
        f"└ Статус: {moderator_emoji} {'онлайн' if moderator_status else 'оффлайн'}\n"
        f"└ Время обработки: до 30 минут\n\n"
        "*Часы работы:*\n"
        "└ Ежедневно: с 9:00 до 20:00 (МСК)\n\n"
        "ℹ️ Используйте кнопки меню ниже для навигации"
    )
    
    # Get the keyboard for main menu
    keyboard = get_main_menu_keyboard()
    
    # Send message with keyboard
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_return_to_main(callback: CallbackQuery):
    """Handler for returning to the main menu via callback"""
    await callback.answer()  # Answer the callback query
    await show_main_menu(callback.message)

async def callback_group(callback: CallbackQuery):
    """Handler for the Group button in main menu"""
    await callback.answer()  # Answer the callback query
    
    text = (
        "📢 *Наша группа Narkoz Team*\n\n"
        "Подписывайтесь на нашу официальную группу, чтобы быть в курсе всех обновлений, акций и важных новостей!\n\n"
        "🔗 [Narkoz Team Группа](https://t.me/+j28PRQtxybplMTMy)\n\n"
        "В группе вы найдете:\n"
        "- Анонсы новых функций\n"
        "- Информацию о техническом обслуживании\n"
        "- Советы по эффективному использованию сервиса\n"
        "- Возможность задать вопросы администраторам\n\n"
        "Присоединяйтесь сейчас!"
    )
    
    # Get back keyboard
    keyboard = get_back_keyboard("main_menu")
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)

async def callback_prices(callback: CallbackQuery):
    """Handler for the Prices button in main menu"""
    await callback.answer()  # Answer the callback query
    
    # Получаем текущее время в московском часовом поясе
    moscow_time = get_moscow_time()
    
    text = (
        "💸 *Прайс-лист на услуги*\n"
        f"⏰ _Актуально на {moscow_time}_\n\n"
        "1 час - 10$\n"
        "2 часа - 13$\n"
        "3 часа - 16$\n\n"
        "‼️ Есть обьем - есть бонусы!"
    )
    
    # Get back keyboard
    keyboard = get_back_keyboard("main_menu")
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

def register_menu_handlers(dp: Dispatcher):
    """Register all menu-related handlers"""
    # Commands
    dp.message.register(start_command, Command("start"))
    
    # Callback handlers
    dp.callback_query.register(callback_return_to_main, F.data == "main_menu")
    dp.callback_query.register(callback_group, F.data == "group")
    dp.callback_query.register(callback_prices, F.data == "prices")
