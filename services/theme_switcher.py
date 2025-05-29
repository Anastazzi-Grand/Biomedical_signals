from PyQt6.QtWidgets import QWidget, QLabel, QCheckBox, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

class ThemeSwitcher(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Родительский виджет, к которому применяются стили
        self.dark_theme = True  # По умолчанию темная тема

        # Настройка макета
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Горизонтальный макет для надписи и чекбокса
        self.theme_layout = QHBoxLayout()

        # Надпись для текущей темы
        self.theme_label = QLabel("Темная тема")
        self.theme_label.setAlignment(Qt.AlignmentFlag.AlignRight)  # Выравнивание текста по правому краю
        self.theme_layout.addWidget(self.theme_label)  # Добавляем надпись в горизонтальный макет

        # Чекбокс для переключения темы
        self.theme_checkbox = QCheckBox()
        self.theme_checkbox.setChecked(True)  # Темная тема по умолчанию
        self.theme_checkbox.stateChanged.connect(self.toggle_theme)
        self.theme_layout.addWidget(self.theme_checkbox)  # Добавляем чекбокс в горизонтальный макет

        # Добавляем горизонтальный макет в вертикальный макет
        self.layout.addLayout(self.theme_layout)

    def toggle_theme(self):
        """Переключение между темной и светлой темами."""
        self.dark_theme = not self.dark_theme
        if self.dark_theme:
            self.theme_label.setText("Темная тема")
        else:
            self.theme_label.setText("Светлая тема")
        self.apply_theme()

    def apply_theme(self):
        """Применение текущей темы к родительскому виджету."""
        if self.dark_theme:
            # Темная тема
            self.parent.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    color: white;
                }
                QPushButton {
                    background-color: #444444;
                    color: white;
                    border: 1px solid black;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QTabWidget::pane {
                    border: 1px solid black;
                }
                QTabBar::tab {
                    background-color: #444444;
                    color: white;
                    border: 1px solid black;
                    padding: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #555555;
                }
                QLineEdit {
                    background-color: #444444;
                    color: white;
                    border: 1px solid black;
                    padding: 5px;
                }
            """)
        else:
            # Светлая тема
            self.parent.setStyleSheet("""
                QWidget {
                    background-color: white;
                    color: black;
                }
                QPushButton {
                    background-color: lightgray;
                    color: black;
                    border: 1px solid black;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: gray;
                }
                QTabWidget::pane {
                    border: 1px solid black;
                }
                QTabBar::tab {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    padding: 5px;
                }
                QTabBar::tab:selected {
                    background-color: lightgray;
                }
                QLineEdit {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    padding: 5px;
                }
            """)
