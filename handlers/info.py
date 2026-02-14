from aiogram import Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from keyboards import get_back_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_moscow_time

async def info_command(message: types.Message):
    """Handler for /info command that shows useful information"""
    await show_info(message)

async def callback_info(callback: CallbackQuery):
    """Handler for info button via callback"""
    await callback.answer()  # Answer the callback query
    await show_info(callback.message)

async def show_info(message: types.Message):
    """Display useful information"""
    # Получаем московское время
    moscow_time = get_moscow_time()
    
    text = (
        "ℹ️ *Информация о сервисе Narkoz Team*\n"
        f"⏰ _Время сервера: {moscow_time}_\n\n"
        
        "*О сервисе:*\n"
        "Narkoz Team - команда, которая берёт WhatsApp аккаунты в аренду. "
        "Мы предоставляем профессиональные услуги с гарантией качества.\n\n"
        
        "*Часы работы:*\n"
        "└ Ежедневно: с 9:00 до 20:00 (МСК)\n\n"
        
        "*Правила использования:*\n"
        "├ Добавляйте только подготовленные номера\n"
        "├ Следите за уведомлениями в боте\n"
        "└ Своевременно вводите полученные коды\n\n"
        
        "*Цены на услуги:*\n"
        "1 час - 10$\n"
        "2 часа - 13$\n"
        "3 часа - 16$\n\n"
        "‼️ Есть обьем - есть бонусы!\n\n"
        
        "🔔 _Все уведомления и статусы приходят автоматически_"
    )
    
    # Создаем клавиатуру с полезными ссылками
    buttons = [
        [
            InlineKeyboardButton(text="👼 Тех.Поддержка", url="https://t.me/XRAHITELb")
        ],
        [
            InlineKeyboardButton(text="👥 Группа", url="https://t.me/+j28PRQtxybplMTMy")
        ],
        [
            InlineKeyboardButton(text="🛠️ Разработчик бота", url="https://t.me/Quest_Tag")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="main_menu")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

def register_info_handlers(dp: Dispatcher):
    """Register all info-related handlers"""
    # Commands
    dp.message.register(info_command, Command("info"))
    
    # Callbacks
    dp.callback_query.register(callback_info, F.data == "info")
