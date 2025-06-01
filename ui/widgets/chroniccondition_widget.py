from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox, QInputDialog, QLineEdit
from services.chronic_condition_service import (
    create_chronic_condition,
    get_chronic_conditions_with_details,
    search_chronic_conditions_by_patient_fio,
    update_chronic_condition,
    delete_chronic_condition
)
from ui.widgets.date_widget import DateInputDialog


class ChronicConditionWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()

        # Панель поиска (поле ввода + кнопка)
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ФИО пациента для поиска")
        self.search_input.returnPressed.connect(self.filter_by_patient)  # Обработка Enter
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.filter_by_patient)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Таблица данных
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # ID, Название болезни, Дата диагноза, Примечания, Пациент (ФИО, дата рождения)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название болезни", "Дата диагноза", "Примечания", "Пациент (ФИО, дата рождения)"
        ])
        self.table.setColumnHidden(0, True)  # Скрываем столбец ID
        layout.addWidget(self.table)

        # Кнопки CRUD
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_chronic_condition)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_chronic_condition)
        button_layout.addWidget(delete_button)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Загрузка данных при создании виджета
        self.load_data()

    def load_data(self, patient_fio=None):
        """Загрузка данных хронических заболеваний с возможностью фильтрации по пациенту."""
        try:
            if patient_fio:
                conditions = search_chronic_conditions_by_patient_fio(self.db_session, patient_fio)
            else:
                conditions = get_chronic_conditions_with_details(self.db_session)

            # Очищаем таблицу
            self.table.clearContents()
            self.table.setRowCount(len(conditions))

            # Заполняем таблицу данными
            for row, condition in enumerate(conditions):
                self.table.setItem(row, 0, QTableWidgetItem(str(condition["chronicid"])))
                self.table.setItem(row, 1, QTableWidgetItem(condition["conditionname"]))
                self.table.setItem(row, 2, QTableWidgetItem(
                    str(condition["diagnosisdate"]) if condition["diagnosisdate"] else ""))
                self.table.setItem(row, 3, QTableWidgetItem(condition["remarks"] or ""))

                # Создаем выпадающий список для пациента
                combo_box = QComboBox()
                patients = self.get_patients_list()  # Получаем список всех пациентов
                combo_box.addItems(patients)

                # Устанавливаем текущее значение в выпадающем списке
                if condition["patient_fio"]:
                    current_patient_info = f"{condition['patient_fio']} ({condition['patient_birthdate']})"
                    if current_patient_info in patients:  # Проверяем, есть ли такой пациент в списке
                        combo_box.setCurrentText(current_patient_info)

                combo_box.setProperty("row", row)  # Сохраняем текущую строку в данных комбобокса
                self.table.setCellWidget(row, 4, combo_box)

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def get_patients_list(self):
        """Получение списка пациентов для выпадающего списка."""
        try:
            from services.patient_service import get_patients_with_details

            patients = get_patients_with_details(self.db_session)
            return [
                f"{patient['patient_fio']} ({patient['patient_birthdate']})"
                for patient in patients
            ]
        except Exception as e:
            print(f"Ошибка при загрузке пациентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список пациентов: {e}")
            return []

    def filter_by_patient(self):
        """Фильтрация данных по ФИО пациента."""
        query = self.search_input.text().strip()
        if not query:
            self.load_data()  # Если поле поиска пустое, загружаем все данные
        else:
            self.load_data(patient_fio=query)

    def add_chronic_condition(self):
        """Добавление новой хронической болезни."""
        try:
            # Выбор пациента из выпадающего списка
            patients = self.get_patients_list()
            selected_patient, ok = QInputDialog.getItem(
                self, "Добавить хроническое заболевание", "Выберите пациента:", patients, editable=False
            )
            if not ok:
                return

            # Извлечение ФИО пациента из выбранного значения
            patient_fio = selected_patient.split(" (")[0]

            # Ввод названия болезни
            conditionname, ok = QInputDialog.getText(self, "Добавить хроническое заболевание",
                                                     "Введите название болезни:")
            if not ok or not conditionname:
                return

            # Выбор даты диагноза через календарь
            date_dialog = DateInputDialog(self)
            if date_dialog.exec():
                diagnosisdate = date_dialog.get_date()
            else:
                return

            # Ввод примечаний
            remarks, ok = QInputDialog.getText(self, "Добавить хроническое заболевание",
                                               "Введите примечания (опционально):")
            if not ok:
                remarks = None

            # Создаем новую запись
            create_chronic_condition(
                db=self.db_session,
                patient_fio=patient_fio,
                conditionname=conditionname,
                diagnosisdate=diagnosisdate,
                remarks=remarks
            )

            QMessageBox.information(self, "Успех", "Хроническое заболевание успешно добавлено!")
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def delete_chronic_condition(self):
        """Удаление выбранной хронической болезни."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления.")
            return

        chronicid = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить хроническое заболевание с ID {chronicid}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_chronic_condition(self.db_session, chronicid)
                QMessageBox.information(self, "Успех", "Хроническое заболевание успешно удалено.")
                self.load_data()  # Обновляем таблицу
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def save_changes(self):
        """Сохранение изменений, внесенных в таблицу, в базу данных."""
        try:
            for row in range(self.table.rowCount()):
                chronicid = int(self.table.item(row, 0).text())
                conditionname = self.table.item(row, 1).text()
                diagnosisdate = self.table.item(row, 2).text()
                remarks = self.table.item(row, 3).text()

                # Получаем текущее значение пациента из QComboBox
                combo_box = self.table.cellWidget(row, 4)
                if not combo_box:
                    continue
                patient_info = combo_box.currentText()
                patient_fio = patient_info.split(" (")[0] if patient_info else None

                # Обновляем данные в базе
                update_chronic_condition(
                    db=self.db_session,
                    chronicid=chronicid,
                    patient_fio=patient_fio,
                    conditionname=conditionname,
                    diagnosisdate=diagnosisdate if diagnosisdate else None,
                    remarks=remarks if remarks else None
                )

            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
