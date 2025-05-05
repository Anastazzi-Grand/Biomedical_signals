from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from database.session import authenticate_user, get_user_accessible_tables
from database.models import Patient, Doctor, Sessions, ECS_data, PG_data, Polyclinic, Laboratory, Equipment, Analysis_result, Diagnosis, Chronic_condition, Treatment_recommendation

class MainWindow(QMainWindow):
    def __init__(self, username):
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
            db_session = authenticate_user(username, "password")  # Здесь можно передать пароль из входа
            accessible_tables = get_user_accessible_tables(db_session, username)

            # Добавляем вкладки для каждой доступной таблицы
            for table_name in accessible_tables:
                if table_name == "patient":
                    tab_content = self.load_patient_table(db_session)
                elif table_name == "doctor":
                    tab_content = self.load_doctor_table(db_session)
                elif table_name == "session":
                    tab_content = self.load_session_table(db_session)
                elif table_name == "ecs_data":
                    tab_content = self.load_ecs_data_table(db_session)
                elif table_name == "pg_data":
                    tab_content = self.load_pg_data_table(db_session)
                elif table_name == "diagnosis":
                    tab_content = self.load_diagnosis_table(db_session)
                else:
                    tab_content = QLabel(f"Содержимое таблицы: {table_name}")
                self.tab_widget.addTab(tab_content, table_name.capitalize())
        except Exception as e:
            print(f"Ошибка при получении доступных таблиц: {e}")

        # Кнопка "Выход"
        self.exit_button = QPushButton("Выход")
        self.exit_button.clicked.connect(self.logout)
        self.layout.addWidget(self.exit_button)

    def load_patient_table(self, db_session):
        """Загружает данные пациентов в таблицу."""
        patients = db_session.query(Patient).all()
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "ФИО", "Дата рождения", "Адрес", "Телефон"])
        table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            table.setItem(row, 0, QTableWidgetItem(str(patient.patientid)))
            table.setItem(row, 1, QTableWidgetItem(patient.patient_fio))
            table.setItem(row, 2, QTableWidgetItem(str(patient.patient_birthdate)))
            table.setItem(row, 3, QTableWidgetItem(patient.patient_address or ""))
            table.setItem(row, 4, QTableWidgetItem(patient.patient_phone or ""))
        return table

    def load_doctor_table(self, db_session):
        """Загружает данные врачей в таблицу."""
        doctors = db_session.query(Doctor).all()
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "ФИО", "Дата рождения", "Специализация", "Телефон"])
        table.setRowCount(len(doctors))
        for row, doctor in enumerate(doctors):
            table.setItem(row, 0, QTableWidgetItem(str(doctor.doctorid)))
            table.setItem(row, 1, QTableWidgetItem(doctor.doctor_fio))
            table.setItem(row, 2, QTableWidgetItem(str(doctor.doctor_birthdate)))
            table.setItem(row, 3, QTableWidgetItem(doctor.doctor_specialization))
            table.setItem(row, 4, QTableWidgetItem(doctor.doctor_phone or ""))
        return table

    def load_session_table(self, db_session):
        """Загружает данные сеансов в таблицу."""
        sessions = db_session.query(Sessions).all()
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Дата", "Начало", "Конец", "Пациент"])
        table.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            table.setItem(row, 0, QTableWidgetItem(str(session.sessionid)))
            table.setItem(row, 1, QTableWidgetItem(str(session.session_date)))
            table.setItem(row, 2, QTableWidgetItem(str(session.session_starttime)))
            table.setItem(row, 3, QTableWidgetItem(str(session.session_endtime)))
            table.setItem(row, 4, QTableWidgetItem(str(session.patientid)))
        return table

    def load_ecs_data_table(self, db_session):
        """Загружает данные ЭКГ в таблицу."""
        ecs_data = db_session.query(ECS_data).all()
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Сеанс", "RR Length", "RR Time"])
        table.setRowCount(len(ecs_data))
        for row, data in enumerate(ecs_data):
            table.setItem(row, 0, QTableWidgetItem(str(data.ecsdataid)))
            table.setItem(row, 1, QTableWidgetItem(str(data.sessionid)))
            table.setItem(row, 2, QTableWidgetItem(str(data.rr_length)))
            table.setItem(row, 3, QTableWidgetItem(str(data.rr_time)))
        return table

    def load_pg_data_table(self, db_session):
        """Загружает данные ПГ в таблицу."""
        pg_data = db_session.query(PG_data).all()
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Сеанс", "D1", "D2", "Amplitude"])
        table.setRowCount(len(pg_data))
        for row, data in enumerate(pg_data):
            table.setItem(row, 0, QTableWidgetItem(str(data.pgdataid)))
            table.setItem(row, 1, QTableWidgetItem(str(data.sessionid)))
            table.setItem(row, 2, QTableWidgetItem(str(data.d1)))
            table.setItem(row, 3, QTableWidgetItem(str(data.d2)))
            table.setItem(row, 4, QTableWidgetItem(str(data.amplitude) if data.amplitude is not None else ""))
        return table

    def load_diagnosis_table(self, db_session):
        """Загружает данные диагнозов в таблицу."""
        diagnoses = db_session.query(Diagnosis).all()
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Пациент", "Диагноз", "Описание", "Дата"])
        table.setRowCount(len(diagnoses))
        for row, diagnosis in enumerate(diagnoses):
            table.setItem(row, 0, QTableWidgetItem(str(diagnosis.diagnosisid)))
            table.setItem(row, 1, QTableWidgetItem(str(diagnosis.patientid)))
            table.setItem(row, 2, QTableWidgetItem(diagnosis.diagnosis_name or ""))
            table.setItem(row, 3, QTableWidgetItem(diagnosis.description))
            table.setItem(row, 4, QTableWidgetItem(str(diagnosis.date_of_diagnosis)))
        return table

    def logout(self):
        # Закрываем главное окно
        self.close()

        # Открываем окно входа
        from ui.login_window import LoginWindow  # Импортируем здесь, чтобы избежать циклических зависимостей
        self.login_window = LoginWindow()
        self.login_window.show()
