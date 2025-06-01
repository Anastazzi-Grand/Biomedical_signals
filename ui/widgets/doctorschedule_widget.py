from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox, QInputDialog, QComboBox
from services.doctor_schedule_service import (
    create_doctor_schedule,
    get_all_doctor_schedules,
    get_schedule_for_doctor,
    update_doctor_schedule,
    delete_doctor_schedule
)
from ui.widgets.date_widget import DateInputDialog


class DoctorScheduleWidget(QWidget):
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
        self.search_input.setPlaceholderText("Введите ФИО врача для поиска")
        self.search_input.returnPressed.connect(self.filter_by_doctor)  # Обработка Enter
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.filter_by_doctor)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Таблица данных
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # ID, ФИО врача, Дата, Начало, Конец
        self.table.setHorizontalHeaderLabels([
            "ID", "ФИО врача", "Дата", "Начало", "Конец"
        ])
        self.table.setColumnHidden(0, True)  # Скрываем столбец ID
        layout.addWidget(self.table)

        # Кнопки CRUD
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_doctor_schedule)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_doctor_schedule)
        button_layout.addWidget(delete_button)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Загрузка данных при создании виджета
        self.load_data()

    def load_data(self, doctor_fio=None):
        """Загрузка данных расписания врачей с возможностью фильтрации по врачу."""
        try:
            if doctor_fio:
                schedules = get_schedule_for_doctor(self.db_session, doctor_fio)
            else:
                schedules = get_all_doctor_schedules(self.db_session)

            # Очищаем таблицу
            self.table.clearContents()
            self.table.setRowCount(len(schedules))

            # Заполняем таблицу данными
            for row, schedule in enumerate(schedules):
                self.table.setItem(row, 0, QTableWidgetItem(str(schedule["scheduleid"])))
                self.table.setItem(row, 1, QTableWidgetItem(schedule["doctor_fio"]))
                self.table.setItem(row, 2, QTableWidgetItem(str(schedule["workdate"])))
                self.table.setItem(row, 3, QTableWidgetItem(str(schedule["starttime"])))
                self.table.setItem(row, 4, QTableWidgetItem(str(schedule["endtime"])))

            # Автоматическая настройка ширины столбцов
            self.table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def filter_by_doctor(self):
        """Фильтрация данных по ФИО врача."""
        query = self.search_input.text().strip()
        if not query:
            self.load_data()  # Если поле поиска пустое, загружаем все данные
        else:
            self.load_data(doctor_fio=query)

    def add_doctor_schedule(self):
        """Добавление нового расписания врача."""
        try:
            # Выбор врача из выпадающего списка
            doctors = self.get_doctors_list()
            selected_doctor, ok = QInputDialog.getItem(
                self, "Добавить расписание", "Выберите врача:", doctors, editable=False
            )
            if not ok:
                return

            # Извлечение ФИО врача из выбранного значения
            doctor_fio = selected_doctor

            # Выбор даты работы через календарь
            date_dialog = DateInputDialog(self)
            if date_dialog.exec():
                workdate = date_dialog.get_date()
            else:
                return

            # Ввод времени начала работы
            starttime, ok = QInputDialog.getText(self, "Добавить расписание", "Введите время начала работы (HH:MM):")
            if not ok or not starttime:
                return

            # Ввод времени окончания работы
            endtime, ok = QInputDialog.getText(self, "Добавить расписание", "Введите время окончания работы (HH:MM):")
            if not ok or not endtime:
                return

            # Создаем новое расписание
            create_doctor_schedule(
                db=self.db_session,
                doctor_fio=doctor_fio,
                workdate=workdate,
                starttime=starttime,
                endtime=endtime
            )

            QMessageBox.information(self, "Успех", "Расписание успешно добавлено!")
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def delete_doctor_schedule(self):
        """Удаление выбранного расписания врача."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления.")
            return

        scheduleid = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить расписание с ID {scheduleid}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_doctor_schedule(self.db_session, scheduleid)
                QMessageBox.information(self, "Успех", "Расписание успешно удалено.")
                self.load_data()  # Обновляем таблицу
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def save_changes(self):
        """Сохранение изменений, внесенных в таблицу, в базу данных."""
        try:
            for row in range(self.table.rowCount()):
                scheduleid = int(self.table.item(row, 0).text())
                doctor_fio = self.table.item(row, 1).text()
                workdate = self.table.item(row, 2).text()
                starttime = self.table.item(row, 3).text()
                endtime = self.table.item(row, 4).text()

                # Обновляем данные в базе
                update_doctor_schedule(
                    db=self.db_session,
                    scheduleid=scheduleid,
                    doctor_fio=doctor_fio,
                    workdate=workdate,
                    starttime=starttime,
                    endtime=endtime
                )

            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def get_doctors_list(self):
        """Получение списка врачей для выпадающего списка."""
        try:
            from services.doctor_service import get_doctors_with_details

            doctors = get_doctors_with_details(self.db_session)
            return [f"{doctor['doctor_fio']}" for doctor in doctors]
        except Exception as e:
            print(f"Ошибка при загрузке врачей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список врачей: {e}")
            return []
