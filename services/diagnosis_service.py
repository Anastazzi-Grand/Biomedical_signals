from datetime import date

from sqlalchemy.orm import Session, joinedload
from database.models import Diagnosis, Patient, Doctor


# Создание нового диагноза
def create_diagnosis(
    db: Session,
    patient_fio: str,  # Вместо patientid
    diagnosis_name: str = None,
    description: str = None,
    date_of_diagnosis: date = None,
    doctor_fio: str = None,  # Вместо doctorid
):
    # Поиск пациента по ФИО
    patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
    if not patient:
        raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")

    # Поиск врача по ФИО (если указан)
    doctor = None
    if doctor_fio:
        doctor = db.query(Doctor).filter(Doctor.doctor_fio.ilike(doctor_fio)).first()
        if not doctor:
            raise ValueError(f"Врач с ФИО '{doctor_fio}' не найден")

    # Создание диагноза
    new_diagnosis = Diagnosis(
        patientid=patient.patientid,
        diagnosis_name=diagnosis_name,
        description=description,
        date_of_diagnosis=date_of_diagnosis,
        doctorid=doctor.doctorid if doctor else None,
    )
    db.add(new_diagnosis)
    db.commit()
    db.refresh(new_diagnosis)
    return new_diagnosis


# Получение всех диагнозов с заменой внешних ключей на читаемые значения
def get_diagnoses_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех диагнозов с заменой внешних ключей на читаемые значения.
    """
    diagnoses = (
        db.query(Diagnosis)
        .options(joinedload(Diagnosis.patient), joinedload(Diagnosis.doctor))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "diagnosisid": diagnosis.diagnosisid,
            "diagnosisname": diagnosis.diagnosisname,
            "description": diagnosis.description,
            "dateofdiagnosis": diagnosis.dateofdiagnosis,
            "patient_fio": diagnosis.patient.patient_fio if diagnosis.patient else None,
            "doctor_fio": diagnosis.doctor.doctor_fio if diagnosis.doctor else None,
        }
        for diagnosis in diagnoses
    ]
    return result


# Поиск диагнозов по ФИО пациента
def search_diagnoses_by_patient_fio(db: Session, fio: str):
    """
    Поиск диагнозов по частичному совпадению ФИО пациента.
    """
    diagnoses = (
        db.query(Diagnosis)
        .join(Patient, Diagnosis.patientid == Patient.patientid)
        .filter(Patient.patient_fio.ilike(f"%{fio}%"))
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "diagnosisid": diagnosis.diagnosisid,
            "diagnosis_name": diagnosis.diagnosisname,
            "description": diagnosis.description,
            "dateofdiagnosis": diagnosis.dateofdiagnosis,
            "patient_fio": diagnosis.patient.patient_fio if diagnosis.patient else None,
            "doctor_fio": diagnosis.doctor.doctor_fio if diagnosis.doctor else None,
        }
        for diagnosis in diagnoses
    ]
    return result


# Поиск диагнозов по названию
def search_diagnoses_by_name(db: Session, name: str):
    """
    Поиск диагнозов по частичному совпадению названия.
    """
    diagnoses = db.query(Diagnosis).filter(Diagnosis.diagnosis_name.ilike(f"%{name}%")).all()

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "diagnosisid": diagnosis.diagnosisid,
            "diagnosisname": diagnosis.diagnosisname,
            "description": diagnosis.description,
            "dateofdiagnosis": diagnosis.dateofdiagnosis,
            "patient_fio": diagnosis.patient.patient_fio if diagnosis.patient else None,
            "doctor_fio": diagnosis.doctor.doctor_fio if diagnosis.doctor else None,
        }
        for diagnosis in diagnoses
    ]
    return result


# Обновление данных диагноза
def update_diagnosis(
    db: Session,
    diagnosisid: int,
    patient_fio: str = None,  # Вместо patientid
    diagnosis_name: str = None,
    description: str = None,
    date_of_diagnosis: date = None,
    doctor_fio: str = None,  # Вместо doctorid
):
    # Находим диагноз по ID
    diagnosis = db.query(Diagnosis).filter(Diagnosis.diagnosisid == diagnosisid).first()
    if not diagnosis:
        raise ValueError(f"Диагноз с ID {diagnosisid} не найден")

    # Если указано новое ФИО пациента, находим соответствующий ID
    if patient_fio:
        patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
        if not patient:
            raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")
        diagnosis.patientid = patient.patientid

    # Если указано новое ФИО врача, находим соответствующий ID
    if doctor_fio:
        doctor = db.query(Doctor).filter(Doctor.doctor_fio.ilike(doctor_fio)).first()
        if not doctor:
            raise ValueError(f"Врач с ФИО '{doctor_fio}' не найден")
        diagnosis.doctorid = doctor.doctorid

    # Обновляем остальные поля
    if diagnosis_name is not None:
        diagnosis.diagnosis_name = diagnosis_name
    if description is not None:
        diagnosis.description = description
    if date_of_diagnosis is not None:
        diagnosis.date_of_diagnosis = date_of_diagnosis

    # Сохраняем изменения
    db.commit()
    db.refresh(diagnosis)
    return diagnosis


# Удаление диагноза
def delete_diagnosis(db: Session, diagnosisid: int):
    diagnosis = db.query(Diagnosis).filter(Diagnosis.diagnosisid == diagnosisid).first()
    if diagnosis:
        db.delete(diagnosis)
        db.commit()
    return diagnosis
