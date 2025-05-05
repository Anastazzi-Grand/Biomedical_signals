from datetime import date
from sqlalchemy.orm import Session, joinedload
from database.models import Doctor, Polyclinic


# Создание нового врача
def create_doctor(
    db: Session,
    fio: str,
    birthdate: date,
    specialization: str,
    phone: str,
    polyclinic_name: str,  # Вместо polyclinic_id
):
    """
    Создание нового врача по названию поликлиники.
    """
    # Поиск поликлиники по названию
    polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
    if not polyclinic:
        raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")

    new_doctor = Doctor(
        doctor_fio=fio,
        doctor_birthdate=birthdate,
        doctor_specialization=specialization,
        doctor_phone=phone,
        polyclinicid=polyclinic.polyclinicid,
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor


# Получение всех врачей с заменой внешних ключей на читаемые значения
def get_doctors_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех врачей с заменой polyclinicid на название поликлиники.
    """
    doctors = (
        db.query(Doctor)
        .options(joinedload(Doctor.polyclinic))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "doctorid": doctor.doctorid,
            "doctor_fio": doctor.doctor_fio,
            "doctor_birthdate": doctor.doctor_birthdate,
            "doctor_specialization": doctor.doctor_specialization,
            "doctor_phone": doctor.doctor_phone,
            "polyclinic_name": doctor.polyclinic.polyclinic_name if doctor.polyclinic else None,
        }
        for doctor in doctors
    ]
    return result


# Поиск врачей по ФИО
def search_doctors_by_fio(db: Session, fio: str):
    """
    Поиск врачей по частичному совпадению ФИО.
    """
    doctors = db.query(Doctor).filter(Doctor.doctor_fio.ilike(f"%{fio}%")).all()

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "doctorid": doctor.doctorid,
            "doctor_fio": doctor.doctor_fio,
            "doctor_birthdate": doctor.doctor_birthdate,
            "doctor_specialization": doctor.doctor_specialization,
            "doctor_phone": doctor.doctor_phone,
            "polyclinic_name": doctor.polyclinic.polyclinic_name if doctor.polyclinic else None,
        }
        for doctor in doctors
    ]
    return result


# Обновление данных врача
def update_doctor(
    db: Session,
    doctor_id: int,
    fio: str = None,
    birthdate: date = None,
    specialization: str = None,
    phone: str = None,
    polyclinic_name: str = None,  # Вместо polyclinic_id
):
    """
    Обновление данных врача.
    Если указано новое название поликлиники, находим соответствующий polyclinicid.
    """
    doctor = db.query(Doctor).filter(Doctor.doctorid == doctor_id).first()
    if not doctor:
        raise ValueError(f"Врач с ID {doctor_id} не найден")

    # Если указано новое название поликлиники, находим соответствующий ID
    if polyclinic_name:
        polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
        if not polyclinic:
            raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")
        doctor.polyclinicid = polyclinic.polyclinicid

    # Обновляем остальные поля
    if fio is not None:
        doctor.doctor_fio = fio
    if birthdate is not None:
        doctor.doctor_birthdate = birthdate
    if specialization is not None:
        doctor.doctor_specialization = specialization
    if phone is not None:
        doctor.doctor_phone = phone

    db.commit()
    db.refresh(doctor)
    return doctor


# Удаление врача
def delete_doctor(db: Session, doctor_id: int):
    """
    Удаление врача.
    """
    doctor = db.query(Doctor).filter(Doctor.doctorid == doctor_id).first()
    if doctor:
        db.delete(doctor)
        db.commit()
    return {"message": f"Врач с ID {doctor_id} успешно удален"}
