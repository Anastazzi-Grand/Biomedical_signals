import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class RawDataPlotWidget(QWidget):
    def __init__(self, ecs_data, pg_data):
        super().__init__()
        self.ecs_data = ecs_data
        self.pg_data = pg_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Построение графиков
        self.plot_data()

    def plot_data(self):
        # Данные для ЭКС
        rr_times = [data["rr_time"] for data in self.ecs_data]
        x_ecs = range(len(rr_times))  # Используем индексы как временные метки

        # Данные для сигнала дыхания
        amplitudes = [data["amplitude"] for data in self.pg_data]
        x_pg = range(len(amplitudes))  # Используем индексы как временные метки

        # Очистка фигуры
        self.figure.clear()

        # Создание осей
        ax = self.figure.add_subplot(111)

        # Построение графика ЭКС
        ax.plot(x_ecs, rr_times, label="RR_time (ЭКС)", color="red")

        # Построение графика сигнала дыхания
        ax.plot(x_pg, amplitudes, label="Amplitude (ПГ)", color="blue")

        # Настройки графика
        ax.set_title("Сырые данные: ЭКС и сигнал дыхания")
        ax.set_xlabel("Индекс")
        ax.set_ylabel("Значение")
        ax.legend()
        ax.grid(True)

        # Обновление канваса
        self.canvas.draw()
