from datetime import date, time
from database.session import get_db
from services.registration_service import (
    create_registration,
    get_all_registrations_with_details,
    search_registrations_by_patient_fio,
    update_registration,
    delete_registration,
)
from sqlalchemy.exc import IntegrityError

def test_registration_operations():
    # Получение сессии базы данных
    db = next(get_db())

    try:
        # ==================== 1. Создание новой записи в регистратуре ====================
        print("=== Тест: Создание новой записи в регистратуре ===")
        new_registration = create_registration(
            db=db,
            patient_fio="Погонина Е. В.",  # ФИО пациента
            polyclinic_name="Елатомед",  # Название поликлиники
            registration_date=date(2025, 5, 5),
            registration_time=time(9, 0),
        )
        print(f"Создана новая запись: ID={new_registration.registrationid}, Пациент={new_registration.patient.patient_fio}")

        # ==================== 2. Получение всех записей в регистратуре ====================
        print("\n=== Тест: Получение всех записей в регистратуре ===")
        all_registrations = get_all_registrations_with_details(db)
        for reg in all_registrations:
            print(
                f"ID: {reg['registrationid']}, "
                f"Пациент: {reg['patient_fio']}, "
                f"Поликлиника: {reg['polyclinic_name']}, "
                f"Дата: {reg['registration_date']}, "
                f"Время: {reg['registration_time']}"
            )

        # ==================== 3. Поиск записей в регистратуре по ФИО пациента ====================
        print("\n=== Тест: Поиск записей в регистратуре по ФИО пациента ===")
        found_registrations = search_registrations_by_patient_fio(db, patient_fio="Иванов")
        for reg in found_registrations:
            print(
                f"ID: {reg['registrationid']}, "
                f"Пациент: {reg['patient_fio']}, "
                f"Поликлиника: {reg['polyclinic_name']}, "
                f"Дата: {reg['registration_date']}, "
                f"Время: {reg['registration_time']}"
            )

        # ==================== 4. Обновление данных записи в регистратуре ====================
        print("\n=== Тест: Обновление данных записи в регистратуре ===")
        updated_registration = update_registration(
            db=db,
            registration_id=new_registration.registrationid,
            patient_fio="Иванов Иван Иванович",  # Новое ФИО пациента
            polyclinic_name="Елатомед",  # Новое название поликлиники
            registration_time=time(10, 0),  # Новое время
        )
        print(f"Обновлена запись: ID={updated_registration.registrationid}, Пациент={updated_registration.patient.patient_fio}")

        # ==================== 5. Удаление записи в регистратуре ====================
        print("\n=== Тест: Удаление записи в регистратуре ===")
        delete_result = delete_registration(db, registration_id=new_registration.registrationid)
        print(delete_result["message"])

    except ValueError as e:
        print(f"Ошибка: {e}")
    except IntegrityError as e:
        print(f"Ошибка целостности данных: {str(e)}")
    finally:
        # Закрытие сессии
        db.close()


if __name__ == "__main__":
    test_registration_operations()