from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit
from services.treatment_recommendation_service import get_all_treatment_recommendations_with_details

class TreatmentRecommendationWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию диагноза...")
        self.search_input.textChanged.connect(self.filter_recommendations)
        layout.addWidget(self.search_input)

        # Таблица
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        recommendations = get_all_treatment_recommendations_with_details(self.db_session)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Название диагноза", "План лечения", "Примечания"])
        self.table.setRowCount(len(recommendations))
        for row, recommendation in enumerate(recommendations):
            self.table.setItem(row, 0, QTableWidgetItem(recommendation["diagnosisname"]))
            self.table.setItem(row, 1, QTableWidgetItem(recommendation["treatmentplan"]))
            self.table.setItem(row, 2, QTableWidgetItem(recommendation["additionalremarks"] or ""))

    def filter_recommendations(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            diagnosis_name = self.table.item(row, 0).text().lower()
            if search_text in diagnosis_name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
