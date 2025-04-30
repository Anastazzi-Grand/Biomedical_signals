from sqlalchemy.orm import Session
from database.session import get_db  # Импортируем функцию для получения сессии
from database.models import Patient, Doctor, Sessions  # Импортируем модели


# Функция для чтения данных из таблицы "Пациент"
def read_patients(db: Session):
    patients = db.query(Patient).all()  # Выполняем запрос на получение всех записей
    for patient in patients:
        print(f"ID: {patient.patientid}, ФИО: {patient.patient_fio}, Дата рождения: {patient.patient_birthdate}")


# Функция для чтения данных из таблицы "Врач"
def read_doctors(db: Session):
    doctors = db.query(Doctor).all()
    for doctor in doctors:
        print(f"ID: {doctor.doctorid}, ФИО: {doctor.doctor_fio}, Специализация: {doctor.doctor_specialization}")


# Функция для чтения данных из таблицы "Сеанс"
def read_sessions(db: Session):
    sessions = db.query(Sessions).all()
    for session in sessions:
        print(f"ID: {session.sessionid}, Дата: {session.session_date}, Время начала: {session.session_starttime}")


# Основная функция
if __name__ == "__main__":
    # Получаем сессию базы данных
    db = next(get_db())

    print("=== Пациенты ===")
    read_patients(db)

    print("\n=== Врачи ===")
    read_doctors(db)

    print("\n=== Сеансы ===")
    read_sessions(db)
