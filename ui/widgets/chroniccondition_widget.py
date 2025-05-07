from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit
from services.chronic_condition_service import search_chronic_conditions_by_patient_fio

class ChronicConditionWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО пациента...")
        self.search_input.textChanged.connect(self.filter_conditions)
        layout.addWidget(self.search_input)

        # Таблица
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        conditions = search_chronic_conditions_by_patient_fio(self.db_session, "")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Заболевание", "Дата диагноза", "Примечания", "ФИО пациента"])
        self.table.setRowCount(len(conditions))
        for row, condition in enumerate(conditions):
            self.table.setItem(row, 0, QTableWidgetItem(condition["condition_name"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(condition["diagnosis_date"] or "")))
            self.table.setItem(row, 2, QTableWidgetItem(condition["remarks"] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(condition["patient_fio"]))

    def filter_conditions(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            patient_fio = self.table.item(row, 3).text().lower()
            if search_text in patient_fio:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
