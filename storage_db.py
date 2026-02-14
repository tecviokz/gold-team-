import datetime
import json
from typing import Dict, List, Optional, Union, Any
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from models import User, PhoneNumber, PhoneDetails, Admin, SystemSetting
from db_init import Session
from cache import cached_setting, cached_admin_ids, cached_user_info, clear_cache, clear_user_cache

def add_number_to_queue(user_id: Union[int, str], phone_number: str) -> bool:
    """Add a phone number to the queue for a specific user"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Проверяем существование пользователя
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id)
            session.add(user)
            session.flush()
        
        existing_phone = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.phone_number == phone_number)
        ).first()
        
        if existing_phone:
            existing_phone.status = "waiting"
            existing_phone.updated_at = datetime.datetime.utcnow()
        else:
            new_phone = PhoneNumber(
                user_id=user_id,
                phone_number=phone_number,
                status="waiting"
            )
            session.add(new_phone)
            session.add(PhoneDetails(phone_number=new_phone))
        
        session.commit()
        return True
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in add_number_to_queue: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def remove_number_from_queue(user_id: Union[int, str], phone_number: str) -> bool:
    """Remove a phone number from the queue"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Находим запись о номере
        phone = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.phone_number == phone_number)
        ).first()
        
        if phone:
            # Удаляем номер (каскадное удаление сработает для details)
            session.delete(phone)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in remove_number_from_queue: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def get_user_numbers(user_id: Union[int, str]) -> Dict[str, str]:
    """Get all phone numbers in queue for a specific user"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Получаем все номера пользователя
        phones = session.query(PhoneNumber).filter(PhoneNumber.user_id == user_id).all()
        
        # Преобразуем в нужный формат {phone_number: status}
        result = {phone.phone_number: phone.status for phone in phones}
        session.close()
        return result
    except SQLAlchemyError as e:
        print(f"Database error in get_user_numbers: {str(e)}")
        return {}
    finally:
        if session:
            session.close()

def get_user_queue_count(user_id: Union[int, str]) -> int:
    """Get the count of phone numbers in queue for a specific user"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Считаем количество номеров пользователя
        count = session.query(PhoneNumber).filter(PhoneNumber.user_id == user_id).count()
        session.close()
        return count
    except SQLAlchemyError as e:
        print(f"Database error in get_user_queue_count: {str(e)}")
        return 0
    finally:
        if session:
            session.close()

def get_queue_count() -> int:
    """Get the total count of phone numbers in queue across all users"""
    session = None
    try:
        session = Session()
        
        # Считаем общее количество номеров
        count = session.query(PhoneNumber).count()
        session.close()
        return count
    except SQLAlchemyError as e:
        print(f"Database error in get_queue_count: {str(e)}")
        return 0
    finally:
        if session:
            session.close()

