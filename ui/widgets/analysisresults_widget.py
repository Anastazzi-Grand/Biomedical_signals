from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox

class AnalysisResultWidget(QWidget):
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
        self.table.setColumnCount(7)  # ID, Дата сессии, Начало, ФИО пациента, ФИО врача, ЭКС данные, ПГ данные
        self.table.setHorizontalHeaderLabels([
            "ID", "Дата сессии", "Начало", "ФИО пациента", "ФИО врача", "ЭКС данные", "ПГ данные"
        ])
        self.table.setColumnHidden(0, True)  # Скрываем столбец ID
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Загрузка данных при создании виджета
        self.load_data()

    def load_data(self, patient_fio=None):
        """Загрузка данных analysis_result с возможностью фильтрации по пациенту."""
        try:
            from services.analysis_service import get_analysis_results_by_patient_fio

            # Если ФИО не указано, загружаем все данные
            if not patient_fio:
                analysis_results = get_analysis_results_by_patient_fio(self.db_session, "%")  # Используем % для частичного совпадения
            else:
                analysis_results = get_analysis_results_by_patient_fio(self.db_session, f"%{patient_fio}%")

            # Очищаем таблицу
            self.table.clearContents()
            self.table.setRowCount(len(analysis_results))

            # Заполняем таблицу данными
            for row, data in enumerate(analysis_results):
                self.table.setItem(row, 0, QTableWidgetItem(str(data["analysisresultid"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(data["session_date"])))
                self.table.setItem(row, 2, QTableWidgetItem(str(data["session_starttime"])))
                self.table.setItem(row, 3, QTableWidgetItem(data["patient_fio"]))
                self.table.setItem(row, 4, QTableWidgetItem(data["doctor_fio"]))
                self.table.setItem(row, 5, QTableWidgetItem(str(data["processed_ecs_data"])))
                self.table.setItem(row, 6, QTableWidgetItem(str(data["processed_pg_data"])))

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def filter_by_patient(self):
        """Фильтрация данных по ФИО пациента."""
        query = self.search_input.text().strip()
        if not query:
            # Если поле поиска пустое, загружаем все данные
            self.load_data(patient_fio=None)
        else:
            # Иначе фильтруем по ФИО
            self.load_data(patient_fio=query)
