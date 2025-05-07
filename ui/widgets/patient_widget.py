from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox


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
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        from database.models import Patient
        try:
            patients = self.db_session.query(Patient).all()
            self.table.setRowCount(len(patients))
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Дата рождения", "Адрес", "Телефон"])
            for row, patient in enumerate(patients):
                self.table.setItem(row, 0, QTableWidgetItem(str(patient.patientid)))
                self.table.setItem(row, 1, QTableWidgetItem(patient.patient_fio))
                self.table.setItem(row, 2, QTableWidgetItem(str(patient.patient_birthdate)))
                self.table.setItem(row, 3, QTableWidgetItem(patient.patient_address or ""))
                self.table.setItem(row, 4, QTableWidgetItem(patient.patient_phone or ""))
        except Exception as e:
            print(f"Ошибка при загрузке данных пациентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

