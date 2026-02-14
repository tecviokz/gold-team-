import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Admin, SystemSetting

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL")

# Если URL не задан или это PostgreSQL (который требует пароля), переключаемся на SQLite
if not DATABASE_URL or "neon.tech" in DATABASE_URL:
    # Создаем папку instance если её нет
    if not os.path.exists('instance'):
        os.makedirs('instance')
    DATABASE_URL = "sqlite:///instance/database.db"
    print(f"Using SQLite database at {DATABASE_URL}")

# Создаем движок SQLAlchemy
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Настройки для PostgreSQL (если URL валидный и не Neon)
    engine = create_engine(
        DATABASE_URL, 
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=300
    )

# Создаем фабрику сессий
SessionFactory = sessionmaker(bind=engine)

# Создаем scoped session для потокобезопасности
Session = scoped_session(SessionFactory)

def init_db():
    """Инициализирует базу данных: создает таблицы и добавляет начальные данные"""
    # Создаем все таблицы
    Base.metadata.create_all(engine)
    
    session = Session()
    
    try:
        # Проверяем, есть ли главные администраторы
        main_admin_ids = ["1235561237", "7527380558"]
        
        for admin_id in main_admin_ids:
            existing_admin = session.query(Admin).filter(Admin.id == admin_id).first()
            if not existing_admin:
                # Создаем главного администратора
                admin = Admin(id=admin_id, is_main_admin=True)
                session.add(admin)
                print(f"Создан главный администратор с ID {admin_id}")
        
        # Инициализируем системные настройки
        work_status_setting = session.query(SystemSetting).filter(SystemSetting.key == "work_status").first()
        if not work_status_setting:
            setting = SystemSetting(key="work_status", value=True)
            session.add(setting)
            print("Создана настройка work_status со значением True")
        
        moderator_status_setting = session.query(SystemSetting).filter(SystemSetting.key == "moderator_status").first()
        if not moderator_status_setting:
            setting = SystemSetting(key="moderator_status", value=False)
            session.add(setting)
            print("Создана настройка moderator_status со значением False")
        
        # Сохраняем изменения
        session.commit()
        print("База данных успешно инициализирована")
        
    except Exception as e:
        session.rollback()
        print(f"Ошибка инициализации базы данных: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_db()