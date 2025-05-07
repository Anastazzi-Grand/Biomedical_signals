from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from services.chronic_condition_service import search_chronic_conditions_by_patient_fio
from services.patient_activity_service import get_all_patient_activities_with_details
from services.diagnosis_service import search_diagnoses_by_patient_fio
from services.treatment_recommendation_service import get_all_treatment_recommendations_with_details
from services.analysis_service import get_analysis_results_with_details


class DetailWindow(QMainWindow):
    def __init__(self, db_session, detail_type, patient_fio=None):
        """
        :param db_session: Сессия базы данных
        :param detail_type: Тип данных для отображения (например, "Хронические заболевания")
        :param patient_fio: ФИО пациента (опционально)
        """
        super().__init__()
        self.db_session = db_session
        self.detail_type = detail_type
        self.patient_fio = patient_fio
        self.setWindowTitle(f"Детали: {detail_type}")
        self.setGeometry(200, 200, 800, 600)

        # Главный виджет и макет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Заголовок
        self.title_label = QLabel(f"Детали: {detail_type}")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Поле поиска (только для хронических заболеваний, диагнозов и рекомендаций по лечению)
        if detail_type in ["Хронические заболевания", "Диагнозы", "Рекомендации по лечению"]:
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по ФИО пациента...")
            self.search_input.textChanged.connect(self.filter_data)
            self.layout.addWidget(self.search_input)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.close)
        self.layout.addWidget(self.back_button)

        # Загрузка данных
        self.load_data()

    def load_data(self):
        """
        Загружает данные в таблицу в зависимости от типа деталей.
        """
        if self.detail_type == "Хронические заболевания":
            self.load_chronic_conditions()
        elif self.detail_type == "Активности пациента":
            self.load_patient_activities()
        elif self.detail_type == "Результаты анализа":
            self.load_analysis_results()
        elif self.detail_type == "Диагнозы":
            self.load_diagnoses()
        elif self.detail_type == "Рекомендации по лечению":
            self.load_treatment_recommendations()
        else:
            self.show_error_message("Неизвестный тип данных.")

    def load_chronic_conditions(self):
        """
        Загружает хронические заболевания пациентов.
        """
        conditions = search_chronic_conditions_by_patient_fio(self.db_session, self.patient_fio or "")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Заболевание", "Дата диагноза", "Примечания", "ФИО пациента"])
        self.table.setRowCount(len(conditions))

        for row, condition in enumerate(conditions):
            condition_name = condition["condition_name"]
            diagnosis_date = condition["diagnosis_date"] or ""
            remarks = condition["remarks"] or ""
            patient_fio = condition["patient_fio"]

            self.table.setItem(row, 0, QTableWidgetItem(condition_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(diagnosis_date)))
            self.table.setItem(row, 2, QTableWidgetItem(remarks))
            self.table.setItem(row, 3, QTableWidgetItem(patient_fio))

    def load_patient_activities(self):
        """
        Загружает активности пациентов.
        """
        activities = get_all_patient_activities_with_details(self.db_session, self.patient_fio)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Вид активности", "Описание"])
        self.table.setRowCount(len(activities))

        for row, activity in enumerate(activities):
            activity_name = activity["activity_name"]
            description = activity["description"] or ""

            self.table.setItem(row, 0, QTableWidgetItem(activity_name))
            self.table.setItem(row, 1, QTableWidgetItem(description))

    def load_analysis_results(self):
        """
        Загружает результаты анализа.
        """
        results = get_analysis_results_with_details(self.db_session)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Дата сеанса", "RR-анализ", "DU-анализ", "ФИО пациента"])
        self.table.setRowCount(len(results))

        for row, result in enumerate(results):
            session_date = result["session_date"]
            rr_analysis = result["rr_analysis"]
            du_analysis = result["du_analysis"]
            patient_fio = result["patient_fio"]

            self.table.setItem(row, 0, QTableWidgetItem(str(session_date)))
            self.table.setItem(row, 1, QTableWidgetItem(rr_analysis))
            self.table.setItem(row, 2, QTableWidgetItem(du_analysis))
            self.table.setItem(row, 3, QTableWidgetItem(patient_fio))

    def load_diagnoses(self):
        """
        Загружает диагнозы пациентов.
        """
        diagnoses = search_diagnoses_by_patient_fio(self.db_session, self.patient_fio or "")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ФИО пациента", "Название", "Описание", "Дата", "ФИО врача"])
        self.table.setRowCount(len(diagnoses))

        for row, diagnosis in enumerate(diagnoses):
            patient_fio = diagnosis["patient_fio"]
            diagnosis_name = diagnosis["diagnosis_name"]
            description = diagnosis["description"] or ""
            date_of_diagnosis = diagnosis["date_of_diagnosis"]
            doctor_fio = diagnosis["doctor_fio"]

            self.table.setItem(row, 0, QTableWidgetItem(patient_fio))
            self.table.setItem(row, 1, QTableWidgetItem(diagnosis_name))
            self.table.setItem(row, 2, QTableWidgetItem(description))
            self.table.setItem(row, 3, QTableWidgetItem(str(date_of_diagnosis)))
            self.table.setItem(row, 4, QTableWidgetItem(doctor_fio))

    def load_treatment_recommendations(self):
        """
        Загружает рекомендации по лечению.
        """
        recommendations = get_all_treatment_recommendations_with_details(self.db_session)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Название диагноза", "План лечения", "Примечания"])
        self.table.setRowCount(len(recommendations))

        for row, recommendation in enumerate(recommendations):
            diagnosis_name = recommendation["diagnosisname"]
            treatment_plan = recommendation["treatmentplan"]
            additional_remarks = recommendation["additionalremarks"] or ""

            self.table.setItem(row, 0, QTableWidgetItem(diagnosis_name))
            self.table.setItem(row, 1, QTableWidgetItem(treatment_plan))
            self.table.setItem(row, 2, QTableWidgetItem(additional_remarks))

    def filter_data(self):
        """
        Фильтрует данные в таблице по ФИО пациента.
        """
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            patient_fio = self.table.item(row, 3).text().lower()  # Предполагается, что ФИО пациента в 4-м столбце
            if search_text in patient_fio:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def show_error_message(self, message):
        """
        Показывает сообщение об ошибке.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec()
