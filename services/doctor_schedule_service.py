from datetime import date, time

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import Doctor_schedule, Doctor


# Создание нового расписания врача
def create_doctor_schedule(
    db: Session,
    doctor_fio: str,  # Вместо doctorid
    workdate: date,
    starttime: time,
    endtime: time,
):
    """
    Создание нового расписания врача по ФИО врача.
    """
    # Поиск врача по ФИО
    doctor = db.query(Doctor).filter(Doctor.doctor_fio.ilike(doctor_fio)).first()
    if not doctor:
        raise ValueError(f"Врач с ФИО '{doctor_fio}' не найден")

    # Проверка корректности временного интервала
    if starttime >= endtime:
        raise ValueError("Время начала должно быть меньше времени окончания")

    new_schedule = Doctor_schedule(
        doctorid=doctor.doctorid,
        workdate=workdate,
        starttime=starttime,
        endtime=endtime,
    )
    try:
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании расписания: {str(e)}")
    return new_schedule


# Получение всех записей расписания врачей
def get_all_doctor_schedules(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех записей расписания врачей с заменой doctorid на ФИО врача.
    """
    schedules = (
        db.query(Doctor_schedule)
        .join(Doctor, Doctor_schedule.doctorid == Doctor.doctorid)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "scheduleid": schedule.scheduleid,
            "doctor_fio": schedule.doctor.doctor_fio,
            "workdate": schedule.workdate,
            "starttime": schedule.starttime,
            "endtime": schedule.endtime,
        }
        for schedule in schedules
    ]
    return result


# Получение расписания для конкретного врача
def get_schedule_for_doctor(db: Session, doctor_fio: str):
    """
    Получение расписания для конкретного врача по его ФИО.
    """
    schedules = (
        db.query(Doctor_schedule)
        .join(Doctor, Doctor_schedule.doctorid == Doctor.doctorid)
        .filter(Doctor.doctor_fio.ilike(doctor_fio))
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "scheduleid": schedule.scheduleid,
            "doctor_fio": schedule.doctor.doctor_fio,
            "workdate": schedule.workdate,
            "starttime": schedule.starttime,
            "endtime": schedule.endtime,
        }
        for schedule in schedules
    ]
    return result


# Получение доступных слотов для записи к врачу
# Получение доступных слотов для записи к врачу
def get_available_slots_for_doctor(db: Session, doctor_fio: str):
    """
    Получение доступных временных слотов для записи к врачу.
    Использует хранимую процедуру `get_available_slots_for_doctor`.
    """
    # Поиск ID врача по ФИО
    doctor = db.query(Doctor).filter(Doctor.doctor_fio.ilike(doctor_fio)).first()
    if not doctor:
        raise ValueError(f"Врач с ФИО '{doctor_fio}' не найден")

    # Вызов хранимой процедуры
    result = db.execute(
        text("SELECT * FROM get_available_slots_for_doctor(:doctor_id)"),
        {"doctor_id": doctor.doctorid},
    ).fetchall()  # Получаем список кортежей

    # Преобразуем результат в список словарей
    slots = [
        {
            "doctor_fio": row[0],  # Первый столбец
            "workdate": row[1],    # Второй столбец
            "starttime": row[2],   # Третий столбец
            "endtime": row[3],     # Четвертый столбец
            "freeslot": row[4],    # Пятый столбец
        }
        for row in result
    ]
    return slots


# Обновление расписания врача
def update_doctor_schedule(
    db: Session,
    scheduleid: int,
    doctor_fio: str = None,  # Вместо doctorid
    workdate: date = None,
    starttime: time = None,
    endtime: time = None,
):
    """
    Обновление расписания врача.
    Если указано новое ФИО врача, находим соответствующий doctorid.
    """
    schedule = db.query(Doctor_schedule).filter(Doctor_schedule.scheduleid == scheduleid).first()
    if not schedule:
        raise ValueError(f"Расписание с ID {scheduleid} не найдено")

    # Если указано новое ФИО врача, находим соответствующий ID
    if doctor_fio:
        doctor = db.query(Doctor).filter(Doctor.doctor_fio.ilike(doctor_fio)).first()
        if not doctor:
            raise ValueError(f"Врач с ФИО '{doctor_fio}' не найден")
        schedule.doctorid = doctor.doctorid

    # Обновляем остальные поля
    if workdate is not None:
        schedule.workdate = workdate
    if starttime is not None:
        schedule.starttime = starttime
    if endtime is not None:
        schedule.endtime = endtime

    # Проверка корректности временного интервала
    if schedule.starttime >= schedule.endtime:
        raise ValueError("Время начала должно быть меньше времени окончания")

    db.commit()
    db.refresh(schedule)
    return schedule


# Удаление расписания врача
def delete_doctor_schedule(db: Session, scheduleid: int):
    """
    Удаление расписания врача.
    """
    schedule = db.query(Doctor_schedule).filter(Doctor_schedule.scheduleid == scheduleid).first()
    if schedule:
        db.delete(schedule)
        db.commit()
    return {"message": f"Расписание с ID {scheduleid} успешно удалено"}
