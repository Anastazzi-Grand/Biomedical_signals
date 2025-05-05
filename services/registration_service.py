from datetime import date, time

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import Registration, Patient, Polyclinic


# Создание новой записи в регистратуре
def create_registration(
    db: Session,
    patient_fio: str,  # Вместо patientid
    polyclinic_name: str,  # Вместо polyclinicid
    registration_date: date,
    registration_time: time,
):
    """
    Создание новой записи в регистратуре.
    Использует ФИО пациента и название поликлиники вместо их ID.
    """
    # Поиск пациента по ФИО
    patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
    if not patient:
        raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")

    # Поиск поликлиники по названию
    polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
    if not polyclinic:
        raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")

    new_registration = Registration(
        patientid=patient.patientid,
        polyclinicid=polyclinic.polyclinicid,
        registration_date=registration_date,
        registration_time=registration_time,
    )
    try:
        db.add(new_registration)
        db.commit()
        db.refresh(new_registration)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании записи в регистратуре: {str(e)}")
    return new_registration


# Получение всех записей в регистратуре с деталями
def get_all_registrations_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех записей в регистратуре с заменой ID на читаемые значения.
    """
    registrations = (
        db.query(Registration)
        .join(Patient, Registration.patientid == Patient.patientid)
        .join(Polyclinic, Registration.polyclinicid == Polyclinic.polyclinicid)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "registrationid": registration.registrationid,
            "patient_fio": registration.patient.patient_fio,
            "polyclinic_name": registration.polyclinic.polyclinic_name,
            "registration_date": registration.registration_date,
            "registration_time": registration.registration_time,
        }
        for registration in registrations
    ]
    return result


# Поиск записей в регистратуре по ФИО пациента
def search_registrations_by_patient_fio(db: Session, patient_fio: str):
    """
    Поиск записей в регистратуре по частичному совпадению ФИО пациента.
    """
    registrations = (
        db.query(Registration)
        .join(Patient, Registration.patientid == Patient.patientid)
        .filter(Patient.patient_fio.ilike(f"%{patient_fio}%"))
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "registrationid": registration.registrationid,
            "patient_fio": registration.patient.patient_fio,
            "polyclinic_name": registration.polyclinic.polyclinic_name,
            "registration_date": registration.registration_date,
            "registration_time": registration.registration_time,
        }
        for registration in registrations
    ]
    return result


# Обновление данных записи в регистратуре
def update_registration(
    db: Session,
    registration_id: int,
    patient_fio: str = None,  # Вместо patientid
    polyclinic_name: str = None,  # Вместо polyclinicid
    registration_date: date = None,
    registration_time: time = None,
):
    """
    Обновление данных записи в регистратуре.
    Если указано новое ФИО пациента или название поликлиники, находим соответствующие ID.
    """
    registration = db.query(Registration).filter(Registration.registrationid == registration_id).first()
    if not registration:
        raise ValueError(f"Запись в регистратуре с ID {registration_id} не найдена")

    # Если указано новое ФИО пациента, находим соответствующий ID
    if patient_fio:
        patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
        if not patient:
            raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")
        registration.patientid = patient.patientid

    # Если указано новое название поликлиники, находим соответствующий ID
    if polyclinic_name:
        polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
        if not polyclinic:
            raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")
        registration.polyclinicid = polyclinic.polyclinicid

    # Обновляем остальные поля
    if registration_date is not None:
        registration.registration_date = registration_date
    if registration_time is not None:
        registration.registration_time = registration_time

    db.commit()
    db.refresh(registration)
    return registration


# Удаление записи в регистратуре
def delete_registration(db: Session, registration_id: int):
    """
    Удаление записи в регистратуре.
    """
    registration = db.query(Registration).filter(Registration.registrationid == registration_id).first()
    if not registration:
        raise ValueError(f"Запись в регистратуре с ID {registration_id} не найдена")

    db.delete(registration)
    db.commit()
    return {"message": f"Запись в регистратуре с ID {registration_id} успешно удалена"}
