from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import Polyclinic, Laboratory, Doctor


# Создание новой поликлиники
def create_polyclinic(
    db: Session,
    polyclinic_name: str,
    polyclinic_address: str,
    polyclinic_phone: str = None,
):
    """
    Создание новой поликлиники.
    """
    new_polyclinic = Polyclinic(
        polyclinic_name=polyclinic_name,
        polyclinic_address=polyclinic_address,
        polyclinic_phone=polyclinic_phone,
    )
    try:
        db.add(new_polyclinic)
        db.commit()
        db.refresh(new_polyclinic)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании поликлиники: {str(e)}")
    return new_polyclinic

def get_all_polyclinics_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех поликлиник с заменой polyclinicid на название поликлиники.
    """
    polyclinics = db.query(Polyclinic).offset(skip).limit(limit).all()
    return [
        {
            "polyclinicid": polyclinic.polyclinicid,
            "polyclinic_name": polyclinic.polyclinic_name,
        }
        for polyclinic in polyclinics
    ]

# Получение всех поликлиник с деталями
# def get_all_polyclinics_with_details(db: Session, skip: int = 0, limit: int = 100):
#     """
#     Получение всех поликлиник с количеством лабораторий и врачей.
#     """
#     polyclinics = (
#         db.query(Polyclinic)
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )
#
#     # Формируем результат с дополнительными деталями
#     result = [
#         {
#             "polyclinicid": polyclinic.polyclinicid,
#             "polyclinic_name": polyclinic.polyclinic_name,
#             "polyclinic_address": polyclinic.polyclinic_address,
#             "polyclinic_phone": polyclinic.polyclinic_phone,
#             "laboratory_count": len(polyclinic.laboratories),
#             "doctor_count": len(polyclinic.doctors),
#         }
#         for polyclinic in polyclinics
#     ]
#     return result


# Поиск поликлиник по названию
def search_polyclinics_by_name(db: Session, name: str):
    """
    Поиск поликлиник по частичному совпадению названия.
    """
    polyclinics = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(f"%{name}%")).all()

    # Формируем результат с дополнительными деталями
    result = [
        {
            "polyclinicid": polyclinic.polyclinicid,
            "polyclinic_name": polyclinic.polyclinic_name,
            "polyclinic_address": polyclinic.polyclinic_address,
            "polyclinic_phone": polyclinic.polyclinic_phone,
            "laboratory_count": len(polyclinic.laboratories),
            "doctor_count": len(polyclinic.doctors),
        }
        for polyclinic in polyclinics
    ]
    return result


# Обновление данных поликлиники
def update_polyclinic(
    db: Session,
    polyclinic_id: int,
    polyclinic_name: str = None,
    polyclinic_address: str = None,
    polyclinic_phone: str = None,
):
    """
    Обновление данных поликлиники.
    """
    polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinicid == polyclinic_id).first()
    if not polyclinic:
        raise ValueError(f"Поликлиника с ID {polyclinic_id} не найдена")

    # Обновляем поля
    if polyclinic_name is not None:
        polyclinic.polyclinic_name = polyclinic_name
    if polyclinic_address is not None:
        polyclinic.polyclinic_address = polyclinic_address
    if polyclinic_phone is not None:
        polyclinic.polyclinic_phone = polyclinic_phone

    db.commit()
    db.refresh(polyclinic)
    return polyclinic


# Удаление поликлиники
def delete_polyclinic(db: Session, polyclinic_id: int):
    """
    Удаление поликлиники.
    """
    polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinicid == polyclinic_id).first()
    if not polyclinic:
        raise ValueError(f"Поликлиника с ID {polyclinic_id} не найдена")

    # Проверка зависимостей
    if polyclinic.laboratories or polyclinic.doctors:
        raise ValueError("Невозможно удалить поликлинику, так как она имеет связанные лаборатории или врачей.")

    db.delete(polyclinic)
    db.commit()
    return {"message": f"Поликлиника с ID {polyclinic_id} успешно удалена"}


# ==================== Дополнительные функции ====================


def get_laboratories_in_polyclinic(db: Session, polyclinic_id: int):
    """
    Получить список лабораторий для конкретной поликлиники.
    """
    laboratories = (
        db.query(Laboratory)
        .filter(Laboratory.polyclinicid == polyclinic_id)
        .all()
    )

    # Формируем результат
    result = [
        {
            "labid": lab.labid,
            "lab_name": lab.lab_name,
            "lab_address": lab.lab_address,
        }
        for lab in laboratories
    ]
    return result


def get_doctors_in_polyclinic(db: Session, polyclinic_id: int):
    """
    Получить список врачей для конкретной поликлиники.
    """
    doctors = (
        db.query(Doctor)
        .filter(Doctor.polyclinicid == polyclinic_id)
        .all()
    )

    # Формируем результат
    result = [
        {
            "doctorid": doctor.doctorid,
            "doctor_fio": doctor.doctor_fio,
            "doctor_specialization": doctor.doctor_specialization,
            "doctor_phone": doctor.doctor_phone,
        }
        for doctor in doctors
    ]
    return result
