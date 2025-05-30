from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QRadioButton, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

class EpochSelectionWidget(QWidget):
    def __init__(self, db_session, rr_times, amplitudes, session_id):
        super().__init__()
        self.db_session = db_session
        self.rr_times = rr_times  # RR-интервалы (ЭКС)
        self.amplitudes = amplitudes  # Амплитуды дыхания
        self.selected_epoch_start = None  # Начало выбранной эпохи
        self.selected_epoch_end = None  # Конец выбранной эпохи
        self.is_manual_selection = True  # Флаг для ручного/автоматического выбора
        self.session_id = session_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Выберите 'Эпоху' (ровный участок сигнала):")
        layout.addWidget(title_label)

        # Выбор режима: автоматический или ручной
        self.manual_radio = QRadioButton("Ручной выбор")
        self.auto_radio = QRadioButton("Автоматический выбор")
        self.manual_radio.setChecked(True)  # По умолчанию ручной выбор

        # Группировка радиокнопок
        radio_group = QHBoxLayout()
        radio_group.addWidget(self.manual_radio)
        radio_group.addWidget(self.auto_radio)
        layout.addLayout(radio_group)

        # Поле для ввода количества кардиоциклов
        cycle_count_layout = QHBoxLayout()
        self.cycle_count_input = QLineEdit()
        self.cycle_count_input.setText("30")  # Значение по умолчанию
        cycle_count_layout.addWidget(QLabel("Количество кардиоциклов (мин. 30):"))
        cycle_count_layout.addWidget(self.cycle_count_input)
        layout.addLayout(cycle_count_layout)

        # Поля для ручного ввода
        self.start_index_input = QLineEdit()
        self.end_index_input = QLineEdit()
        self.start_index_input.setEnabled(True)
        self.end_index_input.setEnabled(True)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Начальный индекс:"))
        input_layout.addWidget(self.start_index_input)
        input_layout.addWidget(QLabel("Конечный индекс:"))
        input_layout.addWidget(self.end_index_input)
        layout.addLayout(input_layout)

        # Кнопка "Применить"
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.apply_selection)
        layout.addWidget(self.apply_button)

        # Информационная метка
        self.epoch_info_label = QLabel("Выбранный участок: Не выбрано")
        layout.addWidget(self.epoch_info_label)

        # График
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Установка макета
        self.setLayout(layout)

        # Обработчики событий для переключения режима
        self.manual_radio.toggled.connect(self.toggle_selection_mode)
        self.auto_radio.toggled.connect(self.toggle_selection_mode)

        # Инициализация графика
        self.plot_data()

    def toggle_selection_mode(self):
        """Переключение между ручным и автоматическим выбором."""
        if self.manual_radio.isChecked():
            self.is_manual_selection = True
            self.start_index_input.setEnabled(True)
            self.end_index_input.setEnabled(True)
            self.cycle_count_input.setEnabled(False)
        elif self.auto_radio.isChecked():
            self.is_manual_selection = False
            self.start_index_input.setEnabled(False)
            self.end_index_input.setEnabled(False)
            self.cycle_count_input.setEnabled(True)

    def perform_auto_selection(self):
        """Автоматический выбор наиболее ровного участка сигнала."""
        try:
            cycle_count = int(self.cycle_count_input.text())
            if cycle_count < 30 or cycle_count > len(self.rr_times):
                raise ValueError("Количество кардиоциклов должно быть не менее 30 и не более длины сигнала.")

            min_std = float('inf')  # Минимальное СКО
            best_start_index = 0  # Индекс начала лучшего участка
            signal_length = len(self.rr_times)

            for i in range(signal_length - cycle_count + 1):
                segment = self.rr_times[i:i + cycle_count]
                std = np.std(segment)
                mean = np.mean(segment)
                outliers = [x for x in segment if abs(x - mean) > 3 * std]

                if std < min_std and len(outliers) == 0:
                    min_std = std
                    best_start_index = i

            self.selected_epoch_start = best_start_index
            self.selected_epoch_end = best_start_index + cycle_count - 1
            self.epoch_info_label.setText(f"Выбранный участок: {self.selected_epoch_start} - {self.selected_epoch_end}")
            self.highlight_selected_epoch()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def apply_selection(self):
        """Применение выбора эпохи."""
        if self.is_manual_selection:
            try:
                start = int(self.start_index_input.text())
                end = int(self.end_index_input.text())

                # Проверка корректности введенных значений
                if start < 0 or end >= len(self.rr_times):
                    raise ValueError("Индексы выходят за границы сигнала.")
                if end - start + 1 < 30:
                    raise ValueError("Выбранный участок должен содержать не менее 30 кардиоциклов.")

                self.selected_epoch_start = start
                self.selected_epoch_end = end
                self.epoch_info_label.setText(f"Выбранный участок: {start} - {end}")
                self.highlight_selected_epoch()
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))
        else:
            self.perform_auto_selection()

    def plot_data(self):
        """Отображение исходных данных на графике."""
        self.ax.clear()
        self.ax.plot(self.rr_times, label="RR-интервалы (ЭКС)", color="red")  # ЭКС — красный
        self.ax.plot(self.amplitudes, label="Амплитуды дыхания", color="blue")  # Сигнал дыхания — синий
        self.ax.set_title("Выбор эпохи")
        self.ax.legend()
        self.ax.grid(True)  # Добавляем сетку
        self.canvas.draw()

    def highlight_selected_epoch(self):
        """Выделение выбранной эпохи на графике."""
        self.plot_data()
        if self.selected_epoch_start is not None and self.selected_epoch_end is not None:
            self.ax.axvspan(self.selected_epoch_start, self.selected_epoch_end, color='yellow', alpha=0.5)
            self.canvas.draw()

    def update_data(self, rr_times, amplitudes):
        """
        Обновление данных и восстановление состояния выбора эпохи.
        """
        print("Обновление данных в EpochSelectionWidget")
        self.rr_times = rr_times
        self.amplitudes = amplitudes

        # Восстанавливаем выбранный участок, если он был
        if self.selected_epoch_start is not None and self.selected_epoch_end is not None:
            self.epoch_info_label.setText(f"Выбранный участок: {self.selected_epoch_start} - {self.selected_epoch_end}")

        # Перерисовываем график
        self.plot_data()
