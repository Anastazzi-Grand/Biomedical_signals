from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class ProcessedDataWidget(QWidget):
    def __init__(self, processed_ecs_data, processed_pg_data):
        super().__init__()
        self.processed_ecs_data = processed_ecs_data
        self.processed_pg_data = processed_pg_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Создаем график
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Установка макета
        self.setLayout(layout)

        # Отображение данных
        self.plot_data()

    def plot_data(self):
        """Отображение обработанных данных на графике."""
        self.ax.clear()

        # Отображение данных
        self.ax.plot(self.processed_ecs_data, label="Обработанные RR-интервалы", color="red")
        self.ax.plot(self.processed_pg_data, label="Обработанные амплитуды дыхания", color="blue")

        # Настройка графика
        self.ax.set_title("Обработанные данные")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Значение")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()
