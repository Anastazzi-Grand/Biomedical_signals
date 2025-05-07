from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, \
    QInputDialog
from services.patient_activity_service import (
    get_patient_activities_by_fio,
    create_patient_activity,
    update_patient_activity,
    delete_patient_activity,
)

class PatientActivityWidget(QWidget):
    def __init__(self, db_session, patient_fio):
        super().__init__()
        self.db_session = db_session
        self.patient_fio = patient_fio
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию активности...")
        self.search_input.textChanged.connect(self.filter_activities)
        layout.addWidget(self.search_input)

        # Таблица
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)

        # Кнопки
        self.add_button = QPushButton("Добавить активность")
        self.add_button.clicked.connect(self.add_activity)
        layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать активность")
        self.edit_button.clicked.connect(self.edit_activity)
        layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить активность")
        self.delete_button.clicked.connect(self.delete_activity)
        layout.addWidget(self.delete_button)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_data(self):
        activities = get_patient_activities_by_fio(self.db_session, self.patient_fio)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Название", "Описание"])
        self.table.setRowCount(len(activities))
        for row, activity in enumerate(activities):
            self.table.setItem(row, 0, QTableWidgetItem(activity["activityname"]))
            self.table.setItem(row, 1, QTableWidgetItem(activity["description"]))

    def filter_activities(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            activity_name = self.table.item(row, 0).text().lower()
            if search_text in activity_name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def add_activity(self):
        # Открываем диалог для добавления новой активности
        activity_name, ok = QInputDialog.getText(self, "Добавить активность", "Введите название активности:")
        if ok and activity_name:
            try:
                create_patient_activity(self.db_session, self.patient_fio, activity_name)
                self.load_data()  # Обновляем таблицу
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def edit_activity(self):
        # Получаем выбранную строку
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите активность для редактирования.")
            return

        # Получаем данные из таблицы
        activity_name = self.table.item(selected_row, 0).text()
        new_activity_name, ok = QInputDialog.getText(
            self, "Редактировать активность", "Введите новое название активности:", text=activity_name
        )
        if ok and new_activity_name:
            try:
                activity_id = self.get_activity_id_from_row(selected_row)
                update_patient_activity(self.db_session, activity_id, activityname=new_activity_name)
                self.load_data()  # Обновляем таблицу
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def delete_activity(self):
        # Получаем выбранную строку
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите активность для удаления.")
            return

        # Удаляем активность
        try:
            activity_id = self.get_activity_id_from_row(selected_row)
            delete_patient_activity(self.db_session, activity_id)
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def get_activity_id_from_row(self, row):
        # Здесь нужно реализовать логику получения ID активности из строки таблицы
        # Например, можно хранить ID в скрытом столбце таблицы
        pass

    def go_back(self):
        self.close()
