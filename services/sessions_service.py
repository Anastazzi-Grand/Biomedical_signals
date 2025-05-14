from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import Sessions, Patient, Doctor, Laboratory


# Создание нового сеанса
def create_session(
    db: Session,
    session_date: date,
    start_time: str,
    end_time: str,
    patient_fio: str,  # Вместо patient_id
    doctor_fio: str,   # Вместо doctor_id
    lab_name: str,     # Вместо lab_id
):
    """
    Создание нового сеанса.
    Использует ФИО пациента, ФИО врача и название лаборатории вместо их ID.
    """
    # Поиск пациента по ФИО
    patient = db.query(Patient).filter(Patient.patient_fio.ilike(patient_fio)).first()
    if not patient:
        raise ValueError(f"Пациент с ФИО '{patient_fio}' не найден")

    # Поиск врача по ФИО
    doctor = db.query(Doctor).filter(Doctor.doctor_fio.ilike(doctor_fio)).first()
    if not doctor:
        raise ValueError(f"Врач с ФИО '{doctor_fio}' не найден")

    # Поиск лаборатории по названию
    lab = db.query(Laboratory).filter(Laboratory.lab_name.ilike(lab_name)).first()
    if not lab:
        raise ValueError(f"Лаборатория с названием '{lab_name}' не найдена")

    new_session = Sessions(
        session_date=session_date,
        session_starttime=start_time,
        session_endtime=end_time,
        patientid=patient.patientid,
        doctorid=doctor.doctorid,
        labid=lab.labid,
    )
    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании сеанса: {str(e)}")
    return new_session


# Получение всех сеансов с деталями
def get_sessions_with_details(db: Session):
    """
    Получение всех сеансов с заменой ID на читаемые значения.
    """
    sessions = (
        db.query(Sessions)
        .join(Patient, Sessions.patientid == Patient.patientid)
        .join(Doctor, Sessions.doctorid == Doctor.doctorid)
        .join(Laboratory, Sessions.labid == Laboratory.labid)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "sessionid": session.sessionid,
            "session_date": session.session_date,
            "session_starttime": session.session_starttime,
            "session_endtime": session.session_endtime,
            "patient_fio": session.patient.patient_fio,
            "doctor_fio": session.doctor.doctor_fio,
            "lab_name": session.laboratory.lab_name,
        }
        for session in sessions
    ]
    return result


# Поиск сеансов по дате
def search_sessions_by_date(db: Session, session_date: date):
    """
    Поиск сеансов по дате с заменой ID на читаемые значения.
    """
    sessions = (
        db.query(Sessions)
        .join(Patient, Sessions.patientid == Patient.patientid)
        .join(Doctor, Sessions.doctorid == Doctor.doctorid)
        .join(Laboratory, Sessions.labid == Laboratory.labid)
        .filter(Sessions.session_date == session_date)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "sessionid": session.sessionid,
            "session_date": session.session_date,
            "session_starttime": session.session_starttime,
            "session_endtime": session.session_endtime,
            "patient_fio": session.patient.patient_fio,
            "doctor_fio": session.doctor.doctor_fio,
            "lab_name": session.laboratory.lab_name,
        }
        for session in sessions
    ]
    return result


# Поиск сеансов по ФИО пациента
def get_sessions_by_patient_fio(db: Session, fio: str):
    """
    Поиск сеансов по частичному совпадению ФИО пациента с заменой ID на читаемые значения.
    """
    sessions = (
        db.query(Sessions)
        .join(Patient, Sessions.patientid == Patient.patientid)
        .join(Doctor, Sessions.doctorid == Doctor.doctorid)
        .join(Laboratory, Sessions.labid == Laboratory.labid)
        .filter(Patient.patient_fio.ilike(f"%{fio}%"))
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "sessionid": session.sessionid,
            "session_date": session.session_date,
            "session_starttime": session.session_starttime,
            "session_endtime": session.session_endtime,
            "patient_fio": session.patient.patient_fio,
            "doctor_fio": session.doctor.doctor_fio,
            "lab_name": session.laboratory.lab_name,
        }
        for session in sessions
    ]
    return result


# Удаление сеанса
def delete_session(db: Session, session_id: int):
    """
    Удаление сеанса.
    """
    session = db.query(Sessions).filter(Sessions.sessionid == session_id).first()
    if not session:
        raise ValueError(f"Сеанс с ID {session_id} не найден")

    db.delete(session)
    db.commit()
    return {"message": f"Сеанс с ID {session_id} успешно удален"}
