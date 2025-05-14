from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QLabel, QCheckBox
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
        self.filtered_rr_times = None  # Для хранения отфильтрованных данных
        self.filtered_amplitudes = None

        # Определение диапазонов фильтров как атрибутов класса
        self.lowpass_cutoffs = [1.0, 2.0, 30.0, 50.0]  # Возможные значения частоты среза для ФНЧ
        self.bandpass_ranges = {
            "HF": (0.15, 0.4),
            "LF": (0.04, 0.15),
            "VLF": (0.003, 0.04)
        }  # Диапазоны полосовых фильтров
        self.window_sizes = [5, 10, 20]  # Размеры окна для скользящего окна

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Заголовок
        title_label = QLabel("Выберите фильтры:")
        layout.addWidget(title_label)

        # Группа для ФНЧ (метод Баттерворта)
        lowpass_butter_radio_buttons = []
        lowpass_butter_group = QHBoxLayout()
        for cutoff in self.lowpass_cutoffs:
            radio_button = QRadioButton(f"ФНЧ ({cutoff} Гц)")
            lowpass_butter_group.addWidget(radio_button)
            lowpass_butter_radio_buttons.append(radio_button)
        layout.addLayout(lowpass_butter_group)

        # Группа для скользящего окна
        moving_average_radio_buttons = []
        moving_average_group = QHBoxLayout()
        for size in self.window_sizes:
            radio_button = QRadioButton(f"Скользящее окно (окно {size})")
            moving_average_group.addWidget(radio_button)
            moving_average_radio_buttons.append(radio_button)
        layout.addLayout(moving_average_group)

        # Объединяем группы ФНЧ в одну
        self.lowpass_radio_buttons = lowpass_butter_radio_buttons + moving_average_radio_buttons

        # Группа для полосового фильтра
        self.bandpass_checkboxes = []

        bandpass_group = QHBoxLayout()
        for name in self.bandpass_ranges.keys():
            checkbox = QCheckBox(name)
            bandpass_group.addWidget(checkbox)
            self.bandpass_checkboxes.append(checkbox)
        layout.addLayout(bandpass_group)

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

        # Первый график (шире)
        ax1 = self.figure.add_subplot(131)
        ax1.plot(self.rr_times, label="RR_time (ЭКС)", color="red")
        ax1.plot(self.amplitudes, label="Amplitude (ПГ)", color="blue")
        ax1.set_title("Сигналы")
        ax1.legend()
        ax1.grid(True)

        # Второй график (спектральный анализ)
        ax2 = self.figure.add_subplot(132)
        freqs_rr, spectrum_rr = self.compute_spectrum(self.rr_times)
        freqs_amp, spectrum_amp = self.compute_spectrum(self.amplitudes)

        ax2.plot(freqs_rr, spectrum_rr, label="RR_time (спектр)", color="red")
        ax2.plot(freqs_amp, spectrum_amp, label="Amplitude (спектр)", color="blue")
        ax2.set_title("Спектральный анализ")
        ax2.set_xlabel("Частота (Гц)")
        ax2.set_ylabel("Амплитуда")
        ax2.legend()
        ax2.grid(True)

        ymin, ymax = ax2.get_xlim()  # Получаем текущие пределы оси Y
        ax2.set_xlim(ymin, ymax / 2)  # Устанавливаем новые пределы, уменьшенные в 2 раза

        # Третий график (полосовой фильтр)
        ax3 = self.figure.add_subplot(133)
        ax3.set_title("Результаты полосового фильтра")
        ax3.set_xlabel("Частота (Гц)")
        ax3.set_ylabel("Амплитуда")
        ax3.grid(True)

        self.canvas.draw()

    def apply_filters(self):
        """Применение выбранных фильтров."""
        rr_times = np.array(self.rr_times)
        amplitudes = np.array(self.amplitudes)

        # 1. Применение ФНЧ
        selected_lowpass_type = None
        selected_lowpass_param = None

        # Проверяем, какой ФНЧ выбран
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

        # 2. Применение полосового фильтра
        bandpass_filtered_rr_times = rr_times.copy()
        bandpass_filtered_amplitudes = amplitudes.copy()

        for i, checkbox in enumerate(self.bandpass_checkboxes):
            if checkbox.isChecked():
                name, (lowcut, highcut) = list(self.bandpass_ranges.items())[i]
                bandpass_filtered_rr_times = self.apply_bandpass_filter(bandpass_filtered_rr_times, lowcut=lowcut,
                                                                        highcut=highcut, fs=self.fs)
                bandpass_filtered_amplitudes = self.apply_bandpass_filter(bandpass_filtered_amplitudes, lowcut=lowcut,
                                                                          highcut=highcut, fs=self.fs)

        # 3. Применение других фильтров
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

        # Сохраняем результаты полосового фильтра
        self.bandpass_filtered_rr_times = bandpass_filtered_rr_times
        self.bandpass_filtered_amplitudes = bandpass_filtered_amplitudes

        # Вычисляем корреляцию
        corr_raw = np.corrcoef(self.rr_times, self.amplitudes)[0, 1]
        corr_centered = np.corrcoef(rr_times, amplitudes)[0, 1]

        # Обновление графика
        self.figure.clear()

        # Первый график
        ax1 = self.figure.add_subplot(131)
        ax1.plot(rr_times, label="RR_time (обработанный)", color="red")
        ax1.plot(amplitudes, label="Amplitude (обработанный)", color="blue")
        ax1.set_title("Обработанные сигналы")
        ax1.legend()
        ax1.grid(True)

        # Второй график
        ax2 = self.figure.add_subplot(132)
        freqs_rr, spectrum_rr = self.compute_spectrum(rr_times)
        freqs_amp, spectrum_amp = self.compute_spectrum(amplitudes)

        ax2.plot(freqs_rr, spectrum_rr, label="RR_time (спектр)", color="red")
        ax2.plot(freqs_amp, spectrum_amp, label="Amplitude (спектр)", color="blue")
        ax2.set_title("Спектральный анализ")
        ax2.set_xlabel("Частота (Гц)")
        ax2.set_ylabel("Амплитуда")
        ax2.legend()
        ax2.grid(True)

        ymin, ymax = ax2.get_xlim()  # Получаем текущие пределы оси Y
        ax2.set_xlim(ymin, ymax / 2)  # Устанавливаем новые пределы, уменьшенные в 2 раза

        # Третий график (полосовой фильтр)
        ax3 = self.figure.add_subplot(133)
        ax3.plot(self.bandpass_filtered_rr_times, label="HF (RR_time)", linestyle="--", color="red")
        ax3.plot(self.bandpass_filtered_amplitudes, label="HF (Amplitude)", linestyle="-.", color="blue")
        ax3.set_title("Результаты полосового фильтра")
        ax3.set_xlabel("Индекс")
        ax3.set_ylabel("Значение")
        ax3.legend()
        ax3.grid(True)

        self.canvas.draw()

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

    @staticmethod
    def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
        """Применение полосового фильтра."""
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band', analog=False)
        return filtfilt(b, a, data)

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
            'bandpass': [],
            'window_size': None
        }
        for i, button in enumerate(self.lowpass_radio_buttons):
            if button.isChecked():
                if i < len(self.lowpass_cutoffs):
                    state['lowpass'] = self.lowpass_cutoffs[i]
                else:
                    state['window_size'] = self.window_sizes[i - len(self.lowpass_cutoffs)]
                break

        for i, checkbox in enumerate(self.bandpass_checkboxes):
            if checkbox.isChecked():
                state['bandpass'].append(list(self.bandpass_ranges.keys())[i])

        return state

    def set_filter_state(self, state):
        """Устанавливает состояние фильтров."""
        for i, button in enumerate(self.lowpass_radio_buttons):
            if i < len(self.lowpass_cutoffs):
                button.setChecked(state['lowpass'] == self.lowpass_cutoffs[i])
            else:
                button.setChecked(state['window_size'] == self.window_sizes[i - len(self.lowpass_cutoffs)])

        for i, checkbox in enumerate(self.bandpass_checkboxes):
            checkbox.setChecked(list(self.bandpass_ranges.keys())[i] in state['bandpass'])

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
