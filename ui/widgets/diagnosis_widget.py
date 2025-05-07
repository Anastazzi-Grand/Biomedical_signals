from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit
from services.diagnosis_service import search_diagnoses_by_patient_fio

class DiagnosisWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО пациента...")
        self.search_input.textChanged.connect(self.filter_diagnoses)
        layout.addWidget(self.search_input)

        # Таблица
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        diagnoses = search_diagnoses_by_patient_fio(self.db_session, "")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ФИО пациента", "Название", "Описание", "Дата", "ФИО врача"])
        self.table.setRowCount(len(diagnoses))
        for row, diagnosis in enumerate(diagnoses):
            self.table.setItem(row, 0, QTableWidgetItem(diagnosis["patient_fio"]))
            self.table.setItem(row, 1, QTableWidgetItem(diagnosis["diagnosisname"]))
            self.table.setItem(row, 2, QTableWidgetItem(diagnosis["description"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(diagnosis["dateofdiagnosis"])))
            self.table.setItem(row, 4, QTableWidgetItem(diagnosis["doctor_fio"] or ""))

    def filter_diagnoses(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            patient_fio = self.table.item(row, 0).text().lower()
            if search_text in patient_fio:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
