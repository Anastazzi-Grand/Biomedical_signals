from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox, QInputDialog
from PyQt6.QtCore import Qt


class ActivityTypeWidget(QWidget):
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
        self.search_input.setPlaceholderText("Введите название для поиска")
        self.search_input.returnPressed.connect(self.search_activity_types)  # Обработка Enter
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_activity_types)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Таблица данных
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # ID, Название, Описание
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Описание"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)  # Разрешаем редактирование
        self.table.setColumnHidden(0, True)  # Скрываем столбец ID
        layout.addWidget(self.table)

        # Кнопки CRUD
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_activity_type)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_activity_type)
        button_layout.addWidget(delete_button)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Загрузка данных при создании виджета
        self.load_data()

    def load_data(self, query=None):
        """Загрузка данных в таблицу."""
        try:
            from services.activity_type_service import get_activity_types, search_activity_types_by_name

            if query:
                activity_types = search_activity_types_by_name(self.db_session, query)
            else:
                activity_types = get_activity_types(self.db_session)

            self.table.setRowCount(len(activity_types))
            for row, activity in enumerate(activity_types):
                self.table.setItem(row, 0, QTableWidgetItem(str(activity.activitytypeid)))  # ID
                self.table.setItem(row, 1, QTableWidgetItem(activity.activityname))  # Название
                self.table.setItem(row, 2, QTableWidgetItem(activity.description or ""))  # Описание
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def search_activity_types(self):
        """Поиск типов активностей по названию."""
        query = self.search_input.text().strip()
        self.load_data(query=query)

    def add_activity_type(self):
        """Добавление нового типа активности."""
        try:
            name, ok = QInputDialog.getText(self, "Добавление типа активности", "Введите название:")
            if not ok or not name:
                return

            description, ok = QInputDialog.getText(self, "Добавление типа активности", "Введите описание:")
            if not ok:
                return

            from services.activity_type_service import create_activity_type
            create_activity_type(self.db_session, activityname=name, description=description)
            QMessageBox.information(self, "Успех", "Тип активности успешно добавлен.")
            self.load_data()  # Обновляем таблицу
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def delete_activity_type(self):
        """Удаление выбранного типа активности."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления.")
            return

        activitytypeid = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить тип активности с ID {activitytypeid}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                from services.activity_type_service import delete_activity_type
                delete_activity_type(self.db_session, activitytypeid)
                QMessageBox.information(self, "Успех", "Тип активности успешно удален.")
                self.load_data()  # Обновляем таблицу
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def save_changes(self):
        """Сохранение изменений в таблице."""
        try:
            from services.activity_type_service import update_activity_type

            for row in range(self.table.rowCount()):
                activitytypeid = int(self.table.item(row, 0).text())  # ID
                activityname = self.table.item(row, 1).text()  # Название
                description = self.table.item(row, 2).text()  # Описание

                # Обновляем данные в базе
                update_activity_type(self.db_session, activitytypeid, activityname=activityname, description=description)

            QMessageBox.information(self, "Успех", "Изменения успешно сохранены.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
