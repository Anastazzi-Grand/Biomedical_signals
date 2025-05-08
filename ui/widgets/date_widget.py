from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDateEdit, QPushButton


class DateInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите дату")
        layout = QVBoxLayout()

        # Создаем виджет для выбора даты
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())  # Устанавливаем текущую дату по умолчанию
        layout.addWidget(self.date_edit)

        # Кнопка "Сохранить"
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.accept)  # Закрывает диалог с результатом "Accepted"
        layout.addWidget(save_button)

        self.setLayout(layout)

    def get_date(self):
        """
        Возвращает выбранную дату в формате строки 'YYYY-MM-DD'.
        """
        return self.date_edit.date().toString("yyyy-MM-dd")