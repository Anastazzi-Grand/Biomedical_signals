from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QTabWidget

from database.session import authenticate_user, get_user_accessible_tables
from ui.widgets.ecs_widget import ECSDataWidget
from ui.widgets.patient_widget import PatientWidget
from ui.widgets.pg_widget import PGDataWidget
from ui.widgets.researcher_widget import ResearcherWidget
from ui.widgets.sessions_widget import SessionWidget


class MainWindow(QMainWindow):
    def __init__(self, username, password):
        super().__init__()

        # Сохраняем логин и пароль
        self.username = username
        self.password = password

        # Инициализация интерфейса
        self.setup_main_interface(username, password)

        # Флаг для отображения главного меню
        self.is_main_menu_visible = False

    def setup_main_interface(self, username, password):
        """Инициализирует основной интерфейс."""
        self.setWindowTitle("Главная страница")
        self.setGeometry(100, 100, 800, 600)

        # Главный виджет и макет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Приветствие
        self.welcome_label = QLabel(f"Добро пожаловать, {username}!")
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.welcome_label)

        # Создаем вкладки
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Создаем сессию для получения доступных таблиц
        try:
            self.db_session = authenticate_user(username, password)  # Инициализируем self.db_session
            if not self.db_session:
                raise Exception("Не удалось создать сессию базы данных.")

            accessible_tables = get_user_accessible_tables(self.db_session, username)
            if not accessible_tables:
                raise Exception("Нет доступных таблиц для пользователя.")

            # Добавляем вкладки для каждой доступной таблицы
            for table_name in accessible_tables:
                if table_name == 'patient':
                    tab_content = PatientWidget(self.db_session)
                elif table_name == 'ecs_data':
                    tab_content = ECSDataWidget(self.db_session)
                elif table_name == 'pg_data':
                    tab_content = PGDataWidget(self.db_session)
                elif table_name == 'session':
                    tab_content = SessionWidget(self.db_session)
                else:
                    tab_content = QLabel(f"Содержимое таблицы: {table_name}")
                self.tab_widget.addTab(tab_content, table_name.capitalize())
        except Exception as e:
            print(f"Ошибка при получении доступных таблиц: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

        # Кнопка "В главное меню"
        self.main_menu_button = QPushButton("В главное меню")
        self.main_menu_button.clicked.connect(self.show_main_menu)
        self.layout.addWidget(self.main_menu_button)

        # Кнопка "Выход"
        self.exit_button = QPushButton("Выход")
        self.exit_button.clicked.connect(self.logout)
        self.layout.addWidget(self.exit_button)

    def show_main_menu(self):
        """Показывает главное меню с тремя кнопками."""
        if self.is_main_menu_visible:
            return

        # Очищаем текущий интерфейс
        self.clear_current_interface()

        print("Создание ResearcherWidget...")
        try:
            print(f"Передаваемая db_session: {self.db_session}")
            self.main_menu_widget = ResearcherWidget(self.db_session)  # Передаем db_session
        except Exception as e:
            print(f"Ошибка при создании ResearcherWidget: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось отобразить главное меню: {e}")
            return

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.return_to_tabs)

        # Устанавливаем макет главного меню
        self.layout.addWidget(self.main_menu_widget)
        self.layout.addWidget(self.back_button)

        # Обновляем флаг
        self.is_main_menu_visible = True

    def clear_current_interface(self):
        """Очищает текущий интерфейс."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def return_to_tabs(self):
        """Возвращает к вкладкам."""
        if not self.is_main_menu_visible:
            print("Уже на вкладках, ничего не делаем.")
            return

        print("Очистка интерфейса...")
        self.clear_current_interface()

        print("Восстановление основного интерфейса...")
        self.setup_main_interface(self.username, self.password)  # Используем сохраненные данные

        print("Обновление флага is_main_menu_visible...")
        self.is_main_menu_visible = False

    def logout(self):
        """Выход из системы."""
        self.close()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()