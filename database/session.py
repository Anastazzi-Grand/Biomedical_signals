from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Настройка подключения
DATABASE_URL = "postgresql+psycopg2://postgres:nasa@localhost:5432/Biomedical_signals"
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
