from aiogram import Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
    get_admin_menu_keyboard,
    get_back_keyboard,
    get_admin_numbers_keyboard,
    get_work_status_keyboard,
    get_admin_number_actions_keyboard,
    get_admin_confirmation_keyboard,
    get_admins_list_keyboard
)

from storage_db import (
    get_all_numbers,
    update_number_status,
    get_work_status,
    set_work_status,
    get_moderator_status,
    set_moderator_status,
    get_admin_ids,
    add_admin_id,
    remove_admin_id,
    get_user_info,
    save_user_info,
    get_phone_details,
    save_phone_details,
    update_number_status_with_notification
)

from utils import (
    get_status_emoji,
    get_status_text,
    get_status_description,
    format_date,
    notify_user,
    get_moscow_time
)

# Состояния для обработки скриншотов кодов и сообщений
class AdminCodeForm(StatesGroup):
    waiting_for_screenshot = State()
    waiting_for_confirmation = State()

# Состояния для изменения статуса номера
class AdminChangeStatusForm(StatesGroup):
    waiting_for_status = State()
    waiting_for_confirmation = State()

# Обработчик команды /work - проверка прав администратора
async def work_command(message: types.Message):
    """Handler for /work command that gives access to admin panel"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    admin_ids = get_admin_ids()
    
    if str(user_id) in admin_ids or user_id in admin_ids:
        await show_admin_menu(message)
    else:
        await message.answer(
            "❌ *У вас нет доступа к административной панели*\n\n"
            "Обратитесь к главному администратору для получения прав.",
            parse_mode="Markdown"
        )

async def show_admin_menu(message: types.Message):
    """Display the admin panel menu"""
    # Получаем текущие статусы
    work_status = get_work_status()
    work_emoji = "✅" if work_status else "🚫"
    
    moderator_status = get_moderator_status()
    moderator_emoji = "🟢" if moderator_status else "🔴"
    
    # Получаем московское время
    moscow_time = get_moscow_time()
    
    # Общее количество номеров
    all_numbers = get_all_numbers()
    total_users = len(all_numbers)
    total_numbers = sum(len(nums) for nums in all_numbers.values())
    
    waiting_count = len([n for user_nums in all_numbers.values() for n, status in user_nums.items() if status == "waiting"])
    processed_count = len([n for user_nums in all_numbers.values() for n, status in user_nums.items() if status == "processed"])
    rejected_count = len([n for user_nums in all_numbers.values() for n, status in user_nums.items() if status == "rejected"])
    
    # Проверяем, является ли пользователь главным администратором
    from utils import is_main_admin
    user_id = str(message.from_user.id)
    is_user_main_admin = is_main_admin(user_id)
    
    # Получаем общее количество администраторов
    from storage_db import get_admin_ids
    admin_count = len(get_admin_ids())
    
    # Форматируем сообщение администратора
    text = (
        "🔐 *Административная панель Narkoz Team*\n"
        f"⏰ _Время сервера: {moscow_time}_\n\n"
        f"*Статус системы:*\n"
        f"├ Работа: {work_emoji} {'активна' if work_status else 'остановлена'}\n"
        f"└ Модератор: {moderator_emoji} {'в сети' if moderator_status else 'не в сети'}\n\n"
        
        f"*Статистика номеров:*\n"
        f"├ Всего пользователей: {total_users}\n"
        f"├ Всего номеров: {total_numbers}\n"
        f"├ В ожидании: {waiting_count}\n"
        f"├ Обработано: {processed_count}\n"
        f"└ Отклонено: {rejected_count}\n\n"
        
        f"*Персонал:*\n"
        f"└ Администраторов: {admin_count}\n\n"
    )
    
    # Добавляем информацию о статусе прав для главного администратора
    if is_user_main_admin:
        text += "*Ваш статус:*\n└ Главный администратор 👑\n\n"
    
    text += f"*Команды:*\n└ Выберите действие в меню ниже"
    
    # Получаем клавиатуру для админ-меню в соответствии с правами
    keyboard = get_admin_menu_keyboard(is_main_admin=is_user_main_admin)
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_admin_menu(callback: CallbackQuery):
    """Handler for returning to admin menu"""
    await callback.answer()  # Отвечаем на запрос
    await show_admin_menu(callback.message)

async def callback_toggle_work(callback: CallbackQuery):
    """Handler for toggling work status"""
    await callback.answer()  # Отвечаем на запрос
    
    # Получаем текущий статус работы
    current_status = get_work_status()
    
    # Меняем статус на противоположный
    new_status = not current_status
    set_work_status(new_status)
    
    status_text = "запущена" if new_status else "остановлена"
    
    await callback.message.answer(
        f"✅ *Статус работы изменен*\n\n"
        f"Работа {status_text}.",
        parse_mode="Markdown"
    )
    
    # Возвращаемся в меню администратора
    await show_admin_menu(callback.message)

async def callback_toggle_moderator(callback: CallbackQuery):
    """Handler for toggling moderator status"""
    await callback.answer()  # Отвечаем на запрос
    
    # Получаем текущий статус модератора
    current_status = get_moderator_status()
    
    # Меняем статус на противоположный
    new_status = not current_status
    set_moderator_status(new_status)
    
    status_text = "в сети" if new_status else "не в сети"
    
    await callback.message.answer(
        f"✅ *Статус модератора изменен*\n\n"
        f"Модератор {status_text}.",
        parse_mode="Markdown"
    )
    
    # Возвращаемся в меню администратора
    await show_admin_menu(callback.message)

async def callback_admin_numbers(callback: CallbackQuery):
    """Handler for viewing all numbers as admin"""
    await callback.answer()  # Отвечаем на запрос
    
    all_numbers = get_all_numbers()
    
    if not all_numbers:
        await callback.message.answer(
            "📭 *В системе пока нет номеров*",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Получаем московское время
    moscow_time = get_moscow_time()
    
    # Формируем сообщение со всеми номерами
    text = f"📋 *Все номера в системе:*\n⏰ _Обновлено: {moscow_time}_\n\n"
    
    # Получаем клавиатуру для всех номеров
    keyboard = get_admin_numbers_keyboard(all_numbers)
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_number_action(callback: CallbackQuery, state: FSMContext):
    """Handler for selecting an action for a specific number"""
    await callback.answer()  # Отвечаем на запрос
    
    # Извлекаем номер из данных callback
    # Формат данных: "number_action:user_id:phone_number"
    data_parts = callback.data.split(":")
    user_id = data_parts[1]
    phone_number = data_parts[2]
    
    # Сохраняем данные в state
    await state.update_data(user_id=user_id, phone_number=phone_number)
    
    text = (
        f"📱 *Действия с номером:* `{phone_number}`\n\n"
        f"Выберите действие:"
    )
    
    # Клавиатура с действиями для номера
    keyboard = get_admin_number_actions_keyboard(user_id, phone_number)
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_set_status(callback: CallbackQuery, state: FSMContext):
    """Handler for setting status of a number"""
    await callback.answer()  # Отвечаем на запрос
    
    # Извлекаем данные из callback
    # Формат данных: "set_status:user_id:phone_number:new_status"
    data_parts = callback.data.split(":")
    user_id = data_parts[1]
    phone_number = data_parts[2]
    new_status = data_parts[3]
    
    # Получаем эмодзи и текст статуса
    status_emoji = get_status_emoji(new_status)
    status_text = get_status_text(new_status)
    
    # Сохраняем информацию о пользователе, если она отсутствует
    # Это важно при первом взаимодействии с номером
    user_info = get_user_info(user_id)
    if not user_info:
        # Если информация о пользователе отсутствует, сохраняем базовые данные
        save_user_info(user_id, "", "Пользователь", f"ID:{user_id}")
    
    # Обновляем статус номера с сохранением деталей для уведомления
    note = f"Статус изменен администратором {callback.from_user.full_name}"
    update_number_status_with_notification(user_id, phone_number, new_status, note)
    
    # Отправляем уведомление пользователю о смене статуса
    status_description = get_status_description(new_status)
    notification_text = (
        f"📢 *Обновление статуса номера*\n\n"
        f"Телефон: `{phone_number}`\n"
        f"Новый статус: {status_emoji} *{status_text}*\n\n"
        f"{status_description}"
    )
    
    # Асинхронно отправляем уведомление
    bot = callback.bot
    try:
        await notify_user(bot, user_id, notification_text)
        notification_result = "✅ Уведомление отправлено пользователю"
    except Exception as e:
        notification_result = f"❌ Ошибка при отправке уведомления: {str(e)}"
    
    # Сообщаем админу об успешном изменении статуса
    admin_message = (
        f"✅ *Статус номера изменен*\n\n"
        f"Номер: `{phone_number}`\n"
        f"Новый статус: {status_emoji} *{status_text}*\n\n"
        f"{notification_result}"
    )
    
    await callback.message.answer(
        admin_message,
        reply_markup=get_back_keyboard("admin_numbers"),
        parse_mode="Markdown"
    )

async def callback_send_code(callback: CallbackQuery, state: FSMContext):
    """Handler for sending code screenshot to user"""
    await callback.answer()  # Отвечаем на запрос
    
    # Извлекаем данные из callback
    # Формат данных: "send_code:user_id:phone_number"
    data_parts = callback.data.split(":")
    user_id = data_parts[1]
    phone_number = data_parts[2]
    
    # Сохраняем данные в state
    await state.update_data(user_id=user_id, phone_number=phone_number)
    
    # Устанавливаем состояние ожидания скриншота
    await state.set_state(AdminCodeForm.waiting_for_screenshot)
    
    await callback.message.answer(
        f"📤 *Отправка кода для номера* `{phone_number}`\n\n"
        f"Отправьте скриншот с кодом, который будет передан пользователю.",
        reply_markup=get_back_keyboard("admin_menu"),
        parse_mode="Markdown"
    )

async def process_code_screenshot(message: types.Message, state: FSMContext):
    """Process the screenshot with code from admin"""
    # Получаем данные из state
    data = await state.get_data()
    user_id = data.get("user_id")
    phone_number = data.get("phone_number")
    
    # Проверяем, что есть фото или документ
    if not message.photo and not message.document:
        await message.answer(
            "❌ *Скриншот не обнаружен*\n\n"
            "Пожалуйста, отправьте изображение со скриншотом кода.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Сохраняем ID файла (фото или документа)
    file_id = None
    if message.photo:
        # Берем последнее (самое крупное) фото
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith('image/'):
        file_id = message.document.file_id
    
    if not file_id:
        await message.answer(
            "❌ *Формат файла не поддерживается*\n\n"
            "Пожалуйста, отправьте изображение со скриншотом кода.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Сохраняем file_id в state
    await state.update_data(file_id=file_id)
    
    # Запрашиваем подтверждение
    await state.set_state(AdminCodeForm.waiting_for_confirmation)
    
    text = (
        f"⚠️ *Подтверждение отправки кода*\n\n"
        f"Вы собираетесь отправить код для номера `{phone_number}` пользователю.\n\n"
        f"Подтвердите отправку:"
    )
    
    keyboard = get_admin_confirmation_keyboard("send_code")
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_confirm_code_sending(callback: CallbackQuery, state: FSMContext):
    """Handler for confirming code sending"""
    await callback.answer()  # Отвечаем на запрос
    
    # Получаем данные из state
    data = await state.get_data()
    target_user_id = data.get("user_id")
    phone_number = data.get("phone_number")
    file_id = data.get("file_id")
    
    if not all([target_user_id, phone_number, file_id]):
        await callback.message.answer(
            "❌ *Ошибка*\n\n"
            "Не удалось получить все необходимые данные. Попробуйте снова.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        await state.clear()
        return
    
    # Отправляем сообщение пользователю с кодом
    try:
        # Предполагаем, что бот доступен через state (можно передать его другим способом)
        bot = callback.bot
        
        # Создаем кнопки для пользователя: "Буду вводить" и "Не буду вводить"
        user_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Буду вводить", callback_data=f"code_response:yes:{phone_number}"),
                types.InlineKeyboardButton(text="❌ Не буду вводить", callback_data=f"code_response:no:{phone_number}")
            ]
        ])
        
        # Сначала отправляем текст
        user_text = (
            f"📲 *Код для вашего номера*\n\n"
            f"Получен код для номера `{phone_number}`.\n"
            f"Пожалуйста, подтвердите, будете ли вы использовать код:"
        )
        
        await bot.send_message(
            chat_id=target_user_id,
            text=user_text,
            reply_markup=user_keyboard,
            parse_mode="Markdown"
        )
        
        # Затем отправляем фото
        await bot.send_photo(
            chat_id=target_user_id,
            photo=file_id,
            caption=f"Код для номера {phone_number}"
        )
        
        # Обновляем статус номера на "обработан"
        update_number_status(target_user_id, phone_number, "processed")
        
        # Сообщаем админу об успешной отправке
        await callback.message.answer(
            f"✅ *Код успешно отправлен*\n\n"
            f"Скриншот кода для номера `{phone_number}` отправлен пользователю.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        # В случае ошибки
        await callback.message.answer(
            f"❌ *Ошибка при отправке кода*\n\n"
            f"Не удалось отправить код пользователю.\n"
            f"Ошибка: {str(e)}",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
    
    # Очищаем состояние
    await state.clear()

async def callback_cancel_code_sending(callback: CallbackQuery, state: FSMContext):
    """Handler for canceling code sending"""
    await callback.answer()  # Отвечаем на запрос
    
    # Очищаем состояние
    await state.clear()
    
    await callback.message.answer(
        "❌ *Отправка кода отменена*",
        reply_markup=get_back_keyboard("admin_menu"),
        parse_mode="Markdown"
    )

async def callback_code_response(callback: CallbackQuery):
    """Handler for user's response to code"""
    await callback.answer()  # Отвечаем на запрос
    
    # Извлекаем данные из callback
    # Формат данных: "code_response:response:phone_number"
    data_parts = callback.data.split(":")
    response = data_parts[1]  # yes или no
    phone_number = data_parts[2]
    user_id = str(callback.from_user.id)
    
    # Получаем информацию о пользователе
    from storage_db import get_user_info
    user_info = get_user_info(user_id) or {}
    username = user_info.get("username", "")
    first_name = user_info.get("first_name", "Неизвестный пользователь")
    last_name = user_info.get("last_name", "")
    
    # Получаем текущее время
    moscow_time = get_moscow_time()
    
    if response == "yes":
        response_text = "✅ Вы подтвердили, что будете использовать код."
        
        await callback.message.answer(
            f"{response_text}\n\n"
            f"Спасибо за ваш ответ! Успешной работы с номером."
        )
    else:
        response_text = "❌ Вы отказались от использования кода."
        
        # Удаляем номер из очереди
        from storage_db import remove_number_from_queue
        remove_number_from_queue(user_id, phone_number)
        
        # Отправляем уведомление пользователю
        await callback.message.answer(
            f"{response_text}\n\n"
            f"Номер `{phone_number}` был удален из системы.\n"
            f"Спасибо за ваш ответ!"
        )
        
        # Отправляем уведомление всем администраторам
        from storage_db import get_admin_ids
        admin_ids = get_admin_ids()
        
        # Формируем текст уведомления для админов
        admin_notification = (
            f"🚫 *Пользователь отказался от кода*\n\n"
            f"👤 Пользователь: {first_name} {last_name}"
            f"{f' (@{username})' if username else ''}\n"
            f"📱 Номер: `{phone_number}`\n"
            f"⏰ Время: {moscow_time}\n\n"
            f"❗ Номер был автоматически удален из системы."
        )
        
        # Отправляем уведомления всем администраторам
        bot = callback.bot
        for admin_id in admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_notification,
                    parse_mode="Markdown"
                )
            except Exception:
                # Игнорируем ошибки при отправке конкретному администратору
                continue

