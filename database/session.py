from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


# Определение URL базы данных
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/Biomedical_signals"

# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для проверки логина и пароля через подключение к базе данных
def authenticate_user(username, password):
    try:
        print(f"Попытка подключения к базе данных с логином: {username}, пароль: {'*' * len(password)}")
        DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@localhost:5432/Biomedical_signals"
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()  # Проверяем подключение
        connection.close()

        # Создаем новую фабрику сессий для текущего движка
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = Session()
        print(f"Успешное подключение для пользователя: {username}")
        return session
    except Exception as e:
        print(f"Ошибка при подключении к базе данных для пользователя {username}: {e}")
        return None


# Функция для получения списка доступных таблиц для пользователя
def get_user_accessible_tables(db_session, username):
    try:
        print("Начало выполнения get_user_accessible_tables...")
        if not db_session or not db_session.is_active:
            print("Сессия базы данных не активна.")
            return []

        # Логируем имя пользователя
        username_lower = username.lower()
        print(f"Имя пользователя для запроса: {username_lower}")

        # Тестовый запрос для проверки подключения
        try:
            test_query = text("SELECT 1")
            test_result = db_session.execute(test_query).scalar()
            print(f"Тестовый запрос выполнен: {test_result}")
        except Exception as e:
            print(f"Ошибка при выполнении тестового запроса: {e}")
            return []

        # Основной запрос
        query = text("""
            SELECT DISTINCT table_name
            FROM information_schema.table_privileges
            WHERE LOWER(grantee) = :username
              AND privilege_type = 'SELECT'
              AND table_schema = 'public'
        """)
        print(f"Выполняем запрос для пользователя {username}...")
        result = db_session.execute(query, {"username": username_lower})
        accessible_tables = [row[0] for row in result]
        print(f"Доступные таблицы для пользователя {username}: {accessible_tables}")
        return accessible_tables
    except SQLAlchemyError as sql_err:
        print(f"SQLAlchemyError при получении доступных таблиц: {sql_err}")
        print(f"Параметры запроса: username={username}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка при получении доступных таблиц: {e}")
        return []