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
        self.root.title("UNIVERSALUMRECHNER V1")  
        self.root.geometry("1000x750")
        
        # API-Einstellungen
        self.api_file = "converter_api.json"
        self.rates_file = "currency_rates.json"
        self.API_KEY = self.load_api_key()
        self.BASE_URL = "https://v6.exchangerate-api.com/v6/"
        self.rates = {}
        self.last_update = None
        self.currency_mode = False

        # Stile
        self.setup_styles()
        
        # Alle möglichen Umrechnungen
        self.units = self.load_units()
        
        # Variablen
        self.setup_variables()
        
        # Benutzeroberfläche
        self.create_interface()
        
        # Initialisierung
        self.initialize_data()

    def setup_styles(self):
        """Stile einrichten"""
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
        """Einheiten laden"""
        units = {
            # Masse
            "Masse": {
                "Kilogramm (kg)": 1.0,
                "Gramm (g)": 0.001,
                "Milligramm (mg)": 1e-6,
                "Tonne (t)": 1000.0,
                "Pfund (lb)": 0.453592,
                "Unze (oz)": 0.0283495,
                "Karat (ct)": 0.0002
            },
            
            # Länge
            "Länge": {
                "Meter (m)": 1.0,
                "Kilometer (km)": 1000.0,
                "Zentimeter (cm)": 0.01,
                "Millimeter (mm)": 0.001,
                "Mikrometer (µm)": 1e-6,
                "Zoll (in)": 0.0254,
                "Fuß (ft)": 0.3048,
                "Yard (yd)": 0.9144,
                "Meile (mi)": 1609.34,
                "Seemeile (nmi)": 1852.0
            },
            
            # Volumen
            "Volumen": {
                "Liter (L)": 1.0,
                "Milliliter (mL)": 0.001,
                "Gallone (gal)": 3.78541,
                "Pinte (pt)": 0.473176,
                "Kubikmeter (m³)": 1000.0,
                "Kubikzoll (in³)": 0.0163871,
                "Teelöffel (tsp)": 0.00492892,
                "Esslöffel (tbsp)": 0.0147868,
                "Tasse (cup)": 0.236588
            },
            
            # Temperatur
            "Temperatur": {
                "Celsius (°C)": "celsius",
                "Fahrenheit (°F)": "fahrenheit",
                "Kelvin (K)": "kelvin"
            },
            
            # Fläche
            "Fläche": {
                "Quadratmeter (m²)": 1.0,
                "Quadratkilometer (km²)": 1e6,
                "Quadratzentimeter (cm²)": 0.0001,
                "Hektar (ha)": 10000.0,
                "Acre (ac)": 4046.86,
                "Quadratmeile (mi²)": 2.59e6,
                "Quadratfuß (ft²)": 0.092903
            },
            
            # Geschwindigkeit
            "Geschwindigkeit": {
                "m/s": 1.0,
                "km/h": 0.277778,
                "mph": 0.44704,
                "Knoten": 0.514444,
                "Mach": 343.0
            },
            
            # Daten
            "Daten": {
                "Bit (bit)": 1.0,
                "Byte (B)": 8.0,
                "Kilobyte (KB)": 8192.0,
                "Megabyte (MB)": 8388608.0,
                "Gigabyte (GB)": 8589934592.0,
                "Terabyte (TB)": 8796093022208.0
            },
            
            # Energie
            "Energie": {
                "Joule (J)": 1.0,
                "Kilojoule (kJ)": 1000.0,
                "Kalorie (cal)": 4.184,
                "Kilokalorie (kcal)": 4184.0,
                "kWh": 3600000.0,
                "Elektronenvolt (eV)": 1.60218e-19
            },
            
            # Druck
            "Druck": {
                "Pascal (Pa)": 1.0,
                "Bar (bar)": 100000.0,
                "Atmosphäre (atm)": 101325.0,
                "mmHg": 133.322,
                "PSI": 6894.76
            },
            
            # Zeit
            "Zeit": {
                "Sekunde (s)": 1.0,
                "Minute (min)": 60.0,
                "Stunde (h)": 3600.0,
                "Tag": 86400.0,
                "Woche": 604800.0,
                "Jahr": 31536000.0
            },
            
            # Strahlung
            "Strahlung": {
                "Sievert (Sv)": 1.0,
                "Rem (rem)": 0.01,
                "Rad (rad)": 0.01,
                "Gray (Gy)": 1.0,
                "Röntgen (R)": 0.00933
            },
            
            # Astronomie
            "Astronomie": {
                "Lichtjahr (ly)": 1.0,
                "Astronomische Einheit (AE)": 63241.1,
                "Parsec (pc)": 3.26156,
                "Kilometer (km)": 9.461e12,
                "Monddistanz (LD)": 384400.0
            },
            
            # Küche
            "Küche": {
                "Gramm (g)": 1.0,
                "Kilogramm (kg)": 1000.0,
                "Unze (oz)": 28.3495,
                "Pfund (lb)": 453.592,
                "Teelöffel (tsp)": 5.0,
                "Esslöffel (tbsp)": 15.0,
                "Tasse (cup)": 240.0,
                "Milliliter (mL)": 1.0,
                "Liter (L)": 1000.0
            },
            
            # Winkel
            "Winkel": {
                "Grad (°)": 1.0,
                "Radiant (rad)": 57.2958,
                "Gon (grad)": 0.9,
                "Umdrehung (rev)": 360.0
            }
        }
        
        # Währungen separat
        self.currency_units = {
            "USD (US-Dollar)": 1.0,
            "EUR (Euro)": 0.85,
            "RUB (Russischer Rubel)": 75.0,
            "GBP (Britisches Pfund)": 0.75,
            "JPY (Japanischer Yen)": 110.0,
            "CNY (Chinesischer Yuan)": 6.5,
            "AUD (Australischer Dollar)": 1.35,
            "CAD (Kanadischer Dollar)": 1.25,
            "CHF (Schweizer Franken)": 0.92,
            "INR (Indische Rupie)": 75.0,
            "BRL (Brasilianischer Real)": 5.25
        }
        
        return units
    
    def setup_variables(self):
        """Variablen initialisieren"""
        self.current_category = tk.StringVar(value="Masse")
        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        self.input_value = tk.StringVar(value="1.0")
        self.result_value = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Bereit")
        self.api_key_var = tk.StringVar(value=self.API_KEY or "")
        self.history = []
    
    def create_interface(self):
        """Benutzeroberfläche erstellen"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Kopfzeile
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="UNIVERSALUMRECHNER V1",
                 style='Header.TLabel').pack(fill=tk.X, ipady=10)
        
        # Moduswechsel-Button
        self.mode_btn = ttk.Button(
            main_frame, 
            text="Währungsrechner", 
            style='Currency.TButton',
            command=self.toggle_currency_mode
        )
        self.mode_btn.pack(fill=tk.X, pady=5)
        
        # API-Rahmen (nur Währungen)
        self.api_frame = ttk.Frame(main_frame, style='Api.TFrame')
        
        ttk.Label(self.api_frame, text="API-Schlüssel:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        api_entry = ttk.Entry(self.api_frame, textvariable=self.api_key_var, width=40)
        api_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="API speichern", 
                  command=self.save_api_key).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Kurse aktualisieren", 
                  command=self.update_currency_rates).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Anleitung", 
                  command=self.show_api_instructions).grid(row=0, column=4, padx=5, pady=5)
        
        # Umrechnungsrahmen
        self.conv_frame = ttk.LabelFrame(main_frame, text="Umrechnung")
        self.conv_frame.pack(fill=tk.X, pady=5)
        
        # Kategorie (im Währungsmodus ausgeblendet)
        self.category_label = ttk.Label(self.conv_frame, text="Kategorie:")
        self.category_combo = ttk.Combobox(
            self.conv_frame, 
            textvariable=self.current_category, 
            values=list(self.units.keys()), 
            state="readonly", 
            width=25
        )
        self.category_combo.bind("<<ComboboxSelected>>", self.update_units)
        
        # Einheiten
        self.units_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.units_frame, text="Von:").pack(side=tk.LEFT, padx=5)
        self.from_combo = ttk.Combobox(self.units_frame, textvariable=self.from_unit, width=30)
        self.from_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.units_frame, text="↔", style='Symbol.TButton',
                  command=self.swap_units, width=3).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.units_frame, text="Zu:").pack(side=tk.LEFT, padx=5)
        self.to_combo = ttk.Combobox(self.units_frame, textvariable=self.to_unit, width=30)
        self.to_combo.pack(side=tk.LEFT, padx=5)
        
        # Eingabewert
        self.value_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.value_frame, text="Wert:").pack(side=tk.LEFT, padx=5)
        self.input_entry = ttk.Entry(self.value_frame, textvariable=self.input_value, width=20)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.value_frame, text="Umrechnen", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        
        # Ergebnis
        result_frame = ttk.LabelFrame(main_frame, text="Ergebnis")
        result_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(result_frame, textvariable=self.result_value, 
                 font=('Segoe UI', 12, 'bold'), state='readonly').pack(fill=tk.X, padx=5, pady=5, ipady=5)
        
        # Status
        ttk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # Verlauf
        history_frame = ttk.LabelFrame(main_frame, text="Verlauf (letzte 20)")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                                    font=('Consolas', 9))
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # Verlauf-Buttons
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(history_btn_frame, text="Verlauf löschen", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_btn_frame, text="Verlauf speichern", 
                  command=self.save_history).pack(side=tk.LEFT, padx=5)
        
        # Beenden-Button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Beenden", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def toggle_currency_mode(self):
        """Zwischen normalem und Währungsrechner wechseln"""
        self.currency_mode = not self.currency_mode
        
        if self.currency_mode:
            self.mode_btn.config(text="Normaler Rechner", style='Normal.TButton')
            self.api_frame.pack(fill=tk.X, pady=5, before=self.conv_frame)
            
            # Kategorien ausblenden
            self.category_label.grid_forget()
            self.category_combo.grid_forget()
            
            # Währungseinheiten aktualisieren
            self.from_combo['values'] = list(self.currency_units.keys())
            self.to_combo['values'] = list(self.currency_units.keys())
            
            if not self.from_unit.get() or self.from_unit.get() not in self.currency_units:
                self.from_unit.set("USD (US-Dollar)")
            if not self.to_unit.get() or self.to_unit.get() not in self.currency_units:
                self.to_unit.set("EUR (Euro)")
        else:
            self.mode_btn.config(text="Währungsrechner", style='Currency.TButton')
            self.api_frame.pack_forget()
            
            # Kategorien anzeigen
            self.category_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            self.category_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Normale Einheiten wiederherstellen
            self.update_units()
        
        # Layout aktualisieren
        self.units_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)
        self.value_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        # Bei Moduswechsel Eingabe zurücksetzen
        self.input_value.set("1.0")
        self.result_value.set("")
    
    def initialize_data(self):
        """Daten initialisieren"""
        self.load_currency_rates()
        self.update_units()
        self.load_history()
        self.toggle_currency_mode()  # Start im normalen Modus
        self.toggle_currency_mode()  # Zurückschalten für korrekte Initialisierung
    
    def update_units(self, event=None):
        """Einheitenliste aktualisieren"""
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
        """API-Schlüssel aus Datei laden"""
        try:
            if os.path.exists(self.api_file):
                with open(self.api_file, 'r') as f:
                    data = json.load(f)
                    return data.get('api_key', "")
        except Exception as e:
            print(f"Fehler beim Laden des API-Schlüssels: {e}")
        return ""
    
    def save_api_key(self):
        """API-Schlüssel in Datei speichern"""
        self.API_KEY = self.api_key_var.get().strip()
        try:
            with open(self.api_file, 'w') as f:
                json.dump({'api_key': self.API_KEY}, f)
            messagebox.showinfo("Erfolg", "API-Schlüssel gespeichert!")
            self.load_currency_rates()  # Kurse mit neuem Schlüssel laden
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def show_api_instructions(self):
        """API-Anleitung anzeigen"""
        instructions = """
        Für Währungen wird ein API-Schlüssel benötigt:
        
        1. Besuchen Sie: https://www.exchangerate-api.com/
        2. Klicken Sie auf "Get Free Key"
        3. Registrieren Sie sich mit Ihrer E-Mail
        4. Sie erhalten den API-Schlüssel per E-Mail
        5. Kopieren Sie den Schlüssel und fügen Sie ihn oben ein
        6. Klicken Sie auf "API speichern"
        
        Der kostenlose Tarif ermöglicht 1500 Anfragen/Monat.
        Klicken Sie auf "Kurse aktualisieren" zum Aktualisieren.
        """
        messagebox.showinfo("API-Anleitung", instructions)
    
    def load_currency_rates(self):
        """Wechselkurse aus Datei oder API laden"""
        try:
            # Versuch, aus Datei zu laden
            if os.path.exists(self.rates_file):
                with open(self.rates_file, 'r') as f:
                    data = json.load(f)
                    last_update = datetime.strptime(data['last_update'], '%Y-%m-%d')
                    
                    # Wenn letzte Aktualisierung weniger als 7 Tage her
                    if datetime.now() - last_update < timedelta(days=7):
                        self.rates = data['rates']
                        self.last_update = last_update
                        self.status_var.set(f"Kurse geladen ({last_update.strftime('%d.%m.%Y')})")
                        
                        # Koeffizienten in currency_units aktualisieren
                        for curr, rate in self.rates.items():
                            for key in list(self.currency_units.keys()):
                                if key.startswith(curr + " "):
                                    self.currency_units[key] = rate
                                    break
                        return
            
            # Wenn keine Datei oder veraltete Daten, aber API-Schlüssel vorhanden - aktualisieren
            if self.API_KEY:
                self.update_currency_rates()
            else:
                self.status_var.set("Verwendete gespeicherte Kurse (nicht aktualisiert)")
                
        except Exception as e:
            self.status_var.set(f"Fehler beim Laden: {str(e)}")
            # Standardwerte verwenden
    
    def update_currency_rates(self):
        """Wechselkurse via API aktualisieren"""
        if not self.API_KEY:
            messagebox.showwarning("Fehler", "API-Schlüssel eingeben zum Aktualisieren")
            return
            
        try:
            self.status_var.set("Aktualisiere Kurse...")
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
                
                # Koeffizienten in currency_units aktualisieren
                for curr, rate in self.rates.items():
                    for key in list(self.currency_units.keys()):
                        if key.startswith(curr + " "):
                            self.currency_units[key] = rate
                            break
                
                # In Datei speichern
                self.last_update = datetime.now()
                with open(self.rates_file, 'w') as f:
                    json.dump({
                        'rates': self.rates,
                        'last_update': self.last_update.strftime('%Y-%m-%d')
                    }, f)
                
                self.status_var.set(f"Kurse aktualisiert ({self.last_update.strftime('%d.%m.%Y')})")
                messagebox.showinfo("Erfolg", "Wechselkurse erfolgreich aktualisiert!")
            else:
                error_msg = data.get('error-type', 'Unbekannter Fehler')
                self.status_var.set(f"API-Fehler: {error_msg}")
                messagebox.showerror("API-Fehler", f"Aktualisierungsfehler: {error_msg}")
                
        except Exception as e:
            self.status_var.set(f"Aktualisierungsfehler: {str(e)}")
            messagebox.showerror("Fehler", f"Aktualisierungsfehler: {str(e)}")
    
    def get_currency_name(self, code):
        """Währungsname anhand Code erhalten"""
        names = {
            'USD': 'US-Dollar',
            'EUR': 'Euro',
            'RUB': 'Russischer Rubel',
            'GBP': 'Britisches Pfund',
            'JPY': 'Japanischer Yen',
            'CNY': 'Chinesischer Yuan',
            'AUD': 'Australischer Dollar',
            'CAD': 'Kanadischer Dollar',
            'CHF': 'Schweizer Franken',
            'INR': 'Indische Rupie',
            'BRL': 'Brasilianischer Real'
        }
        return names.get(code, code)
    
    def convert(self):
        """Umrechnung durchführen"""
        try:
            input_value = self.input_value.get()
            if not input_value:
                raise ValueError("Geben Sie einen Wert ein")
            
            value = float(input_value)
            
            if self.currency_mode:
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Währungen auswählen")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                
                # Überprüfen, ob Währungen im Wörterbuch existieren
                if from_unit not in self.currency_units or to_unit not in self.currency_units:
                    raise ValueError("Ausgewählte Währungen nicht gefunden")
                
                # Umrechnung mit gespeicherten Werten
                result = value * (self.currency_units[to_unit] / self.currency_units[from_unit])
                self.add_to_history(f"{value} {from_unit} → {result:.6f} {to_unit} (Währung)")
            else:
                category = self.current_category.get()
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Einheiten auswählen")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                    
                if category == "Temperatur":
                    result = self.convert_temperature(value, from_unit, to_unit)
                else:
                    # Andere Kategorien verwenden Standardlogik
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
            
            # Ergebnis formatieren (überflüssige Nullen entfernen)
            formatted_result = "{0:.8f}".format(result).rstrip('0').rstrip('.') if '.' in "{0:.8f}".format(result) else str(result)
            self.result_value.set(formatted_result)
            
        except ValueError as e:
            messagebox.showerror("Fehler", f"Eingabefehler: {str(e)}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Umrechnungsfehler: {str(e)}")
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Temperatur umrechnen"""
        if from_unit == to_unit:
            return value
            
        # Zu Celsius
        if "Fahrenheit" in from_unit:
            celsius = (value - 32) * 5/9
        elif "Kelvin" in from_unit:
            celsius = value - 273.15
        else:
            celsius = value
            
        # Von Celsius
        if "Fahrenheit" in to_unit:
            return celsius * 9/5 + 32
        elif "Kelvin" in to_unit:
            return celsius + 273.15
        else:
            return celsius
    
    def swap_units(self):
        """Einheiten tauschen"""
        from_unit = self.from_unit.get()
        to_unit = self.to_unit.get()
        self.from_unit.set(to_unit)
        self.to_unit.set(from_unit)
        if self.result_value.get():
            self.convert()
    
    def add_to_history(self, entry):
        """Zum Verlauf hinzufügen"""
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
        """Verlauf löschen"""
        self.history = []
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def save_history(self):
        """Verlauf speichern"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
                title="Verlauf speichern"
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Umrechnungsverlauf:\n")
                    f.write("="*50 + "\n")
                    for i, item in enumerate(self.history, 1):
                        f.write(f"{i}. {item}\n")
                messagebox.showinfo("Erfolg", "Verlauf gespeichert")
        except Exception as e:
            messagebox.showerror("Fehler", f"Speicherfehler: {str(e)}")
    
    def load_history(self):
        """Verlauf laden"""
        try:
            if os.path.exists("converter_history.json"):
                with open("converter_history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.add_to_history("Verlauf geladen")
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalConverter(root)
    root.mainloop()