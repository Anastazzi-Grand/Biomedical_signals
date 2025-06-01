from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


# Определение URL базы данных
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/Biomedical_signals"

# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Функция для проверки логина и пароля через подключение к базе данных
def authenticate_user(username, password):
    try:
        DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@localhost:5432/Biomedical_signals"
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()  # Проверяем подключение
        connection.close()

        # Создаем новую фабрику сессий для текущего движка
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = Session()
        return session
    except Exception as e:
        print(f"Ошибка при подключении к базе данных для пользователя {username}: {e}")
        return None


# Функция для получения списка доступных таблиц для пользователя
def get_user_accessible_tables(db_session, username):
    try:
        if not db_session or not db_session.is_active:
            print("Сессия базы данных не активна.")
            return []

        # Логируем имя пользователя
        username_lower = username.lower()

        # Основной запрос
        query = text("""
            SELECT DISTINCT table_name
            FROM information_schema.table_privileges
            WHERE LOWER(grantee) = :username
              AND privilege_type = 'SELECT'
              AND table_schema = 'public'
        """)
        result = db_session.execute(query, {"username": username_lower})
        accessible_tables = [row[0] for row in result]
        return accessible_tables
    except SQLAlchemyError as sql_err:
        return []
    except Exception as e:
        print(f"Ошибка получения списка доступных таблиц: {e}")
        return []

# Функция для создания новой сессии
def get_db_session():
    """
    Создает и возвращает новую сессию базы данных.
    """
    try:
        db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return db_session
    except Exception as e:
        print(f"Ошибка при создании сессии базы данных: {e}")
        return None