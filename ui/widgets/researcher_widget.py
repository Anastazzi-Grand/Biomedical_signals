from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox

from services.analysis_service import get_analysis_result_by_sessionid, get_analysis_results_by_sessionid
from services.ecs_service import get_ecs_data_by_session_id
from services.pg_service import get_pg_data_by_session_id
from ui.widgets.plots.processed_data_widget import ProcessedDataWidget
from ui.widgets.plots.row_data_plot_widget import RawDataPlotWidget
from ui.widgets.plots.signal_processing_widget import SignalProcessingWidget


class ResearcherWidget(QWidget):
    def __init__(self, db_session, parent_widget=None):
        super().__init__()
        if not db_session:
            raise ValueError("Сессия базы данных не передана или недействительна.")
        self.db_session = db_session
        self.parent_widget = parent_widget  # Ссылка на родительский виджет
        self.init_ui()
        self.raw_data_plot_widget = None
        self.signal_processing_widget = None

    def init_ui(self):
        # Основной макет
        layout = QVBoxLayout()

        button_style = """
            QPushButton {
                padding: 3px;
                min-width: 200px;
            }
        """

        self.raw_data_button = QPushButton("Посмотреть сырые данные")
        self.raw_data_button.setStyleSheet(button_style)
        self.raw_data_button.clicked.connect(self.view_raw_data)

        self.process_signals_button = QPushButton("Обработать сигналы")
        self.process_signals_button.setStyleSheet(button_style)
        self.process_signals_button.clicked.connect(self.process_signals)

        self.processed_data_button = QPushButton("Посмотреть обработанные данные")
        self.processed_data_button.setStyleSheet(button_style)
        self.processed_data_button.clicked.connect(self.view_processed_data)

        font = self.raw_data_button.font()
        font.setPointSize(10)  # Увеличиваем размер шрифта до 12 пунктов

        self.raw_data_button.setFont(font)
        self.process_signals_button.setFont(font)
        self.processed_data_button.setFont(font)

        # Добавляем кнопки в макет
        layout.addWidget(self.raw_data_button)
        layout.addWidget(self.process_signals_button)
        layout.addWidget(self.processed_data_button)

        # Устанавливаем макет
        self.setLayout(layout)

    def view_raw_data(self):
        """Открывает диалоговое окно для выбора пациента и просмотра сырых данных."""
        try:
            # Выбираем сеанс
            session_id = self.select_session()
            if session_id is None:
                return

            # Загружаем данные ЭКС и ПГ
            ecs_data = get_ecs_data_by_session_id(self.db_session, session_id)
            pg_data = get_pg_data_by_session_id(self.db_session, session_id)

            if not ecs_data or not pg_data:
                QMessageBox.warning(self, "Ошибка", "Данные для выбранного пациента недоступны.")
                return

            # Создаем виджет с графиками
            self.raw_data_plot_widget = RawDataPlotWidget(ecs_data, pg_data)  # Сохраняем ссылку
            self.raw_data_plot_widget.setWindowTitle("Сырые данные: ЭКС и сигнал дыхания")
            self.raw_data_plot_widget.show()  # Показываем виджет

        except Exception as e:
            print(f"Ошибка при просмотре сырых данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def process_signals(self):
        """Открывает диалоговое окно для выбора пациента и обработки сигналов."""
        try:
            # Выбираем сеанс
            session_id = self.select_session()
            if session_id is None:
                return

            # Открываем виджет обработки сигналов
            self.signal_processing_widget = SignalProcessingWidget(self.db_session, session_id)  # Сохраняем ссылку
            self.signal_processing_widget.setWindowTitle("Обработка сигналов")
            self.signal_processing_widget.show()

        except Exception as e:
            print(f"Ошибка при обработке сигналов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось обработать сигналы: {e}")

    def view_processed_data(self):
        """Открывает диалоговое окно для выбора пациента и просмотра обработанных данных."""
        try:
            # Выбираем сеанс
            session_id = self.select_session()
            if session_id is None:
                return

            # Получаем обработанные данные из таблицы "Результаты анализа"
            analysis_results = get_analysis_results_by_sessionid(self.db_session, session_id)
            if not analysis_results:
                QMessageBox.warning(self, "Ошибка", "Нет обработанных данных для выбранного сеанса.")
                return

            # Извлекаем данные для графика
            processed_ecs_data = [result.processed_ecs_data for result in analysis_results]
            processed_pg_data = [result.processed_pg_data for result in analysis_results]

            # Создаем виджет обработанных данных
            self.processed_data_widget = ProcessedDataWidget(processed_ecs_data, processed_pg_data)
            self.processed_data_widget.setWindowTitle("Обработанные данные")
            self.processed_data_widget.show()

        except Exception as e:
            print(f"Ошибка при просмотре обработанных данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def get_filtered_patient_list(self):
        """Возвращает отфильтрованный список пациентов с дополнительной информацией."""
        try:
            from services.sessions_service import get_sessions_with_details
            from services.ecs_service import get_ecs_data_by_session_id
            from services.pg_service import get_pg_data_by_session_id

            # Получаем список всех сеансов
            all_sessions = get_sessions_with_details(self.db_session)
            if not all_sessions:
                QMessageBox.information(self, "Информация", "Нет доступных сеансов.")
                return []

            # Фильтруем сеансы: только те, которые содержат данные ЭКС или ПГ
            filtered_sessions = [
                session for session in all_sessions
                if get_ecs_data_by_session_id(self.db_session, session["sessionid"]) or
                   get_pg_data_by_session_id(self.db_session, session["sessionid"])
            ]
            if not filtered_sessions:
                QMessageBox.information(self, "Информация", "Нет сеансов с данными ЭКС или ПГ.")
                return []

            # Формируем список пациентов с дополнительной информацией
            patient_info_list = [
                f"{session['patient_fio']} ({session['session_date']}, {session['session_starttime']})"
                for session in filtered_sessions
            ]

            return filtered_sessions, patient_info_list

        except Exception as e:
            print(f"Ошибка при получении списка пациентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")
            return [], []


    def select_session(self):
        """
        Общий метод для выбора сеанса записи пациента.
        Возвращает session_id выбранного сеанса или None, если сеанс не выбран.
        """
        try:
            # Получаем отфильтрованный список пациентов
            filtered_sessions, patient_info_list = self.get_filtered_patient_list()
            if not filtered_sessions:
                return None

            # Открываем диалоговое окно для выбора пациента
            selected_patient_info, ok = QInputDialog.getItem(
                self,
                "Выберите запись пациента",
                "Запись:",
                patient_info_list,
                editable=False
            )
            if not ok:
                return None

            # Находим выбранный сеанс по информации
            selected_patient_fio = selected_patient_info.split(" (")[0]
            selected_session = next(
                (session for session in filtered_sessions if session["patient_fio"] == selected_patient_fio), None
            )
            if not selected_session:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти сессию для выбранного пациента.")
                return None

            return selected_session["sessionid"]

        except Exception as e:
            print(f"Ошибка при выборе сеанса: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось выбрать сеанс: {e}")
            return None