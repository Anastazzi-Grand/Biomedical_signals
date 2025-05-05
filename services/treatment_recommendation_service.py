from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database.models import Treatment_recommendation, Diagnosis


# Создание новой рекомендации по лечению
def create_treatment_recommendation(
    db: Session,
    diagnosisname: str,  # Вместо diagnosisid
    treatmentplan: str,
    additionalremarks: str = None,
):
    """
    Создание новой рекомендации по лечению.
    Использует название диагноза вместо его ID.
    """
    # Поиск диагноза по названию
    diagnosis = db.query(Diagnosis).filter(Diagnosis.diagnosisname.ilike(diagnosisname)).first()
    if not diagnosis:
        raise ValueError(f"Диагноз с названием '{diagnosisname}' не найден")

    new_recommendation = Treatment_recommendation(
        diagnosisid=diagnosis.diagnosisid,
        treatmentplan=treatmentplan,
        additionalremarks=additionalremarks,
    )
    try:
        db.add(new_recommendation)
        db.commit()
        db.refresh(new_recommendation)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании рекомендации: {str(e)}")
    return new_recommendation


# Получение всех рекомендаций по лечению с деталями
def get_all_treatment_recommendations_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех рекомендаций по лечению с заменой diagnosisid на название диагноза.
    """
    recommendations = (
        db.query(Treatment_recommendation)
        .join(Diagnosis, Treatment_recommendation.diagnosisid == Diagnosis.diagnosisid)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "recommendationid": recommendation.recommendationid,
            "diagnosisname": recommendation.diagnosis.diagnosisname,
            "treatmentplan": recommendation.treatmentplan,
            "additionalremarks": recommendation.additionalremarks,
        }
        for recommendation in recommendations
    ]
    return result


# Получение рекомендации по лечению по ID
def get_treatment_recommendation_by_id(db: Session, recommendationid: int):
    """
    Получение рекомендации по лечению по её ID с заменой diagnosisid на название диагноза.
    """
    recommendation = (
        db.query(Treatment_recommendation)
        .options(joinedload(Treatment_recommendation.diagnosis))
        .filter(Treatment_recommendation.recommendationid == recommendationid)
        .first()
    )
    if not recommendation:
        raise ValueError(f"Рекомендация с ID {recommendationid} не найдена")

    return {
        "recommendationid": recommendation.recommendationid,
        "diagnosisname": recommendation.diagnosis.diagnosisname,
        "treatmentplan": recommendation.treatmentplan,
        "additionalremarks": recommendation.additionalremarks,
    }


# Обновление рекомендации по лечению
def update_treatment_recommendation(
    db: Session,
    recommendationid: int,
    diagnosisname: str = None,  # Вместо diagnosisid
    treatmentplan: str = None,
    additionalremarks: str = None,
):
    """
    Обновление рекомендации по лечению.
    Если указано новое название диагноза, находим соответствующий diagnosisid.
    """
    recommendation = db.query(Treatment_recommendation).filter(Treatment_recommendation.recommendationid == recommendationid).first()
    if not recommendation:
        raise ValueError(f"Рекомендация с ID {recommendationid} не найдена")

    # Если указано новое название диагноза, находим соответствующий ID
    if diagnosisname:
        diagnosis = db.query(Diagnosis).filter(Diagnosis.diagnosisname.ilike(diagnosisname)).first()
        if not diagnosis:
            raise ValueError(f"Диагноз с названием '{diagnosisname}' не найден")
        recommendation.diagnosisid = diagnosis.diagnosisid

    # Обновляем остальные поля
    if treatmentplan is not None:
        recommendation.treatment_plan = treatmentplan
    if additionalremarks is not None:
        recommendation.additional_remarks = additionalremarks

    db.commit()
    db.refresh(recommendation)
    return recommendation


# Удаление рекомендации по лечению
def delete_treatment_recommendation(db: Session, recommendationid: int):
    """
    Удаление рекомендации по лечению.
    """
    recommendation = db.query(Treatment_recommendation).filter(Treatment_recommendation.recommendationid == recommendationid).first()
    if not recommendation:
        raise ValueError(f"Рекомендация с ID {recommendationid} не найдена")

    db.delete(recommendation)
    db.commit()
    return {"message": f"Рекомендация с ID {recommendationid} успешно удалена"}
