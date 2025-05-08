from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from database.session import authenticate_user, get_user_accessible_tables, get_db_session
from database.models import Patient, Doctor, Sessions, ECS_data, PG_data, Polyclinic, Laboratory, Equipment, Analysis_result, Diagnosis, Chronic_condition, Treatment_recommendation
from ui.widgets.diagnosis_widget import DiagnosisWidget
from ui.widgets.ecs_widget import ECSDataWidget
from ui.widgets.patient_widget import PatientWidget
from ui.widgets.pg_widget import PGDataWidget


class MainWindow(QMainWindow):
    def __init__(self, username, password):
        super().__init__()

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
            db_session = authenticate_user(username, password)  # Используем переданный пароль
            if not db_session:
                raise Exception("Не удалось создать сессию базы данных.")

            accessible_tables = get_user_accessible_tables(db_session, username)
            if not accessible_tables:
                raise Exception("Нет доступных таблиц для пользователя.")

            # Добавляем вкладки для каждой доступной таблицы
            for table_name in accessible_tables:
                # Удаляем лишние кавычки и пробелы
                print("TABLE NAME", table_name)

                if table_name == 'patient':
                    tab_content = PatientWidget(authenticate_user(username, password))
                elif table_name == 'ecs_data':
                    tab_content = ECSDataWidget(authenticate_user(username, password))
                elif table_name == 'pg_data':
                    tab_content = PGDataWidget(authenticate_user(username, password))
                # elif table_name == 'diagnosis':
                #     tab_content = DiagnosisWidget(authenticate_user(username, password))
                else:
                    tab_content = QLabel(f"Содержимое таблицы: {table_name}")
                self.tab_widget.addTab(tab_content, table_name.capitalize())
        except Exception as e:
            print(f"Ошибка при получении доступных таблиц: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

        # Кнопка "Выход"
        self.exit_button = QPushButton("Выход")
        self.exit_button.clicked.connect(self.logout)
        self.layout.addWidget(self.exit_button)

    def logout(self):
        # Закрываем главное окно
        self.close()

        # Открываем окно входа
        from ui.login_window import LoginWindow  # Импортируем здесь, чтобы избежать циклических зависимостей
        self.login_window = LoginWindow()
        self.login_window.show()


# from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QMessageBox
# from database.session import authenticate_user, get_user_accessible_tables
# from ui.widgets.patient_widget import PatientWidget
# from ui.widgets.ecs_widget import ECSDataWidget
# from ui.widgets.pg_widget import PGDataWidget
# from ui.widgets.patientactivity_widget import PatientActivityWidget
# from ui.widgets.analysis_widget import AnalysisResultWidget
# from ui.widgets.diagnosis_widget import DiagnosisWidget
# from ui.widgets.chroniccondition_widget import ChronicConditionWidget
# from ui.widgets.treatmentrecommendation_widget import TreatmentRecommendationWidget


# class MainWindow(QMainWindow):
#     def __init__(self, username, password):
#         super().__init__()
#
#         self.setWindowTitle("Главная страница")
#         self.setGeometry(100, 100, 800, 600)
#
#         # Главный виджет и макет
#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.layout = QVBoxLayout()
#         self.central_widget.setLayout(self.layout)
#
#         # Приветствие
#         self.welcome_label = QLabel(f"Добро пожаловать, {username}!")
#         self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
#         self.layout.addWidget(self.welcome_label)
#
#         # Создаем вкладки
#         self.tab_widget = QTabWidget()
#         self.layout.addWidget(self.tab_widget)
#
#         # Создаем сессию для получения доступных таблиц
#         # try:
#         #     db_session = authenticate_user(username, password)  # Используем переданный пароль
#         #     if not db_session:
#         #         raise Exception("Не удалось создать сессию базы данных.")
#         #
#         #     accessible_tables = get_user_accessible_tables(db_session, username)
#         #     if not accessible_tables:
#         #         raise Exception("Нет доступных таблиц для пользователя.")
#
#             # Добавляем вкладки для каждой доступной таблицы
#             # for table_name in accessible_tables:
#             #     if table_name == "patient":
#             #         tab_content = PatientWidget(db_session)
#             #     elif table_name == "ecs_data":
#             #         tab_content = ECSDataWidget(db_session)
#             #     elif table_name == "pg_data":
#             #         tab_content = PGDataWidget(db_session)
#             #     elif table_name == "patient_activity":
#             #         tab_content = PatientActivityWidget(db_session)
#             #     elif table_name == "analysis_result":
#             #         tab_content = AnalysisResultWidget(db_session)
#             #     elif table_name == "diagnosis":
#             #         tab_content = DiagnosisWidget(db_session)
#             #     elif table_name == "chronic_condition":
#             #         tab_content = ChronicConditionWidget(db_session)
#             #     elif table_name == "treatment_recommendation":
#             #         tab_content = TreatmentRecommendationWidget(db_session)
#             #     else:
#             #         tab_content = QLabel(f"Содержимое таблицы: {table_name}")
#             #     self.tab_widget.addTab(tab_content, table_name.capitalize())
#         # except Exception as e:
#         #     print(f"Ошибка при получении доступных таблиц: {e}")
#         #     QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")
#
#         # Кнопка "Выход"
#         self.exit_button = QPushButton("Выход")
#         self.exit_button.clicked.connect(self.logout)
#         self.layout.addWidget(self.exit_button)
#
#     def logout(self):
#         # Закрываем главное окно
#         self.close()
#
#         # Открываем окно входа
#         from ui.login_window import LoginWindow  # Импортируем здесь, чтобы избежать циклических зависимостей
#         self.login_window = LoginWindow()
#         self.login_window.show()
