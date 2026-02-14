from typing import Dict, List, Optional, Union
import os
import datetime

def format_phone_number(phone: str) -> str:
    """Format a phone number for display"""
    if not phone:
        return ""
    
    # Basic formatting, can be expanded to include country-specific formats
    if phone.startswith('+'):
        # Just return as is for now
        return phone
    
    # Add '+' if missing
    return f"+{phone}"

def validate_phone_number(phone: str) -> bool:
    """
    Validate a phone number
    
    Simple validation:
    - Should start with '+'
    - Should contain only digits after '+'
    - Should be at least 10 digits long
    """
    if not phone or not isinstance(phone, str):
        return False
    
    if not phone.startswith('+'):
        return False
    
    # Check if everything after '+' is digit
    if not phone[1:].isdigit():
        return False
    
    # Check length (at least 10 digits after '+')
    if len(phone[1:]) < 10:
        return False
    
    return True

def filter_waiting_numbers(numbers: Dict[str, str]) -> Dict[str, str]:
    """Filter numbers to get only those with 'waiting' status"""
    return {num: status for num, status in numbers.items() if status == "waiting"}

def filter_processed_numbers(numbers: Dict[str, str]) -> Dict[str, str]:
    """Filter numbers to get only those with 'processed' status"""
    return {num: status for num, status in numbers.items() if status == "processed"}

def filter_rejected_numbers(numbers: Dict[str, str]) -> Dict[str, str]:
    """Filter numbers to get only those with 'rejected' status"""
    return {num: status for num, status in numbers.items() if status == "rejected"}

def get_status_emoji(status: str) -> str:
    """Return an appropriate emoji for a given status"""
    statuses = {
        "waiting": "⏳",
        "processed": "✅",
        "rejected": "❌",
        "in_progress": "🔄",
        "failed": "🔥",  # Статус "слетел"
        "pending": "⌛",  # В ожидании кода
        "canceled": "🚫",  # Отменён пользователем
        "expired": "⏱️"    # Истек срок действия
    }
    return statuses.get(status, "❓")

def get_status_text(status: str) -> str:
    """Return a formatted text description of a status"""
    statuses = {
        "waiting": "В ожидании",
        "processed": "Обработан",
        "rejected": "Отклонен",
        "in_progress": "В обработке",
        "failed": "Слетел",
        "pending": "Ожидает кода",
        "canceled": "Отменен",
        "expired": "Истек срок"
    }
    return statuses.get(status, "Неизвестно")

def get_status_description(status: str) -> str:
    """Return a detailed description of a status for user notifications"""
    descriptions = {
        "waiting": "Ваш номер находится в очереди на обработку. Пожалуйста, ожидайте.",
        "processed": "Ваш номер был успешно обработан. Проверьте наличие кода.",
        "rejected": "Ваш номер был отклонен. Обратитесь к администратору для получения дополнительной информации.",
        "in_progress": "Ваш номер сейчас обрабатывается. Оставайтесь на связи.",
        "failed": "При обработке вашего номера произошла ошибка. Номер слетел. Свяжитесь с администратором.",
        "pending": "Для вашего номера доступен код. Пожалуйста, проверьте сообщения.",
        "canceled": "Обработка вашего номера была отменена.",
        "expired": "Срок действия вашего номера в очереди истек. Вы можете добавить его повторно."
    }
    return descriptions.get(status, "Статус вашего номера был изменен. Свяжитесь с администратором для получения дополнительной информации.")

def is_admin(user_id: Union[int, str]) -> bool:
    """Check if a user is an admin"""
    from storage_db import get_admin_ids
    # Convert to string for consistency
    user_id = str(user_id)
    return user_id in get_admin_ids()

def is_main_admin(user_id: Union[int, str]) -> bool:
    """Check if a user is a main admin with extended privileges"""
    # Convert to string for consistency
    user_id = str(user_id)
    # Главные администраторы (их ID захардкожены)
    main_admin_ids = ["1235561237", "7527380558"]
    return user_id in main_admin_ids

def format_date(timestamp: Optional[float] = None) -> str:
    """Format a timestamp as a readable date string in Moscow timezone (GMT+3)"""
    if timestamp is None:
        timestamp = datetime.datetime.now().timestamp()
    
    # Создаем смещение для московского времени (GMT+3)
    moscow_timezone = datetime.timezone(datetime.timedelta(hours=3))
    
    # Преобразуем timestamp в UTC, а затем применяем московское смещение
    date = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).astimezone(moscow_timezone)
    
    # Форматируем дату с указанием часового пояса
    return date.strftime("%d.%m.%Y %H:%M:%S (MSK)")

# Функция для получения текущего времени в Москве
def get_moscow_time() -> str:
    """Получить текущее время в Москве в форматированном виде"""
    moscow_timezone = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(moscow_timezone)
    return now.strftime("%H:%M:%S (MSK)")

# Функция для уведомления пользователя через бота вместо SMS
async def notify_user(bot, user_id: Union[int, str], message: str) -> bool:
    """
    Отправить уведомление пользователю через бота
    
    Returns:
        bool: True если успешно, False в противном случае
    """
    try:
        user_id = str(user_id)
        # Добавляем текущее московское время к сообщению
        moscow_time = get_moscow_time()
        message_with_time = f"{message}\n\n_Время отправки: {moscow_time}_"
        
        await bot.send_message(
            chat_id=user_id,
            text=message_with_time,
            parse_mode="Markdown"
        )
        print(f"Уведомление отправлено пользователю {user_id}")
        return True
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")
        return False

async def notify_admins(bot, message: str) -> list:
    """
    Отправить уведомление всем администраторам через бота
    
    Returns:
        list: Список ID администраторов, которым успешно было отправлено сообщение
    """
    from storage_db import get_admin_ids
    admin_ids = get_admin_ids()
    
    # Список администраторов, которым успешно отправлено сообщение
    notified_admins = []
    
    for admin_id in admin_ids:
        try:
            # Добавляем текущее московское время к сообщению
            moscow_time = get_moscow_time()
            message_with_time = f"{message}\n\n_Время отправки: {moscow_time}_"
            
            await bot.send_message(
                chat_id=admin_id, 
                text=message_with_time, 
                parse_mode="Markdown"
            )
            notified_admins.append(admin_id)
            print(f"Уведомление отправлено администратору {admin_id}")
        except Exception as e:
            print(f"Ошибка при отправке уведомления администратору {admin_id}: {str(e)}")
    
    return notified_admins
