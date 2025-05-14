from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox, QInputDialog, QComboBox, QDateEdit, QDialog
from datetime import date

from ui.widgets.date_widget import DateInputDialog


class SessionWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.sessions_data = []  # Хранение данных о сеансах
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()

        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите дату или ФИО пациента")
        self.search_input.returnPressed.connect(self.search_sessions)
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_sessions)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Таблица
        self.table = QTableWidget()
        self.load_data()
        layout.addWidget(self.table)

        # Кнопки
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_session)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_selected_session)
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_data(self, sessions=None):
        """Загрузка данных в таблицу."""
        try:
            from services.sessions_service import get_sessions_with_details

            if not sessions:
                sessions = get_sessions_with_details(self.db_session)
            self.sessions_data = sessions

            # Очищаем таблицу
            self.table.clearContents()
            self.table.setRowCount(len(sessions))
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "ID", "Дата", "Начало", "Конец", "Пациент", "Врач", "Лаборатория"
            ])

            # Заполняем таблицу данными
            for row, session in enumerate(sessions):
                self.table.setItem(row, 0, QTableWidgetItem(str(session["sessionid"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(session["session_date"])))
                self.table.setItem(row, 2, QTableWidgetItem(str(session["session_starttime"])))
                self.table.setItem(row, 3, QTableWidgetItem(str(session["session_endtime"])))

                # Выпадающий список для пациента
                patient_combo = QComboBox()
                patient_combo.addItems([s["patient_fio"] for s in sessions])
                patient_combo.setCurrentText(session["patient_fio"])
                self.table.setCellWidget(row, 4, patient_combo)

                # Выпадающий список для врача
                doctor_combo = QComboBox()
                doctor_combo.addItems([s["doctor_fio"] for s in sessions])
                doctor_combo.setCurrentText(session["doctor_fio"])
                self.table.setCellWidget(row, 5, doctor_combo)

                # Выпадающий список для лаборатории
                lab_combo = QComboBox()
                lab_combo.addItems([s["lab_name"] for s in sessions])
                lab_combo.setCurrentText(session["lab_name"])
                self.table.setCellWidget(row, 6, lab_combo)

            # Скрываем первый столбец (ID сеанса)
            self.table.setColumnHidden(0, True)

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def save_changes(self):
        """Сохранение изменений в базе данных."""
        try:
            from services.sessions_service import update_session

            for row in range(self.table.rowCount()):
                session_id = self.get_session_id_from_row(row)
                if not session_id:
                    continue

                session_date = self.table.item(row, 1).text()
                start_time = self.table.item(row, 2).text()
                end_time = self.table.item(row, 3).text()

                # Получение значений из выпадающих списков
                patient_fio = self.table.cellWidget(row, 4).currentText()
                doctor_fio = self.table.cellWidget(row, 5).currentText()
                lab_name = self.table.cellWidget(row, 6).currentText()

                # Обновляем данные сеанса
                update_session(
                    self.db_session,
                    session_id=session_id,
                    session_date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                    patient_fio=patient_fio,
                    doctor_fio=doctor_fio,
                    lab_name=lab_name
                )

            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
            self.load_data()  # Обновляем таблицу

        except PermissionError as e:
            QMessageBox.critical(self, "Ошибка доступа", str(e))
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {e}")

    def add_session(self):
        """Добавление нового сеанса."""
        try:
            from services.sessions_service import create_session

            # Выбор даты через календарь
            date_dialog = DateInputDialog(self)
            if not date_dialog.exec():
                return
            session_date = date_dialog.get_date()

            # Выбор времени начала через диалог
            start_time, ok = QInputDialog.getText(self, "Добавить сеанс", "Введите время начала (ЧЧ:ММ):")
            if not ok or not self.validate_time(start_time):
                QMessageBox.warning(self, "Ошибка", "Неверный формат времени.")
                return

            # Выбор времени окончания через диалог
            end_time, ok = QInputDialog.getText(self, "Добавить сеанс", "Введите время окончания (ЧЧ:ММ):")
            if not ok or not self.validate_time(end_time):
                QMessageBox.warning(self, "Ошибка", "Неверный формат времени.")
                return

            # Выбор пациента из выпадающего списка
            patients = self.get_all_patients()
            patient_fio, ok = QInputDialog.getItem(self, "Выберите пациента", "Пациент:", patients, editable=False)
            if not ok:
                return

            # Выбор врача из выпадающего списка
            doctors = self.get_all_doctors()
            doctor_fio, ok = QInputDialog.getItem(self, "Выберите врача", "Врач:", doctors, editable=False)
            if not ok:
                return

            # Выбор лаборатории из выпадающего списка
            labs = self.get_all_labs()
            lab_name, ok = QInputDialog.getItem(self, "Выберите лабораторию", "Лаборатория:", labs, editable=False)
            if not ok:
                return

            # Создаем новый сеанс
            create_session(
                self.db_session,
                session_date=session_date,
                start_time=start_time,
                end_time=end_time,
                patient_fio=patient_fio,
                doctor_fio=doctor_fio,
                lab_name=lab_name
            )

            QMessageBox.information(self, "Успех", "Сеанс успешно добавлен!")
            self.load_data()  # Обновляем таблицу

        except Exception as e:
            print(f"Ошибка при добавлении сеанса: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить сеанс: {e}")

    def validate_time(self, time_str):
        """Проверка корректности формата времени (ЧЧ:ММ)."""
        try:
            hours, minutes = map(int, time_str.split(":"))
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except ValueError:
            return False

    def get_all_patients(self):
        """Получение списка всех пациентов."""
        from services.patient_service import get_patients_with_details
        sessions = get_patients_with_details(self.db_session)
        return list(set(session["patient_fio"] for session in sessions))

    def get_all_doctors(self):
        """Получение списка всех врачей."""
        from services.doctor_service import get_doctors_with_details
        sessions = get_doctors_with_details(self.db_session)
        return list(set(session["doctor_fio"] for session in sessions))

    def get_all_labs(self):
        """Получение списка всех лабораторий."""
        from services.laboratory_service import get_all_laboratories_with_details
        sessions = get_all_laboratories_with_details(self.db_session)
        return list(set(session["lab_name"] for session in sessions))

    def delete_selected_session(self):
        """Удаление выбранного сеанса."""
        try:
            from services.sessions_service import delete_session

            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Внимание", "Выберите строку для удаления.")
                return

            session_id = self.get_session_id_from_row(selected_row)
            if not session_id:
                return

            # Удаляем сеанс
            delete_session(self.db_session, session_id)
            QMessageBox.information(self, "Успех", "Сеанс успешно удален!")
            self.load_data()  # Обновляем таблицу

        except PermissionError as e:
            QMessageBox.critical(self, "Ошибка доступа", str(e))
        except Exception as e:
            print(f"Ошибка при удалении сеанса: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить сеанс: {e}")

    def search_sessions(self):
        """Поиск сеансов по дате или ФИО пациента."""
        try:
            from services.sessions_service import search_sessions_by_date, get_sessions_by_patient_fio

            query = self.search_input.text().strip()
            if not query:
                self.load_data()
                return

            # Проверяем, является ли запрос датой
            try:
                session_date = date.fromisoformat(query)
                sessions = search_sessions_by_date(self.db_session, session_date)
            except ValueError:
                # Если не дата, ищем по ФИО пациента
                sessions = get_sessions_by_patient_fio(self.db_session, query)

            if not sessions:
                QMessageBox.information(self, "Результат", "Сеансы не найдены.")
                return

            self.load_data(sessions)

        except Exception as e:
            print(f"Ошибка при поиске сеансов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск: {e}")

    def get_session_id_from_row(self, row):
        """Получение ID сеанса из строки таблицы."""
        try:
            session_id = self.table.item(row, 0).text()
            return int(session_id)
        except Exception as e:
            print(f"Ошибка при получении ID сеанса из строки {row}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить ID сеанса: {e}")
            return None
