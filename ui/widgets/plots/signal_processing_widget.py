from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

class SignalProcessingWidget(QWidget):
    def __init__(self, db_session, session_id):
        super().__init__()
        self.db_session = db_session
        self.session_id = session_id
        self.current_step = 0  # Текущий этап обработки
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

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def show_step(self):
        """Отображение текущего этапа обработки."""
        # Очистка предыдущего содержимого
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self.current_step == 0:
            self.show_initial_data()
        else:
            self.show_placeholder()

    def show_initial_data(self):
        """Отображение исходных данных и корреляции."""
        # Вычитание постоянных составляющих
        rr_mean = np.mean(self.rr_times)
        amplitude_mean = np.mean(self.amplitudes)

        rr_centered = self.rr_times - rr_mean
        amplitude_centered = self.amplitudes - amplitude_mean

        # Корреляционные значения
        corr_raw = np.corrcoef(self.rr_times, self.amplitudes)[0, 1]
        corr_centered = np.corrcoef(rr_centered, amplitude_centered)[0, 1]

        # Создаем фигуру для графиков
        figure = plt.figure(figsize=(12, 6))
        grid = QGridLayout()

        # График 1: Исходные данные
        ax1 = figure.add_subplot(121)
        ax1.plot(self.rr_times, label="RR_time (ЭКС)", color="blue")
        ax1.plot(self.amplitudes, label="Amplitude (ПГ)", color="red")
        ax1.set_title("Исходные данные")
        ax1.set_xlabel("Индекс")
        ax1.set_ylabel("Значение")
        ax1.legend()
        ax1.grid(True)

        # График 2: Обработанные данные
        ax2 = figure.add_subplot(122)
        ax2.plot(rr_centered, label="RR_time (обраб.)", color="blue")
        ax2.plot(amplitude_centered, label="Amplitude (обраб.)", color="red")
        ax2.set_title("Обработанные данные")
        ax2.set_xlabel("Индекс")
        ax2.set_ylabel("Значение")
        ax2.legend()
        ax2.grid(True)

        # Отображение графиков
        canvas = FigureCanvas(figure)
        grid.addWidget(canvas, 0, 0, 1, 2)

        # Корреляционные значения
        correlation_label = QLabel(
            f"Корреляция исходных данных: {corr_raw:.4f}\n"
            f"Корреляция обработанных данных: {corr_centered:.4f}"
        )
        grid.addWidget(correlation_label, 1, 0, 1, 2)

        # Добавляем макет в основной контент
        self.content_layout.addLayout(grid)

    def show_placeholder(self):
        """Заполнитель для других этапов."""
        placeholder_label = QLabel("Здесь будет следующий этап обработки")
        self.content_layout.addWidget(placeholder_label)

    def go_to_next_step(self):
        """Переход к следующему этапу."""
        self.current_step += 1
        self.prev_button.setEnabled(True)  # Активируем кнопку "Назад"
        self.step_label.setText(f"Этап {self.current_step + 1}: Следующий этап")
        if self.current_step == 1:  # Если это последний этап
            self.next_button.setEnabled(False)
        self.show_step()

    def go_to_previous_step(self):
        """Возврат к предыдущему этапу."""
        self.current_step -= 1
        self.next_button.setEnabled(True)  # Активируем кнопк
