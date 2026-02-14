from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from keyboards import (
    get_numbers_menu_keyboard,
    get_back_keyboard,
    get_my_numbers_keyboard,
    get_delete_numbers_keyboard
)
from storage_db import (
    add_number_to_queue,
    remove_number_from_queue,
    get_user_numbers,
    get_user_stats
)
from utils import validate_phone_number, format_phone_number, get_moscow_time

# Define states for adding a number
class AddNumberForm(StatesGroup):
    waiting_for_number = State()

async def callback_numbers_menu(callback: CallbackQuery):
    """Handler for the Numbers button in main menu"""
    await callback.answer()  # Answer the callback query
    
    # Проверяем статус работы
    from storage_db import get_work_status
    work_status = get_work_status()
    
    # Если работа не активна, то блокируем доступ к функционалу
    if not work_status:
        # Получаем московское время
        moscow_time = get_moscow_time()
        
        await callback.message.answer(
            "🚫 *Работа сейчас не активна*\n\n"
            f"⏰ Время проверки: {moscow_time}\n\n"
            "На данный момент использование бота невозможно. "
            "Пожалуйста, попробуйте позже или свяжитесь с администратором.\n\n"
            "Когда работа будет активирована, вы сможете добавлять номера и использовать все функции бота.",
            reply_markup=get_back_keyboard("main_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Получаем информацию о пользователе
    user_id = str(callback.from_user.id)  # Преобразуем ID в строку
    
    # Получаем статистику пользователя
    from storage_db import get_user_stats
    stats = get_user_stats(user_id)
    
    # Динамически формируем текст на основе статистики
    active_queue = stats['in_queue'] if 'in_queue' in stats else 0
    queue_info = f"\n*Ваши номера:*\n└ {active_queue} номер(ов) в очереди" if active_queue > 0 else ""
    
    text = (
        "📱 *Управление номерами*\n\n"
        "*❗ Важные рекомендации:*\n"
        "├ Прогревайте номера перед добавлением в очередь\n"
        "├ Новые номера могут проработать менее 30 минут\n"
        "├ Регулярно проверяйте статус в разделе «Очередь»\n"
        "└ При любых проблемах обращайтесь к модератору\n\n"
        "*📊 Статистика обработки:*\n"
        "├ Среднее время ожидания: ~15-20 минут\n"
        "├ Успешность обработки: 97%\n"
        f"└ Приоритет для постоянных клиентов{queue_info}\n\n"
        "Выберите нужное действие в меню ниже:"
    )
    
    # Get the keyboard for numbers menu
    keyboard = get_numbers_menu_keyboard()
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_add_number(callback: CallbackQuery, state: FSMContext):
    """Handler for the Add Number button in numbers menu"""
    await callback.answer()  # Answer the callback query
    
    # Проверяем статус работы
    from storage_db import get_work_status
    work_status = get_work_status()
    
    # Если работа не активна, то блокируем доступ к функционалу
    if not work_status:
        # Получаем московское время
        moscow_time = get_moscow_time()
        
        await callback.message.answer(
            "🚫 *Работа сейчас не активна*\n\n"
            f"⏰ Время проверки: {moscow_time}\n\n"
            "На данный момент использование бота невозможно. "
            "Пожалуйста, попробуйте позже или свяжитесь с администратором.",
            reply_markup=get_back_keyboard("main_menu"),
            parse_mode="Markdown"
        )
        return
    
    text = (
        "📞 *Добавление номера в очередь*\n\n"
        "*Укажите номер телефона в международном формате:*\n"
        "└ Пример: `+79998887766`\n\n"
        "*Рекомендации:*\n"
        "├ Используйте только активные номера\n"
        "├ Убедитесь, что номер прогрет\n"
        "└ Номер должен начинаться с '+' и содержать только цифры\n\n"
        "Введите номер телефона сейчас:"
    )
    
    # Set state to waiting for number input
    await state.set_state(AddNumberForm.waiting_for_number)
    
    # Get back keyboard
    keyboard = get_back_keyboard("numbers_menu")
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def process_add_number(message: types.Message, state: FSMContext):
    """Process the number input when adding a number"""
    user_id = str(message.from_user.id)
    phone_number = message.text.strip()
    
    # Используем validate_phone_number для проверки номера
    if not validate_phone_number(phone_number):
        await message.answer(
            "❌ *Некорректный формат номера*\n\n"
            "Номер должен:\n"
            "• Начинаться со знака '+'\n"
            "• Содержать не менее 10 цифр\n"
            "• Содержать только цифры после '+'\n\n"
            "Пример: `+79998887766`\n\n"
            "Пожалуйста, введите номер еще раз:",
            reply_markup=get_back_keyboard("numbers_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Форматируем номер перед добавлением
    phone_number = format_phone_number(phone_number)
    
    # Сохраняем информацию о пользователе
    from storage_db import save_user_info, save_phone_details
    
    # Получаем информацию о пользователе из сообщения
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    
    # Сохраняем информацию о пользователе
    save_user_info(user_id, username, first_name, last_name)
    
    # Add number to queue
    add_number_to_queue(user_id, phone_number)
    
    # Сохраняем дополнительную информацию о номере
    save_phone_details(
        user_id, 
        phone_number, 
        status="waiting", 
        note=f"Добавлен пользователем {first_name} {last_name}"
    )
    
    # Clear state
    await state.clear()
    
    await message.answer(
        f"✅ *Номер успешно добавлен!*\n\n"
        f"Телефон `{phone_number}` добавлен в очередь на обработку.\n\n"
        f"• Текущий статус: *В ожидании*\n"
        f"• Примерное время обработки: 10-15 минут\n\n"
        f"Вы можете отслеживать статус в разделе «📝 Очередь»",
        reply_markup=get_numbers_menu_keyboard(),
        parse_mode="Markdown"
    )

async def callback_delete_number(callback: CallbackQuery):
    """Handler for the Delete Number button in numbers menu"""
    await callback.answer()  # Answer the callback query
    
    user_id = str(callback.from_user.id)  # Преобразуем ID в строку
    user_numbers = get_user_numbers(user_id)
    
    if not user_numbers:
        await callback.message.answer(
            "📭 *У вас нет номеров в очереди*\n\n"
            "Сначала добавьте номер через меню «➕ Добавить»",
            reply_markup=get_back_keyboard("numbers_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Выведем список номеров в сообщении
    numbers_list = ""
    for i, (number, status) in enumerate(user_numbers.items(), 1):
        status_emoji = "⏳" if status == "waiting" else "✅" if status == "processed" else "❌"
        numbers_list += f"{i}. `{number}` {status_emoji}\n"
    
    text = (
        "🗑️ *Удаление номера из очереди*\n\n"
        f"У вас {len(user_numbers)} номер(ов) в системе:\n"
        f"{numbers_list}\n"
        "Выберите номер, который хотите удалить:\n\n"
        "⚠️ *Внимание!* Это действие нельзя отменить. "
        "Если вы удалите номер, его придется добавлять заново."
    )
    
    # Get keyboard with user's numbers
    keyboard = get_delete_numbers_keyboard(user_numbers)
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_delete_specific_number(callback: CallbackQuery):
    """Handler for deleting a specific number"""
    await callback.answer()  # Answer the callback query
    
    # Extract the number from callback data
    # Format of callback data: "delete_number:+79998887766"
    phone_number = callback.data.split(':')[1]
    user_id = str(callback.from_user.id)  # Преобразуем ID в строку
    
    # Remove the number from queue
    remove_number_from_queue(user_id, phone_number)
    
    await callback.message.answer(
        f"✅ *Номер успешно удален!*\n\n"
        f"Телефон `{phone_number}` был удален из очереди.\n\n"
        f"Вы всегда можете добавить новые номера через кнопку «➕ Добавить»",
        reply_markup=get_numbers_menu_keyboard(),
        parse_mode="Markdown"
    )

async def callback_show_queue(callback: CallbackQuery):
    """Handler for showing the user's numbers in queue"""
    await callback.answer()  # Answer the callback query
    
    user_id = str(callback.from_user.id)  # Преобразуем ID в строку
    user_numbers = get_user_numbers(user_id)
    
    if not user_numbers:
        await callback.message.answer(
            "📭 *У вас пока нет номеров в очереди*\n\nДобавьте номер с помощью кнопки «➕ Добавить»",
            reply_markup=get_back_keyboard("numbers_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Импортируем функции для статусов
    from utils import get_status_emoji, get_status_text
    
    # Получаем текущее время по Москве
    moscow_time = get_moscow_time()
    
    # Format the text with all numbers and statuses
    text = f"📋 *Отчет по вашим номерам*\n⏰ _Обновлено: {moscow_time}_\n\n"
    
    # Счетчики для разных статусов
    waiting_count = 0
    processed_count = 0
    rejected_count = 0
    failed_count = 0
    other_count = 0
    
    # Импортируем функцию для получения деталей номера
    from storage_db import get_phone_details
    
    for i, (number, status) in enumerate(user_numbers.items(), 1):
        # Получаем эмодзи и текст статуса
        status_emoji = get_status_emoji(status)
        status_text = get_status_text(status)
        
        # Получаем дополнительную информацию
        details = get_phone_details(user_id, number)
        
        # Форматируем время добавления, если есть
        added_info = ""
        if details.get("added_at"):
            from utils import format_date
            added_date = format_date(details["added_at"])
            added_info = f" • {added_date}"
        
        # Форматируем заметку, если есть
        note_info = ""
        if details.get("note"):
            note = details["note"]
            if len(note) > 30:
                note = note[:27] + "..."
            note_info = f"\n   _Заметка: {note}_"
        
        # Добавляем информацию о номере
        text += f"{i}. `{number}` — {status_emoji} *{status_text}*{added_info}{note_info}\n"
        
        # Увеличиваем соответствующий счетчик
        if status == "waiting":
            waiting_count += 1
        elif status == "processed":
            processed_count += 1
        elif status == "rejected":
            rejected_count += 1
        elif status == "failed":
            failed_count += 1
        else:
            other_count += 1
    
    # Add summary
    text += f"\n*Сводка:*\n"
    text += f"├ В ожидании: {waiting_count} номеров\n"
    text += f"├ Обработано: {processed_count} номеров\n"
    if rejected_count > 0:
        text += f"├ Отклонено: {rejected_count} номеров\n"
    if failed_count > 0:
        text += f"├ Слетело: {failed_count} номеров\n"
    if other_count > 0:
        text += f"└ Другие статусы: {other_count} номеров\n"
    else:
        text = text.replace("├ Обработано", "└ Обработано")
    
    if waiting_count > 0:
        text += "\n⚠️ _Оставайтесь в чате для получения уведомлений о статусе ваших номеров_"
    
    # Get back keyboard
    keyboard = get_back_keyboard("numbers_menu")
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_show_stats(callback: CallbackQuery):
    """Handler for showing user statistics"""
    await callback.answer()  # Answer the callback query
    
    user_id = str(callback.from_user.id)  # Преобразуем ID в строку
    stats = get_user_stats(user_id)
    
    # Получаем текущее время по Москве
    moscow_time = get_moscow_time()
    
    text = (
        "📊 *Статистика обработки номеров*\n"
        f"⏰ _Данные на {moscow_time}_\n\n"
        "*Общие показатели:*\n"
        f"├ Всего добавлено: {stats['total_added']} номеров\n"
        f"├ Успешно обработано: {stats['processed']} номеров\n"
        f"├ Отклонено/отменено: {stats['rejected']} номеров\n"
        f"└ Текущая очередь: {stats['in_queue']} номеров\n\n"
    )
    
    # Добавим расчетные показатели
    if stats['total_added'] > 0:
        success_rate = round((stats['processed'] / stats['total_added']) * 100, 1)
        text += (
            f"*Эффективность:*\n"
            f"└ Успешность обработки: {success_rate}%\n\n"
        )
    
    if stats['in_queue'] > 0:
        text += (
            "*Прогноз обработки:*\n"
            f"└ Приблизительное время ожидания: ~{stats['in_queue'] * 10} минут\n\n"
        )
        
    text += (
        "_Статистика обновляется в режиме реального времени_"
    )
    
    # Get back keyboard
    keyboard = get_back_keyboard("numbers_menu")
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_back_to_numbers(callback: CallbackQuery, state: FSMContext):
    """Handler for going back to numbers menu"""
    await callback.answer()  # Answer the callback query
    
    # Clear any ongoing state
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    
    # Return to numbers menu
    await callback_numbers_menu(callback)

def register_numbers_handlers(dp: Dispatcher):
    """Register all numbers-related handlers"""
    # Callback handlers
    dp.callback_query.register(callback_numbers_menu, F.data == "numbers")
    dp.callback_query.register(callback_add_number, F.data == "add_number")
    dp.callback_query.register(callback_delete_number, F.data == "delete_number")
    dp.callback_query.register(callback_show_queue, F.data == "show_queue")
    dp.callback_query.register(callback_show_stats, F.data == "show_stats")
    dp.callback_query.register(callback_back_to_numbers, F.data == "numbers_menu")
    
    # Register handler for deleting specific numbers
    dp.callback_query.register(
        callback_delete_specific_number,
        F.data.startswith("delete_number:")
    )
    
    # Message handlers (with states)
    dp.message.register(
        process_add_number,
        AddNumberForm.waiting_for_number
    )
