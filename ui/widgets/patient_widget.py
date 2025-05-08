from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, \
    QHBoxLayout, QInputDialog, QComboBox

from ui.widgets.date_widget import DateInputDialog


class PatientWidget(QWidget):
    def __init__(self, db_session):
        super().__init__()
        try:
            self.db_session = db_session
            self.init_ui()
        except Exception as e:
            print(f"Ошибка при инициализации PatientWidget: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def init_ui(self):
        layout = QVBoxLayout()

        # Панель поиска (поле ввода + кнопка)
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ФИО для поиска")
        self.search_input.returnPressed.connect(self.search_patients)  # Обработка Enter
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_patients)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        # Таблица
        self.table = QTableWidget()
        self.load_data()

        # Кнопки
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_patient)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_selected_patient)
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)

        # Добавляем элементы в макет
        layout.addLayout(search_layout)  # Панель поиска
        layout.addWidget(self.table)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def load_data(self, patients=None):
        """Загружает данные пациентов из базы данных."""
        try:
            from services.patient_service import get_patients_with_details
            from services.polyclinic_service import get_all_polyclinics_with_details

            if not patients:
                patients = get_patients_with_details(self.db_session)
            patients.sort(key=lambda x: x["patient_fio"])  # Сортировка по ФИО

            # Настройка таблицы
            self.table.setRowCount(len(patients))
            self.table.setColumnCount(6)  # Добавляем один скрытый столбец для ID и столбец для поликлиники
            self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Дата рождения", "Адрес", "Телефон", "Поликлиника"])

            # Получаем список всех поликлиник
            polyclinics = get_all_polyclinics_with_details(self.db_session)
            polyclinic_names = [polyclinic["polyclinic_name"] for polyclinic in polyclinics]

            for row, patient in enumerate(patients):
                # Скрытый столбец: ID пациента
                self.table.setItem(row, 0, QTableWidgetItem(str(patient["patientid"])))
                self.table.setItem(row, 1, QTableWidgetItem(patient["patient_fio"]))
                self.table.setItem(row, 2, QTableWidgetItem(str(patient["patient_birthdate"])))
                self.table.setItem(row, 3, QTableWidgetItem(patient["patient_address"] or ""))
                self.table.setItem(row, 4, QTableWidgetItem(patient["patient_phone"] or ""))

                # Выпадающий список для поликлиники
                combo_box = QComboBox()
                combo_box.addItems(polyclinic_names)
                current_polyclinic = patient["polyclinic_name"]
                # if current_polyclinic in polyclinic_names:
                combo_box.setCurrentText(current_polyclinic)

                # Сохраняем текущую строку в данных комбобокса
                combo_box.setProperty("row", row)

                # Устанавливаем комбобокс в ячейку
                self.table.setCellWidget(row, 5, combo_box)

            # Скрываем первый столбец (ID пациента)
            self.table.setColumnHidden(0, True)

        except Exception as e:
            print(f"Ошибка при загрузке данных пациентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def save_changes(self):
        """Сохраняет изменения, внесенные в таблицу, в базу данных."""
        try:
            from services.patient_service import update_patient
            from services.polyclinic_service import get_polyclinic_by_name

            for row in range(self.table.rowCount()):
                patient_id = self.get_patient_id_from_row(row)  # Получаем ID пациента
                if not patient_id:
                    continue

                patient_fio = self.table.item(row, 1).text()  # ФИО
                patient_birthdate = self.table.item(row, 2).text()  # Дата рождения
                patient_address = self.table.item(row, 3).text()  # Адрес
                patient_phone = self.table.item(row, 4).text()  # Телефон

                # Получаем текущее значение поликлиники из QComboBox
                combo_box = self.table.cellWidget(row, 5)  # QComboBox в столбце "Поликлиника"
                if not combo_box:
                    raise ValueError(f"Не найден выпадающий список для строки {row}")

                current_polyclinic_name = combo_box.currentText()  # Название поликлиники

                # Находим ID поликлиники по её названию
                polyclinic = get_polyclinic_by_name(self.db_session, current_polyclinic_name)
                if not polyclinic:
                    raise ValueError(f"Поликлиника с названием '{current_polyclinic_name}' не найдена")

                polyclinic_id = polyclinic.polyclinicid

                # Обновляем данные пациента
                update_patient(
                    self.db_session,
                    patient_id=patient_id,
                    fio=patient_fio,
                    birthdate=patient_birthdate,
                    address=patient_address,
                    phone=patient_phone,
                    polyclinic_name=current_polyclinic_name  # Передаем название для логики сервиса
                )

            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except PermissionError as e:
            QMessageBox.critical(self, "Ошибка доступа", str(e))
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {e}")

    def add_patient(self):
        """Добавляет нового пациента."""
        try:
            from services.patient_service import create_patient
            from services.polyclinic_service import get_all_polyclinics_with_details

            # Диалоговое окно для ввода данных
            fio, ok = QInputDialog.getText(self, "Добавить пациента", "Введите ФИО пациента:")
            if not ok:
                return

            # Выбор даты рождения через календарь
            date_dialog = DateInputDialog(self)
            if date_dialog.exec():  # Проверяем, что пользователь нажал "Сохранить"
                birthdate = date_dialog.get_date()
            else:
                return  # Если пользователь закрыл диалог, выходим

            # Выбор поликлиники из выпадающего списка
            polyclinics = get_all_polyclinics_with_details(self.db_session)
            polyclinic_names = [polyclinic["polyclinic_name"] for polyclinic in polyclinics]
            selected_polyclinic, ok = QInputDialog.getItem(
                self, "Выберите поликлинику", "Поликлиника:", polyclinic_names, editable=False
            )
            if not ok:
                return

            # Ввод адреса и телефона
            address, ok = QInputDialog.getText(self, "Добавить пациента", "Введите адрес:")
            if not ok:
                return

            phone, ok = QInputDialog.getText(self, "Добавить пациента", "Введите телефон:")
            if not ok:
                return

            # Создаем нового пациента
            create_patient(
                self.db_session,
                fio=fio,
                birthdate=birthdate,
                address=address,
                phone=phone,
                polyclinic_name=selected_polyclinic
            )
            QMessageBox.information(self, "Успех", "Пациент успешно добавлен!")
            self.load_data()  # Обновляем таблицу
        except Exception as e:
            print(f"Ошибка при добавлении пациента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить пациента: {e}")

    def delete_selected_patient(self):
        """Удаляет выбранного пациента после подтверждения."""
        try:
            from services.patient_service import delete_patient

            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Внимание", "Выберите ячейку для удаления.")
                return

            selected_row = selected_items[0].row()
            patient_id = self.get_patient_id_from_row(selected_row)
            if not patient_id:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить ID пациента.")
                return

            # Подтверждение удаления
            confirm = QMessageBox.question(
                self,
                "Подтверждение удаления",
                "Вы точно хотите удалить данные об этом пациенте?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                # Удаляем пациента
                delete_patient(self.db_session, patient_id=patient_id)
                QMessageBox.information(self, "Успех", "Пациент успешно удален!")
                self.load_data()  # Обновляем таблицу
        except PermissionError as e:
            QMessageBox.critical(self, "Ошибка доступа", str(e))
        except Exception as e:
            print(f"Ошибка при удалении пациента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить пациента: {e}")

    def search_patients(self):
        """Ищет пациентов по ФИО."""
        try:
            from services.patient_service import search_patients_by_fio, get_patients_with_details

            fio = self.search_input.text().strip()
            if not fio:
                # Если поле поиска пустое, загружаем все данные
                self.load_data()
                return

            patients = search_patients_by_fio(self.db_session, fio)
            if not patients:
                QMessageBox.information(self, "Результат", "Пациенты не найдены.")
                return

            # Загружаем найденных пациентов в таблицу
            self.load_data(patients)
        except Exception as e:
            print(f"Ошибка при поиске пациентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск: {e}")

    def get_patient_id_from_row(self, row):
        """
        Получает ID пациента из строки таблицы.
        Использует скрытый столбец таблицы для хранения patient_id.
        """
        try:
            patient_id_item = self.table.item(row, 0)
            if not patient_id_item:
                raise ValueError("ID пациента не найден в таблице.")

            patient_id = patient_id_item.text()
            return int(patient_id)  # Преобразуем в целое число
        except Exception as e:
            print(f"Ошибка при получении ID пациента из строки {row}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить ID пациента: {e}")
            return None


