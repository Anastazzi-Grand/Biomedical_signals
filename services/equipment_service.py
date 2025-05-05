from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database.models import Equipment, Laboratory


# Создание нового оборудования
def create_equipment(
    db: Session,
    equipment_name: str,
    equipment_serial: str,  # Серийный номер
    labid: int,  # ID лаборатории
):
    """
    Создание нового оборудования.
    Проверяет существование лаборатории перед созданием.
    """
    # Проверка существования лаборатории
    lab = db.query(Laboratory).filter(Laboratory.labid == labid).first()
    if not lab:
        raise ValueError(f"Лаборатория с ID {labid} не найдена")

    new_equipment = Equipment(
        equipment_name=equipment_name,
        equipment_serial=equipment_serial,
        labid=labid,
    )
    try:
        db.add(new_equipment)
        db.commit()
        db.refresh(new_equipment)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка при создании оборудования: {str(e)}")
    return new_equipment


# Получение всех записей оборудования с деталями
def get_all_equipment_with_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение всех записей оборудования с заменой labid на название лаборатории.
    """
    equipment_list = (
        db.query(Equipment)
        .join(Laboratory, Equipment.labid == Laboratory.labid)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Формируем результат с заменой внешних ключей
    result = [
        {
            "equipmentid": equipment.equipmentid,
            "equipment_name": equipment.equipment_name,
            "equipment_serial": equipment.equipment_serial,
            "lab_name": equipment.lab.lab_name if equipment.lab else None,
        }
        for equipment in equipment_list
    ]
    return result


# Получение информации о конкретном оборудовании
def get_equipment_by_id(db: Session, equipment_id: int):
    """
    Получение информации о конкретном оборудовании с заменой labid на название лаборатории.
    """
    equipment = (
        db.query(Equipment)
        .options(joinedload(Equipment.lab))
        .filter(Equipment.equipmentid == equipment_id)
        .first()
    )
    if not equipment:
        raise ValueError(f"Оборудование с ID {equipment_id} не найдено")

    return {
        "equipmentid": equipment.equipmentid,
        "equipment_name": equipment.equipment_name,
        "equipment_serial": equipment.equipment_serial,
        "lab_name": equipment.lab.lab_name if equipment.lab else None,
    }


# Обновление данных оборудования
def update_equipment(
    db: Session,
    equipment_id: int,
    equipment_name: str = None,
    equipment_serial: str = None,
    labid: int = None,
):
    """
    Обновление данных оборудования.
    """
    equipment = db.query(Equipment).filter(Equipment.equipmentid == equipment_id).first()
    if not equipment:
        raise ValueError(f"Оборудование с ID {equipment_id} не найдено")

    # Обновляем поля
    if equipment_name is not None:
        equipment.equipment_name = equipment_name
    if equipment_serial is not None:
        equipment.equipment_serial = equipment_serial
    if labid is not None:
        lab = db.query(Laboratory).filter(Laboratory.labid == labid).first()
        if not lab:
            raise ValueError(f"Лаборатория с ID {labid} не найдена")
        equipment.labid = labid

    db.commit()
    db.refresh(equipment)
    return equipment


# Удаление оборудования
def delete_equipment(db: Session, equipment_id: int):
    """
    Удаление оборудования.
    """
    equipment = db.query(Equipment).filter(Equipment.equipmentid == equipment_id).first()
    if not equipment:
        raise ValueError(f"Оборудование с ID {equipment_id} не найдено")

    db.delete(equipment)
    db.commit()
    return {"message": f"Оборудование с ID {equipment_id} успешно удалено"}
