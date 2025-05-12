from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox, QDialog

from ui.widgets.import_data_widget import ImportDataWidget


class ECSDataWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()

        # Панель поиска (выпадающий список + кнопка "Поиск")
        search_layout = QHBoxLayout()
        self.patient_combo = QComboBox()
        self.patient_combo.setPlaceholderText("Выберите пациента")
        self.load_patients()  # Загружаем список пациентов
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.filter_by_patient)
        search_layout.addWidget(self.patient_combo)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Таблица данных
        self.table = QTableWidget()
        self.load_data()  # Загружаем все данные по умолчанию
        layout.addWidget(self.table)

        # Кнопка "Добавить"
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.open_import_dialog)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def open_import_dialog(self):
        """Открытие диалогового окна для импорта данных."""
        print("Открытие диалогового окна для импорта данных.")
        dialog = ImportDataWidget(self.db_session, parent=self)
        result = dialog.exec()  # Открываем модальное окно
        if result == QDialog.DialogCode.Accepted:
            print("Диалог завершен успешно.")
            self.load_data()  # Обновляем таблицу после импорта данных
        else:
            print("Диалог закрыт без сохранения.")

    def load_patients(self):
        """Загрузка списка пациентов для выпадающего списка."""
        try:
            from services.sessions_service import get_sessions_with_details

            sessions = get_sessions_with_details(self.db_session)
            patients = list(set(session["patient_fio"] for session in sessions))
            self.patient_combo.addItems(patients)
        except Exception as e:
            print(f"Ошибка при загрузке пациентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список пациентов: {e}")

    def load_data(self, patient_fio=None):
        """Загрузка данных ECS_data с возможностью фильтрации по пациенту."""
        try:
            from services.ecs_service import get_ecs_data_with_details

            # Получаем данные ECS_data
            if patient_fio:
                ecs_data = [
                    data for data in get_ecs_data_with_details(self.db_session)
                    if data["patient_fio"] == patient_fio
                ]
            else:
                ecs_data = get_ecs_data_with_details(self.db_session)

            # Очищаем таблицу
            self.table.clearContents()
            self.table.setRowCount(len(ecs_data))
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "ID", "Дата сессии", "Начало", "ФИО пациента", "ФИО врача", "Длина RR", "Время RR"
            ])

            # Заполняем таблицу данными
            for row, data in enumerate(ecs_data):
                self.table.setItem(row, 0, QTableWidgetItem(str(data["ecsdataid"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(data["session_date"])))
                self.table.setItem(row, 2, QTableWidgetItem(str(data["session_starttime"])))
                self.table.setItem(row, 3, QTableWidgetItem(data["patient_fio"]))
                self.table.setItem(row, 4, QTableWidgetItem(data["doctor_fio"]))
                self.table.setItem(row, 5, QTableWidgetItem(str(data["rr_length"])))
                self.table.setItem(row, 6, QTableWidgetItem(str(data["rr_time"])))

            self.table.setColumnHidden(0, True)  # Скрываем столбец ID

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def filter_by_patient(self):
        """Фильтрация данных по выбранному пациенту."""
        selected_patient = self.patient_combo.currentText()
        if not selected_patient:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента.")
            return

        self.load_data(patient_fio=selected_patient)
