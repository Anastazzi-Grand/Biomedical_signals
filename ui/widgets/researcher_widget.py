from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox


class ResearcherWidget(QWidget):
    def __init__(self, db_session, parent_widget=None):
        super().__init__()
        if not db_session:
            raise ValueError("Сессия базы данных не передана или недействительна.")
        self.db_session = db_session
        self.parent_widget = parent_widget  # Ссылка на родительский виджет
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Кнопки
        self.raw_data_button = QPushButton("Посмотреть сырые данные")
        self.raw_data_button.clicked.connect(self.view_raw_data)

        self.process_signals_button = QPushButton("Обработать сигналы")
        self.process_signals_button.clicked.connect(self.process_signals)

        self.processed_data_button = QPushButton("Посмотреть обработанные данные")
        self.processed_data_button.clicked.connect(self.view_processed_data)

        # Добавляем кнопки в макет
        layout.addWidget(self.raw_data_button)
        layout.addWidget(self.process_signals_button)
        layout.addWidget(self.processed_data_button)

        self.setLayout(layout)

    def view_raw_data(self):
        """Открывает диалоговое окно для выбора пациента и просмотра сырых данных."""
        try:
            from services.sessions_service import get_sessions_with_details

            # Получаем список всех сеансов
            sessions = get_sessions_with_details(self.db_session)
            if not sessions:
                QMessageBox.information(self, "Информация", "Нет доступных сеансов.")
                return

            # Формируем список пациентов
            patient_fios = [session["patient_fio"] for session in sessions]

            # Открываем диалоговое окно для выбора пациента
            selected_patient, ok = QInputDialog.getItem(
                self,
                "Выберите пациента",
                "Пациент:",
                patient_fios,
                editable=False
            )
            if not ok:
                return

            # Пока просто выводим сообщение о выбранном пациенте
            QMessageBox.information(self, "Сырые данные", f"Выбран пациент: {selected_patient}")
        except Exception as e:
            print(f"Ошибка при просмотре сырых данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def process_signals(self):
        """Открывает диалоговое окно для выбора пациента и обработки сигналов."""
        try:
            from services.sessions_service import get_sessions_with_details

            # Получаем список всех сеансов
            sessions = get_sessions_with_details(self.db_session)
            if not sessions:
                QMessageBox.information(self, "Информация", "Нет доступных сеансов.")
                return

            # Формируем список пациентов
            patient_fios = [session["patient_fio"] for session in sessions]

            # Открываем диалоговое окно для выбора пациента
            selected_patient, ok = QInputDialog.getItem(
                self,
                "Выберите пациента",
                "Пациент:",
                patient_fios,
                editable=False
            )
            if not ok:
                return

            # Пока просто выводим сообщение о выбранном пациенте
            QMessageBox.information(self, "Обработка сигналов", f"Выбран пациент: {selected_patient}")
        except Exception as e:
            print(f"Ошибка при обработке сигналов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось обработать сигналы: {e}")

    def view_processed_data(self):
        """Открывает диалоговое окно для выбора пациента и просмотра обработанных данных."""
        try:
            from services.sessions_service import get_sessions_with_details

            # Получаем список всех сеансов
            sessions = get_sessions_with_details(self.db_session)
            if not sessions:
                QMessageBox.information(self, "Информация", "Нет доступных сеансов.")
                return

            # Формируем список пациентов
            patient_fios = [session["patient_fio"] for session in sessions]

            # Открываем диалоговое окно для выбора пациента
            selected_patient, ok = QInputDialog.getItem(
                self,
                "Выберите пациента",
                "Пациент:",
                patient_fios,
                editable=False
            )
            if not ok:
                return

            # Пока просто выводим сообщение о выбранном пациенте
            QMessageBox.information(self, "Обработанные данные", f"Выбран пациент: {selected_patient}")
        except Exception as e:
            print(f"Ошибка при просмотре обработанных данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

