from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QLabel, QCheckBox
from matplotlib import gridspec
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
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Выберите фильтры:")
        layout.addWidget(title_label)

        # Радиокнопки для выбора ФНЧ
        self.lowpass_radio_buttons = []
        lowpass_cutoffs = [0.5, 1.0, 2.0, 5.0]  # Возможные значения частоты среза

        for cutoff in lowpass_cutoffs:
            radio_button = QRadioButton(f"ФНЧ ({cutoff} Гц)")
            layout.addWidget(radio_button)
            self.lowpass_radio_buttons.append(radio_button)

        # Чекбоксы для других фильтров
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
        self.figure = plt.figure(figsize=(12, 6))
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
        ax1 = self.figure.add_subplot(121)
        ax1.plot(self.rr_times, label="RR_time (ЭКС)", color="blue")
        ax1.plot(self.amplitudes, label="Amplitude (ПГ)", color="red")
        ax1.set_title("Сигналы")
        ax1.legend()
        ax1.grid(True)

        # Второй график (уже)
        ax2 = self.figure.add_subplot(122)
        freqs_rr, spectrum_rr = self.compute_spectrum(self.rr_times)
        freqs_amp, spectrum_amp = self.compute_spectrum(self.amplitudes)

        ax2.plot(freqs_rr, spectrum_rr, label="RR_time (спектр)", color="blue")
        ax2.plot(freqs_amp, spectrum_amp, label="Amplitude (спектр)", color="red")
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

        lowpass_cutoffs = [0.5, 1.0, 2.0, 5.0]  # Возможные значения частоты среза

        selected_cutoff = None
        for i, button in enumerate(self.lowpass_radio_buttons):
            if button.isChecked():
                selected_cutoff = lowpass_cutoffs[i]
                break

        if selected_cutoff is not None:
            rr_times = self.apply_lowpass_filter(rr_times, cutoff=selected_cutoff, fs=self.fs)
            amplitudes = self.apply_lowpass_filter(amplitudes, cutoff=selected_cutoff, fs=self.fs)

        if self.highpass_checkbox.isChecked():
            rr_times = self.apply_highpass_filter(rr_times, cutoff=0.05, fs=self.fs)
            amplitudes = self.apply_highpass_filter(amplitudes, cutoff=0.05, fs=self.fs)

        if self.notch_checkbox.isChecked():
            rr_times = self.apply_notch_filter(rr_times, notch_freq=50, fs=self.fs)
            amplitudes = self.apply_notch_filter(amplitudes, notch_freq=50, fs=self.fs)

        if self.center_checkbox.isChecked():
            rr_times = rr_times - np.mean(rr_times)
            amplitudes = amplitudes - np.mean(amplitudes)

        # Вычисляем корреляцию
        corr_raw = np.corrcoef(self.rr_times, self.amplitudes)[0, 1]
        corr_centered = np.corrcoef(rr_times, amplitudes)[0, 1]

        # Обновление графика
        self.figure.clear()

        # Первый график (шире)
        ax1 = self.figure.add_subplot(121)
        ax1.plot(rr_times, label="RR_time (обработанный)", color="blue")
        ax1.plot(amplitudes, label="Amplitude (обработанный)", color="red")
        ax1.set_title("Обработанные сигналы")
        ax1.legend()
        ax1.grid(True)

        # Второй график (уже)
        ax2 = self.figure.add_subplot(122)
        freqs_rr, spectrum_rr = self.compute_spectrum(rr_times)
        freqs_amp, spectrum_amp = self.compute_spectrum(amplitudes)

        ax2.plot(freqs_rr, spectrum_rr, label="RR_time (спектр)", color="blue")
        ax2.plot(freqs_amp, spectrum_amp, label="Amplitude (спектр)", color="red")
        ax2.set_title("Спектральный анализ")
        ax2.set_xlabel("Частота (Гц)")
        ax2.set_ylabel("Амплитуда")
        ax2.legend()
        ax2.grid(True)

        ymin, ymax = ax2.get_xlim()  # Получаем текущие пределы оси Y
        ax2.set_xlim(ymin, ymax / 2)  # Устанавливаем новые пределы, уменьшенные в 2 раза

        self.canvas.draw()

        # Обновляем метку с корреляцией
        self.correlation_label.setText(
            f"Корреляция исходных данных: {corr_raw:.4f}\n"
            f"Корреляция обработанных данных: {corr_centered:.4f}"
        )

    @staticmethod
    def compute_spectrum(data):
        """Вычисление спектра сигнала с помощью FFT."""
        n = len(data)  # Длина сигнала
        spectrum = np.abs(np.fft.fft(data))  # Берем модуль FFT
        freqs = np.fft.fftfreq(n, d=1/200)  # Частоты
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
