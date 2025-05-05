from datetime import date, time
from sqlalchemy.orm import Session, joinedload
from database.models import Analysis_result, Sessions


# Создание нового результата анализа
def create_analysis_result(
    db: Session,
    session_date: date,  # Вместо sessionid
    session_starttime: time,  # Вместо sessionid
    rr_analysis: str,
    du_analysis: str,
):
    """
    Создание нового результата анализа по дате и времени сеанса.
    """
    # Поиск сеанса по дате и времени
    session = (
        db.query(Sessions)
        .filter(Sessions.session_date == session_date, Sessions.session_starttime == session_starttime)
        .first()
    )
    if not session:
        raise ValueError(f"Сеанс с датой '{session_date}' и временем '{session_starttime}' не найден")

    # Создание результата анализа
    new_result = Analysis_result(
        sessionid=session.sessionid,
        rr_analysis=rr_analysis,
        du_analysis=du_analysis,
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result


# Получение всех результатов анализа с заменой внешних ключей на читаемые значения
def get_analysis_results_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех результатов анализа с заменой внешних ключей на читаемые значения.
    """
    results = (
        db.query(Analysis_result)
        .options(joinedload(Analysis_result.session))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "analysisresultid": result.analysisresultid,
            "session_date": result.session.session_date if result.session else None,
            "session_starttime": result.session.session_starttime if result.session else None,
            "session_endtime": result.session.session_endtime if result.session else None,
            "rr_analysis": result.rr_analysis,
            "du_analysis": result.du_analysis,
        }
        for result in results
    ]
    return result


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
            "rr_analysis": result.rr_analysis,
            "du_analysis": result.du_analysis,
        }
        for result in results
    ]
    return result


# Обновление данных результата анализа
def update_analysis_result(
    db: Session,
    analysisresultid: int,
    session_date: date = None,  # Вместо sessionid
    session_starttime: time = None,  # Вместо sessionid
    rr_analysis: str = None,
    du_analysis: str = None,
):
    """
    Обновление данных результата анализа по дате и времени сеанса.
    """
    # Находим результат анализа по ID
    result = db.query(Analysis_result).filter(Analysis_result.analysisresultid == analysisresultid).first()
    if not result:
        raise ValueError(f"Результат анализа с ID {analysisresultid} не найден")

    # Если указана новая дата и время сеанса, находим соответствующий ID
    if session_date and session_starttime:
        session = (
            db.query(Sessions)
            .filter(Sessions.session_date == session_date, Sessions.session_starttime == session_starttime)
            .first()
        )
        if not session:
            raise ValueError(f"Сеанс с датой '{session_date}' и временем '{session_starttime}' не найден")
        result.sessionid = session.sessionid

    # Обновляем остальные поля
    if rr_analysis is not None:
        result.rr_analysis = rr_analysis
    if du_analysis is not None:
        result.du_analysis = du_analysis

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