# Состояния для добавления администратора
class AdminAddAdminForm(StatesGroup):
    waiting_for_user_id = State()

# Обработчики для управления администраторами
async def callback_manage_admins(callback: CallbackQuery):
    """Handler for managing admins"""
    await callback.answer()  # Отвечаем на запрос
    
    # Проверяем, является ли пользователь главным администратором
    from utils import is_main_admin
    user_id = str(callback.from_user.id)
    
    if not is_main_admin(user_id):
        await callback.message.answer(
            "🚫 *Недостаточно прав*\n\n"
            "Только главные администраторы могут управлять списком администраторов.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Получаем список администраторов
    from storage_db import get_admin_ids
    admin_ids = get_admin_ids()
    
    # Получаем московское время
    moscow_time = get_moscow_time()
    
    # Создаем текст сообщения
    text = (
        f"👥 *Управление администраторами*\n"
        f"⏰ _Время сервера: {moscow_time}_\n\n"
        f"*Всего администраторов:* {len(admin_ids)}\n\n"
        f"Выберите действие или администратора для удаления:"
    )
    
    # Получаем клавиатуру с администраторами
    keyboard = get_admins_list_keyboard(admin_ids)
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def callback_add_admin(callback: CallbackQuery, state: FSMContext):
    """Handler for adding a new admin"""
    await callback.answer()  # Отвечаем на запрос
    
    # Проверяем, является ли пользователь главным администратором
    from utils import is_main_admin
    user_id = str(callback.from_user.id)
    
    if not is_main_admin(user_id):
        await callback.message.answer(
            "🚫 *Недостаточно прав*\n\n"
            "Только главные администраторы могут добавлять администраторов.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Устанавливаем состояние ожидания ID пользователя
    await state.set_state(AdminAddAdminForm.waiting_for_user_id)
    
    await callback.message.answer(
        "👤 *Добавление нового администратора*\n\n"
        "Введите ID пользователя Telegram, которого хотите добавить как администратора.\n\n"
        "_Примечание: пользователь должен начать диалог с ботом, чтобы его можно было добавить._",
        reply_markup=get_back_keyboard("admin_menu"),
        parse_mode="Markdown"
    )

async def process_add_admin(message: types.Message, state: FSMContext):
    """Process the admin ID input"""
    # Получаем введенный ID
    new_admin_id = message.text.strip()
    
    # Проверяем, что ID состоит только из цифр
    if not new_admin_id.isdigit():
        await message.answer(
            "❌ *Некорректный формат ID*\n\n"
            "ID пользователя должен состоять только из цифр.\n"
            "Пожалуйста, введите корректный ID:",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Проверяем, не является ли пользователь уже администратором
    from storage_db import get_admin_ids, add_admin_id
    admin_ids = get_admin_ids()
    
    if new_admin_id in admin_ids:
        await message.answer(
            "⚠️ *Пользователь уже является администратором*\n\n"
            "Этот пользователь уже имеет права администратора.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        await state.clear()
        return
    
    # Добавляем нового администратора
    success = add_admin_id(new_admin_id)
    
    if success:
        # Очищаем состояние
        await state.clear()
        
        # Отправляем уведомление новому администратору
        try:
            bot = message.bot
            admin_notification = (
                "🎉 *Поздравляем! Вам предоставлены права администратора*\n\n"
                "Теперь вы можете использовать команду /work для доступа к панели администратора.\n\n"
                "С новыми правами приходит ответственность. Используйте их с умом!"
            )
            
            await bot.send_message(
                chat_id=new_admin_id,
                text=admin_notification,
                parse_mode="Markdown"
            )
            
            notification_status = "✅ Уведомление отправлено новому администратору"
        except Exception:
            notification_status = "⚠️ Не удалось отправить уведомление. Возможно, пользователь не начал диалог с ботом"
        
        # Сообщаем о успешном добавлении
        await message.answer(
            f"✅ *Администратор успешно добавлен*\n\n"
            f"ID: {new_admin_id}\n\n"
            f"{notification_status}",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
    else:
        # В случае ошибки
        await message.answer(
            "❌ *Ошибка при добавлении администратора*\n\n"
            "Не удалось добавить администратора. Пожалуйста, попробуйте ещё раз.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        await state.clear()

async def callback_remove_admin(callback: CallbackQuery):
    """Handler for removing an admin"""
    await callback.answer()  # Отвечаем на запрос
    
    # Проверяем, является ли пользователь главным администратором
    from utils import is_main_admin
    user_id = str(callback.from_user.id)
    
    if not is_main_admin(user_id):
        await callback.message.answer(
            "🚫 *Недостаточно прав*\n\n"
            "Только главные администраторы могут удалять администраторов.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Извлекаем ID администратора для удаления
    # Формат данных: "remove_admin:admin_id"
    admin_id_to_remove = callback.data.split(":")[1]
    
    # Проверяем, не является ли удаляемый администратор главным
    if is_main_admin(admin_id_to_remove):
        await callback.message.answer(
            "🚫 *Невозможно удалить главного администратора*\n\n"
            "Главные администраторы не могут быть удалены через интерфейс бота.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
        return
    
    # Удаляем администратора
    from storage_db import remove_admin_id
    success = remove_admin_id(admin_id_to_remove)
    
    if success:
        # Отправляем уведомление удаленному администратору
        try:
            bot = callback.bot
            notification = (
                "ℹ️ *Изменение прав доступа*\n\n"
                "Ваши права администратора были отозваны.\n"
                "Если вы считаете, что произошла ошибка, свяжитесь с главным администратором."
            )
            
            await bot.send_message(
                chat_id=admin_id_to_remove,
                text=notification,
                parse_mode="Markdown"
            )
            
            notification_status = "✅ Уведомление отправлено бывшему администратору"
        except Exception:
            notification_status = "⚠️ Не удалось отправить уведомление"
        
        # Сообщаем об успешном удалении
        await callback.message.answer(
            f"✅ *Администратор успешно удален*\n\n"
            f"ID: {admin_id_to_remove}\n\n"
            f"{notification_status}",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )
    else:
        # В случае ошибки
        await callback.message.answer(
            "❌ *Ошибка при удалении администратора*\n\n"
            "Не удалось удалить администратора. Возможно, он уже был удален.",
            reply_markup=get_back_keyboard("admin_menu"),
            parse_mode="Markdown"
        )

def register_admin_handlers(dp: Dispatcher):
    """Register all admin-related handlers"""
    # Команды
    dp.message.register(work_command, Command("work"))
    
    # Callback обработчики для админ-меню
    dp.callback_query.register(callback_admin_menu, F.data == "admin_menu")
    dp.callback_query.register(callback_toggle_work, F.data == "toggle_work")
    dp.callback_query.register(callback_toggle_moderator, F.data == "toggle_moderator")
    dp.callback_query.register(callback_admin_numbers, F.data == "admin_numbers")
    
    # Обработчики для управления администраторами
    dp.callback_query.register(callback_manage_admins, F.data == "manage_admins")
    dp.callback_query.register(callback_add_admin, F.data == "add_admin")
    dp.callback_query.register(
        callback_remove_admin,
        F.data.startswith("remove_admin:")
    )
    
    # Обработчик сообщения с ID нового администратора
    dp.message.register(
        process_add_admin,
        AdminAddAdminForm.waiting_for_user_id
    )
    
    # Callback обработчики для работы с номерами
    dp.callback_query.register(
        callback_number_action,
        F.data.startswith("number_action:")
    )
    
    dp.callback_query.register(
        callback_set_status,
        F.data.startswith("set_status:")
    )
    
    dp.callback_query.register(
        callback_send_code,
        F.data.startswith("send_code:")
    )
    
    # Обработчики для подтверждения отправки кода
    dp.callback_query.register(
        callback_confirm_code_sending,
        F.data == "confirm:send_code"
    )
    
    dp.callback_query.register(
        callback_cancel_code_sending,
        F.data == "cancel:send_code"
    )
    
    # Обработчик ответа пользователя на код
    dp.callback_query.register(
        callback_code_response,
        F.data.startswith("code_response:")
    )
    
    # Обработчики сообщений с состояниями
    dp.message.register(
        process_code_screenshot,
        AdminCodeForm.waiting_for_screenshot
    )