@cached_setting("work_status")
def get_work_status() -> bool:
    """Get the current work status"""
    session = None
    try:
        session = Session()
        
        # Получаем значение настройки
        setting = session.query(SystemSetting).filter(SystemSetting.key == "work_status").first()
        
        if setting:
            status = setting.value
        else:
            # Если настройки нет, создаем её
            setting = SystemSetting(key="work_status", value=False)
            session.add(setting)
            session.commit()
            status = False
        
        session.close()
        return bool(status)
    except SQLAlchemyError as e:
        print(f"Database error in get_work_status: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def set_work_status(status: bool) -> bool:
    """Set the work status"""
    session = None
    try:
        session = Session()
        
        # Получаем существующую настройку или создаем новую
        setting = session.query(SystemSetting).filter(SystemSetting.key == "work_status").first()
        
        if setting:
            setting.value = status
        else:
            setting = SystemSetting(key="work_status", value=status)
            session.add(setting)
        
        session.commit()
        
        # Очищаем кэш для этой настройки
        clear_cache('settings')
        
        session.close()
        return True
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in set_work_status: {str(e)}")
        return False
    finally:
        if session:
            session.close()

@cached_setting("moderator_status")
def get_moderator_status() -> bool:
    """Get the current moderator status"""
    session = None
    try:
        session = Session()
        
        # Получаем значение настройки
        setting = session.query(SystemSetting).filter(SystemSetting.key == "moderator_status").first()
        
        if setting:
            status = setting.value
        else:
            # Если настройки нет, создаем её
            setting = SystemSetting(key="moderator_status", value=False)
            session.add(setting)
            session.commit()
            status = False
        
        session.close()
        return bool(status)
    except SQLAlchemyError as e:
        print(f"Database error in get_moderator_status: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def set_moderator_status(status: bool) -> bool:
    """Set the moderator status"""
    session = None
    try:
        session = Session()
        
        # Получаем существующую настройку или создаем новую
        setting = session.query(SystemSetting).filter(SystemSetting.key == "moderator_status").first()
        
        if setting:
            setting.value = status
        else:
            setting = SystemSetting(key="moderator_status", value=status)
            session.add(setting)
        
        session.commit()
        
        # Очищаем кэш для этой настройки
        clear_cache('settings')
        
        session.close()
        return True
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in set_moderator_status: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def get_user_stats(user_id: Union[int, str]) -> Dict[str, int]:
    """Get statistics for a specific user"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Получаем общее количество номеров пользователя
        total_added = session.query(PhoneNumber).filter(PhoneNumber.user_id == user_id).count()
        
        # Количество обработанных номеров
        processed = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.status == "processed")
        ).count()
        
        # Количество отклоненных номеров
        rejected = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.status == "rejected")
        ).count()
        
        session.close()
        return {
            "total_added": total_added,
            "processed": processed,
            "rejected": rejected
        }
    except SQLAlchemyError as e:
        print(f"Database error in get_user_stats: {str(e)}")
        return {"total_added": 0, "processed": 0, "rejected": 0}
    finally:
        if session:
            session.close()

def update_number_status(user_id: Union[int, str], phone_number: str, new_status: str) -> bool:
    """Update the status of a phone number in the queue"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Находим номер
        phone = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.phone_number == phone_number)
        ).first()
        
        if phone:
            # Обновляем статус
            phone.status = new_status
            phone.updated_at = datetime.datetime.utcnow()
            
            # Если статус "processed", обновляем время обработки
            if new_status == "processed" and phone.details:
                phone.details.processed_at = datetime.datetime.utcnow()
            
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in update_number_status: {str(e)}")
        return False
    finally:
        if session:
            session.close()

@cached_admin_ids
def get_admin_ids() -> List[str]:
    """Get the list of admin IDs"""
    session = None
    try:
        session = Session()
        
        # Получаем всех администраторов
        admins = session.query(Admin).all()
        admin_ids = [admin.id for admin in admins]
        
        session.close()
        return admin_ids
    except SQLAlchemyError as e:
        print(f"Database error in get_admin_ids: {str(e)}")
        return []
    finally:
        if session:
            session.close()

def add_admin_id(admin_id: Union[int, str]) -> bool:
    """Add an admin ID to the list"""
    session = None
    try:
        session = Session()
        admin_id = str(admin_id)
        
        # Проверяем, существует ли администратор
        existing_admin = session.query(Admin).filter(Admin.id == admin_id).first()
        
        if not existing_admin:
            # Создаем нового администратора
            admin = Admin(id=admin_id, is_main_admin=False)
            session.add(admin)
            session.commit()
            
            # Очищаем кэш администраторов
            clear_cache('admin_ids')
            
            return True
        return False  # Администратор уже существует
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in add_admin_id: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def remove_admin_id(admin_id: Union[int, str]) -> bool:
    """Remove an admin ID from the list"""
    session = None
    try:
        session = Session()
        admin_id = str(admin_id)
        
        # Находим администратора
        admin = session.query(Admin).filter(Admin.id == admin_id).first()
        
        if admin:
            # Проверяем, не является ли он главным администратором
            if not admin.is_main_admin:
                session.delete(admin)
                session.commit()
                
                # Очищаем кэш администраторов
                clear_cache('admin_ids')
                
                return True
            return False  # Нельзя удалить главного администратора
        return False  # Администратор не найден
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in remove_admin_id: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def get_all_numbers() -> Dict[str, Dict[str, str]]:
    """Get all phone numbers in the system"""
    session = None
    try:
        session = Session()
        
        # Получаем все номера
        phones = session.query(PhoneNumber).all()
        
        # Преобразуем в нужный формат {user_id: {phone_number: status}}
        result = {}
        for phone in phones:
            user_id = phone.user_id
            if user_id not in result:
                result[user_id] = {}
            result[user_id][phone.phone_number] = phone.status
        
        session.close()
        return result
    except SQLAlchemyError as e:
        print(f"Database error in get_all_numbers: {str(e)}")
        return {}
    finally:
        if session:
            session.close()

