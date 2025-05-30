import os

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QMessageBox, QDialog, QFileDialog
from PyQt6.QtCore import Qt  # Для доступа к флагам
from sqlalchemy import text


class ImportDataWidget(QDialog):
    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()

        # Поле для ввода пути к файлу
        file_path_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Введите путь к файлу")
        file_path_layout.addWidget(self.file_path_input)

        # Кнопка "Выбрать файл"
        select_file_button = QPushButton("Выбрать файл")
        select_file_button.clicked.connect(self.select_file)
        file_path_layout.addWidget(select_file_button)
        layout.addLayout(file_path_layout)

        # Выпадающий список для выбора сеанса
        session_layout = QHBoxLayout()
        self.session_combo = QComboBox()
        self.session_combo.setPlaceholderText("Выберите сеанс")
        self.load_sessions()  # Загружаем список сеансов
        session_layout.addWidget(self.session_combo)
        layout.addLayout(session_layout)

        # Кнопки "Добавить" и "Отмена"
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.import_data)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)  # Закрывает диалог с результатом Rejected
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_file(self):
        """Открывает диалоговое окно для выбора файла."""
        try:
            print("Метод select_file вызван")  # Отладочный вывод

            # Опции для диалогового окна
            options = QFileDialog.Option.DontUseNativeDialog  # Пример опции
            # Если опций нет, можно передать None:
            # options = None

            initial_dir = "C:\\Program Files\\PostgreSQL\\16\\data\\files"
            if not os.path.exists(initial_dir):
                initial_dir = ""  # Используем домашнюю директорию, если указанная не существует

            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите файл",
                initial_dir,
                "Текстовые файлы (*.txt);;Все файлы (*)",
                options=options
            )
            if file_name:
                self.file_path_input.setText(file_name)
        except Exception as e:
            print(f"Ошибка при выборе файла: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось выбрать файл: {e}")

    def load_sessions(self):
        """Загрузка списка сеансов для выпадающего списка."""
        try:
            from services.sessions_service import get_sessions_with_details

            sessions = get_sessions_with_details(self.db_session)
            for session in sessions:
                display_text = (
                    f"{session['session_date']} {session['session_starttime']} - "
                    f"{session['session_endtime']} | "
                    f"Пациент: {session['patient_fio']} | "
                    f"Врач: {session['doctor_fio']} | "
                    f"Лаборатория: {session['lab_name']}"
                )
                self.session_combo.addItem(display_text, userData=session["sessionid"])
        except Exception as e:
            print(f"Ошибка при загрузке сеансов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список сеансов: {e}")

    def import_data(self):
        """Импорт данных из файла в таблицы PG_data и ECS_data."""
        print("Класс ImportDataWidget в import_data()")
        file_path = self.file_path_input.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Ошибка", "Введите путь к файлу.")
            return

        selected_session_index = self.session_combo.currentIndex()
        if selected_session_index == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите сеанс.")
            return

        session_id = self.session_combo.itemData(selected_session_index)
        if not session_id:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить ID сеанса.")
            return

        # Проверка существования файла
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден.")
            return

        try:
            # Проверяем, есть ли уже данные для указанного сеанса
            from services.ecs_service import get_ecs_data_by_session_id, delete_ecs_data_by_session_id
            from services.pg_service import get_pg_data_by_session_id, delete_pg_data_by_session_id

            existing_ecs_data = get_ecs_data_by_session_id(self.db_session, session_id)
            existing_pg_data = get_pg_data_by_session_id(self.db_session, session_id)

            if existing_ecs_data or existing_pg_data:
                # Если данные уже существуют, спрашиваем пользователя, хочет ли он их перезаписать
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    "Данные на указанный сеанс уже есть. Хотите перезаписать?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.No:
                    # Если пользователь отказался, выходим из метода
                    return

                # Если пользователь согласился, удаляем старые данные
                delete_ecs_data_by_session_id(self.db_session, session_id)
                delete_pg_data_by_session_id(self.db_session, session_id)

            # Добавляем новые данные
            sql_query = text("""
            SELECT import_data_from_file(:file_path, :session_id);
            """)
            self.db_session.execute(sql_query, {"file_path": file_path, "session_id": session_id})
            self.db_session.commit()

            QMessageBox.information(self, "Успех", "Данные успешно импортированы!")

            # Закрываем диалоговое окно после успешного импорта
            self.accept()

        except Exception as e:
            self.db_session.rollback()  # Откатываем транзакцию в случае ошибки
            print(f"Ошибка при импорте данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать данные: {e}")
