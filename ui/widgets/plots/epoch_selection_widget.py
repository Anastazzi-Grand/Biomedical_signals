from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector


class EpochSelectionWidget(QWidget):
    def __init__(self, db_session, rr_times, amplitudes):
        super().__init__()
        print("Инициализация EpochSelectionWidget")
        self.db_session = db_session
        self.rr_times = rr_times  # RR-интервалы
        self.amplitudes = amplitudes  # Амплитуды дыхания
        self.selected_epoch_start = None  # Начало выбранной эпохи
        self.selected_epoch_end = None  # Конец выбранной эпохи
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Выберите 'Эпоху' (участок сигнала):")
        layout.addWidget(title_label)

        # Чекбокс для автоматического выбора эпохи
        self.auto_select_checkbox = QCheckBox("Автоматически выбрать эпоху (30 кардиоциклов)")
        self.auto_select_checkbox.setChecked(True)  # По умолчанию включено
        layout.addWidget(self.auto_select_checkbox)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Выбрать участок вручную")
        self.select_button.clicked.connect(self.enable_manual_selection)
        button_layout.addWidget(self.select_button)

        self.reset_button = QPushButton("Сбросить выбор")
        self.reset_button.clicked.connect(self.reset_selection)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        # График
        self.figure = plt.figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Метка для информации о выбранном участке
        self.epoch_info_label = QLabel("Выбранный участок: Не выбрано")
        layout.addWidget(self.epoch_info_label)

        self.setLayout(layout)

        # Отображение исходных данных
        self.plot_data()

    def update_data(self, rr_times, amplitudes):
        """Обновляет данные и перерисовывает график."""
        self.rr_times = rr_times
        self.amplitudes = amplitudes
        self.plot_data()

    def plot_data(self):
        """Отображение данных на графике."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.rr_times, label="RR_time (ЭКС)", color="blue")
        ax.plot(self.amplitudes, label="Amplitude (ПГ)", color="red")
        ax.set_title("Выбор 'Эпохи'")
        ax.set_xlabel("Индекс")
        ax.set_ylabel("Значение")
        ax.legend()
        ax.grid(True)

        if self.auto_select_checkbox.isChecked():
            self.auto_select_epoch(ax)

        if self.selected_epoch_start is not None and self.selected_epoch_end is not None:
            ax.axvspan(self.selected_epoch_start, self.selected_epoch_end, color="yellow", alpha=0.3)

        self.canvas.draw()

    def auto_select_epoch(self, ax):
        """Автоматический выбор эпохи (30 кардиоциклов)."""
        if len(self.rr_times) < 30:
            print("Недостаточно данных для автоматического выбора эпохи.")
            return

        # Вычисляем индексы начала и конца эпохи
        self.selected_epoch_start = 0
        self.selected_epoch_end = 30

        # Обновляем метку с информацией о выбранном участке
        self.epoch_info_label.setText(
            f"Выбранный участок: {self.selected_epoch_start} - {self.selected_epoch_end}"
        )

        # Выделяем участок на графике
        ax.axvspan(self.selected_epoch_start, self.selected_epoch_end, color="yellow", alpha=0.3)

    def enable_manual_selection(self):
        """Включение ручного выбора участка."""
        print("Включение ручного выбора участка")

        # Очищаем график для нового выбора
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.rr_times, label="RR_time (ЭКС)", color="blue")
        ax.plot(self.amplitudes, label="Amplitude (ПГ)", color="red")
        ax.set_title("Выбор 'Эпохи'")
        ax.set_xlabel("Индекс")
        ax.set_ylabel("Значение")
        ax.legend()
        ax.grid(True)

        # Добавляем SpanSelector для ручного выбора
        def onselect(xmin, xmax):
            self.selected_epoch_start = int(xmin)
            self.selected_epoch_end = int(xmax)
            print(f"Выбран участок: {self.selected_epoch_start} - {self.selected_epoch_end}")
            self.epoch_info_label.setText(
                f"Выбранный участок: {self.selected_epoch_start} - {self.selected_epoch_end}"
            )
            self.plot_data()

        span = SpanSelector(ax, onselect, "horizontal", useblit=True, rectprops=dict(alpha=0.5, facecolor="yellow"))
        self.canvas.draw()

    def reset_selection(self):
        """Сброс выбора эпохи."""
        self.selected_epoch_start = None
        self.selected_epoch_end = None
        self.epoch_info_label.setText("Выбранный участок: Не выбрано")
        self.plot_data()
