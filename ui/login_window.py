from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from database.session import authenticate_user

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Система обработки и отображения биомедицинских сигналов")
        self.setGeometry(100, 100, 400, 300)

        # Главный виджет и макет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Заголовок
        self.title_label = QLabel("Система обработки и отображения биомедицинских сигналов")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Подзаголовок
        self.subtitle_label = QLabel("Вход в систему")
        self.subtitle_label.setStyleSheet("font-size: 14px; margin-top: 20px;")
        self.layout.addWidget(self.subtitle_label)

        # Поле для логина
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.layout.addWidget(self.login_input)

        # Поле для пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        # Место для ошибок
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.layout.addWidget(self.error_label)

        # Кнопка "Ввод"
        self.login_button = QPushButton("Ввод")
        self.login_button.clicked.connect(self.authenticate_user)
        self.layout.addWidget(self.login_button)

        # Обработка клавиши Enter
        self.login_input.returnPressed.connect(self.authenticate_user)
        self.password_input.returnPressed.connect(self.authenticate_user)

    def authenticate_user(self):
        username = self.login_input.text()
        password = self.password_input.text()

        # Отладка: вывод значений логина и пароля
        print(f"Введенный логин: {username}")
        print(f"Введенный пароль: {'*' * len(password)}")

        if not username or not password:
            self.error_label.setText("Введите логин и пароль!")
            return

        # Проверяем учетные данные
        db_session = authenticate_user(username, password)
        if db_session:
            self.error_label.setText("")  # Очистка ошибок
            self.open_main_window(username, password)
        else:
            self.error_label.setText("Неправильные логин или пароль!")

    def open_main_window(self, username, password):
        # Открытие главного окна после успешного входа
        from ui.main_window import MainWindow  # Импортируем здесь, чтобы избежать циклических зависимостей
        self.main_window = MainWindow(username, password)  # Передаем пароль
        self.main_window.show()
        self.close()
