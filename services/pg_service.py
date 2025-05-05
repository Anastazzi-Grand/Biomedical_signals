from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from database.models import PG_data, Sessions


# Создание новой записи PG_data
def create_pg_data(db: Session, session_id: int, d1: int, d2: int, amplitude: float = None):
    """
    Создание новой записи PG_data.
    Если amplitude не указан, он будет рассчитан автоматически.
    """
    # Проверка существования сессии
    session = db.query(Sessions).filter(Sessions.sessionid == session_id).first()
    if not session:
        raise ValueError(f"Сессия с ID {session_id} не найдена")

    new_pg_data = PG_data(
        sessionid=session_id,
        d1=d1,
        d2=d2,
        amplitude=amplitude,
    )
    db.add(new_pg_data)
    db.commit()
    db.refresh(new_pg_data)
    return new_pg_data


# Получение всех записей PG_data с заменой внешних ключей на читаемые значения
def get_pg_data_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех записей PG_data с заменой sessionid на детали сессии.
    """
    pg_data_list = (
        db.query(PG_data)
        .options(joinedload(PG_data.session))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "pgdataid": pg_data.pgdataid,
            "session_date": pg_data.session.session_date if pg_data.session else None,
            "session_starttime": pg_data.session.session_starttime if pg_data.session else None,
            "session_endtime": pg_data.session.session_endtime if pg_data.session else None,
            "patient_fio": pg_data.session.patient.patient_fio if pg_data.session and pg_data.session.patient else None,
            "doctor_fio": pg_data.session.doctor.doctor_fio if pg_data.session and pg_data.session.doctor else None,
            "d1": pg_data.d1,
            "d2": pg_data.d2,
            "amplitude": pg_data.amplitude,
        }
        for pg_data in pg_data_list
    ]
    return result


# Получение данных PG_data по ID сессии
def get_pg_data_by_session_id(db: Session, session_id: int):
    """
    Получение данных PG_data по ID сессии с заменой sessionid на детали сессии.
    """
    pg_data_list = (
        db.query(PG_data)
        .options(joinedload(PG_data.session))
        .filter(PG_data.sessionid == session_id)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "pgdataid": pg_data.pgdataid,
            "session_date": pg_data.session.session_date if pg_data.session else None,
            "session_starttime": pg_data.session.session_starttime if pg_data.session else None,
            "session_endtime": pg_data.session.session_endtime if pg_data.session else None,
            "patient_fio": pg_data.session.patient.patient_fio if pg_data.session and pg_data.session.patient else None,
            "doctor_fio": pg_data.session.doctor.doctor_fio if pg_data.session and pg_data.session.doctor else None,
            "d1": pg_data.d1,
            "d2": pg_data.d2,
            "amplitude": pg_data.amplitude,
        }
        for pg_data in pg_data_list
    ]
    return result


# Обновление данных PG_data
def update_pg_data(db: Session, pgdataid: int, d1: int = None, d2: int = None, amplitude: float = None):
    """
    Обновление данных PG_data.
    """
    pg_data = db.query(PG_data).filter(PG_data.pgdataid == pgdataid).first()
    if not pg_data:
        raise ValueError(f"Запись PG_data с ID {pgdataid} не найдена")

    # Обновляем поля
    if d1 is not None:
        pg_data.d1 = d1
    if d2 is not None:
        pg_data.d2 = d2
    if amplitude is not None:
        pg_data.amplitude = amplitude

    db.commit()
    db.refresh(pg_data)
    return pg_data


# Удаление данных PG_data
def delete_pg_data(db: Session, pgdataid: int):
    """
    Удаление данных PG_data.
    """
    pg_data = db.query(PG_data).filter(PG_data.pgdataid == pgdataid).first()
    if not pg_data:
        raise ValueError(f"Запись PG_data с ID {pgdataid} не найдена")

    db.delete(pg_data)
    db.commit()
    return {"message": f"Запись PG_data с ID {pgdataid} успешно удалена"}
