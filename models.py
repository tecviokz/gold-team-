import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Инициализируем SQLAlchemy
db = SQLAlchemy(model_class=Base)

class User(Base):
    """Модель для хранения информации о пользователях"""
    __tablename__ = 'users'
    
    id = Column(String(50), primary_key=True)  # Telegram user_id как строка
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    phone_numbers = relationship("PhoneNumber", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.id}>"


class PhoneNumber(Base):
    """Модель для хранения номеров телефонов"""
    __tablename__ = 'phone_numbers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    phone_number = Column(String(20), nullable=False)
    status = Column(String(50), default="waiting")  # waiting, processed, rejected и т.д.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    note = Column(Text, nullable=True)  # Дополнительная информация или примечания
    
    # Отношения
    user = relationship("User", back_populates="phone_numbers")
    details = relationship("PhoneDetails", back_populates="phone_number", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PhoneNumber {self.phone_number} ({self.status})>"


class PhoneDetails(Base):
    """Модель для хранения дополнительных деталей о номере"""
    __tablename__ = 'phone_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number_id = Column(Integer, ForeignKey('phone_numbers.id', ondelete='CASCADE'), nullable=False)
    processed_at = Column(DateTime, nullable=True)  # Время обработки
    processor_id = Column(String(50), nullable=True)  # ID админа, который обработал
    code_sent = Column(Boolean, default=False)  # Был ли отправлен код
    code_accepted = Column(Boolean, nullable=True)  # Принял ли пользователь код
    
    # Отношения
    phone_number = relationship("PhoneNumber", back_populates="details")
    
    def __repr__(self):
        return f"<PhoneDetails for {self.phone_number_id}>"


class Admin(Base):
    """Модель для хранения информации об администраторах"""
    __tablename__ = 'admins'
    
    id = Column(String(50), primary_key=True)  # Telegram user_id как строка
    is_main_admin = Column(Boolean, default=False)  # Является ли главным админом
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Admin {self.id} ({'Main' if self.is_main_admin else 'Regular'})>"


class SystemSetting(Base):
    """Модель для хранения системных настроек"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON, nullable=True)  # Значение может быть любого типа
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemSetting {self.key}>"