def save_user_info(user_id: Union[int, str], username: str, first_name: str, last_name: str) -> bool:
    """Save information about a user"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Проверяем существование пользователя
        user = session.query(User).filter(User.id == user_id).first()
        
        if user:
            # Обновляем информацию существующего пользователя
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.updated_at = datetime.datetime.utcnow()
        else:
            # Создаем нового пользователя
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
        
        session.commit()
        
        # Очищаем кэш информации о пользователе
        clear_user_cache(user_id)
        
        return True
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in save_user_info: {str(e)}")
        return False
    finally:
        if session:
            session.close()

@cached_user_info
def get_user_info(user_id: Union[int, str]) -> Dict[str, Any]:
    """Get information about a user"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Получаем пользователя
        user = session.query(User).filter(User.id == user_id).first()
        
        if user:
            # Преобразуем в словарь
            result = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.timestamp() if user.created_at else None
            }
            session.close()
            return result
        session.close()
        return {}
    except SQLAlchemyError as e:
        print(f"Database error in get_user_info: {str(e)}")
        return {}
    finally:
        if session:
            session.close()

def save_phone_details(user_id: Union[int, str], phone_number: str, status: Optional[str] = None, note: Optional[str] = None) -> bool:
    """Save additional details about a phone number"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Находим номер
        phone = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.phone_number == phone_number)
        ).first()
        
        if not phone:
            # Если номер не существует, создаем его
            phone = PhoneNumber(
                user_id=user_id,
                phone_number=phone_number,
                status=status or "waiting"
            )
            session.add(phone)
            session.flush()  # Чтобы получить ID нового номера
            
            # Создаем запись с деталями
            details = PhoneDetails(phone_number=phone)
            session.add(details)
        
        # Если статус указан, обновляем его
        if status:
            phone.status = status
        
        # Если примечание указано, обновляем его
        if note:
            phone.note = note
        
        # Обновляем время изменения
        phone.updated_at = datetime.datetime.utcnow()
        
        session.commit()
        return True
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in save_phone_details: {str(e)}")
        return False
    finally:
        if session:
            session.close()

def get_phone_details(user_id: Union[int, str], phone_number: str) -> Dict[str, Any]:
    """Get additional details about a phone number"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Находим номер
        phone = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.phone_number == phone_number)
        ).first()
        
        if phone:
            # Получаем детали
            result = {
                "status": phone.status,
                "added_at": phone.created_at.timestamp() if phone.created_at else None,
                "updated_at": phone.updated_at.timestamp() if phone.updated_at else None,
                "note": phone.note
            }
            
            # Если есть дополнительные детали, добавляем их
            if phone.details:
                result.update({
                    "processed_at": phone.details.processed_at.timestamp() if phone.details.processed_at else None,
                    "processor_id": phone.details.processor_id,
                    "code_sent": phone.details.code_sent,
                    "code_accepted": phone.details.code_accepted
                })
            
            session.close()
            return result
        
        session.close()
        return {}
    except SQLAlchemyError as e:
        print(f"Database error in get_phone_details: {str(e)}")
        return {}
    finally:
        if session:
            session.close()

def update_number_status_with_notification(user_id: Union[int, str], phone_number: str, new_status: str, note: Optional[str] = None) -> bool:
    """Update the status of a phone number and save details for notification"""
    session = None
    try:
        session = Session()
        user_id = str(user_id)
        
        # Находим номер
        phone = session.query(PhoneNumber).filter(
            and_(PhoneNumber.user_id == user_id, PhoneNumber.phone_number == phone_number)
        ).first()
        
        if phone:
            # Обновляем статус и примечание
            phone.status = new_status
            if note:
                phone.note = note
            
            # Обновляем время
            phone.updated_at = datetime.datetime.utcnow()
            
            # Если статус "processed", обновляем время обработки в деталях
            if new_status == "processed" and phone.details:
                phone.details.processed_at = datetime.datetime.utcnow()
            
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        print(f"Database error in update_number_status_with_notification: {str(e)}")
        return False
    finally:
        if session:
            session.close()

# Функция для инициализации хранилища
def initialize_db_storage():
    """Initialize the database storage if needed"""
    from db_init import init_db
    init_db()