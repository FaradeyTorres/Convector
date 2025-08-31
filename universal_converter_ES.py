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
        self.root.title("CONVERSOR UNIVERSAL V1")  
        self.root.geometry("1000x750")
        
        # Configuración API
        self.api_file = "converter_api.json"
        self.rates_file = "currency_rates.json"
        self.API_KEY = self.load_api_key()
        self.BASE_URL = "https://v6.exchangerate-api.com/v6/"
        self.rates = {}
        self.last_update = None
        self.currency_mode = False

        # Estilos
        self.setup_styles()
        
        # Todas las conversiones posibles
        self.units = self.load_units()
        
        # Variables
        self.setup_variables()
        
        # Interfaz
        self.create_interface()
        
        # Inicialización
        self.initialize_data()

    def setup_styles(self):
        """Configurar estilos"""
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
        """Cargar unidades"""
        units = {
            # Masa
            "Masa": {
                "Kilogramo (kg)": 1.0,
                "Gramo (g)": 0.001,
                "Miligramo (mg)": 1e-6,
                "Tonelada (t)": 1000.0,
                "Libra (lb)": 0.453592,
                "Onza (oz)": 0.0283495,
                "Quilate (ct)": 0.0002
            },
            
            # Longitud
            "Longitud": {
                "Metro (m)": 1.0,
                "Kilómetro (km)": 1000.0,
                "Centímetro (cm)": 0.01,
                "Milímetro (mm)": 0.001,
                "Micrómetro (µm)": 1e-6,
                "Pulgada (in)": 0.0254,
                "Pie (ft)": 0.3048,
                "Yarda (yd)": 0.9144,
                "Milla (mi)": 1609.34,
                "Milla náutica (nmi)": 1852.0
            },
            
            # Volumen
            "Volumen": {
                "Litro (L)": 1.0,
                "Mililitro (mL)": 0.001,
                "Galón (gal)": 3.78541,
                "Pinta (pt)": 0.473176,
                "Metro cúbico (m³)": 1000.0,
                "Pulgada cúbica (in³)": 0.0163871,
                "Cucharadita (tsp)": 0.00492892,
                "Cucharada (tbsp)": 0.0147868,
                "Taza (cup)": 0.236588
            },
            
            # Temperatura
            "Temperatura": {
                "Celsius (°C)": "celsius",
                "Fahrenheit (°F)": "fahrenheit",
                "Kelvin (K)": "kelvin"
            },
            
            # Área
            "Área": {
                "Metro cuadrado (m²)": 1.0,
                "Kilómetro cuadrado (km²)": 1e6,
                "Centímetro cuadrado (cm²)": 0.0001,
                "Hectárea (ha)": 10000.0,
                "Acre (ac)": 4046.86,
                "Milla cuadrada (mi²)": 2.59e6,
                "Pie cuadrado (ft²)": 0.092903
            },
            
            # Velocidad
            "Velocidad": {
                "m/s": 1.0,
                "km/h": 0.277778,
                "mph": 0.44704,
                "Nudos": 0.514444,
                "Mach": 343.0
            },
            
            # Datos
            "Datos": {
                "Bit (bit)": 1.0,
                "Byte (B)": 8.0,
                "Kilobyte (KB)": 8192.0,
                "Megabyte (MB)": 8388608.0,
                "Gigabyte (GB)": 8589934592.0,
                "Terabyte (TB)": 8796093022208.0
            },
            
            # Energía
            "Energía": {
                "Julio (J)": 1.0,
                "Kilojulio (kJ)": 1000.0,
                "Caloría (cal)": 4.184,
                "Kilocaloría (kcal)": 4184.0,
                "kWh": 3600000.0,
                "Electronvoltio (eV)": 1.60218e-19
            },
            
            # Presión
            "Presión": {
                "Pascal (Pa)": 1.0,
                "Bar (bar)": 100000.0,
                "Atmósfera (atm)": 101325.0,
                "mmHg": 133.322,
                "PSI": 6894.76
            },
            
            # Tiempo
            "Tiempo": {
                "Segundo (s)": 1.0,
                "Minuto (min)": 60.0,
                "Hora (h)": 3600.0,
                "Día": 86400.0,
                "Semana": 604800.0,
                "Año": 31536000.0
            },
            
            # Radiación
            "Radiación": {
                "Sievert (Sv)": 1.0,
                "Rem (rem)": 0.01,
                "Rad (rad)": 0.01,
                "Gray (Gy)": 1.0,
                "Roentgen (R)": 0.00933
            },
            
            # Astronomía
            "Astronomía": {
                "Año luz (ly)": 1.0,
                "Unidad astronómica (AU)": 63241.1,
                "Pársec (pc)": 3.26156,
                "Kilómetro (km)": 9.461e12,
                "Distancia lunar (LD)": 384400.0
            },
            
            # Cocina
            "Cocina": {
                "Gramo (g)": 1.0,
                "Kilogramo (kg)": 1000.0,
                "Onza (oz)": 28.3495,
                "Libra (lb)": 453.592,
                "Cucharadita (tsp)": 5.0,
                "Cucharada (tbsp)": 15.0,
                "Taza (cup)": 240.0,
                "Mililitro (mL)": 1.0,
                "Litro (L)": 1000.0
            },
            
            # Ángulos
            "Ángulos": {
                "Grado (°)": 1.0,
                "Radián (rad)": 57.2958,
                "Gradian (grad)": 0.9,
                "Revolución (rev)": 360.0
            }
        }
        
        # Divisas
        self.currency_units = {
            "USD (Dólar EE.UU.)": 1.0,
            "EUR (Euro)": 0.85,
            "RUB (Rublo ruso)": 75.0,
            "GBP (Libra esterlina)": 0.75,
            "JPY (Yen japonés)": 110.0,
            "CNY (Yuan chino)": 6.5,
            "AUD (Dólar australiano)": 1.35,
            "CAD (Dólar canadiense)": 1.25,
            "CHF (Franco suizo)": 0.92,
            "INR (Rupia india)": 75.0,
            "BRL (Real brasileño)": 5.25
        }
        
        return units
    
    def setup_variables(self):
        """Inicializar variables"""
        self.current_category = tk.StringVar(value="Masa")
        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        self.input_value = tk.StringVar(value="1.0")
        self.result_value = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Listo")
        self.api_key_var = tk.StringVar(value=self.API_KEY or "")
        self.history = []
    
    def create_interface(self):
        """Crear interfaz"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Encabezado
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="CONVERSOR UNIVERSAL V1",
                 style='Header.TLabel').pack(fill=tk.X, ipady=10)
        
        # Botón cambio modo
        self.mode_btn = ttk.Button(
            main_frame, 
            text="Conversor de divisas", 
            style='Currency.TButton',
            command=self.toggle_currency_mode
        )
        self.mode_btn.pack(fill=tk.X, pady=5)
        
        # Marco API (solo divisas)
        self.api_frame = ttk.Frame(main_frame, style='Api.TFrame')
        
        ttk.Label(self.api_frame, text="Clave API:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        api_entry = ttk.Entry(self.api_frame, textvariable=self.api_key_var, width=40)
        api_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Guardar API", 
                  command=self.save_api_key).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Actualizar tasas", 
                  command=self.update_currency_rates).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Instrucciones", 
                  command=self.show_api_instructions).grid(row=0, column=4, padx=5, pady=5)
        
        # Marco conversión
        self.conv_frame = ttk.LabelFrame(main_frame, text="Conversión")
        self.conv_frame.pack(fill=tk.X, pady=5)
        
        # Categoría (oculto en modo divisas)
        self.category_label = ttk.Label(self.conv_frame, text="Categoría:")
        self.category_combo = ttk.Combobox(
            self.conv_frame, 
            textvariable=self.current_category, 
            values=list(self.units.keys()), 
            state="readonly", 
            width=25
        )
        self.category_combo.bind("<<ComboboxSelected>>", self.update_units)
        
        # Unidades
        self.units_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.units_frame, text="De:").pack(side=tk.LEFT, padx=5)
        self.from_combo = ttk.Combobox(self.units_frame, textvariable=self.from_unit, width=30)
        self.from_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.units_frame, text="↔", style='Symbol.TButton',
                  command=self.swap_units, width=3).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.units_frame, text="A:").pack(side=tk.LEFT, padx=5)
        self.to_combo = ttk.Combobox(self.units_frame, textvariable=self.to_unit, width=30)
        self.to_combo.pack(side=tk.LEFT, padx=5)
        
        # Valor entrada
        self.value_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.value_frame, text="Valor:").pack(side=tk.LEFT, padx=5)
        self.input_entry = ttk.Entry(self.value_frame, textvariable=self.input_value, width=20)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.value_frame, text="Convertir", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        
        # Resultado
        result_frame = ttk.LabelFrame(main_frame, text="Resultado")
        result_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(result_frame, textvariable=self.result_value, 
                 font=('Segoe UI', 12, 'bold'), state='readonly').pack(fill=tk.X, padx=5, pady=5, ipady=5)
        
        # Estado
        ttk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # Historial
        history_frame = ttk.LabelFrame(main_frame, text="Historial (últimos 20)")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                                    font=('Consolas', 9))
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # Botones historial
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(history_btn_frame, text="Limpiar historial", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_btn_frame, text="Guardar historial", 
                  command=self.save_history).pack(side=tk.LEFT, padx=5)
        
        # Botón salir
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Salir", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def toggle_currency_mode(self):
        """Cambiar entre modo normal y divisas"""
        self.currency_mode = not self.currency_mode
        
        if self.currency_mode:
            self.mode_btn.config(text="Conversor normal", style='Normal.TButton')
            self.api_frame.pack(fill=tk.X, pady=5, before=self.conv_frame)
            
            # Ocultar categorías
            self.category_label.grid_forget()
            self.category_combo.grid_forget()
            
            # Actualizar unidades para divisas
            self.from_combo['values'] = list(self.currency_units.keys())
            self.to_combo['values'] = list(self.currency_units.keys())
            
            if not self.from_unit.get() or self.from_unit.get() not in self.currency_units:
                self.from_unit.set("USD (Dólar EE.UU.)")
            if not self.to_unit.get() or self.to_unit.get() not in self.currency_units:
                self.to_unit.set("EUR (Euro)")
        else:
            self.mode_btn.config(text="Conversor de divisas", style='Currency.TButton')
            self.api_frame.pack_forget()
            
            # Mostrar categorías
            self.category_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            self.category_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Restaurar unidades normales
            self.update_units()
        
        # Actualizar layout
        self.units_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)
        self.value_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        # Limpiar campo al cambiar modo
        self.input_value.set("1.0")
        self.result_value.set("")
    
    def initialize_data(self):
        """Inicializar datos"""
        self.load_currency_rates()
        self.update_units()
        self.load_history()
        self.toggle_currency_mode()  # Empezar en modo normal
        self.toggle_currency_mode()  # Cambiar para inicialización correcta
    
    def update_units(self, event=None):
        """Actualizar lista de unidades"""
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
        """Cargar clave API desde archivo"""
        try:
            if os.path.exists(self.api_file):
                with open(self.api_file, 'r') as f:
                    data = json.load(f)
                    return data.get('api_key', "")
        except Exception as e:
            print(f"Error cargando API: {e}")
        return ""
    
    def save_api_key(self):
        """Guardar clave API en archivo"""
        self.API_KEY = self.api_key_var.get().strip()
        try:
            with open(self.api_file, 'w') as f:
                json.dump({'api_key': self.API_KEY}, f)
            messagebox.showinfo("Éxito", "¡Clave API guardada!")
            self.load_currency_rates()  # Intentar cargar tasas con nueva clave
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando clave: {str(e)}")
    
    def show_api_instructions(self):
        """Mostrar instrucciones API"""
        instructions = """
        Para divisas necesita clave API:
        
        1. Visite: https://www.exchangerate-api.com/
        2. Haga clic en "Get Free Key"
        3. Regístrese con su email
        4. Recibirá la clave API por email
        5. Cópiela y péguela arriba
        6. Haga clic en "Guardar API"
        
        Plan gratuito permite 1500 solicitudes/mes.
        Haga clic en "Actualizar tasas" para refrescar.
        """
        messagebox.showinfo("Instrucciones API", instructions)
    
    def load_currency_rates(self):
        """Cargar tasas de cambio desde archivo o API"""
        try:
            # Intentar cargar desde archivo
            if os.path.exists(self.rates_file):
                with open(self.rates_file, 'r') as f:
                    data = json.load(f)
                    last_update = datetime.strptime(data['last_update'], '%Y-%m-%d')
                    
                    # Si la última actualización fue hace menos de 7 días
                    if datetime.now() - last_update < timedelta(days=7):
                        self.rates = data['rates']
                        self.last_update = last_update
                        self.status_var.set(f"Tasas cargadas ({last_update.strftime('%d/%m/%Y')})")
                        
                        # Actualizar currency_units
                        for curr, rate in self.rates.items():
                            for key in list(self.currency_units.keys()):
                                if key.startswith(curr + " "):
                                    self.currency_units[key] = rate
                                    break
                        return
            
            # Si no hay archivo o datos viejos, pero hay API - actualizar
            if self.API_KEY:
                self.update_currency_rates()
            else:
                self.status_var.set("Usando tasas guardadas (no actualizadas)")
                
        except Exception as e:
            self.status_var.set(f"Error cargando tasas: {str(e)}")
            # Usar valores por defecto
    
    def update_currency_rates(self):
        """Actualizar tasas de cambio via API"""
        if not self.API_KEY:
            messagebox.showwarning("Error", "Ingrese clave API para actualizar")
            return
            
        try:
            self.status_var.set("Actualizando tasas...")
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
                
                # Actualizar currency_units
                for curr, rate in self.rates.items():
                    for key in list(self.currency_units.keys()):
                        if key.startswith(curr + " "):
                            self.currency_units[key] = rate
                            break
                
                # Guardar en archivo
                self.last_update = datetime.now()
                with open(self.rates_file, 'w') as f:
                    json.dump({
                        'rates': self.rates,
                        'last_update': self.last_update.strftime('%Y-%m-%d')
                    }, f)
                
                self.status_var.set(f"Tasas actualizadas ({self.last_update.strftime('%d/%m/%Y')})")
                messagebox.showinfo("Éxito", "¡Tasas actualizadas!")
            else:
                error_msg = data.get('error-type', 'Error desconocido')
                self.status_var.set(f"Error API: {error_msg}")
                messagebox.showerror("Error API", f"Error actualizando: {error_msg}")
                
        except Exception as e:
            self.status_var.set(f"Error actualizando: {str(e)}")
            messagebox.showerror("Error", f"Error actualizando: {str(e)}")
    
    def get_currency_name(self, code):
        """Obtener nombre de moneda por código"""
        names = {
            'USD': 'Dólar EE.UU.',
            'EUR': 'Euro',
            'RUB': 'Rublo ruso',
            'GBP': 'Libra esterlina',
            'JPY': 'Yen japonés',
            'CNY': 'Yuan chino',
            'AUD': 'Dólar australiano',
            'CAD': 'Dólar canadiense',
            'CHF': 'Franco suizo',
            'INR': 'Rupia india',
            'BRL': 'Real brasileño'
        }
        return names.get(code, code)
    
    def convert(self):
        """Realizar conversión"""
        try:
            input_value = self.input_value.get()
            if not input_value:
                raise ValueError("Ingrese valor a convertir")
            
            value = float(input_value)
            
            if self.currency_mode:
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Seleccione divisas")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                
                # Verificar existencia en diccionario
                if from_unit not in self.currency_units or to_unit not in self.currency_units:
                    raise ValueError("Divisas no encontradas")
                
                # Conversión usando valores guardados
                result = value * (self.currency_units[to_unit] / self.currency_units[from_unit])
                self.add_to_history(f"{value} {from_unit} → {result:.6f} {to_unit} (Divisas)")
            else:
                category = self.current_category.get()
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Seleccione unidades")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                    
                if category == "Temperatura":
                    result = self.convert_temperature(value, from_unit, to_unit)
                else:
                    # Otras categorías usan lógica estándar
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
            
            # Formatear resultado (quitar ceros)
            formatted_result = "{0:.8f}".format(result).rstrip('0').rstrip('.') if '.' in "{0:.8f}".format(result) else str(result)
            self.result_value.set(formatted_result)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error entrada: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error conversión: {str(e)}")
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Convertir temperatura"""
        if from_unit == to_unit:
            return value
            
        # A Celsius
        if "Fahrenheit" in from_unit:
            celsius = (value - 32) * 5/9
        elif "Kelvin" in from_unit:
            celsius = value - 273.15
        else:
            celsius = value
            
        # Desde Celsius
        if "Fahrenheit" in to_unit:
            return celsius * 9/5 + 32
        elif "Kelvin" in to_unit:
            return celsius + 273.15
        else:
            return celsius
    
    def swap_units(self):
        """Intercambiar unidades"""
        from_unit = self.from_unit.get()
        to_unit = self.to_unit.get()
        self.from_unit.set(to_unit)
        self.to_unit.set(from_unit)
        if self.result_value.get():
            self.convert()
    
    def add_to_history(self, entry):
        """Agregar al historial"""
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
        """Limpiar historial"""
        self.history = []
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def save_history(self):
        """Guardar historial a archivo"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos texto", "*.txt"), ("Todos", "*.*")],
                title="Guardar historial"
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Historial conversiones:\n")
                    f.write("="*50 + "\n")
                    for i, item in enumerate(self.history, 1):
                        f.write(f"{i}. {item}\n")
                messagebox.showinfo("Éxito", "Historial guardado")
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando: {str(e)}")
    
    def load_history(self):
        """Cargar historial desde archivo"""
        try:
            if os.path.exists("converter_history.json"):
                with open("converter_history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.add_to_history("Historial cargado")
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalConverter(root)
    root.mainloop()