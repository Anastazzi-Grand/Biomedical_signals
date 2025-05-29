from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QLineEdit, \
    QMessageBox, QButtonGroup
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.signal import butter, filtfilt, cheby1
from scipy.stats import f


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
        self.lowpass_cutoffs = [50, 55, 60, 0.5]  # Возможные значения частоты среза для ФНЧ Баттерворта
        self.chebyshev_params = [
            {"cutoff": 0.4, "order": 2, "ripple": 0.5},  # Параметры для ФНЧ Чебышева
            {"cutoff": 50, "order": 2, "ripple": 0.3},
            {"cutoff": 0.2, "order": 2, "ripple": 0.1}
        ]

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Выберите фильтры:")
        layout.addWidget(title_label)

        # Создаем группу для чекбоксов ФНЧ
        self.lowpass_group = QButtonGroup(self)
        self.lowpass_group.setExclusive(True)  # Разрешает выбор только одного чекбокса

        lowpass_checkboxes = []
        lowpass_butter_group = QHBoxLayout()
        for cutoff in self.lowpass_cutoffs:
            checkbox = QCheckBox(f"ФНЧ ({cutoff} Гц)")
            lowpass_butter_group.addWidget(checkbox)
            lowpass_checkboxes.append(checkbox)
            self.lowpass_group.addButton(checkbox)  # Добавляем в группу

        # Добавляем группу ФНЧ
        layout.addLayout(lowpass_butter_group)

        # Группа для ФНЧ Чебышева
        chebyshev_checkboxes = []
        chebyshev_group = QHBoxLayout()
        for params in self.chebyshev_params:
            label = f"ФНЧ Чебышева (частота {params['cutoff']} Гц, порядок {params['order']}, пульсация {params['ripple']})"
            checkbox = QCheckBox(label)
            chebyshev_group.addWidget(checkbox)
            chebyshev_checkboxes.append(checkbox)
            self.lowpass_group.addButton(checkbox)  # Добавляем в ту же группу

        layout.addLayout(chebyshev_group)

        # Объединяем группы ФНЧ в одну
        self.lowpass_checkboxes = lowpass_checkboxes + chebyshev_checkboxes

        # Кнопка "Убрать выбор ФНЧ"
        reset_button = QPushButton("Убрать выбор ФНЧ")
        reset_button.clicked.connect(self.reset_lowpass_selection)  # Подключаем обработчик
        layout.addWidget(reset_button)

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
        ax1.plot(self.filtered_rr_times, label="RR_time (обработанный)", color="red", linewidth=1)
        ax1.plot(self.filtered_amplitudes, label="Amplitude (обработанный)", color="blue", linewidth=1)
        ax1.set_title("Обработанные сигналы")
        ax1.legend()
        ax1.grid(True)

        # Второй график (спектральный анализ)
        ax2 = self.figure.add_subplot(122)
        freqs_rr, spectrum_rr = self.compute_spectrum(self.filtered_rr_times)
        freqs_amp, spectrum_amp = self.compute_spectrum(self.filtered_amplitudes)

        ax2.plot(freqs_rr, spectrum_rr, label="RR_time (спектр)", color="red", linewidth=1)
        ax2.plot(freqs_amp, spectrum_amp, label="Amplitude (спектр)", color="blue", linewidth=1)
        ax2.set_title("Спектральный анализ")
        ax2.set_xlabel("Частота (Гц)")
        ax2.set_ylabel("Амплитуда")
        ax2.legend()
        ax2.grid(True)

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

        # Проверяем выбор ФНЧ
        selected_lowpass_type = None
        selected_lowpass_param = None
        for i, checkbox in enumerate(self.lowpass_checkboxes):
            if checkbox.isChecked():
                if i < len(self.lowpass_cutoffs):  # ФНЧ (Баттерворта)
                    selected_lowpass_type = "butter"
                    selected_lowpass_param = self.lowpass_cutoffs[i]
                else:  # ФНЧ Чебышева
                    selected_chebyshev_index = i - len(self.lowpass_cutoffs)
                    if selected_chebyshev_index < 0 or selected_chebyshev_index >= len(self.chebyshev_params):
                        QMessageBox.warning(self, "Ошибка", "Некорректный индекс для параметров ФНЧ Чебышева")
                        return
                    selected_lowpass_type = "chebyshev"
                    selected_lowpass_param = self.chebyshev_params[selected_chebyshev_index]
                break

        # Применяем выбранный ФНЧ, только если он выбран
        if selected_lowpass_type == "butter":
            rr_times = self.apply_lowpass_filter(rr_times, cutoff=selected_lowpass_param, fs=self.fs)
            amplitudes = self.apply_lowpass_filter(amplitudes, cutoff=selected_lowpass_param, fs=self.fs)
        elif selected_lowpass_type == "chebyshev":
            params = selected_lowpass_param
            try:
                rr_times = self.chebyshev_lowpass_filter(
                    rr_times, cutoff=params["cutoff"], fs=self.fs, order=params["order"], ripple=params["ripple"]
                )
                amplitudes = self.chebyshev_lowpass_filter(
                    amplitudes, cutoff=params["cutoff"], fs=self.fs, order=params["order"], ripple=params["ripple"]
                )
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось применить ФНЧ Чебышева: {e}")
                return
        # Применение других фильтров
        if self.highpass_checkbox.isChecked():
            rr_times = self.apply_highpass_filter(rr_times, cutoff=0.05, fs=self.fs)
            amplitudes = self.apply_highpass_filter(amplitudes, cutoff=0.05, fs=self.fs)
        if self.notch_checkbox.isChecked():
            rr_times = self.apply_notch_filter(rr_times, notch_freq=50, fs=self.fs)
            amplitudes = self.apply_notch_filter(amplitudes, notch_freq=50, fs=self.fs)
        if self.center_checkbox.isChecked():
            # Нормализация сигнала
            # вычисляет стандартное отклонение элементов массива
            # Нормализация данных перед вычислением спектра
            # amplitudes = (amplitudes - np.mean(amplitudes)) / np.std(amplitudes)
            rr_times = (rr_times - np.mean(rr_times)) / np.std(rr_times)
            amplitudes = amplitudes - np.mean(amplitudes)

        # Сохраняем отфильтрованные данные
        self.filtered_rr_times = rr_times
        self.filtered_amplitudes = amplitudes

        # Перерисовываем графики
        self.plot_data()

        # Вычисляем корреляцию
        corr_raw = np.corrcoef(self.rr_times, self.amplitudes)[0, 1]
        corr_centered = np.corrcoef(rr_times, amplitudes)[0, 1]

        # Вычисляем корреляционное отношение
        correlation_ratio = self.calculate_correlation_ratio(rr_times, amplitudes)

        # Проверка линейности связи
        linearity_check = self.check_linearity(rr_times, amplitudes)

        # Критерий Фишера
        fisher_test_result = self.fisher_test(rr_times, amplitudes)

        # Обновляем метку с корреляцией
        self.correlation_label.setText(
            f"Корреляция исходных данных: {corr_raw:.4f}\n"
            f"Корреляция обработанных данных: {corr_centered:.4f}\n"
            f"Корреляционное отношение: {correlation_ratio:.4f} (чем ближе к 1, тем лучше)\n"
            f"Проверка линейности связи: {linearity_check} (должна быть линейная)\n"
            f"Критерий Фишера: {fisher_test_result:.4f} (значимость > 0.05)"
        )

    def get_filtered_data(self):
        if self.filtered_rr_times is None or self.filtered_amplitudes is None:
            print("Фильтры не были применены")
            return None, None

        print("Возвращаем отфильтрованные данные")
        return self.filtered_rr_times, self.filtered_amplitudes

    def get_filter_state(self):
        """Возвращает текущее состояние фильтров."""
        state = {
            'lowpass': None,  # Для ФНЧ Баттерворта
            'chebyshev_params': None,  # Для ФНЧ Чебышева
            'highpass': self.highpass_checkbox.isChecked(),
            'notch': self.notch_checkbox.isChecked(),
            'center': self.center_checkbox.isChecked()
        }

        # Проверяем выбор ФНЧ среди чекбоксов
        for i, checkbox in enumerate(self.lowpass_checkboxes):
            if checkbox.isChecked():
                if i < len(self.lowpass_cutoffs):  # ФНЧ (Баттерворта)
                    state['lowpass'] = self.lowpass_cutoffs[i]
                else:  # ФНЧ Чебышева
                    chebyshev_index = i - len(self.lowpass_cutoffs)
                    state['chebyshev_params'] = self.chebyshev_params[chebyshev_index]
                break

        return state

    def set_filter_state(self, state):
        """Устанавливает состояние фильтров."""
        # Сначала снимаем все выделения
        self.lowpass_group.setExclusive(False)
        for checkbox in self.lowpass_checkboxes:
            checkbox.setChecked(False)

        # Устанавливаем нужные чекбоксы
        for i, checkbox in enumerate(self.lowpass_checkboxes):
            if i < len(self.lowpass_cutoffs):  # ФНЧ (Баттерворта)
                if state['lowpass'] == self.lowpass_cutoffs[i]:
                    checkbox.setChecked(True)
            else:  # ФНЧ Чебышева
                chebyshev_index = i - len(self.lowpass_cutoffs)
                if state['chebyshev_params'] == self.chebyshev_params[chebyshev_index]:
                    checkbox.setChecked(True)

        # Возвращаем эксклюзивный режим
        self.lowpass_group.setExclusive(True)

        # Устанавливаем остальные фильтры
        self.highpass_checkbox.setChecked(state['highpass'])
        self.notch_checkbox.setChecked(state['notch'])
        self.center_checkbox.setChecked(state['center'])

    @staticmethod
    def compute_spectrum(data):
        """Вычисление спектра сигнала с помощью FFT."""
        n = len(data)  # Длина сигнала
        spectrum = np.abs(np.fft.fft(data)) / n  # Нормализованный спектр
        freqs = np.fft.fftfreq(n, d=1 / 1)  # Частоты

        # Берем только положительные частоты
        spectrum = spectrum[:n // 2]
        freqs = freqs[:n // 2]

        # Фильтрация малых значений
        spectrum = np.where(spectrum < 0.001, 0, spectrum)

        return freqs, spectrum

    @staticmethod
    def apply_lowpass_filter(data, cutoff, fs, order=1):
        """
        Применение ФНЧ Баттерворта.
        Формула: H(s) = 1 / (s^2 + s * (w_c / Q) + w_c^2),
        где w_c = 2 * pi * cutoff — угловая частота среза.
        Реализация через scipy.signal.butter.
        """
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    @staticmethod
    def chebyshev_lowpass_filter(data, cutoff, fs, order, ripple):
        """
        Реализация ФНЧ Чебышева.
        """
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist

        # Расчет коэффициентов фильтра Чебышева
        b, a = cheby1(order, ripple, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    @staticmethod
    def apply_highpass_filter(data, cutoff, fs, order=4):
        """
        Применение ФВЧ Баттерворта.
        Формула: H(s) = s^2 / (s^2 + s * (w_c / Q) + w_c^2),
        где w_c = 2 * pi * cutoff — угловая частота среза.
        Реализация через scipy.signal.butter.
        """
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return filtfilt(b, a, data)

    @staticmethod
    def apply_notch_filter(data, notch_freq, fs, quality_factor=30):
        """
        Применение режекторного фильтра.
        Формула: H(s) = (s^2 + w_0^2) / (s^2 + s * (w_0 / Q) + w_0^2),
        где w_0 = 2 * pi * notch_freq — угловая частота режекции.
        Реализация через scipy.signal.iirnotch.
        """
        nyquist = 0.5 * fs
        normal_notch_freq = notch_freq / nyquist # Нормированная частота режекции
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

    def reset_lowpass_selection(self):
        """Снимает выделение со всех чекбоксов ФНЧ."""
        # Временно отключаем эксклюзивный режим
        self.lowpass_group.setExclusive(False)
        for checkbox in self.lowpass_checkboxes:
            checkbox.setChecked(False)
        # Возвращаем эксклюзивный режим
        self.lowpass_group.setExclusive(True)

    def calculate_DRmgr(self, rr_times):
        """Вычисление межгрупповой дисперсии."""
        J = len(rr_times)
        Rcpv = np.mean(rr_times)
        NKL, bin_edges = np.histogram(rr_times, bins=16)
        cpR = np.histogram(rr_times, bins=16, weights=rr_times)[0] / NKL
        DRmgr = np.sum(NKL * (cpR - Rcpv) ** 2) / J
        return DRmgr

    def calculate_DR(self, rr_times):
        """Вычисление общей дисперсии."""
        DR = np.var(rr_times)
        return DR

    def calculate_correlation_ratio(self, rr_times, amplitudes):
        """Вычисление корреляционного отношения."""
        J = len(rr_times)
        Rcpv = np.mean(rr_times)  # Общее среднее RR-интервалов

        # Разделение данных на группы (классы)
        NKL, bin_edges = np.histogram(amplitudes, bins=16)
        cpR = np.histogram(amplitudes, bins=16, weights=rr_times)[0] / NKL

        # Вычисление межгрупповой дисперсии
        DRmgr = np.sum(NKL * (cpR - Rcpv) ** 2) / J

        # Вычисление общей дисперсии
        DR = np.var(rr_times)

        # Корреляционное отношение
        correlation_ratio = np.sqrt(DRmgr / DR)
        return correlation_ratio

    def check_linearity(self, rr_times, amplitudes):
        """Проверка линейности связи по критерию Блекмана."""
        J = len(rr_times)
        r = np.corrcoef(rr_times, amplitudes)[0, 1]
        Vrasch = J * (r ** 2)

        # Критическое значение для α = 0.05
        critical_value = f.ppf(0.95, 1, J - 2)  # Критическое значение F-распределения

        if Vrasch >= critical_value:
            return f"{Vrasch:.4f} - Линейная связь"
        else:
            return f"{Vrasch:.4f} - Нелинейная связь"

    def fisher_test(self, rr_times, amplitudes):
        """Критерий Фишера для проверки значимости корреляции."""
        J = len(rr_times)
        r = np.corrcoef(rr_times, amplitudes)[0, 1]
        F = (J - 2) * (r ** 2) / (1 - r ** 2)
        return F