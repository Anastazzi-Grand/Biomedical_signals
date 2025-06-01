from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox, QInputDialog, QComboBox
from services.diagnosis_service import (
    create_diagnosis,
    get_diagnoses_with_details,
    search_diagnoses_by_patient_fio,
    update_diagnosis,
    delete_diagnosis
)
from ui.widgets.date_widget import DateInputDialog


class DiagnosisWidget(QWidget):
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
        self.table.setColumnCount(6)  # ID, Название диагноза, Описание, Дата, Пациент, Врач
        self.table.setHorizontalHeaderLabels([
            "ID", "Название диагноза", "Описание", "Дата", "Пациент (ФИО, дата рождения)", "Врач (ФИО, дата рождения)"
        ])
        self.table.setColumnHidden(0, True)  # Скрываем столбец ID
        layout.addWidget(self.table)

        # Кнопки CRUD
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_diagnosis)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_diagnosis)
        button_layout.addWidget(delete_button)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Загрузка данных при создании виджета
        self.load_data()

    def load_data(self, patient_fio=None):
        """Загрузка данных диагнозов с возможностью фильтрации по пациенту."""
        try:
            if patient_fio:
                diagnoses = search_diagnoses_by_patient_fio(self.db_session, patient_fio)
            else:
                diagnoses = get_diagnoses_with_details(self.db_session)

            # Очищаем таблицу
            self.table.clearContents()
            self.table.setRowCount(len(diagnoses))

            # Заполняем таблицу данными
            for row, diagnosis in enumerate(diagnoses):
                self.table.setItem(row, 0, QTableWidgetItem(str(diagnosis["diagnosisid"])))
                self.table.setItem(row, 1, QTableWidgetItem(diagnosis["diagnosisname"] or ""))
                self.table.setItem(row, 2, QTableWidgetItem(diagnosis["description"]))
                self.table.setItem(row, 3, QTableWidgetItem(
                    str(diagnosis["dateofdiagnosis"]) if diagnosis["dateofdiagnosis"] else ""))

                # Выпадающий список для пациента
                patient_combo = QComboBox()
                patients = self.get_patients_list()
                patient_combo.addItems(patients)
                current_patient_info = f"{diagnosis['patient_fio']} ({diagnosis['patient_birthdate']})" if diagnosis[
                                                                                                               'patient_fio'] and \
                                                                                                           diagnosis[
                                                                                                               'patient_birthdate'] else ""
                if current_patient_info in patients:
                    patient_combo.setCurrentText(current_patient_info)
                patient_combo.setProperty("row", row)
                self.table.setCellWidget(row, 4, patient_combo)

                # Выпадающий список для врача
                doctor_combo = QComboBox()
                doctors = self.get_doctors_list()
                doctor_combo.addItems(doctors)
                current_doctor_info = f"{diagnosis['doctor_fio']} ({diagnosis['doctor_birthdate']})" if diagnosis[
                                                                                                            'doctor_fio'] and \
                                                                                                        diagnosis[
                                                                                                            'doctor_birthdate'] else ""
                if current_doctor_info in doctors:
                    doctor_combo.setCurrentText(current_doctor_info)
                doctor_combo.setProperty("row", row)
                self.table.setCellWidget(row, 5, doctor_combo)

            # Автоматическая настройка ширины столбцов
            self.table.resizeColumnsToContents()

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

    def get_doctors_list(self):
        """Получение списка врачей для выпадающего списка."""
        try:
            from services.doctor_service import get_doctors_with_details

            doctors = get_doctors_with_details(self.db_session)
            return [
                f"{doctor['doctor_fio']} ({doctor['doctor_birthdate']})"
                for doctor in doctors
            ]
        except Exception as e:
            print(f"Ошибка при загрузке врачей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список врачей: {e}")
            return []

    def filter_by_patient(self):
        """Фильтрация данных по ФИО пациента."""
        query = self.search_input.text().strip()
        if not query:
            self.load_data()  # Если поле поиска пустое, загружаем все данные
        else:
            self.load_data(patient_fio=query)

    def add_diagnosis(self):
        """Добавление нового диагноза."""
        try:
            # Выбор пациента из выпадающего списка
            patients = self.get_patients_list()
            selected_patient, ok = QInputDialog.getItem(
                self, "Добавить диагноз", "Выберите пациента:", patients, editable=False
            )
            if not ok:
                return

            # Извлечение ФИО пациента из выбранного значения
            patient_fio = selected_patient.split(" (")[0]

            # Ввод названия диагноза
            diagnosis_name, ok = QInputDialog.getText(self, "Добавить диагноз", "Введите название диагноза:")
            if not ok:
                return

            # Ввод описания диагноза
            description, ok = QInputDialog.getText(self, "Добавить диагноз", "Введите описание диагноза:")
            if not ok or not description:
                return

            # Выбор даты диагноза через календарь
            date_dialog = DateInputDialog(self)
            if date_dialog.exec():
                date_of_diagnosis = date_dialog.get_date()
            else:
                return

            # Выбор врача из выпадающего списка
            doctors = self.get_doctors_list()
            selected_doctor, ok = QInputDialog.getItem(
                self, "Добавить диагноз", "Выберите врача:", doctors, editable=False
            )
            if not ok:
                return

            # Извлечение ФИО врача из выбранного значения
            doctor_fio = selected_doctor.split(" (")[0] if selected_doctor else None

            # Создаем новый диагноз
            create_diagnosis(
                db=self.db_session,
                patient_fio=patient_fio,
                diagnosisname=diagnosis_name,
                description=description,
                dateofdiagnosis=date_of_diagnosis,
                doctor_fio=doctor_fio
            )

            QMessageBox.information(self, "Успех", "Диагноз успешно добавлен!")
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def delete_diagnosis(self):
        """Удаление выбранного диагноза."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления.")
            return

        diagnosisid = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить диагноз с ID {diagnosisid}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_diagnosis(self.db_session, diagnosisid)
                QMessageBox.information(self, "Успех", "Диагноз успешно удален.")
                self.load_data()  # Обновляем таблицу
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def save_changes(self):
        """Сохранение изменений, внесенных в таблицу, в базу данных."""
        try:
            for row in range(self.table.rowCount()):
                diagnosisid = int(self.table.item(row, 0).text())
                diagnosisname = self.table.item(row, 1).text()
                description = self.table.item(row, 2).text()
                dateofdiagnosis = self.table.item(row, 3).text()

                # Получаем текущее значение пациента из QComboBox
                patient_combo = self.table.cellWidget(row, 4)
                if patient_combo:
                    patient_info = patient_combo.currentText()
                    patient_fio = patient_info.split(" (")[0] if patient_info else None
                else:
                    patient_fio = None

                # Получаем текущее значение врача из QComboBox
                doctor_combo = self.table.cellWidget(row, 5)
                if doctor_combo:
                    doctor_info = doctor_combo.currentText()
                    doctor_fio = doctor_info.split(" (")[0] if doctor_info else None
                else:
                    doctor_fio = None

                # Обновляем данные в базе
                update_diagnosis(
                    db=self.db_session,
                    diagnosisid=diagnosisid,
                    patient_fio=patient_fio,
                    diagnosis_name=diagnosisname,
                    description=description,
                    date_of_diagnosis=dateofdiagnosis if dateofdiagnosis else None,
                    doctor_fio=doctor_fio
                )

            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
