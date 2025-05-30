from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from database.models import ECS_data, Sessions


# Создание новой записи ECS_data
def create_ecs_data(db: Session, session_id: int, rr_length: int, rr_time: float = None):
    """
    Создание новой записи ECS_data.
    Если rr_time не указан, он будет рассчитан автоматически.
    """
    # Проверка существования сессии
    session_obj = db.query(Sessions).filter(Sessions.sessionid == session_id).first()
    if not session_obj:
        raise ValueError(f"Сессия с ID {session_id} не найдена")

    # Создаем новую запись ECS_data
    new_ecs_data = ECS_data(
        sessionid=session_id,
        rr_length=rr_length,
        rr_time=rr_time,
    )
    db.add(new_ecs_data)
    db.commit()
    db.refresh(new_ecs_data)
    return new_ecs_data


# Получение всех записей ECS_data с заменой внешних ключей на читаемые значения
def get_ecs_data_with_details(db: Session, skip: int = 0):
    """
    Получение всех записей ECS_data с заменой sessionid на детали сессии.
    """
    ecs_data_list = (
        db.query(ECS_data)
        .options(joinedload(ECS_data.session))
        .offset(skip)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "ecsdataid": ecs_data.ecsdataid,
            "session_date": ecs_data.session.session_date if ecs_data.session else None,
            "session_starttime": ecs_data.session.session_starttime if ecs_data.session else None,
            "session_endtime": ecs_data.session.session_endtime if ecs_data.session else None,
            "patient_fio": ecs_data.session.patient.patient_fio if ecs_data.session and ecs_data.session.patient else None,
            "doctor_fio": ecs_data.session.doctor.doctor_fio if ecs_data.session and ecs_data.session.doctor else None,
            "rr_length": ecs_data.rr_length,
            "rr_time": ecs_data.rr_time,
        }
        for ecs_data in ecs_data_list
    ]
    return result


# Получение данных ECS_data по ID сессии
def get_ecs_data_by_session_id(db: Session, session_id: int):
    """
    Получение данных ECS_data по ID сессии с заменой sessionid на детали сессии.
    """
    ecs_data_list = (
        db.query(ECS_data)
        .options(joinedload(ECS_data.session))
        .filter(ECS_data.sessionid == session_id)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "ecsdataid": ecs_data.ecsdataid,
            "session_date": ecs_data.session.session_date if ecs_data.session else None,
            "session_starttime": ecs_data.session.session_starttime if ecs_data.session else None,
            "session_endtime": ecs_data.session.session_endtime if ecs_data.session else None,
            "patient_fio": ecs_data.session.patient.patient_fio if ecs_data.session and ecs_data.session.patient else None,
            "doctor_fio": ecs_data.session.doctor.doctor_fio if ecs_data.session and ecs_data.session.doctor else None,
            "rr_length": ecs_data.rr_length,
            "rr_time": ecs_data.rr_time,
        }
        for ecs_data in ecs_data_list
    ]
    return result


# Обновление данных ECS_data
def update_ecs_data(db: Session, ecsdataid: int, rr_length: int = None, rr_time: float = None):
    """
    Обновление данных ECS_data.
    """
    ecs_data = db.query(ECS_data).filter(ECS_data.ecsdataid == ecsdataid).first()
    if not ecs_data:
        raise ValueError(f"Запись ECS_data с ID {ecsdataid} не найдена")

    # Обновляем поля
    if rr_length is not None:
        ecs_data.rr_length = rr_length
    if rr_time is not None:
        ecs_data.rr_time = rr_time

    db.commit()
    db.refresh(ecs_data)
    return ecs_data


# Удаление данных ECS_data
def delete_ecs_data(db: Session, ecsdataid: int):
    """
    Удаление данных ECS_data.
    """
    ecs_data = db.query(ECS_data).filter(ECS_data.ecsdataid == ecsdataid).first()
    if not ecs_data:
        raise ValueError(f"Запись ECS_data с ID {ecsdataid} не найдена")

    db.delete(ecs_data)
    db.commit()
    return {"message": f"Запись ECS_data с ID {ecsdataid} успешно удалена"}


def delete_ecs_data_by_session_id(db: Session, session_id: int):
    """
    Удаление всех данных ECS_data для указанного сеанса.
    """
    ecs_data = db.query(ECS_data).filter(ECS_data.sessionid == session_id).all()
    if not ecs_data:
        raise ValueError(f"Нет данных ECS_data для сеанса с ID {session_id}")

    for data in ecs_data:
        db.delete(data)
    db.commit()
    return {"message": f"Все данные ECS_data для сеанса с ID {session_id} успешно удалены"}
