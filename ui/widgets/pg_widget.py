from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

class PGDataWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        from database.models import PG_data  # Импортируем модель
        pg_data_records = self.db_session.query(PG_data).all()
        self.table.setRowCount(len(pg_data_records))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "D1", "D2", "Amplitude"])
        for row, record in enumerate(pg_data_records):
            self.table.setItem(row, 0, QTableWidgetItem(str(record.pgdataid)))
            self.table.setItem(row, 1, QTableWidgetItem(str(record.d1)))
            self.table.setItem(row, 2, QTableWidgetItem(str(record.d2)))
            self.table.setItem(row, 3, QTableWidgetItem(str(record.amplitude or "")))