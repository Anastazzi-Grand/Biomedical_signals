from datetime import date, time
from sqlalchemy.orm import Session, joinedload
from database.models import Analysis_result, Sessions


# Создание нового результата анализа
def create_analysis_result(
    db: Session,
    sessionid: int,
    processed_ecs_data: float,
    processed_pg_data: float,
):

    # Создание результата анализа
    new_result = Analysis_result(
        sessionid=sessionid,
        processed_ecs_data=processed_ecs_data,
        processed_pg_data=processed_pg_data,
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result


# Получение всех результатов анализа с заменой внешних ключей на читаемые значения
def get_analysis_results_with_details(db: Session, skip: int = 0):
    """
    Получение всех результатов анализа с заменой внешних ключей на читаемые значения.
    """
    results = (
        db.query(Analysis_result)
        .options(joinedload(Analysis_result.session))
        .offset(skip)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "analysisresultid": result.analysisresultid,
            "session_date": result.session.session_date if result.session else None,
            "session_starttime": result.session.session_starttime if result.session else None,
            "session_endtime": result.session.session_endtime if result.session else None,
            "processed_ecs_data": result.processed_ecs_data,
            "processed_pg_data": result.processed_pg_data,
        }
        for result in results
    ]
    return result

def get_analysis_result_by_sessionid(db: Session, sessionid: int):
    """
    Получение результата анализа по ID сеанса.
    """
    result = db.query(Analysis_result).filter(Analysis_result.sessionid == sessionid).first()
    return result

def get_analysis_results_by_sessionid(db: Session, session_id: int):
    """
    Получение всех результатов анализа для указанного сеанса.
    """
    results = db.query(Analysis_result).filter(Analysis_result.sessionid == session_id).all()
    return results  # Всегда возвращаем список


# Поиск результатов анализа по дате и времени сеанса
def get_analysis_results_by_session_datetime(db: Session, session_date: date, session_time: time):
    """
    Поиск результатов анализа по дате и времени сеанса.
    """
    results = (
        db.query(Analysis_result)
        .join(Sessions, Analysis_result.sessionid == Sessions.sessionid)
        .filter(Sessions.session_date == session_date, Sessions.session_starttime == session_time)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "analysisresultid": result.analysisresultid,
            "session_date": result.session.session_date if result.session else None,
            "session_starttime": result.session.session_starttime if result.session else None,
            "session_endtime": result.session.session_endtime if result.session else None,
            "processed_ecs_data": result.processed_ecs_data,
            "processed_pg_data": result.processed_pg_data,
        }
        for result in results
    ]
    return result


# Обновление данных результата анализа
def update_analysis_result(
    db: Session,
    analysisresultid: int,
    sessionid: int = None,
    processed_ecs_data: float = None,
    processed_pg_data: float = None,
):

    # Находим результат анализа по ID
    result = db.query(Analysis_result).filter(Analysis_result.analysisresultid == analysisresultid).first()
    if not result:
        raise ValueError(f"Результат анализа с ID {analysisresultid} не найден")

    # Обновляем остальные поля
    if processed_ecs_data is not None:
        result.processed_ecs_data = processed_ecs_data
    if processed_pg_data is not None:
        result.processed_pg_data = processed_pg_data
    if sessionid is not None:
        result.session_id = sessionid

    # Сохраняем изменения
    db.commit()
    db.refresh(result)
    return result


# Удаление результата анализа
def delete_analysis_result(db: Session, analysisresultid: int):
    """
    Удаление результата анализа.
    """
    result = db.query(Analysis_result).filter(Analysis_result.analysisresultid == analysisresultid).first()
    if result:
        db.delete(result)
        db.commit()
    return result

def delete_analysis_results_by_sessionid(db: Session, sessionid: int):
    """
    Удаление всех записей результатов анализа для указанного sessionid.
    """
    db.query(Analysis_result).filter(Analysis_result.sessionid == sessionid).delete()
    db.commit()
