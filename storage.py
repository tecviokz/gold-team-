# In-memory storage for the bot
# In a production environment, you would use a database

# Store phone numbers in queue by user_id
# Format: {user_id: {phone_number: status}}
phone_queue = {}

# Store statistics by user_id
# Format: {user_id: {total_added: int, processed: int, rejected: int}}
user_stats = {}

# Store user information
# Format: {user_id: {username: str, first_name: str, last_name: str, added_date: timestamp}}
user_info = {}

# Store additional information about phone numbers
# Format: {user_id: {phone_number: {status: str, added_at: timestamp, processed_at: timestamp, note: str}}}
phone_details = {}

# Global bot status
work_status = False  # Whether work is active
moderator_status = False  # Whether moderator is online

# Admin IDs - пользователи с правами администратора
# Реальные ID администраторов
admin_ids = ["1925179708", "8401265081"]

def initialize_storage():
    """Initialize the storage with default values"""
    global work_status, moderator_status, admin_ids
    work_status = True  # Начинаем с активным статусом работы
    moderator_status = True  # Начинаем с активным статусом модератора
    
    # Убедимся, что указаны правильные ID администраторов
    if not ("8401265081" in admin_ids and "1925179708" in admin_ids):
        # Сбросим список и добавим нужные ID
        admin_ids = ["1925179708", "8401265081"]

# Queue management functions
def add_number_to_queue(user_id, phone_number):
    """Add a phone number to the queue for a specific user"""
    if user_id not in phone_queue:
        phone_queue[user_id] = {}
    
    # Add the number with 'waiting' status
    phone_queue[user_id][phone_number] = "waiting"
    
    # Update statistics
    if user_id not in user_stats:
        user_stats[user_id] = {"total_added": 0, "processed": 0, "rejected": 0}
    
    user_stats[user_id]["total_added"] += 1

def remove_number_from_queue(user_id, phone_number):
    """Remove a phone number from the queue"""
    if user_id in phone_queue and phone_number in phone_queue[user_id]:
        del phone_queue[user_id][phone_number]

def get_user_numbers(user_id):
    """Get all phone numbers in queue for a specific user"""
    return phone_queue.get(user_id, {})

def get_user_queue_count(user_id):
    """Get the count of phone numbers in queue for a specific user"""
    return len(get_user_numbers(user_id))

def get_queue_count():
    """Get the total count of phone numbers in queue across all users"""
    total = 0
    for user_numbers in phone_queue.values():
        total += len(user_numbers)
    return total

# Status functions
def get_work_status():
    """Get the current work status"""
    return work_status

def set_work_status(status):
    """Set the work status"""
    global work_status
    work_status = status

def get_moderator_status():
    """Get the current moderator status"""
    return moderator_status

def set_moderator_status(status):
    """Set the moderator status"""
    global moderator_status
    moderator_status = status

# Statistics functions
def get_user_stats(user_id):
    """Get statistics for a specific user"""
    if user_id not in user_stats:
        user_stats[user_id] = {"total_added": 0, "processed": 0, "rejected": 0}
    
    # Calculate in_queue from phone_queue
    in_queue = get_user_queue_count(user_id)
    
    # Add in_queue to returned stats
    stats = user_stats[user_id].copy()
    stats["in_queue"] = in_queue
    
    return stats

def update_number_status(user_id, phone_number, new_status):
    """Update the status of a phone number in the queue"""
    # Преобразуем пользовательский ID в строку для консистентности
    user_id = str(user_id)
    
    if user_id in phone_queue and phone_number in phone_queue[user_id]:
        if new_status == "processed":
            # Обновляем статистику перед удалением
            if user_id not in user_stats:
                user_stats[user_id] = {"total_added": 1, "processed": 0, "rejected": 0}
            user_stats[user_id]["processed"] += 1
            # Просто меняем статус вместо удаления
            phone_queue[user_id][phone_number] = new_status
        elif new_status == "rejected":
            # Обновляем статистику перед удалением
            if user_id not in user_stats:
                user_stats[user_id] = {"total_added": 1, "processed": 0, "rejected": 0}
            user_stats[user_id]["rejected"] += 1
            # Просто меняем статус вместо удаления
            phone_queue[user_id][phone_number] = new_status
        else:
            # Просто обновляем статус
            phone_queue[user_id][phone_number] = new_status
    
# Функции для работы с администраторами
def get_admin_ids():
    """Get the list of admin IDs"""
    global admin_ids
    return admin_ids

def add_admin_id(admin_id):
    """Add an admin ID to the list"""
    global admin_ids
    # Преобразуем admin_id в строку для консистентности
    admin_id = str(admin_id)
    if admin_id not in admin_ids:
        admin_ids.append(admin_id)
    return True

def remove_admin_id(admin_id):
    """Remove an admin ID from the list"""
    global admin_ids
    # Преобразуем admin_id в строку для консистентности
    admin_id = str(admin_id)
    if admin_id in admin_ids:
        admin_ids.remove(admin_id)
        return True
    return False

def get_all_numbers():
    """Get all phone numbers in the system"""
    return phone_queue

# Функции для работы с информацией о пользователях
def save_user_info(user_id, username, first_name, last_name):
    """Save information about a user"""
    global user_info
    user_id = str(user_id)
    
    import time
    current_time = time.time()
    
    # Обновляем или создаем запись пользователя
    if user_id not in user_info:
        user_info[user_id] = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "added_date": current_time
        }
    else:
        # Только обновляем информацию, не меняя дату добавления
        user_info[user_id].update({
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        })
        
def get_user_info(user_id):
    """Get information about a user"""
    user_id = str(user_id)
    return user_info.get(user_id, {})

# Функции для работы с дополнительной информацией о номерах
def save_phone_details(user_id, phone_number, status=None, note=None):
    """Save additional details about a phone number"""
    global phone_details
    user_id = str(user_id)
    
    import time
    current_time = time.time()
    
    # Создаем структуру, если она не существует
    if user_id not in phone_details:
        phone_details[user_id] = {}
    
    # Создаем или обновляем информацию о номере
    if phone_number not in phone_details[user_id]:
        phone_details[user_id][phone_number] = {
            "status": status or "waiting",
            "added_at": current_time,
            "processed_at": None,
            "note": note or ""
        }
    else:
        # Обновляем существующую информацию
        if status:
            phone_details[user_id][phone_number]["status"] = status
            if status in ["processed", "rejected", "failed"]:
                phone_details[user_id][phone_number]["processed_at"] = current_time
        
        if note is not None:  # Позволяет установить пустую заметку
            phone_details[user_id][phone_number]["note"] = note

def get_phone_details(user_id, phone_number):
    """Get additional details about a phone number"""
    user_id = str(user_id)
    
    if user_id in phone_details and phone_number in phone_details[user_id]:
        return phone_details[user_id][phone_number]
    
    # Возвращаем структуру по умолчанию, если нет информации
    import time
    return {
        "status": "waiting",
        "added_at": time.time(),
        "processed_at": None,
        "note": ""
    }

def update_number_status_with_notification(user_id, phone_number, new_status, note=None):
    """Update the status of a phone number and save details for notification"""
    user_id = str(user_id)
    
    # Обновляем статус в основной структуре
    update_number_status(user_id, phone_number, new_status)
    
    # Сохраняем детали для уведомления
    save_phone_details(user_id, phone_number, status=new_status, note=note)
    
    # Возвращаем True, если номер существует и был обновлен
    return user_id in phone_queue and phone_number in phone_queue[user_id]
