from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, \
    QInputDialog, QDialog, QDateEdit


class PatientWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        try:
            self.db_session = db_session
            self.init_ui()
        except Exception as e:
            print(f"Ошибка при инициализации PatientWidget: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def init_ui(self):
        layout = QVBoxLayout()

        # Таблица
        self.table = QTableWidget()
        self.load_data()

        # Кнопки
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_patient)
        layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_selected_patient)
        layout.addWidget(self.delete_button)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        # Добавляем элементы в макет
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        """Загружает данные пациентов из базы данных."""
        try:
            from services.patient_service import get_patients_with_details

            patients = get_patients_with_details(self.db_session)
            patients.sort(key=lambda x: x["patient_fio"])  # Сортировка по ФИО

            # Настройка таблицы
            self.table.setRowCount(len(patients))
            self.table.setColumnCount(5)  # Добавляем один скрытый столбец для ID
            self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Дата рождения", "Адрес", "Телефон"])

            for row, patient in enumerate(patients):
                # Скрытый столбец: ID пациента
                self.table.setItem(row, 0, QTableWidgetItem(str(patient["patientid"])))
                self.table.setItem(row, 1, QTableWidgetItem(patient["patient_fio"]))
                self.table.setItem(row, 2, QTableWidgetItem(str(patient["patient_birthdate"])))
                self.table.setItem(row, 3, QTableWidgetItem(patient["patient_address"] or ""))
                self.table.setItem(row, 4, QTableWidgetItem(patient["patient_phone"] or ""))

            # Скрываем первый столбец (ID пациента)
            self.table.setColumnHidden(0, True)

        except Exception as e:
            print(f"Ошибка при загрузке данных пациентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def save_changes(self):
        """Сохраняет изменения, внесенные в таблицу, в базу данных."""
        try:
            from services.patient_service import update_patient

            for row in range(self.table.rowCount()):
                patient_id = self.get_patient_id_from_row(row)  # Получаем ID пациента
                if not patient_id:
                    continue

                patient_fio = self.table.item(row, 1).text()  # ФИО
                patient_birthdate = self.table.item(row, 2).text()  # Дата рождения
                patient_address = self.table.item(row, 3).text()  # Адрес
                patient_phone = self.table.item(row, 4).text()  # Телефон

                # Обновляем данные пациента
                update_patient(
                    self.db_session,
                    patient_id=patient_id,
                    fio=patient_fio,
                    birthdate=patient_birthdate,
                    address=patient_address,
                    phone=patient_phone
                )

            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except PermissionError as e:
            QMessageBox.critical(self, "Ошибка доступа", str(e))
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {e}")

    def add_patient(self):
        """Добавляет нового пациента."""
        try:
            from services.patient_service import create_patient
            from services.polyclinic_service import get_all_polyclinics_with_details

            # Диалоговое окно для ввода данных
            fio, ok = QInputDialog.getText(self, "Добавить пациента", "Введите ФИО пациента:")
            if not ok:
                return

            # Выбор даты рождения через календарь
            date_dialog = DateInputDialog(self)
            if date_dialog.exec():  # Проверяем, что пользователь нажал "Сохранить"
                birthdate = date_dialog.get_date()
            else:
                return  # Если пользователь закрыл диалог, выходим

            # Выбор поликлиники из выпадающего списка
            polyclinics = get_all_polyclinics_with_details(self.db_session)
            polyclinic_names = [polyclinic["polyclinic_name"] for polyclinic in polyclinics]
            selected_polyclinic, ok = QInputDialog.getItem(
                self, "Выберите поликлинику", "Поликлиника:", polyclinic_names, editable=False
            )
            if not ok:
                return

            # Ввод адреса и телефона
            address, ok = QInputDialog.getText(self, "Добавить пациента", "Введите адрес:")
            if not ok:
                return

            phone, ok = QInputDialog.getText(self, "Добавить пациента", "Введите телефон:")
            if not ok:
                return

            # Создаем нового пациента
            create_patient(
                self.db_session,
                fio=fio,
                birthdate=birthdate,
                address=address,
                phone=phone,
                polyclinic_name=selected_polyclinic
            )
            QMessageBox.information(self, "Успех", "Пациент успешно добавлен!")
            self.load_data()  # Обновляем таблицу
        except Exception as e:
            print(f"Ошибка при добавлении пациента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить пациента: {e}")

    def delete_selected_patient(self):
        """Удаляет выбранного пациента."""
        try:
            from services.patient_service import delete_patient

            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Внимание", "Выберите строку для удаления.")
                return

            patient_id = self.get_patient_id_from_row(selected_row)
            if not patient_id:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить ID пациента.")
                return

            # Удаляем пациента
            delete_patient(self.db_session, patient_id=patient_id)
            QMessageBox.information(self, "Успех", "Пациент успешно удален!")
            self.load_data()  # Обновляем таблицу
        except PermissionError as e:
            QMessageBox.critical(self, "Ошибка доступа", str(e))
        except Exception as e:
            print(f"Ошибка при удалении пациента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить пациента: {e}")

    def get_patient_id_from_row(self, row):
        """
        Получает ID пациента из строки таблицы.
        Использует скрытый столбец таблицы для хранения patient_id.
        """
        try:
            # Предполагается, что ID пациента хранится в первом (скрытом) столбце таблицы
            patient_id_item = self.table.item(row, 0)
            if not patient_id_item:
                raise ValueError("ID пациента не найден в таблице.")

            patient_id = patient_id_item.text()
            return int(patient_id)  # Преобразуем в целое число
        except Exception as e:
            print(f"Ошибка при получении ID пациента из строки {row}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить ID пациента: {e}")
            return None



class DateInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите дату")
        layout = QVBoxLayout()

        # Создаем виджет для выбора даты
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())  # Устанавливаем текущую дату по умолчанию
        layout.addWidget(self.date_edit)

        # Кнопка "Сохранить"
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.accept)  # Закрывает диалог с результатом "Accepted"
        layout.addWidget(save_button)

        self.setLayout(layout)

    def get_date(self):
        """
        Возвращает выбранную дату в формате строки 'YYYY-MM-DD'.
        """
        return self.date_edit.date().toString("yyyy-MM-dd")