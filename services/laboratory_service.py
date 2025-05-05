from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database.models import Laboratory, Polyclinic


# Создание новой лаборатории
def create_laboratory(
    db: Session,
    lab_name: str,
    lab_address: str,
    polyclinic_name: str,  # Вместо polyclinicid
):
    """
    Создание новой лаборатории.
    """
    # Поиск поликлиники по названию
    polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
    if not polyclinic:
        raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")

    new_lab = Laboratory(
        lab_name=lab_name,
        lab_address=lab_address,
        polyclinicid=polyclinic.polyclinicid,
    )
    try:
        db.add(new_lab)
        db.commit()
        db.refresh(new_lab)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании лаборатории: {str(e)}")
    return new_lab


# Получение всех записей лабораторий с деталями
def get_all_laboratories_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех записей лабораторий с заменой polyclinicid на название поликлиники.
    """
    labs = (
        db.query(Laboratory)
        .join(Polyclinic, Laboratory.polyclinicid == Polyclinic.polyclinicid)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "labid": lab.labid,
            "lab_name": lab.lab_name,
            "lab_address": lab.lab_address,
            "polyclinic_name": lab.polyclinic.polyclinic_name if lab.polyclinic else None,
        }
        for lab in labs
    ]
    return result


# Получение информации о конкретной лаборатории
def get_laboratory_by_id(db: Session, lab_id: int):
    """
    Получение информации о конкретной лаборатории с заменой polyclinicid на название поликлиники.
    """
    lab = (
        db.query(Laboratory)
        .options(joinedload(Laboratory.polyclinic))
        .filter(Laboratory.labid == lab_id)
        .first()
    )
    if not lab:
        raise ValueError(f"Лаборатория с ID {lab_id} не найдена")

    return {
        "labid": lab.labid,
        "lab_name": lab.lab_name,
        "lab_address": lab.lab_address,
        "polyclinic_name": lab.polyclinic.polyclinic_name if lab.polyclinic else None,
    }


# Обновление данных лаборатории
def update_laboratory(
    db: Session,
    lab_id: int,
    lab_name: str = None,
    lab_address: str = None,
    polyclinic_name: str = None,  # Вместо polyclinicid
):
    """
    Обновление данных лаборатории.
    Если указано новое название поликлиники, находим соответствующий polyclinicid.
    """
    lab = db.query(Laboratory).filter(Laboratory.labid == lab_id).first()
    if not lab:
        raise ValueError(f"Лаборатория с ID {lab_id} не найдена")

    # Если указано новое название поликлиники, находим соответствующий ID
    if polyclinic_name:
        polyclinic = db.query(Polyclinic).filter(Polyclinic.polyclinic_name.ilike(polyclinic_name)).first()
        if not polyclinic:
            raise ValueError(f"Поликлиника с названием '{polyclinic_name}' не найдена")
        lab.polyclinicid = polyclinic.polyclinicid

    # Обновляем остальные поля
    if lab_name is not None:
        lab.lab_name = lab_name
    if lab_address is not None:
        lab.lab_address = lab_address

    db.commit()
    db.refresh(lab)
    return lab


# Удаление лаборатории
def delete_laboratory(db: Session, lab_id: int):
    """
    Удаление лаборатории.
    """
    lab = db.query(Laboratory).filter(Laboratory.labid == lab_id).first()
    if not lab:
        raise ValueError(f"Лаборатория с ID {lab_id} не найдена")

    db.delete(lab)
    db.commit()
    return {"message": f"Лаборатория с ID {lab_id} успешно удалена"}
