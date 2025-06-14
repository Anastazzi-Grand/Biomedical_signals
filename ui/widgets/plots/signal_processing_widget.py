from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

from services.theme_switcher import ThemeSwitcher
from ui.widgets.plots.creating_time_series_widget import CreatingTimeSeriesWidget
from ui.widgets.plots.epoch_selection_widget import EpochSelectionWidget
from ui.widgets.plots.filter_selection_widget import FilterSelectionWidget


class SignalProcessingWidget(QWidget):
    def __init__(self, db_session, session_id):
        super().__init__()
        self.WIDGETS_COUNT = 3

        self.db_session = db_session
        self.session_id = session_id
        self.current_step = 0  # Текущий этап обработки
        self.rr_times = []  # Данные RR-интервалов
        self.amplitudes = []  # Данные амплитуд дыхания
        self.filter_state = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Верхняя панель с навигацией
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("< Предыдущий этап")
        self.prev_button.clicked.connect(self.go_to_previous_step)
        self.prev_button.setEnabled(False)  # На первом этапе кнопка "Назад" неактивна
        self.next_button = QPushButton("Следующий этап >")
        self.next_button.clicked.connect(self.go_to_next_step)

        # Добавляем метку для описания текущего этапа
        self.step_label = QLabel("Этап 1: Исходные данные и корреляция")
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.step_label)
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)

        # Основной контент
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        self.setLayout(layout)

        # Загружаем данные и отображаем первый этап
        self.load_data()
        self.show_step()

    def load_data(self):
        """Загрузка данных ЭКС и сигнала дыхания."""
        try:
            from services.ecs_service import get_ecs_data_by_session_id
            from services.pg_service import get_pg_data_by_session_id

            # Загружаем данные ЭКС
            ecs_data = get_ecs_data_by_session_id(self.db_session, self.session_id)
            if not ecs_data:
                raise ValueError("Данные ЭКС отсутствуют")

            # Загружаем данные сигнала дыхания
            pg_data = get_pg_data_by_session_id(self.db_session, self.session_id)
            if not pg_data:
                raise ValueError("Данные сигнала дыхания отсутствуют")

            # Извлечение значений
            self.rr_times = [data["rr_time"] for data in ecs_data]
            self.amplitudes = [data["amplitude"] for data in pg_data]

            print(f"Загружено {len(self.rr_times)} RR-интервалов и {len(self.amplitudes)} значений амплитуд.")

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def show_step(self):
        try:
            print(f"Отображение этапа {self.current_step}")

            # Сохраняем состояние фильтров перед сменой этапа
            if hasattr(self, "filter_widget"):
                self.filter_state = self.filter_widget.get_filter_state()

            # Скрываем все виджеты
            for i in range(self.content_layout.count()):
                widget = self.content_layout.itemAt(i).widget()
                if widget:
                    widget.hide()

            # Показываем нужный виджет
            if self.current_step == 0:
                print("Показываем исходные данные")
                self.step_label.setText(f"Этап {self.current_step + 1}: Исходные данные")
                self.show_initial_data()
            elif self.current_step == 1:
                print("Показываем выбор фильтров")
                self.step_label.setText(f"Этап {self.current_step + 1}: Предварительная обработка")
                self.show_filter_selection()
                if hasattr(self, "filter_widget") and self.filter_state:
                    self.filter_widget.set_filter_state(self.filter_state)
            elif self.current_step == 2:
                print("Показываем выбор эпохи")
                self.step_label.setText(f"Этап {self.current_step + 1}: Выбор \"Эпохи\"")
                self.show_epoch_selection()
            elif self.current_step == 3:
                print("Показываем создание временных рядов")
                self.step_label.setText(f"Этап {self.current_step + 1}: Ряды RRi и dUi")
                self.show_creating_time_series()
            else:
                print("Показываем заполнитель")
                self.show_placeholder()
        except Exception as e:
            print(f"Ошибка в show_step: {e}")

    def show_filter_selection(self):
        """Отображение виджета для выбора фильтров."""
        if not hasattr(self, "filter_widget"):
            print("Создаем новый FilterSelectionWidget")
            self.filter_widget = FilterSelectionWidget(
                self.db_session,
                self.rr_times,  # Передаем данные RR-интервалов
                self.amplitudes,  # Передаем данные амплитуд дыхания
                self.session_id
            )
            self.content_layout.addWidget(self.filter_widget)
        else:
            print("Используем существующий FilterSelectionWidget")

        # Показываем виджет
        self.filter_widget.show()

    def show_epoch_selection(self):
        """Отображение виджета для выбора эпохи."""
        filtered_rr_times, filtered_amplitudes = self.filter_widget.get_filtered_data()
        if filtered_rr_times is None or filtered_amplitudes is None:
            QMessageBox.warning(
                self,
                "Внимание",
                "Фильтры не были применены. Примените фильтры перед выбором эпохи."
            )
            return

        if not hasattr(self, "epoch_widget"):
            print("Создаем новый EpochSelectionWidget")
            self.epoch_widget = EpochSelectionWidget(
                self.db_session,
                filtered_rr_times,
                filtered_amplitudes,
                self.session_id
            )
            self.content_layout.addWidget(self.epoch_widget)
        else:
            print("Используем существующий EpochSelectionWidget")
            self.epoch_widget.update_data(filtered_rr_times, filtered_amplitudes)

        self.epoch_widget.show()

    def show_creating_time_series(self):
        """Отображение создания временных рядов."""
        if not hasattr(self, "epoch_widget") or self.epoch_widget.selected_epoch_start is None:
            QMessageBox.warning(self, "Внимание", "Эпоха не выбрана. Выберите эпоху перед этим этапом.")
            return

        # Берем данные из выбранной эпохи
        start = self.epoch_widget.selected_epoch_start
        end = self.epoch_widget.selected_epoch_end
        rr_times = self.filter_widget.filtered_rr_times[start:end]
        amplitudes = self.filter_widget.filtered_amplitudes[start:end]


        if not hasattr(self, "time_series_widget"):
            print("Создаем новый CreatingTimeSeriesWidget")
            self.time_series_widget = CreatingTimeSeriesWidget(self.db_session, rr_times, amplitudes, self.session_id)
            self.content_layout.addWidget(self.time_series_widget)
        else:
            print("Используем существующий CreatingTimeSeriesWidget")
            self.time_series_widget.update_data(rr_times, amplitudes, self.session_id)

        self.time_series_widget.show()

    def show_initial_data(self):
        """Отображение исходных данных и корреляции."""
        if not hasattr(self, "canvas"):
            print("Создаем новый график")
            # Корреляционные значения
            corr_raw = np.corrcoef(self.rr_times, self.amplitudes)[0, 1]

            # Создаем фигуру для графиков
            self.figure = plt.figure(figsize=(12, 6))

            # График 1: Исходные данные
            ax1 = self.figure.add_subplot(111)
            ax1.plot(self.rr_times, label="RR_time (ЭКС)", color="red")
            ax1.plot(self.amplitudes, label="Amplitude (ПГ)", color="blue")
            ax1.set_title("Исходные данные")
            ax1.set_xlabel("Индекс")
            ax1.set_ylabel("Значение")
            ax1.legend()
            ax1.grid(True)

            # Отображение графиков
            self.canvas = FigureCanvas(self.figure)
            self.content_layout.addWidget(self.canvas)

            # Корреляционные значения
            self.correlation_label = QLabel(
                f"Корреляция исходных данных: {corr_raw:.4f}\n"
            )
            self.content_layout.addWidget(self.correlation_label)
        else:
            print("Используем существующий график")

        # Показываем виджеты
        self.canvas.show()
        self.correlation_label.show()

    def show_placeholder(self):
        """Заполнитель для других этапов."""
        placeholder_label = QLabel("Здесь будет следующий этап обработки")
        self.content_layout.addWidget(placeholder_label)

    def go_to_next_step(self):
        """Переход к следующему этапу."""
        if self.current_step == 1:  # Переход с этапа 2 на этап 3
            if not hasattr(self.filter_widget, "filtered_rr_times") or not hasattr(self.filter_widget,
                                                                                   "filtered_amplitudes"):
                QMessageBox.warning(self, "Внимание",
                                    "Фильтры не были применены. Примените фильтры перед выбором эпохи.")
                return
        self.current_step += 1
        self.prev_button.setEnabled(True)
        self.step_label.setText(f"Этап {self.current_step + 1}: Следующий этап")
        if self.current_step == self.WIDGETS_COUNT:
            self.next_button.setEnabled(False)
        self.show_step()

    def go_to_previous_step(self):
        """Возврат к предыдущему этапу."""
        if self.current_step <= 0:  # Минимальный этап
            return
        self.current_step -= 1
        print(f"Возврат к этапу {self.current_step}")
        self.next_button.setEnabled(True)
        self.prev_button.setEnabled(self.current_step > 0)
        self.step_label.setText(f"Этап {self.current_step + 1}: Текущий этап")
        if self.current_step == 0:
            print("Показываем исходные данные")
            self.step_label.setText(f"Этап {self.current_step + 1}: Исходные данные")
        elif self.current_step == 1:
            print("Показываем выбор фильтров")
            self.step_label.setText(f"Этап {self.current_step + 1}: Предварительная обработка")
        elif self.current_step == 2:
            print("Показываем выбор эпохи")
            self.step_label.setText(f"Этап {self.current_step + 1}: Выбор \"Эпохи\"")
        elif self.current_step == 3:
            print("Показываем создание временных рядов")
            self.step_label.setText(f"Этап {self.current_step + 1}: Ряды RRi и dUi")
        self.show_step()
