from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

# Определение URL базы данных
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/Biomedical_signals"

# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для проверки логина и пароля через подключение к базе данных
def authenticate_user(username, password):
    try:
        # Попытка создания подключения к базе данных с указанными учетными данными
        DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@localhost:5432/Biomedical_signals"
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()  # Проверяем, можно ли установить соединение
        connection.close()
        return True  # Учетные данные верны
    except SQLAlchemyError:
        return False  # Учетные данные неверны

# Функция для получения списка доступных таблиц для пользователя
def get_user_accessible_tables(db_session, username):
    """
    Получает список таблиц, к которым у пользователя есть доступ.
    """
    query = text("""
        SELECT DISTINCT table_name
        FROM information_schema.table_privileges
        WHERE grantee = :username AND privilege_type = 'SELECT'
    """)
    result = db_session.execute(query, {"username": username})
    return [row[0] for row in result]

# Генератор для управления сессиями базы данных
@contextmanager
def get_db():
    """
    Генератор для предоставления сессии базы данных.
    Используется для автоматического закрытия сессии после завершения работы.
    """
    db = SessionLocal()
    try:
        yield db  # Предоставляем сессию для использования
    finally:
        db.close()  # Закрываем сессию после завершения
