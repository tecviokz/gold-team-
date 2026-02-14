"""
Модуль для кэширования часто используемых данных.
Это помогает избежать частых обращений к базе данных.
"""
import time
from typing import Dict, Any, Callable, Optional, TypeVar, List, Tuple

# Тип для кэшируемых значений
T = TypeVar('T')

# Кэш для хранения системных настроек: ключ -> (значение, временная метка)
_settings_cache: Dict[str, Tuple[Any, float]] = {}

# Кэш для хранения списка администраторов: временная метка истечения кэша
_admin_ids_cache: Optional[Tuple[List[str], float]] = None

# Кэш для хранения информации о пользователях: user_id -> (инфо, временная метка)
_user_info_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}

# Время жизни кэша (в секундах)
CACHE_TTL = {
    'settings': 30,      # Настройки кэшируются на 30 секунд
    'admin_ids': 60,     # Список админов кэшируется на 60 секунд
    'user_info': 300,    # Информация о пользователях кэшируется на 5 минут
}

def cached_setting(key: str) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Декоратор для кэширования системных настроек.
    
    Args:
        key: Ключ настройки
        
    Returns:
        Декорированная функция, которая использует кэш
    """
    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        def wrapper() -> T:
            global _settings_cache
            
            # Проверяем наличие значения в кэше и его актуальность
            if key in _settings_cache:
                value, timestamp = _settings_cache[key]
                if time.time() - timestamp < CACHE_TTL['settings']:
                    return value
            
            # Если значения нет в кэше или оно устарело, вызываем оригинальную функцию
            value = func()
            _settings_cache[key] = (value, time.time())
            return value
        
        return wrapper
    
    return decorator

def cached_admin_ids(func: Callable[[], List[str]]) -> Callable[[], List[str]]:
    """
    Декоратор для кэширования списка ID администраторов.
    
    Args:
        func: Функция, которая возвращает список ID администраторов
        
    Returns:
        Декорированная функция, которая использует кэш
    """
    def wrapper() -> List[str]:
        global _admin_ids_cache
        
        # Проверяем наличие списка в кэше и его актуальность
        if _admin_ids_cache:
            admin_ids, timestamp = _admin_ids_cache
            if time.time() - timestamp < CACHE_TTL['admin_ids']:
                return admin_ids
        
        # Если списка нет в кэше или он устарел, вызываем оригинальную функцию
        admin_ids = func()
        _admin_ids_cache = (admin_ids, time.time())
        return admin_ids
    
    return wrapper

def cached_user_info(func: Callable[[str], Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
    """
    Декоратор для кэширования информации о пользователях.
    
    Args:
        func: Функция, которая возвращает информацию о пользователе
        
    Returns:
        Декорированная функция, которая использует кэш
    """
    def wrapper(user_id: str) -> Dict[str, Any]:
        global _user_info_cache
        
        # Проверяем наличие информации в кэше и ее актуальность
        if user_id in _user_info_cache:
            info, timestamp = _user_info_cache[user_id]
            if time.time() - timestamp < CACHE_TTL['user_info']:
                return info
        
        # Если информации нет в кэше или она устарела, вызываем оригинальную функцию
        info = func(user_id)
        _user_info_cache[user_id] = (info, time.time())
        return info
    
    return wrapper

def clear_cache(cache_type: Optional[str] = None):
    """
    Очищает кэш.
    
    Args:
        cache_type: Тип кэша для очистки ('settings', 'admin_ids', 'user_info', None для очистки всего кэша)
    """
    global _settings_cache, _admin_ids_cache, _user_info_cache
    
    if cache_type is None or cache_type == 'settings':
        _settings_cache = {}
    
    if cache_type is None or cache_type == 'admin_ids':
        _admin_ids_cache = None
    
    if cache_type is None or cache_type == 'user_info':
        _user_info_cache = {}

def clear_user_cache(user_id: str):
    """
    Очищает кэш для конкретного пользователя.
    
    Args:
        user_id: ID пользователя
    """
    global _user_info_cache
    
    if user_id in _user_info_cache:
        del _user_info_cache[user_id]