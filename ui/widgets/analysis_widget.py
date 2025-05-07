from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QMessageBox
from database.services import (
    create_analysis_result,
    get_analysis_results_with_details,
    update_analysis_result,
    delete_analysis_result,
)


class AnalysisResultWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по дате или времени сеанса...")
        self.search_input.textChanged.connect(self.filter_results)
        layout.addWidget(self.search_input)

        # Таблица
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)

        # Кнопки
        self.add_button = QPushButton("Добавить результат анализа")
        self.add_button.clicked.connect(self.add_result)
        layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать результат анализа")
        self.edit_button.clicked.connect(self.edit_result)
        layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить результат анализа")
        self.delete_button.clicked.connect(self.delete_result)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def load_data(self):
        results = get_analysis_results_with_details(self.db_session)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Дата сеанса", "Время начала", "RR-анализ", "DU-анализ"]
        )
        self.table.setRowCount(len(results))
        for row, result in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(result["session_date"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(result["session_starttime"])))
            self.table.setItem(row, 2, QTableWidgetItem(result["rr_analysis"]))
            self.table.setItem(row, 3, QTableWidgetItem(result["du_analysis"]))

    def filter_results(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            session_date = self.table.item(row, 0).text().lower()
            session_time = self.table.item(row, 1).text().lower()
            if search_text in session_date or search_text in session_time:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def add_result(self):
        # Открываем диалог для добавления нового результата анализа
        session_date, ok = QInputDialog.getText(self, "Добавить результат", "Введите дату сеанса (YYYY-MM-DD):")
        if not ok or not session_date:
            return

        session_starttime, ok = QInputDialog.getText(self, "Добавить результат", "Введите время начала сеанса (HH:MM:SS):")
        if not ok or not session_starttime:
            return

        rr_analysis, ok = QInputDialog.getText(self, "Добавить результат", "Введите RR-анализ:")
        if not ok or not rr_analysis:
            return

        du_analysis, ok = QInputDialog.getText(self, "Добавить результат", "Введите DU-анализ:")
        if not ok or not du_analysis:
            return

        try:
            create_analysis_result(
                self.db_session,
                session_date=session_date,
                session_starttime=session_starttime,
                rr_analysis=rr_analysis,
                du_analysis=du_analysis,
            )
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def edit_result(self):
        # Получаем выбранную строку
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите результат для редактирования.")
            return

        # Получаем данные из таблицы
        session_date = self.table.item(selected_row, 0).text()
        session_starttime = self.table.item(selected_row, 1).text()
        rr_analysis = self.table.item(selected_row, 2).text()
        du_analysis = self.table.item(selected_row, 3).text()

        new_rr_analysis, ok = QInputDialog.getText(
            self, "Редактировать результат", "Введите новый RR-анализ:", text=rr_analysis
        )
        if not ok:
            return

        new_du_analysis, ok = QInputDialog.getText(
            self, "Редактировать результат", "Введите новый DU-анализ:", text=du_analysis
        )
        if not ok:
            return

        try:
            update_analysis_result(
                self.db_session,
                analysisresultid=self.get_result_id_from_row(selected_row),
                session_date=session_date,
                session_starttime=session_starttime,
                rr_analysis=new_rr_analysis,
                du_analysis=new_du_analysis,
            )
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def delete_result(self):
        # Получаем выбранную строку
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите результат для удаления.")
            return

        try:
            delete_analysis_result(self.db_session, self.get_result_id_from_row(selected_row))
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def get_result_id_from_row(self, row):
        # Здесь нужно реализовать логику получения ID результата анализа из строки таблицы
        # Например, можно хранить ID в скрытом столбце таблицы
        pass
