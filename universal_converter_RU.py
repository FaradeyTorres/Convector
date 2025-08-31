import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import json
import math
from datetime import datetime, timedelta
import requests

class UniversalConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("UNIVERSAL CONVERTER V1")  # Изменено на V1
        self.root.geometry("1000x750")
        
        # Настройки API
        self.api_file = "converter_api.json"
        self.rates_file = "currency_rates.json"
        self.API_KEY = self.load_api_key()
        self.BASE_URL = "https://v6.exchangerate-api.com/v6/"
        self.rates = {}
        self.last_update = None
        self.currency_mode = False

        # Стили
        self.setup_styles()
        
        # Все возможные конвертации
        self.units = self.load_units()
        
        # Переменные
        self.setup_variables()
        
        # Создание интерфейса
        self.create_interface()
        
        # Инициализация данных
        self.initialize_data()

    def setup_styles(self):
        """Настройка стилей интерфейса"""
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f8ff')
        self.style.configure('TLabel', background='#f0f8ff', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background='#4682b4', foreground='white', 
                           font=('Segoe UI', 14, 'bold'))
        self.style.configure('TButton', font=('Segoe UI', 10), foreground='black')
        self.style.configure('Symbol.TButton', font=('Arial', 12, 'bold'))
        self.style.configure('Api.TFrame', background='#e6f7ff', relief='groove', borderwidth=2)
        self.style.configure('Currency.TButton', background='#90EE90', font=('Segoe UI', 10, 'bold'))
        self.style.configure('Normal.TButton', background='#ADD8E6', font=('Segoe UI', 10, 'bold'))
    
    def load_units(self):
        """Загрузка всех единиц измерения"""
        units = {
            # Масса
            "Масса": {
                "Килограмм (кг)": 1.0,
                "Грамм (г)": 0.001,
                "Миллиграмм (мг)": 1e-6,
                "Тонна (т)": 1000.0,
                "Фунт (lb)": 0.453592,
                "Унция (oz)": 0.0283495,
                "Карат (кар)": 0.0002
            },
            
            # Длина
            "Длина": {
                "Метр (м)": 1.0,
                "Километр (км)": 1000.0,
                "Сантиметр (см)": 0.01,
                "Миллиметр (мм)": 0.001,
                "Микрометр (мкм)": 1e-6,
                "Дюйм (in)": 0.0254,
                "Фут (ft)": 0.3048,
                "Ярд (yd)": 0.9144,
                "Миля (mi)": 1609.34,
                "Морская миля (nmi)": 1852.0
            },
            
            # Объем
            "Объем": {
                "Литр (л)": 1.0,
                "Миллилитр (мл)": 0.001,
                "Галлон (gal)": 3.78541,
                "Пинта (pt)": 0.473176,
                "Куб. метр (м³)": 1000.0,
                "Куб. дюйм (in³)": 0.0163871,
                "Чайная ложка (tsp)": 0.00492892,
                "Столовая ложка (tbsp)": 0.0147868,
                "Чашка (cup)": 0.236588
            },
            
            # Температура
            "Температура": {
                "Цельсий (°C)": "celsius",
                "Фаренгейт (°F)": "fahrenheit",
                "Кельвин (K)": "kelvin"
            },
            
            # Площадь
            "Площадь": {
                "Кв. метр (м²)": 1.0,
                "Кв. километр (км²)": 1e6,
                "Кв. сантиметр (см²)": 0.0001,
                "Гектар (га)": 10000.0,
                "Акр (ac)": 4046.86,
                "Кв. миля (mi²)": 2.59e6,
                "Кв. фут (ft²)": 0.092903
            },
            
            # Скорость
            "Скорость": {
                "м/с": 1.0,
                "км/ч": 0.277778,
                "миль/ч": 0.44704,
                "узлы": 0.514444,
                "Маха": 343.0
            },
            
            # Данные
            "Данные": {
                "Бит (bit)": 1.0,
                "Байт (B)": 8.0,
                "Килобайт (KB)": 8192.0,
                "Мегабайт (MB)": 8388608.0,
                "Гигабайт (GB)": 8589934592.0,
                "Терабайт (TB)": 8796093022208.0
            },
            
            # Энергия
            "Энергия": {
                "Джоуль (J)": 1.0,
                "Килоджоуль (kJ)": 1000.0,
                "Калория (cal)": 4.184,
                "Килокалория (kcal)": 4184.0,
                "кВт·ч": 3600000.0,
                "Электронвольт (эВ)": 1.60218e-19
            },
            
            # Давление
            "Давление": {
                "Паскаль (Па)": 1.0,
                "Бар (бар)": 100000.0,
                "Атмосфера (атм)": 101325.0,
                "мм рт.ст.": 133.322,
                "PSI": 6894.76
            },
            
            # Время
            "Время": {
                "Секунда (с)": 1.0,
                "Минута (мин)": 60.0,
                "Час (ч)": 3600.0,
                "День": 86400.0,
                "Неделя": 604800.0,
                "Год": 31536000.0
            },
            
            # Радиация
            "Радиация": {
                "Зиверт (Sv)": 1.0,
                "Бэр (rem)": 0.01,
                "Рад (rad)": 0.01,
                "Грей (Gy)": 1.0,
                "Рентген (R)": 0.00933
            },
            
            # Астрономия
            "Астрономия": {
                "Световой год (ly)": 1.0,
                "Астрономическая единица (AU)": 63241.1,
                "Парсек (pc)": 3.26156,
                "Километр (km)": 9.461e12,
                "Лунное расстояние (LD)": 384400.0
            },
            
            # Кухня
            "Кухня": {
                "Грамм (г)": 1.0,
                "Килограмм (кг)": 1000.0,
                "Унция (oz)": 28.3495,
                "Фунт (lb)": 453.592,
                "Чайная ложка (tsp)": 5.0,
                "Столовая ложка (tbsp)": 15.0,
                "Стакан (cup)": 240.0,
                "Милилитр (мл)": 1.0,
                "Литр (л)": 1000.0
            },
            
            # Углы
            "Углы": {
                "Градус (°)": 1.0,
                "Радиан (rad)": 57.2958,
                "Град (grad)": 0.9,
                "Оборот (rev)": 360.0
            }
        }
        
        # Валюта отдельно
        self.currency_units = {
            "USD (Доллар США)": 1.0,
            "EUR (Евро)": 0.85,
            "RUB (Рубль РФ)": 75.0,
            "GBP (Фунт стерлингов)": 0.75,
            "JPY (Японская иена)": 110.0,
            "CNY (Китайский юань)": 6.5,
            "AUD (Австралийский доллар)": 1.35,
            "CAD (Канадский доллар)": 1.25,
            "CHF (Швейцарский франк)": 0.92,
            "INR (Индийская рупия)": 75.0,
            "BRL (Бразильский реал)": 5.25
        }
        
        return units
    
    def setup_variables(self):
        """Инициализация переменных"""
        self.current_category = tk.StringVar(value="Масса")
        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        self.input_value = tk.StringVar(value="1.0")
        self.result_value = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Готов к работе")
        self.api_key_var = tk.StringVar(value=self.API_KEY or "")
        self.history = []
    
    def create_interface(self):
        """Создание интерфейса"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="UNIVERSAL CONVERTER V1",  # Изменено на V1
                 style='Header.TLabel').pack(fill=tk.X, ipady=10)
        
        # Кнопка переключения режима
        self.mode_btn = ttk.Button(
            main_frame, 
            text="Конвертер валют", 
            style='Currency.TButton',
            command=self.toggle_currency_mode
        )
        self.mode_btn.pack(fill=tk.X, pady=5)
        
        # Фрейм API (только для валют)
        self.api_frame = ttk.Frame(main_frame, style='Api.TFrame')
        
        ttk.Label(self.api_frame, text="API Key:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        api_entry = ttk.Entry(self.api_frame, textvariable=self.api_key_var, width=40)
        api_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Сохранить API", 
                  command=self.save_api_key).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Обновить курсы", 
                  command=self.update_currency_rates).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Инструкция", 
                  command=self.show_api_instructions).grid(row=0, column=4, padx=5, pady=5)
        
        # Фрейм конвертации
        self.conv_frame = ttk.LabelFrame(main_frame, text="Конвертация")
        self.conv_frame.pack(fill=tk.X, pady=5)
        
        # Категория (скрывается в режиме валют)
        self.category_label = ttk.Label(self.conv_frame, text="Категория:")
        self.category_combo = ttk.Combobox(
            self.conv_frame, 
            textvariable=self.current_category, 
            values=list(self.units.keys()), 
            state="readonly", 
            width=25
        )
        self.category_combo.bind("<<ComboboxSelected>>", self.update_units)
        
        # Единицы измерения
        self.units_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.units_frame, text="Из:").pack(side=tk.LEFT, padx=5)
        self.from_combo = ttk.Combobox(self.units_frame, textvariable=self.from_unit, width=30)
        self.from_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.units_frame, text="↔", style='Symbol.TButton',
                  command=self.swap_units, width=3).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.units_frame, text="В:").pack(side=tk.LEFT, padx=5)
        self.to_combo = ttk.Combobox(self.units_frame, textvariable=self.to_unit, width=30)
        self.to_combo.pack(side=tk.LEFT, padx=5)
        
        # Ввод значения
        self.value_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.value_frame, text="Значение:").pack(side=tk.LEFT, padx=5)
        self.input_entry = ttk.Entry(self.value_frame, textvariable=self.input_value, width=20)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.value_frame, text="Выполнить конвертацию", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        
        # Результат
        result_frame = ttk.LabelFrame(main_frame, text="Результат")
        result_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(result_frame, textvariable=self.result_value, 
                 font=('Segoe UI', 12, 'bold'), state='readonly').pack(fill=tk.X, padx=5, pady=5, ipady=5)
        
        # Статус
        ttk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # История
        history_frame = ttk.LabelFrame(main_frame, text="История конвертаций (последние 20)")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                                    font=('Consolas', 9))
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # Кнопки под историей
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(history_btn_frame, text="Очистить историю", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_btn_frame, text="Сохранить историю", 
                  command=self.save_history).pack(side=tk.LEFT, padx=5)
        
        # Кнопка выхода
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Выход", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def toggle_currency_mode(self):
        """Переключение между обычным и валютным конвертером"""
        self.currency_mode = not self.currency_mode
        
        if self.currency_mode:
            self.mode_btn.config(text="Обычный конвертер", style='Normal.TButton')
            self.api_frame.pack(fill=tk.X, pady=5, before=self.conv_frame)
            
            # Скрываем категории и показываем только валюты
            self.category_label.grid_forget()
            self.category_combo.grid_forget()
            
            # Обновляем единицы измерения для валют
            self.from_combo['values'] = list(self.currency_units.keys())
            self.to_combo['values'] = list(self.currency_units.keys())
            
            if not self.from_unit.get() or self.from_unit.get() not in self.currency_units:
                self.from_unit.set("USD (Доллар США)")
            if not self.to_unit.get() or self.to_unit.get() not in self.currency_units:
                self.to_unit.set("EUR (Евро)")
        else:
            self.mode_btn.config(text="Конвертер валют", style='Currency.TButton')
            self.api_frame.pack_forget()
            
            # Показываем категории
            self.category_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            self.category_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Возвращаем обычные единицы измерения
            self.update_units()
        
        # Обновляем layout
        self.units_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)
        self.value_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        # Очищаем поле ввода при переключении режима
        self.input_value.set("1.0")
        self.result_value.set("")
    
    def initialize_data(self):
        """Инициализация данных при запуске"""
        self.load_currency_rates()
        self.update_units()
        self.load_history()
        self.toggle_currency_mode()  # Начинаем с обычного режима
        self.toggle_currency_mode()  # Переключаем обратно для правильной инициализации
    
    def update_units(self, event=None):
        """Обновление списка единиц измерения"""
        if self.currency_mode:
            return
            
        category = self.current_category.get()
        units = list(self.units[category].keys())
        
        self.from_combo['values'] = units
        self.to_combo['values'] = units
        
        if units:
            if not self.from_unit.get() or self.from_unit.get() not in units:
                self.from_unit.set(units[0])
            if not self.to_unit.get() or self.to_unit.get() not in units:
                self.to_unit.set(units[1] if len(units) > 1 else units[0])
    
    def load_api_key(self):
        """Загрузка API ключа из файла"""
        try:
            if os.path.exists(self.api_file):
                with open(self.api_file, 'r') as f:
                    data = json.load(f)
                    return data.get('api_key', "")
        except Exception as e:
            print(f"Ошибка загрузки API ключа: {e}")
        return ""
    
    def save_api_key(self):
        """Сохранение API ключа в файл"""
        self.API_KEY = self.api_key_var.get().strip()
        try:
            with open(self.api_file, 'w') as f:
                json.dump({'api_key': self.API_KEY}, f)
            messagebox.showinfo("Успех", "API ключ сохранен!")
            self.load_currency_rates()  # Попробуем загрузить курсы с новым ключом
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить ключ: {str(e)}")
    
    def show_api_instructions(self):
        """Показать инструкцию по получению API ключа"""
        instructions = """
        Для работы с валютами необходим API ключ:
        
        1. Перейдите на сайт: https://www.exchangerate-api.com/
        2. Нажмите "Get Free Key"
        3. Зарегистрируйтесь с помощью email
        4. На ваш email придет ключ API
        5. Скопируйте ключ и вставьте в поле выше
        6. Нажмите "Сохранить API"
        
        Бесплатный тариф дает 1500 запросов в месяц.
        Для обновления курсов нажмите "Обновить курсы".
        """
        messagebox.showinfo("Инструкция по получению API ключа", instructions)
    
    def load_currency_rates(self):
        """Загрузка курсов валют из файла или API"""
        try:
            # Пытаемся загрузить из файла
            if os.path.exists(self.rates_file):
                with open(self.rates_file, 'r') as f:
                    data = json.load(f)
                    last_update = datetime.strptime(data['last_update'], '%Y-%m-%d')
                    
                    # Если с последнего обновления прошло меньше 7 дней
                    if datetime.now() - last_update < timedelta(days=7):
                        self.rates = data['rates']
                        self.last_update = last_update
                        self.status_var.set(f"Курсы загружены из файла ({last_update.strftime('%d.%m.%Y')})")
                        
                        # Обновляем коэффициенты в currency_units
                        for curr, rate in self.rates.items():
                            # Найти валюту в currency_units по коду (начало строки)
                            for key in list(self.currency_units.keys()):
                                if key.startswith(curr + " "):
                                    self.currency_units[key] = rate
                                    break
                        return
            
            # Если файла нет, или данные устарели, но есть API ключ - обновляем
            if self.API_KEY:
                self.update_currency_rates()
            else:
                self.status_var.set("Используются сохраненные курсы (без обновления)")
                
        except Exception as e:
            self.status_var.set(f"Ошибка загрузки курсов: {str(e)}")
            # Используем сохраненные значения по умолчанию
    
    def update_currency_rates(self):
        """Обновление курсов валют через API"""
        if not self.API_KEY:
            messagebox.showwarning("Ошибка", "Введите API ключ для обновления курсов")
            return
            
        try:
            self.status_var.set("Обновление курсов...")
            self.root.update()
            
            response = requests.get(f"{self.BASE_URL}{self.API_KEY}/latest/USD")
            data = response.json()
            
            if data['result'] == 'success':
                self.rates = {
                    'USD': 1.0,
                    'EUR': data['conversion_rates']['EUR'],
                    'RUB': data['conversion_rates']['RUB'],
                    'GBP': data['conversion_rates']['GBP'],
                    'JPY': data['conversion_rates']['JPY'],
                    'CNY': data['conversion_rates']['CNY'],
                    'AUD': data['conversion_rates']['AUD'],
                    'CAD': data['conversion_rates']['CAD'],
                    'CHF': data['conversion_rates']['CHF'],
                    'INR': data['conversion_rates']['INR'],
                    'BRL': data['conversion_rates']['BRL']
                }
                
                # Обновляем коэффициенты в currency_units
                for curr, rate in self.rates.items():
                    for key in list(self.currency_units.keys()):
                        if key.startswith(curr + " "):
                            self.currency_units[key] = rate
                            break
                
                # Сохраняем в файл
                self.last_update = datetime.now()
                with open(self.rates_file, 'w') as f:
                    json.dump({
                        'rates': self.rates,
                        'last_update': self.last_update.strftime('%Y-%m-%d')
                    }, f)
                
                self.status_var.set(f"Курсы обновлены ({self.last_update.strftime('%d.%m.%Y')})")
                messagebox.showinfo("Успех", "Курсы валют успешно обновлены!")
            else:
                error_msg = data.get('error-type', 'Unknown error')
                self.status_var.set(f"Ошибка API: {error_msg}")
                messagebox.showerror("Ошибка API", f"Не удалось обновить курсы: {error_msg}")
                
        except Exception as e:
            self.status_var.set(f"Ошибка обновления: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось обновить курсы: {str(e)}")
    
    def get_currency_name(self, code):
        """Получение названия валюты по коду"""
        names = {
            'USD': 'Доллар США',
            'EUR': 'Евро',
            'RUB': 'Рубль РФ',
            'GBP': 'Фунт стерлингов',
            'JPY': 'Японская иена',
            'CNY': 'Китайский юань',
            'AUD': 'Австралийский доллар',
            'CAD': 'Канадский доллар',
            'CHF': 'Швейцарский франк',
            'INR': 'Индийская рупия',
            'BRL': 'Бразильский реал'
        }
        return names.get(code, code)
    
    def convert(self):
        """Выполнение конвертации"""
        try:
            input_value = self.input_value.get()
            if not input_value:
                raise ValueError("Введите значение для конвертации")
            
            value = float(input_value)
            
            if self.currency_mode:
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Выберите валюты для конвертации")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                
                # Проверяем наличие валют в словаре
                if from_unit not in self.currency_units or to_unit not in self.currency_units:
                    raise ValueError("Выбранные валюты не найдены")
                
                # Конвертация с использованием сохраненных значений
                result = value * (self.currency_units[to_unit] / self.currency_units[from_unit])
                self.add_to_history(f"{value} {from_unit} → {result:.6f} {to_unit} (Валюта)")
            else:
                category = self.current_category.get()
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Выберите единицы измерения")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                    
                if category == "Температура":
                    result = self.convert_temperature(value, from_unit, to_unit)
                else:
                    # Для других категорий используем стандартную логику
                    from_val = self.units[category][from_unit]
                    to_val = self.units[category][to_unit]
                    
                    if callable(from_val):
                        base = from_val(value, False)
                    else:
                        base = value * from_val
                        
                    if callable(to_val):
                        result = to_val(base, True)
                    else:
                        result = base / to_val
                
                self.add_to_history(f"{value} {from_unit} → {result:.6f} {to_unit} ({category})")
            
            # Форматирование результата (удаление лишних нулей)
            formatted_result = "{0:.8f}".format(result).rstrip('0').rstrip('.') if '.' in "{0:.8f}".format(result) else str(result)
            self.result_value.set(formatted_result)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка ввода: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка конвертации: {str(e)}")
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Конвертация температуры"""
        if from_unit == to_unit:
            return value
            
        # Конвертация в Цельсии
        if "Фаренгейт" in from_unit:
            celsius = (value - 32) * 5/9
        elif "Кельвин" in from_unit:
            celsius = value - 273.15
        else:
            celsius = value
            
        # Конвертация из Цельсиев
        if "Фаренгейт" in to_unit:
            return celsius * 9/5 + 32
        elif "Кельвин" in to_unit:
            return celsius + 273.15
        else:
            return celsius
    
    def swap_units(self):
        """Обмен единицами измерения"""
        from_unit = self.from_unit.get()
        to_unit = self.to_unit.get()
        self.from_unit.set(to_unit)
        self.to_unit.set(from_unit)
        if self.result_value.get():
            self.convert()
    
    def add_to_history(self, entry):
        """Добавление записи в историю"""
        self.history.append(entry)
        if len(self.history) > 20:
            self.history.pop(0)
        
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        for i, item in enumerate(reversed(self.history), 1):
            self.history_text.insert(tk.END, f"{i}. {item}\n")
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
    
    def clear_history(self):
        """Очистка истории"""
        self.history = []
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def save_history(self):
        """Сохранение истории в файл"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
                title="Сохранить историю конвертаций"
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("История конвертаций:\n")
                    f.write("="*50 + "\n")
                    for i, item in enumerate(self.history, 1):
                        f.write(f"{i}. {item}\n")
                messagebox.showinfo("Успех", "История успешно сохранена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def load_history(self):
        """Загрузка истории из файла"""
        try:
            if os.path.exists("converter_history.json"):
                with open("converter_history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.add_to_history("История загружена")
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalConverter(root)
    root.mainloop()