from datetime import date
from sqlalchemy.orm import Session, joinedload
from database.models import Chronic_condition, Patient


# Создание новой хронической болезни
def create_chronic_condition(
    db: Session,
    patient_fio: str,  # Вместо patientid
    conditionname: str,
    diagnosisdate: date = None,
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
        conditionname=conditionname,
        diagnosisdate=diagnosisdate,
        remarks=remarks,
    )
    db.add(new_condition)
    db.commit()
    db.refresh(new_condition)
    return new_condition


# Получение всех хронических заболеваний с заменой внешних ключей на читаемые значения
def get_chronic_conditions_with_details(db: Session, skip: int = 0):
    """
    Получение всех хронических заболеваний с заменой patientid на ФИО пациента и дату рождения.
    """
    conditions = (
        db.query(Chronic_condition)
        .options(joinedload(Chronic_condition.patient))
        .offset(skip)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "chronicid": condition.chronicid,
            "conditionname": condition.conditionname,
            "diagnosisdate": condition.diagnosisdate,
            "remarks": condition.remarks,
            "patient_fio": condition.patient.patient_fio if condition.patient else None,
            "patient_birthdate": condition.patient.patient_birthdate if condition.patient else None,
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
            "conditionname": condition.conditionname,
            "diagnosisdate": condition.diagnosisdate,
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
    conditionname: str = None,
    diagnosisdate: date = None,
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
    if conditionname is not None:
        condition.conditionname = conditionname
    if diagnosisdate is not None:
        condition.diagnosis_date = diagnosisdate
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