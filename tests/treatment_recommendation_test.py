from database.session import get_db
from services.treatment_recommendation_service import (
    create_treatment_recommendation,
    get_all_treatment_recommendations_with_details,
    get_treatment_recommendation_by_id,
    update_treatment_recommendation,
    delete_treatment_recommendation,
)
from sqlalchemy.exc import IntegrityError

def test_treatment_recommendation_operations():
    # Получение сессии базы данных
    db = next(get_db())

    try:
        # ==================== 1. Создание новой рекомендации по лечению ====================
        print("=== Тест: Создание новой рекомендации по лечению ===")
        new_recommendation = create_treatment_recommendation(
            db=db,
            diagnosisname="Гипертония",  # Название диагноза
            treatmentplan="Прием лекарственных препаратов",
            additionalremarks="Регулярный мониторинг давления",
        )
        print(f"Создана новая рекомендация: ID={new_recommendation.recommendationid}, Диагноз={new_recommendation.diagnosis.diagnosisname}")

        # ==================== 2. Получение всех рекомендаций по лечению ====================
        print("\n=== Тест: Получение всех рекомендаций по лечению ===")
        all_recommendations = get_all_treatment_recommendations_with_details(db)
        for recommendation in all_recommendations:
            print(
                f"ID: {recommendation['recommendationid']}, "
                f"Диагноз: {recommendation['diagnosisname']}, "
                f"План лечения: {recommendation['treatmentplan']}, "
                f"Примечания: {recommendation['additionalremarks']}"
            )

        # ==================== 3. Получение рекомендации по лечению по ID ====================
        print("\n=== Тест: Получение рекомендации по лечению по ID ===")
        recommendation_details = get_treatment_recommendation_by_id(db, recommendationid=new_recommendation.recommendationid)
        print(
            f"ID: {recommendation_details['recommendationid']}, "
            f"Диагноз: {recommendation_details['diagnosisname']}, "
            f"План лечения: {recommendation_details['treatmentplan']}, "
            f"Примечания: {recommendation_details['additionalremarks']}"
        )

        # ==================== 4. Обновление рекомендации по лечению ====================
        print("\n=== Тест: Обновление рекомендации по лечению ===")
        updated_recommendation = update_treatment_recommendation(
            db=db,
            recommendationid=new_recommendation.recommendationid,
            diagnosisname="Незначительные отклонения",  # Новое название диагноза
            treatmentplan="Контроль уровня сахара",
            additionalremarks="Диета и физическая активность",
        )
        print(f"Обновлена рекомендация: ID={updated_recommendation.recommendationid}, Диагноз={updated_recommendation.diagnosis.diagnosisname}")

        # ==================== 5. Удаление рекомендации по лечению ====================
        print("\n=== Тест: Удаление рекомендации по лечению ===")
        delete_result = delete_treatment_recommendation(db, recommendationid=new_recommendation.recommendationid)
        print(delete_result["message"])

    except ValueError as e:
        print(f"Ошибка: {e}")
    except IntegrityError as e:
        print(f"Ошибка целостности данных: {str(e)}")
    finally:
        # Закрытие сессии
        db.close()


if __name__ == "__main__":
    test_treatment_recommendation_operations()