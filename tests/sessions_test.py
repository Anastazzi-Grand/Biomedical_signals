from datetime import date
from database.session import get_db
from services.sessions_service import (
    create_session,
    get_sessions_with_details,
    search_sessions_by_date,
    get_sessions_by_patient_fio,
    delete_session,
)
from sqlalchemy.exc import IntegrityError

def test_session_operations():
    # Получение сессии базы данных
    db = next(get_db())

    try:
        # ==================== 1. Создание нового сеанса ====================
        print("=== Тест: Создание нового сеанса ===")
        new_session = create_session(
            db=db,
            session_date=date(2025, 5, 5),
            start_time="09:00:00",
            end_time="10:00:00",
            patient_fio="Иванов Иван Иванович",  # ФИО пациента
            doctor_fio="Кузнецова Е. Р.",   # ФИО врача
            lab_name="Лаборатория №1",  # Название лаборатории
        )
        print(f"Создан новый сеанс: ID={new_session.sessionid}, Пациент={new_session.patient.patient_fio}")

        # ==================== 2. Получение всех сеансов ====================
        print("\n=== Тест: Получение всех сеансов ===")
        all_sessions = get_sessions_with_details(db)
        for session in all_sessions:
            print(
                f"ID: {session['sessionid']}, "
                f"Дата: {session['session_date']}, "
                f"Время начала: {session['session_starttime']}, "
                f"Время окончания: {session['session_endtime']}, "
                f"Пациент: {session['patient_fio']}, "
                f"Врач: {session['doctor_fio']}, "
                f"Лаборатория: {session['lab_name']}"
            )

        # ==================== 3. Поиск сеансов по дате ====================
        print("\n=== Тест: Поиск сеансов по дате ===")
        sessions_by_date = search_sessions_by_date(db, session_date=date(2025, 5, 5))
        for session in sessions_by_date:
            print(
                f"ID: {session['sessionid']}, "
                f"Дата: {session['session_date']}, "
                f"Время начала: {session['session_starttime']}, "
                f"Время окончания: {session['session_endtime']}, "
                f"Пациент: {session['patient_fio']}, "
                f"Врач: {session['doctor_fio']}, "
                f"Лаборатория: {session['lab_name']}"
            )

        # ==================== 4. Поиск сеансов по ФИО пациента ====================
        print("\n=== Тест: Поиск сеансов по ФИО пациента ===")
        sessions_by_patient = get_sessions_by_patient_fio(db, fio="Погонина")
        for session in sessions_by_patient:
            print(
                f"ID: {session['sessionid']}, "
                f"Дата: {session['session_date']}, "
                f"Время начала: {session['session_starttime']}, "
                f"Время окончания: {session['session_endtime']}, "
                f"Пациент: {session['patient_fio']}, "
                f"Врач: {session['doctor_fio']}, "
                f"Лаборатория: {session['lab_name']}"
            )

        # ==================== 5. Удаление сеанса ====================
        print("\n=== Тест: Удаление сеанса ===")
        delete_result = delete_session(db, session_id=new_session.sessionid)
        print(delete_result["message"])

    except ValueError as e:
        print(f"Ошибка: {e}")
    except IntegrityError as e:
        print(f"Ошибка целостности данных: {str(e)}")
    finally:
        # Закрытие сессии
        db.close()


if __name__ == "__main__":
    test_session_operations()
