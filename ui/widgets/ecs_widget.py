from PyQt6.QtWidgets import QTableWidgetItem, QPushButton, QTableWidget, QLineEdit, QVBoxLayout, QWidget


class ECSDataWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.filter_data)
        layout.addWidget(self.search_input)

        # Таблица
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        from database.models import ECS_data
        ecs_data_records = self.db_session.query(ECS_data).all()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["RR Length", "RR Time"])
        self.table.setRowCount(len(ecs_data_records))
        for row, record in enumerate(ecs_data_records):
            self.table.setItem(row, 0, QTableWidgetItem(str(record.rr_length)))
            self.table.setItem(row, 1, QTableWidgetItem(str(record.rr_time)))

    def filter_data(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            rr_length = self.table.item(row, 0).text().lower()
            if search_text in rr_length:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

