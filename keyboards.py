from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📱 Номера", callback_data="numbers")],
        [InlineKeyboardButton(text="📢 Группа", callback_data="group")],
        [InlineKeyboardButton(text="💸 Прайсы", callback_data="prices")],
        [InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")]
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_numbers_menu_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for the numbers menu"""
    buttons = [
        [
            InlineKeyboardButton(text="➕ Добавить", callback_data="add_number"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data="delete_number")
        ],
        [
            InlineKeyboardButton(text="📝 Очередь", callback_data="show_queue"),
            InlineKeyboardButton(text="🌐 Статистика", callback_data="show_stats")
        ],
        [InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="main_menu")]
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_back_keyboard(back_to: str) -> InlineKeyboardMarkup:
    """Create a keyboard with only a back button"""
    # The back_to parameter determines where the back button will go
    text = "⬅️ Назад"
    if back_to == "main_menu":
        text += " в главное меню"
    elif back_to == "numbers_menu":
        text += " в меню номеров"
    elif back_to == "admin_menu":
        text += " в меню администратора"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=back_to)]
    ])
    
    return keyboard

def get_my_numbers_keyboard(numbers: dict) -> InlineKeyboardMarkup:
    """Create a keyboard showing user's numbers"""
    buttons = []
    
    # Add a button for each number
    for number, status in numbers.items():
        status_emoji = "⏳" if status == "waiting" else "✅"
        buttons.append([
            InlineKeyboardButton(text=f"{number} - {status_emoji}", callback_data=f"number_info:{number}")
        ])
    
    # Back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="numbers_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_delete_numbers_keyboard(numbers: dict) -> InlineKeyboardMarkup:
    """Create a keyboard for deleting numbers"""
    buttons = []
    
    # Add a button for each number
    for number in numbers:
        buttons.append([
            InlineKeyboardButton(text=f"🗑️ {number}", callback_data=f"delete_number:{number}")
        ])
    
    # Back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="numbers_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Клавиатуры для административной панели

def get_admin_menu_keyboard(is_main_admin=False) -> InlineKeyboardMarkup:
    """Create keyboard for admin menu"""
    buttons = [
        [
            InlineKeyboardButton(text="📱 Номера", callback_data="admin_numbers"),
            InlineKeyboardButton(text="📊 Статус работы", callback_data="toggle_work")
        ],
        [
            InlineKeyboardButton(text="👨‍💼 Статус модератора", callback_data="toggle_moderator")
        ]
    ]
    
    # Добавляем кнопку управления администраторами только для главных администраторов
    if is_main_admin:
        buttons.append([
            InlineKeyboardButton(text="👥 Управление администраторами", callback_data="manage_admins")
        ])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="main_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_admins_list_keyboard(admin_ids: list) -> InlineKeyboardMarkup:
    """Создает клавиатуру со списком всех администраторов"""
    buttons = []
    
    # Получаем информацию о пользователях
    from storage_db import get_user_info
    from utils import is_main_admin
    
    # Добавляем кнопку для каждого администратора
    for admin_id in admin_ids:
        # Получаем информацию о пользователе
        user_info = get_user_info(admin_id) or {}
        username = user_info.get("username", "")
        first_name = user_info.get("first_name", "")
        last_name = user_info.get("last_name", "")
        
        # Формируем имя для отображения
        display_name = f"{first_name} {last_name}"
        if username:
            display_name += f" (@{username})"
        elif not display_name.strip():
            display_name = f"ID: {admin_id}"
            
        # Добавляем метку главного администратора
        if is_main_admin(admin_id):
            display_name += " 👑"
            
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ {display_name}", 
                callback_data=f"remove_admin:{admin_id}"
            )
        ])
    
    # Добавляем кнопку для добавления нового админа
    buttons.append([
        InlineKeyboardButton(text="➕ Добавить администратора", callback_data="add_admin")
    ])
    
    # Добавляем кнопку возврата
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад в меню администратора", callback_data="admin_menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_admin_numbers_keyboard(numbers_dict: dict) -> InlineKeyboardMarkup:
    """Create a keyboard showing all numbers for admin"""
    buttons = []
    
    # Импортируем функцию для получения эмодзи статуса
    from utils import get_status_emoji, get_status_text
    
    # Flatten the dictionary of dictionaries
    # numbers_dict format: {user_id: {phone_number: status}}
    for user_id, numbers in numbers_dict.items():
        for number, status in numbers.items():
            status_emoji = get_status_emoji(status)
            status_short_text = get_status_text(status)
            
            # Получаем информацию о пользователе
            from storage_db import get_user_info
            user_info = get_user_info(user_id)
            username = user_info.get("username", "")
            user_mention = f"@{username}" if username else f"ID:{user_id}"
            
            buttons.append([
                InlineKeyboardButton(
                    text=f"{number} - {status_emoji} {status_short_text} ({user_mention})",
                    callback_data=f"number_action:{user_id}:{number}"
                )
            ])
    
    # Back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад в меню администратора", callback_data="admin_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_work_status_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for changing work status"""
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Включить", callback_data="work_status:on"),
            InlineKeyboardButton(text="🔴 Выключить", callback_data="work_status:off")
        ],
        [InlineKeyboardButton(text="⬅️ Назад в меню администратора", callback_data="admin_menu")]
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_admin_number_actions_keyboard(user_id: str, phone_number: str) -> InlineKeyboardMarkup:
    """Create keyboard for admin actions with a specific number"""
    # Импортируем функции для получения информации о пользователе
    from storage_db import get_user_info, get_phone_details
    from utils import format_date
    
    # Получаем информацию о пользователе
    user_info = get_user_info(user_id)
    phone_details = get_phone_details(user_id, phone_number)
    
    # Формируем заголовок с информацией о пользователе
    user_header = []
    
    # Добавляем кнопку с информацией о пользователе (не активная, только для отображения)
    username = user_info.get("username", "")
    first_name = user_info.get("first_name", "")
    last_name = user_info.get("last_name", "")
    user_display = f"👤 Пользователь: {first_name} {last_name}"
    if username:
        user_display += f" (@{username})"
    
    # Добавляем информацию о номере
    status = phone_details.get("status", "waiting")
    added_at = phone_details.get("added_at")
    added_date = format_date(added_at) if added_at else "неизвестно"
    
    # Кнопки действий
    buttons = [
        # Информация о пользователе - неактивная кнопка
        [InlineKeyboardButton(text=user_display, callback_data="no_action")],
        [InlineKeyboardButton(text=f"📱 Номер добавлен: {added_date}", callback_data="no_action")],
        
        # Разделитель
        [InlineKeyboardButton(text="⎯⎯⎯ Изменить статус ⎯⎯⎯", callback_data="no_action")],
        
        # Основные статусы
        [
            InlineKeyboardButton(
                text="✅ Обработан", 
                callback_data=f"set_status:{user_id}:{phone_number}:processed"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отклонен", 
                callback_data=f"set_status:{user_id}:{phone_number}:rejected"
            )
        ],
        [
            InlineKeyboardButton(
                text="⏳ В ожидании", 
                callback_data=f"set_status:{user_id}:{phone_number}:waiting"
            )
        ],
        
        # Дополнительные статусы
        [
            InlineKeyboardButton(
                text="🔥 Слетел", 
                callback_data=f"set_status:{user_id}:{phone_number}:failed"
            )
        ],
        [
            InlineKeyboardButton(
                text="⌛ Ожидает кода", 
                callback_data=f"set_status:{user_id}:{phone_number}:pending"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫 Отменен", 
                callback_data=f"set_status:{user_id}:{phone_number}:canceled"
            )
        ],
        
        # Действия
        [InlineKeyboardButton(text="⎯⎯⎯ Действия ⎯⎯⎯", callback_data="no_action")],
        [
            InlineKeyboardButton(
                text="📤 Отправить код", 
                callback_data=f"send_code:{user_id}:{phone_number}"
            )
        ],
        [InlineKeyboardButton(text="⬅️ Назад к списку номеров", callback_data="admin_numbers")]
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_admin_confirmation_keyboard(action_type: str) -> InlineKeyboardMarkup:
    """Create keyboard for admin confirmations"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm:{action_type}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel:{action_type}")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
