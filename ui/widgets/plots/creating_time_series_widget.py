from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

from database.models import Analysis_result


class CreatingTimeSeriesWidget(QWidget):
    def __init__(self, db_session, rr_times, amplitudes, session_id):
        super().__init__()
        self.db_session = db_session
        self.rr_times = rr_times  # RR-интервалы (ЭКС)
        self.amplitudes = amplitudes  # Амплитуды дыхания
        self.time_series_rr = None  # Временной ряд RR-интервалов
        self.time_series_pg = None  # Временной ряд амплитуд дыхания
        self.session_id = session_id
        self.init_ui()
        self.initialize_plot()  # Инициализация графика при создании виджета

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Формирование временных рядов")
        layout.addWidget(title_label)

        # Выбор интерполяции
        self.interpolation_checkbox = QCheckBox("Применить интерполяцию")
        self.interpolation_checkbox.stateChanged.connect(self.apply_interpolation)  # Подключаем обработчик
        layout.addWidget(self.interpolation_checkbox)

        # Кнопка "Сохранить"
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_results)
        layout.addWidget(save_button)

        # График
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Информационная метка
        self.info_label = QLabel("Результаты: Не обработано")
        layout.addWidget(self.info_label)

        # Установка макета
        self.setLayout(layout)

    def initialize_plot(self):
        """Инициализация графика без интерполяции."""
        try:
            # Шаг 1: Формирование временного ряда R-зубцов
            time_series = np.cumsum([0] + self.rr_times)  # Моменты времени R-зубцов

            # Без интерполяции
            self.time_series_rr = self.rr_times
            self.time_series_pg = self.amplitudes

            # Отображение графика
            self.plot_data(time_series)

            # Обновление информации
            rr_intervals = np.diff(self.time_series_rr)
            delta_u = np.diff(self.time_series_pg)
            self.info_label.setText(f"RR-интервалы: {len(rr_intervals)} значений\nDelta U: {len(delta_u)} значений")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось инициализировать график: {e}")

    def apply_interpolation(self):
        """Применение или отмена интерполяции в зависимости от состояния чекбокса."""
        try:
            if not self.interpolation_checkbox.isChecked():
                # Если интерполяция не выбрана, возвращаем исходные данные
                self.time_series_rr = self.rr_times
                self.time_series_pg = self.amplitudes
                time_series = np.cumsum([0] + self.rr_times)  # Исходная временная сетка
            else:
                # Если интерполяция выбрана, применяем её
                time_series_raw = np.cumsum([0] + self.rr_times)  # Исходная временная сетка
                step = 0.1  # Шаг интерполяции
                new_time_rr = np.arange(time_series_raw[0], time_series_raw[-1], step)

                # Интерполяция RR-интервалов
                interp_func_rr = interp1d(time_series_raw, self.rr_times, kind='linear', fill_value="extrapolate")
                self.time_series_rr = interp_func_rr(new_time_rr)

                # Интерполяция амплитуд дыхания
                interp_func_pg = interp1d(time_series_raw, self.amplitudes, kind='linear', fill_value="extrapolate")
                self.time_series_pg = interp_func_pg(new_time_rr)

                time_series = new_time_rr  # Новая временная сетка

            # Обновление графика
            self.plot_data(time_series)

            # Обновление информации
            rr_intervals = np.diff(self.time_series_rr)
            delta_u = np.diff(self.time_series_pg)
            self.info_label.setText(f"RR-интервалы: {len(rr_intervals)} значений\nDelta U: {len(delta_u)} значений")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить интерполяцию: {e}")

    def plot_data(self, time_series):
        """Отображение временных рядов на графике."""
        self.ax.clear()

        # Отображение данных с учетом временной сетки
        self.ax.plot(time_series, self.time_series_rr, label="RR-интервалы (ЭКС)", color="red")
        self.ax.plot(time_series, self.time_series_pg, label="Амплитуды дыхания", color="blue")

        # Настройка графика
        self.ax.set_title("Временные ряды")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Значение")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def save_results(self):
        """Сохранение результатов в базу данных."""
        try:
            if self.time_series_rr is None or self.time_series_pg is None:
                raise ValueError("Данные не обработаны.")

            # Округление данных до 4 знаков после запятой
            processed_ecs_data = [round(value, 4) for value in self.time_series_rr]
            processed_pg_data = [round(value, 4) for value in self.time_series_pg]

            from services.analysis_service import (
                create_analysis_result,
                delete_analysis_results_by_sessionid,
            )

            # Проверяем, существуют ли уже данные для этого сеанса
            existing_records_count = (
                self.db_session.query(Analysis_result)
                .filter(Analysis_result.sessionid == self.session_id)
                .count()
            )

            if existing_records_count > 0:
                # Если данные существуют, удаляем их
                delete_analysis_results_by_sessionid(self.db_session, self.session_id)
                print(f"Удалено {existing_records_count} записей для session_id={self.session_id}")

            # Добавляем новые записи
            for ecs_value, pg_value in zip(processed_ecs_data, processed_pg_data):
                create_analysis_result(
                    db=self.db_session,
                    sessionid=self.session_id,
                    processed_ecs_data=ecs_value,
                    processed_pg_data=pg_value,
                )

            # Сообщаем пользователю о результате
            if existing_records_count > 0:
                QMessageBox.information(self, "Успех", "Данные успешно перезаписаны!")
            else:
                QMessageBox.information(self, "Успех", "Данные успешно сохранены!")

        except Exception as e:
            self.db_session.rollback()  # Откат изменений в случае ошибки
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {e}")

    def update_data(self, rr_times, amplitudes, session_id):
        """
        Обновление данных и восстановление состояния виджета.
        """
        print("Обновление данных в CreatingTimeSeriesWidget")
        # Обновляем исходные данные
        self.rr_times = rr_times
        self.amplitudes = amplitudes
        self.session_id = session_id

        # Сбрасываем состояние обработки
        self.time_series_rr = None
        self.time_series_pg = None

        # Пересоздаем график
        self.initialize_plot()
