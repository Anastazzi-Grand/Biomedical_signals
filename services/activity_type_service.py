from sqlalchemy.orm import Session
from database.models import Activity_type


# Создание нового типа активности
def create_activity_type(db: Session, activity_name: str, description: str = None):
    """
    Создание нового типа активности.
    Проверяет уникальность названия активности.
    """
    # Проверка на дублирование названия
    existing_activity = db.query(Activity_type).filter(Activity_type.activity_name.ilike(activity_name)).first()
    if existing_activity:
        raise ValueError(f"Тип активности с названием '{activity_name}' уже существует")

    new_activity_type = Activity_type(
        activity_name=activity_name,
        description=description,
    )
    db.add(new_activity_type)
    db.commit()
    db.refresh(new_activity_type)
    return new_activity_type


# Получение всех типов активностей
def get_activity_types(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех типов активностей с поддержкой пагинации.
    """
    return db.query(Activity_type).offset(skip).limit(limit).all()


# Поиск типов активностей по названию (частичное совпадение)
def search_activity_types_by_name(db: Session, name: str):
    """
    Поиск типов активностей по частичному совпадению названия.
    """
    return db.query(Activity_type).filter(Activity_type.activity_name.ilike(f"%{name}%")).all()


# Обновление данных типа активности
def update_activity_type(db: Session, activitytypeid: int, **kwargs):
    """
    Обновление данных типа активности.
    """
    activity_type = db.query(Activity_type).filter(Activity_type.activitytypeid == activitytypeid).first()
    if not activity_type:
        raise ValueError(f"Тип активности с ID {activitytypeid} не найден")

    # Проверка на уникальность названия, если оно изменяется
    if "activity_name" in kwargs:
        new_activityname = kwargs["activityname"]
        existing_activity = (
            db.query(Activity_type)
            .filter(Activity_type.activity_name.ilike(new_activityname), Activity_type.activitytypeid != activitytypeid)
            .first()
        )
        if existing_activity:
            raise ValueError(f"Тип активности с названием '{new_activityname}' уже существует")

    for key, value in kwargs.items():
        setattr(activity_type, key, value)

    db.commit()
    db.refresh(activity_type)
    return activity_type


# Удаление типа активности
def delete_activity_type(db: Session, activitytypeid: int):
    """
    Удаление типа активности.
    """
    activity_type = db.query(Activity_type).filter(Activity_type.activitytypeid == activitytypeid).first()
    if not activity_type:
        raise ValueError(f"Тип активности с ID {activitytypeid} не найден")

    db.delete(activity_type)
    db.commit()
    return {"message": f"Тип активности с ID {activitytypeid} успешно удален"}
