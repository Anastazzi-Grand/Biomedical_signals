from sqlalchemy.orm import Session
from database.models import Patient_activity, Patient, Activity_type


# Создание новой записи о виде деятельности пациента
def create_patient_activity(
    db: Session,
    patient_fio: str,  # Вместо patientid
    activity_name: str,  # Вместо activitytypeid
):
    """
    Создание новой записи о виде деятельности пациента.
    Использует ФИО пациента и название вида деятельности вместо ID.
    """
    # Поиск пациента по ФИО
    patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
    if not patient:
        raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")

    # Поиск вида деятельности по названию
    activity = db.query(Activity_type).filter(Activity_type.activity_name.ilike(activity_name)).first()
    if not activity:
        raise ValueError(f"Вид деятельности с названием '{activity_name}' не найден")

    new_patient_activity = Patient_activity(
        patientid=patient.patientid,
        activitytypeid=activity.activitytypeid,
    )
    db.add(new_patient_activity)
    db.commit()
    db.refresh(new_patient_activity)
    return new_patient_activity


# Получение всех записей о видах деятельности пациентов с деталями
def get_all_patient_activities_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех записей о видах деятельности пациентов с заменой ID на читаемые значения.
    """
    activities = (
        db.query(Patient_activity)
        .join(Patient, Patient_activity.patientid == Patient.patientid)
        .join(Activity_type, Patient_activity.activitytypeid == Activity_type.activitytypeid)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "patientactivityid": activity.patientactivityid,
            "patient_fio": activity.patient.patient_fio,
            "activityname": activity.activity_type.activityname,
            "description": activity.activity_type.description,
        }
        for activity in activities
    ]
    return result


# Получение записей о видах деятельности конкретного пациента
def get_patient_activities_by_fio(db: Session, patient_fio: str):
    """
    Получение записей о видах деятельности конкретного пациента по его ФИО.
    """
    # Поиск пациента по ФИО
    patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
    if not patient:
        raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")

    activities = (
        db.query(Patient_activity)
        .join(Activity_type, Patient_activity.activitytypeid == Activity_type.activitytypeid)
        .filter(Patient_activity.patientid == patient.patientid)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "patientactivityid": activity.patientactivityid,
            "activityname": activity.activity_type.activityname,
            "description": activity.activity_type.description,
        }
        for activity in activities
    ]
    return result


# Обновление данных о виде деятельности пациента
def update_patient_activity(
    db: Session,
    patientactivityid: int,
    patient_fio: str = None,  # Вместо patientid
    activityname: str = None,  # Вместо activitytypeid
):
    """
    Обновление данных о виде деятельности пациента.
    Если указано новое ФИО пациента или название вида деятельности, находим соответствующие ID.
    """
    activity = db.query(Patient_activity).filter(Patient_activity.patientactivityid == patientactivityid).first()
    if not activity:
        raise ValueError(f"Запись о виде деятельности с ID {patientactivityid} не найдена")

    # Если указано новое ФИО пациента, находим соответствующий ID
    if patient_fio:
        patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
        if not patient:
            raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")
        activity.patientid = patient.patientid

    # Если указано новое название вида деятельности, находим соответствующий ID
    if activityname:
        activity_type = db.query(Activity_type).filter(Activity_type.activityname.ilike(activityname)).first()
        if not activity_type:
            raise ValueError(f"Вид деятельности с названием '{activityname}' не найден")
        activity.activitytypeid = activity_type.activitytypeid

    db.commit()
    db.refresh(activity)
    return activity


# Удаление записи о виде деятельности пациента
def delete_patient_activity(db: Session, patientactivityid: int):
    """
    Удаление записи о виде деятельности пациента.
    """
    activity = db.query(Patient_activity).filter(Patient_activity.patientactivityid == patientactivityid).first()
    if not activity:
        raise ValueError(f"Запись о виде деятельности с ID {patientactivityid} не найдена")

    db.delete(activity)
    db.commit()
    return {"message": f"Запись о виде деятельности с ID {patientactivityid} успешно удалена"}
