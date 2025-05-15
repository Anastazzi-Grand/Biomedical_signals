from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QLabel, QCheckBox, QLineEdit, \
    QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.signal import butter, filtfilt

class FilterSelectionWidget(QWidget):
    def __init__(self, db_session, ecs_data, pg_data):
        super().__init__()
        print("Инициализация FilterSelectionWidget")
        self.db_session = db_session
        self.rr_times = ecs_data
        self.amplitudes = pg_data
        self.fs = 200  # Частота дискретизации

        # Инициализация отфильтрованных данных
        self.filtered_rr_times = np.array(self.rr_times)
        self.filtered_amplitudes = np.array(self.amplitudes)

        # Определение диапазонов фильтров как атрибутов класса
        self.lowpass_cutoffs = [1.0, 2.0, 5.0, 10.0]  # Возможные значения частоты среза для ФНЧ
        self.window_sizes = [5, 10, 20]  # Размеры окна для скользящего окна

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Заголовок
        title_label = QLabel("Выберите фильтры:")
        layout.addWidget(title_label)

        # Радиокнопки для выбора ФНЧ
        lowpass_butter_radio_buttons = []
        lowpass_butter_group = QHBoxLayout()

        for cutoff in self.lowpass_cutoffs:
            radio_button = QRadioButton(f"ФНЧ ({cutoff} Гц)")
            lowpass_butter_group.addWidget(radio_button)
            lowpass_butter_radio_buttons.append(radio_button)

        # Добавляем группу ФНЧ
        layout.addLayout(lowpass_butter_group)

        # Логика для снятия выбора
        for radio_button in lowpass_butter_radio_buttons:
            radio_button.toggled.connect(lambda checked, btn=radio_button: self.toggle_lowpass_filter(btn))

        # Группа для скользящего окна
        moving_average_radio_buttons = []
        moving_average_group = QHBoxLayout()
        for size in self.window_sizes:
            radio_button = QRadioButton(f"Скользящее окно (окно {size})")
            moving_average_group.addWidget(radio_button)
            moving_average_radio_buttons.append(radio_button)
        layout.addLayout(moving_average_group)

        # Логика для снятия выбора
        for radio_button in moving_average_radio_buttons:
            radio_button.toggled.connect(lambda checked, btn=radio_button: self.toggle_lowpass_filter(btn))

        # Объединяем группы ФНЧ в одну
        self.lowpass_radio_buttons = lowpass_butter_radio_buttons + moving_average_radio_buttons

        # Кнопка для удаления артефактов
        self.remove_artifacts_checkbox = QCheckBox("Удаление артефактов")
        layout.addWidget(self.remove_artifacts_checkbox)

        # QLineEdit для ввода начального и конечного индексов
        self.start_index_input = QLineEdit()
        self.end_index_input = QLineEdit()

        # Добавляем эти поля в интерфейс
        indices_layout = QHBoxLayout()
        indices_layout.addWidget(QLabel("Начальный индекс:"))
        indices_layout.addWidget(self.start_index_input)
        indices_layout.addWidget(QLabel("Конечный индекс:"))
        indices_layout.addWidget(self.end_index_input)
        layout.addLayout(indices_layout)

        # Другие фильтры
        self.highpass_checkbox = QCheckBox("Фильтр верхних частот (ФВЧ)")
        self.notch_checkbox = QCheckBox("Режекторный фильтр (50 Гц)")
        self.center_checkbox = QCheckBox("Центрирование данных")
        layout.addWidget(self.highpass_checkbox)
        layout.addWidget(self.notch_checkbox)
        layout.addWidget(self.center_checkbox)

        # Кнопка "Применить"
        apply_button = QPushButton("Применить фильтры")
        apply_button.clicked.connect(self.apply_filters)
        layout.addWidget(apply_button)

        # График
        self.figure = plt.figure(figsize=(15, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Метка для корреляции
        self.correlation_label = QLabel()
        layout.addWidget(self.correlation_label)

        self.setLayout(layout)

        # Отображение исходных данных
        self.plot_data()

    def plot_data(self):
        """Отображение данных на графике."""
        self.figure.clear()

        # Проверяем, есть ли данные для отображения
        if self.filtered_rr_times is None or self.filtered_amplitudes is None:
            print("Ошибка: Отфильтрованные данные не инициализированы.")
            return

        # Первый график
        ax1 = self.figure.add_subplot(121)
        ax1.plot(self.filtered_rr_times, label="RR_time (обработанный)", color="red",
                 linewidth=1)
        ax1.plot(self.filtered_amplitudes, label="Amplitude (обработанный)", color="blue",
                 linewidth=1)
        ax1.set_title("Обработанные сигналы")
        ax1.legend()
        ax1.grid(True)

        # Второй график (спектральный анализ)
        ax2 = self.figure.add_subplot(122)
        freqs_rr, spectrum_rr = self.compute_spectrum(self.filtered_rr_times)
        freqs_amp, spectrum_amp = self.compute_spectrum(self.filtered_amplitudes)

        ax2.plot(freqs_rr, spectrum_rr, label="RR_time (спектр)", color="red", linewidth=1)
        ax2.plot(freqs_amp, spectrum_amp, label="Amplitude (спектр)", color="blue",
                 linewidth=1)
        ax2.set_title("Спектральный анализ")
        ax2.set_xlabel("Частота (Гц)")
        ax2.set_ylabel("Амплитуда")
        ax2.legend()
        ax2.grid(True)

        ymin, ymax = ax2.get_xlim()  # Получаем текущие пределы оси Y
        ax2.set_xlim(ymin, ymax / 2)  # Устанавливаем новые пределы, уменьшенные в 2 раза

        self.canvas.draw()

    def apply_filters(self):
        """Применение выбранных фильтров."""
        rr_times = np.array(self.rr_times)
        amplitudes = np.array(self.amplitudes)

        # Проверяем, выбрано ли удаление артефактов
        if self.remove_artifacts_checkbox.isChecked():
            try:
                # Получаем значения из QLineEdit
                start_index = int(self.start_index_input.text())
                end_index = int(self.end_index_input.text())

                # Проверяем корректность введенных значений
                if start_index < 0 or end_index < 0:
                    raise ValueError("Индексы должны быть неотрицательными.")
                if end_index <= start_index:
                    raise ValueError("Конечный индекс должен быть больше начального.")
                if start_index >= len(rr_times) or end_index > len(rr_times):
                    raise ValueError("Индексы выходят за пределы длины сигнала.")

                # Обрезаем сигналы
                rr_times = rr_times[start_index:end_index]
                amplitudes = amplitudes[start_index:end_index]
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", f"Некорректные значения для удаления артефактов: {e}")
                return

        # Применение ФНЧ
        selected_lowpass_type = None
        selected_lowpass_param = None

        for i, button in enumerate(self.lowpass_radio_buttons):
            if button.isChecked():
                if i < len(self.lowpass_cutoffs):  # ФНЧ (Баттерворта)
                    selected_lowpass_type = "butter"
                    selected_lowpass_param = self.lowpass_cutoffs[i]
                else:  # Скользящее окно
                    selected_lowpass_type = "moving_average"
                    selected_window_size = self.window_sizes[i - len(self.lowpass_cutoffs)]
                    selected_lowpass_param = selected_window_size
                break

        if selected_lowpass_type == "butter":
            rr_times = self.apply_lowpass_filter(rr_times, cutoff=selected_lowpass_param, fs=self.fs)
            amplitudes = self.apply_lowpass_filter(amplitudes, cutoff=selected_lowpass_param, fs=self.fs)
        elif selected_lowpass_type == "moving_average":
            rr_times = self.moving_average_filter(rr_times, window_size=selected_lowpass_param)
            amplitudes = self.moving_average_filter(amplitudes, window_size=selected_lowpass_param)

        # Применение других фильтров
        if self.highpass_checkbox.isChecked():
            rr_times = self.apply_highpass_filter(rr_times, cutoff=0.05, fs=self.fs)
            amplitudes = self.apply_highpass_filter(amplitudes, cutoff=0.05, fs=self.fs)

        if self.notch_checkbox.isChecked():
            rr_times = self.apply_notch_filter(rr_times, notch_freq=50, fs=self.fs)
            amplitudes = self.apply_notch_filter(amplitudes, notch_freq=50, fs=self.fs)

        if self.center_checkbox.isChecked():
            rr_times = rr_times - np.mean(rr_times)
            amplitudes = amplitudes - np.mean(amplitudes)

        # Сохраняем отфильтрованные данные
        self.filtered_rr_times = rr_times
        self.filtered_amplitudes = amplitudes

        # Перерисовываем графики
        self.plot_data()

        # Вычисляем корреляцию
        corr_raw = np.corrcoef(self.rr_times, self.amplitudes)[0, 1]
        corr_centered = np.corrcoef(rr_times, amplitudes)[0, 1]

        # Обновляем метку с корреляцией
        self.correlation_label.setText(
            f"Корреляция исходных данных: {corr_raw:.4f}\n"
            f"Корреляция обработанных данных: {corr_centered:.4f}"
        )

    @staticmethod
    def moving_average_filter(data, window_size):
        """Применение скользящего окна."""
        if window_size < 2:
            return data
        cumsum = np.cumsum(np.insert(data, 0, 0))
        filtered_data = (cumsum[window_size:] - cumsum[:-window_size]) / window_size
        padding = [data[:window_size // 2].mean()] * (window_size // 2)
        filtered_data = np.concatenate((padding, filtered_data, padding))
        return filtered_data

    def get_filtered_data(self):
        if self.filtered_rr_times is None or self.filtered_amplitudes is None:
            print("Фильтры не были применены")
            return None, None

        print("Возвращаем отфильтрованные данные")
        return self.filtered_rr_times, self.filtered_amplitudes

    def get_filter_state(self):
        """Возвращает текущее состояние фильтров."""
        state = {
            'lowpass': None,
            'highpass': self.highpass_checkbox.isChecked(),
            'notch': self.notch_checkbox.isChecked(),
            'center': self.center_checkbox.isChecked(),
            'window_size': None
        }
        for i, button in enumerate(self.lowpass_radio_buttons):
            if button.isChecked():
                if i < len(self.lowpass_cutoffs):
                    state['lowpass'] = self.lowpass_cutoffs[i]
                else:
                    state['window_size'] = self.window_sizes[i - len(self.lowpass_cutoffs)]
                break

        return state

    def set_filter_state(self, state):
        """Устанавливает состояние фильтров."""
        for i, button in enumerate(self.lowpass_radio_buttons):
            if i < len(self.lowpass_cutoffs):
                button.setChecked(state['lowpass'] == self.lowpass_cutoffs[i])
            else:
                button.setChecked(state['window_size'] == self.window_sizes[i - len(self.lowpass_cutoffs)])

        self.highpass_checkbox.setChecked(state['highpass'])
        self.notch_checkbox.setChecked(state['notch'])
        self.center_checkbox.setChecked(state['center'])

    @staticmethod
    def compute_spectrum(data):
        """Вычисление спектра сигнала с помощью FFT."""
        n = len(data)  # Длина сигнала
        spectrum = np.abs(np.fft.fft(data))  # Берем модуль FFT
        freqs = np.fft.fftfreq(n, d=1 / 200)  # Частоты
        spectrum = spectrum[:n // 2]  # Берем только положительные частоты
        freqs = freqs[:n // 2]
        return freqs, spectrum

    @staticmethod
    def apply_lowpass_filter(data, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    @staticmethod
    def apply_highpass_filter(data, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return filtfilt(b, a, data)

    @staticmethod
    def apply_notch_filter(data, notch_freq, fs, quality_factor=30):
        nyquist = 0.5 * fs
        normal_notch_freq = notch_freq / nyquist
        b, a = signal.iirnotch(normal_notch_freq, quality_factor)
        return filtfilt(b, a, data)

    def remove_artifacts(self):
        """Удаление артефактов из сигналов."""
        try:
            # Получаем значения из QLineEdit
            start_index = int(self.start_index_input.text())
            end_index = int(self.end_index_input.text())

            # Проверяем корректность введенных значений
            if start_index < 0 or end_index < 0:
                raise ValueError("Индексы должны быть неотрицательными.")
            if end_index <= start_index:
                raise ValueError("Конечный индекс должен быть больше начального.")
            if start_index >= len(self.filtered_rr_times) or end_index > len(self.filtered_rr_times):
                raise ValueError("Индексы выходят за пределы длины сигнала.")

            # Обрезаем сигналы
            self.filtered_rr_times = self.filtered_rr_times[start_index:end_index]
            self.filtered_amplitudes = self.filtered_amplitudes[start_index:end_index]

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Некорректные значения для удаления артефактов: {e}")

    def toggle_lowpass_filter(self, button):
        """Снятие выбора ФНЧ."""
        if not button.isChecked():
            # Если кнопка отключена, снимаем выбор
            for other_button in self.lowpass_radio_buttons:
                if other_button is not button and other_button.isChecked():
                    other_button.setChecked(False)

