from datetime import date
from sqlalchemy.orm import Session, joinedload
from database.models import Chronic_condition, Patient


# Создание новой хронической болезни
def create_chronic_condition(
    db: Session,
    patient_fio: str,  # Вместо patientid
    condition_name: str,
    diagnosis_date: date = None,
    remarks: str = None,
):
    """
    Создание новой хронической болезни по ФИО пациента.
    """
    # Поиск пациента по ФИО
    patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
    if not patient:
        raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")

    new_condition = Chronic_condition(
        patientid=patient.patientid,
        condition_name=condition_name,
        diagnosis_date=diagnosis_date,
        remarks=remarks,
    )
    db.add(new_condition)
    db.commit()
    db.refresh(new_condition)
    return new_condition


# Получение всех хронических заболеваний с заменой внешних ключей на читаемые значения
def get_chronic_conditions_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех хронических заболеваний с заменой patientid на ФИО пациента.
    """
    conditions = (
        db.query(Chronic_condition)
        .options(joinedload(Chronic_condition.patient))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "chronicid": condition.chronicid,
            "condition_name": condition.condition_name,
            "diagnosis_date": condition.diagnosis_date,
            "remarks": condition.remarks,
            "patient_fio": condition.patient.patient_fio if condition.patient else None,
        }
        for condition in conditions
    ]
    return result


# Поиск хронических заболеваний по имени пациента
def search_chronic_conditions_by_patient_fio(db: Session, fio: str):
    """
    Поиск хронических заболеваний по частичному совпадению ФИО пациента.
    """
    conditions = (
        db.query(Chronic_condition)
        .join(Patient, Chronic_condition.patientid == Patient.patientid)
        .filter(Patient.patient_fio.ilike(f"%{fio}%"))
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "chronicid": condition.chronicid,
            "condition_name": condition.condition_name,
            "diagnosis_date": condition.diagnosis_date,
            "remarks": condition.remarks,
            "patient_fio": condition.patient.patient_fio if condition.patient else None,
        }
        for condition in conditions
    ]
    return result


# Обновление данных хронической болезни
def update_chronic_condition(
    db: Session,
    chronicid: int,
    patient_fio: str = None,  # Вместо patientid
    condition_name: str = None,
    diagnosis_date: date = None,
    remarks: str = None,
):
    """
    Обновление данных хронической болезни.
    Если указано новое ФИО пациента, находим соответствующий patientid.
    """
    condition = db.query(Chronic_condition).filter(Chronic_condition.chronicid == chronicid).first()
    if not condition:
        raise ValueError(f"Хроническое заболевание с ID {chronicid} не найдено")

    # Если указано новое ФИО пациента, находим соответствующий ID
    if patient_fio:
        patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
        if not patient:
            raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")
        condition.patientid = patient.patientid

    # Обновляем остальные поля
    if condition_name is not None:
        condition.condition_name = condition_name
    if diagnosis_date is not None:
        condition.diagnosis_date = diagnosis_date
    if remarks is not None:
        condition.remarks = remarks

    db.commit()
    db.refresh(condition)
    return condition


# Удаление хронической болезни
def delete_chronic_condition(db: Session, chronicid: int):
    """
    Удаление хронической болезни.
    """
    condition = db.query(Chronic_condition).filter(Chronic_condition.chronicid == chronicid).first()
    if condition:
        db.delete(condition)
        db.commit()
    return {"message": f"Хроническое заболевание с ID {chronicid} успешно удалено"}