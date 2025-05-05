from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database.models import Patient, Polyclinic, Treatment_recommendation, Diagnosis, Chronic_condition, Patient_activity, Activity_type


# Создание нового пациента
def create_patient(
    db: Session,
    fio: str,
    birthdate: date,
    address: str,
    phone: str,
    polyclinic_name: str,  # Вместо polyclinic_id
):
    """
    Создание нового пациента.
    Использует название поликлиники вместо её ID.
    """
    # Поиск поликлиники по названию
    polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
    if not polyclinic:
        raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")

    new_patient = Patient(
        patient_fio=fio,
        patient_birthdate=birthdate,
        patient_address=address,
        patient_phone=phone,
        polyclinicid=polyclinic.polyclinicid,
    )
    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании пациента: {str(e)}")
    return new_patient


# Получение всех пациентов с деталями
def get_patients_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех пациентов с заменой polyclinicid на название поликлиники.
    """
    patients = (
        db.query(Patient)
        .join(Polyclinic, Patient.polyclinicid == Polyclinic.polyclinicid)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "patientid": patient.patientid,
            "patient_fio": patient.patient_fio,
            "patient_birthdate": patient.patient_birthdate,
            "patient_address": patient.patient_address,
            "patient_phone": patient.patient_phone,
            "polyclinic_name": patient.polyclinic.polyclinic_name,
        }
        for patient in patients
    ]
    return result


# Поиск пациентов по ФИО
def search_patients_by_fio(db: Session, fio: str):
    """
    Поиск пациентов по частичному совпадению ФИО.
    """
    patients = db.query(Patient).filter(Patient.patient_fio.ilike(f"%{fio}%")).all()

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "patientid": patient.patientid,
            "patient_fio": patient.patient_fio,
            "patient_birthdate": patient.patient_birthdate,
            "patient_address": patient.patient_address,
            "patient_phone": patient.patient_phone,
            "polyclinic_name": patient.polyclinic.polyclinic_name,
        }
        for patient in patients
    ]
    return result


# Обновление данных пациента
def update_patient(
    db: Session,
    patient_id: int,
    fio: str = None,
    birthdate: date = None,
    address: str = None,
    phone: str = None,
    polyclinic_name: str = None,  # Вместо polyclinic_id
):
    """
    Обновление данных пациента.
    Если указано новое название поликлиники, находим соответствующий polyclinicid.
    """
    patient = db.query(Patient).filter(Patient.patientid == patient_id).first()
    if not patient:
        raise ValueError(f"Пациент с ID {patient_id} не найден")

    # Если указано новое название поликлиники, находим соответствующий ID
    if polyclinic_name:
        polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
        if not polyclinic:
            raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")
        patient.polyclinicid = polyclinic.polyclinicid

    # Обновляем остальные поля
    if fio is not None:
        patient.patient_fio = fio
    if birthdate is not None:
        patient.patient_birthdate = birthdate
    if address is not None:
        patient.patient_address = address
    if phone is not None:
        patient.patient_phone = phone

    db.commit()
    db.refresh(patient)
    return patient


# Удаление пациента
def delete_patient(db: Session, patient_id: int):
    """
    Удаление пациента.
    """
    patient = db.query(Patient).filter(Patient.patientid == patient_id).first()
    if not patient:
        raise ValueError(f"Пациент с ID {patient_id} не найден")

    db.delete(patient)
    db.commit()
    return {"message": f"Пациент с ID {patient_id} успешно удален"}


# ==================== Дополнительные функции ====================


def get_patient_activities_with_details(db: Session, patient_id: int):
    """
    Получить список активностей для конкретного пациента с заменой activitytypeid на название вида деятельности.
    """
    activities = (
        db.query(Patient_activity)
        .join(Activity_type, Patient_activity.activitytypeid == Activity_type.activitytypeid)
        .filter(Patient_activity.patientid == patient_id)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "activity_name": activity.activity_type.activity_name,
            "description": activity.activity_type.description,
        }
        for activity in activities
    ]
    return result


def get_patient_chronic_conditions_with_details(db: Session, patient_id: int):
    """
    Получить список хронических заболеваний для конкретного пациента.
    """
    conditions = (
        db.query(Chronic_condition)
        .filter(Chronic_condition.patientid == patient_id)
        .all()
    )

    # Формируем результат
    result = [
        {
            "condition_name": condition.condition_name,
            "diagnosis_date": condition.diagnosis_date,
            "remarks": condition.remarks,
        }
        for condition in conditions
    ]
    return result


def get_patient_treatment_recommendations_with_details(db: Session, patient_id: int):
    """
    Получить список рекомендаций по лечению для конкретного пациента.
    """
    recommendations = (
        db.query(Treatment_recommendation)
        .join(Diagnosis, Treatment_recommendation.diagnosisid == Diagnosis.diagnosisid)
        .filter(Diagnosis.patientid == patient_id)
        .all()
    )

    # Формируем результат
    result = [
        {
            "treatment_plan": recommendation.treatment_plan,
            "additional_remarks": recommendation.additional_remarks,
        }
        for recommendation in recommendations
    ]
    return result


def get_patient_full_details(db: Session, patient_id: int):
    """
    Получить полную информацию о пациенте, включая активности, хронические заболевания и рекомендации по лечению.
    """
    patient = (
        db.query(Patient)
        .options(
            joinedload(Patient.activities),
            joinedload(Patient.chronic_conditions),
            joinedload(Patient.diagnoses),
        )
        .filter(Patient.patientid == patient_id)
        .first()
    )
    if not patient:
        return None

    # Формируем результат
    result = {
        "patient": {
            "patientid": patient.patientid,
            "patient_fio": patient.patient_fio,
            "patient_birthdate": patient.patient_birthdate,
            "patient_address": patient.patient_address,
            "patient_phone": patient.patient_phone,
            "polyclinic_name": patient.polyclinic.polyclinic_name,
        },
        "activities": [
            {
                "activity_name": activity.activitytype.activityname,
                "description": activity.activitytype.description,
            }
            for activity in patient.activities
        ],
        "chronic_conditions": [
            {
                "conditionname": condition.conditionname,
                "diagnosisdate": condition.diagnosisdate,
                "remarks": condition.remarks,
            }
            for condition in patient.chronic_conditions
        ],
        "treatment_recommendations": [
            {
                "treatmentplan": recommendation.treatmentplan,
                "additionalremarks": recommendation.additionalremarks,
            }
            for diagnosis in patient.diagnoses
            for recommendation in diagnosis.treatment_recommendations
        ],
    }
    return result
