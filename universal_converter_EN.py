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
        self.root.title("UNIVERSAL CONVERTER V1")
        self.root.geometry("1000x750")
        
        # API settings
        self.api_file = "converter_api.json"
        self.rates_file = "currency_rates.json"
        self.API_KEY = self.load_api_key()
        self.BASE_URL = "https://v6.exchangerate-api.com/v6/"
        self.rates = {}
        self.last_update = None
        self.currency_mode = False

        # Styles
        self.setup_styles()
        
        # All possible conversions
        self.units = self.load_units()
        
        # Variables
        self.setup_variables()
        
        # Create interface
        self.create_interface()
        
        # Initialize data
        self.initialize_data()

    def setup_styles(self):
        """Set up interface styles"""
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
        """Load all measurement units"""
        units = {
            # Mass
            "Mass": {
                "Kilogram (kg)": 1.0,
                "Gram (g)": 0.001,
                "Milligram (mg)": 1e-6,
                "Tonne (t)": 1000.0,
                "Pound (lb)": 0.453592,
                "Ounce (oz)": 0.0283495,
                "Carat (ct)": 0.0002
            },
            
            # Length
            "Length": {
                "Meter (m)": 1.0,
                "Kilometer (km)": 1000.0,
                "Centimeter (cm)": 0.01,
                "Millimeter (mm)": 0.001,
                "Micrometer (µm)": 1e-6,
                "Inch (in)": 0.0254,
                "Foot (ft)": 0.3048,
                "Yard (yd)": 0.9144,
                "Mile (mi)": 1609.34,
                "Nautical mile (nmi)": 1852.0
            },
            
            # Volume
            "Volume": {
                "Liter (L)": 1.0,
                "Milliliter (mL)": 0.001,
                "Gallon (gal)": 3.78541,
                "Pint (pt)": 0.473176,
                "Cubic meter (m³)": 1000.0,
                "Cubic inch (in³)": 0.0163871,
                "Teaspoon (tsp)": 0.00492892,
                "Tablespoon (tbsp)": 0.0147868,
                "Cup (cup)": 0.236588
            },
            
            # Temperature
            "Temperature": {
                "Celsius (°C)": "celsius",
                "Fahrenheit (°F)": "fahrenheit",
                "Kelvin (K)": "kelvin"
            },
            
            # Area
            "Area": {
                "Square meter (m²)": 1.0,
                "Square kilometer (km²)": 1e6,
                "Square centimeter (cm²)": 0.0001,
                "Hectare (ha)": 10000.0,
                "Acre (ac)": 4046.86,
                "Square mile (mi²)": 2.59e6,
                "Square foot (ft²)": 0.092903
            },
            
            # Speed
            "Speed": {
                "m/s": 1.0,
                "km/h": 0.277778,
                "mph": 0.44704,
                "knots": 0.514444,
                "Mach": 343.0
            },
            
            # Data
            "Data": {
                "Bit (bit)": 1.0,
                "Byte (B)": 8.0,
                "Kilobyte (KB)": 8192.0,
                "Megabyte (MB)": 8388608.0,
                "Gigabyte (GB)": 8589934592.0,
                "Terabyte (TB)": 8796093022208.0
            },
            
            # Energy
            "Energy": {
                "Joule (J)": 1.0,
                "Kilojoule (kJ)": 1000.0,
                "Calorie (cal)": 4.184,
                "Kilocalorie (kcal)": 4184.0,
                "kWh": 3600000.0,
                "Electronvolt (eV)": 1.60218e-19
            },
            
            # Pressure
            "Pressure": {
                "Pascal (Pa)": 1.0,
                "Bar (bar)": 100000.0,
                "Atmosphere (atm)": 101325.0,
                "mmHg": 133.322,
                "PSI": 6894.76
            },
            
            # Time
            "Time": {
                "Second (s)": 1.0,
                "Minute (min)": 60.0,
                "Hour (h)": 3600.0,
                "Day": 86400.0,
                "Week": 604800.0,
                "Year": 31536000.0
            },
            
            # Radiation
            "Radiation": {
                "Sievert (Sv)": 1.0,
                "Rem (rem)": 0.01,
                "Rad (rad)": 0.01,
                "Gray (Gy)": 1.0,
                "Roentgen (R)": 0.00933
            },
            
            # Astronomy
            "Astronomy": {
                "Light year (ly)": 1.0,
                "Astronomical unit (AU)": 63241.1,
                "Parsec (pc)": 3.26156,
                "Kilometer (km)": 9.461e12,
                "Lunar distance (LD)": 384400.0
            },
            
            # Cooking
            "Cooking": {
                "Gram (g)": 1.0,
                "Kilogram (kg)": 1000.0,
                "Ounce (oz)": 28.3495,
                "Pound (lb)": 453.592,
                "Teaspoon (tsp)": 5.0,
                "Tablespoon (tbsp)": 15.0,
                "Cup (cup)": 240.0,
                "Milliliter (mL)": 1.0,
                "Liter (L)": 1000.0
            },
            
            # Angles
            "Angles": {
                "Degree (°)": 1.0,
                "Radian (rad)": 57.2958,
                "Gradian (grad)": 0.9,
                "Revolution (rev)": 360.0
            }
        }
        
        # Currency units separately
        self.currency_units = {
            "USD (US Dollar)": 1.0,
            "EUR (Euro)": 0.85,
            "RUB (Russian Ruble)": 75.0,
            "GBP (British Pound)": 0.75,
            "JPY (Japanese Yen)": 110.0,
            "CNY (Chinese Yuan)": 6.5,
            "AUD (Australian Dollar)": 1.35,
            "CAD (Canadian Dollar)": 1.25,
            "CHF (Swiss Franc)": 0.92,
            "INR (Indian Rupee)": 75.0,
            "BRL (Brazilian Real)": 5.25
        }
        
        return units
    
    def setup_variables(self):
        """Initialize variables"""
        self.current_category = tk.StringVar(value="Mass")
        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        self.input_value = tk.StringVar(value="1.0")
        self.result_value = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")
        self.api_key_var = tk.StringVar(value=self.API_KEY or "")
        self.history = []
    
    def create_interface(self):
        """Create interface"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="UNIVERSAL CONVERTER V1",
                 style='Header.TLabel').pack(fill=tk.X, ipady=10)
        
        # Mode toggle button
        self.mode_btn = ttk.Button(
            main_frame, 
            text="Currency Converter", 
            style='Currency.TButton',
            command=self.toggle_currency_mode
        )
        self.mode_btn.pack(fill=tk.X, pady=5)
        
        # API frame (only for currency)
        self.api_frame = ttk.Frame(main_frame, style='Api.TFrame')
        
        ttk.Label(self.api_frame, text="API Key:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        api_entry = ttk.Entry(self.api_frame, textvariable=self.api_key_var, width=40)
        api_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Save API", 
                  command=self.save_api_key).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Update Rates", 
                  command=self.update_currency_rates).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="Instructions", 
                  command=self.show_api_instructions).grid(row=0, column=4, padx=5, pady=5)
        
        # Conversion frame
        self.conv_frame = ttk.LabelFrame(main_frame, text="Conversion")
        self.conv_frame.pack(fill=tk.X, pady=5)
        
        # Category (hidden in currency mode)
        self.category_label = ttk.Label(self.conv_frame, text="Category:")
        self.category_combo = ttk.Combobox(
            self.conv_frame, 
            textvariable=self.current_category, 
            values=list(self.units.keys()), 
            state="readonly", 
            width=25
        )
        self.category_combo.bind("<<ComboboxSelected>>", self.update_units)
        
        # Units
        self.units_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.units_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_combo = ttk.Combobox(self.units_frame, textvariable=self.from_unit, width=30)
        self.from_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.units_frame, text="↔", style='Symbol.TButton',
                  command=self.swap_units, width=3).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.units_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_combo = ttk.Combobox(self.units_frame, textvariable=self.to_unit, width=30)
        self.to_combo.pack(side=tk.LEFT, padx=5)
        
        # Value input
        self.value_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.value_frame, text="Value:").pack(side=tk.LEFT, padx=5)
        self.input_entry = ttk.Entry(self.value_frame, textvariable=self.input_value, width=20)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.value_frame, text="Convert", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        
        # Result
        result_frame = ttk.LabelFrame(main_frame, text="Result")
        result_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(result_frame, textvariable=self.result_value, 
                 font=('Segoe UI', 12, 'bold'), state='readonly').pack(fill=tk.X, padx=5, pady=5, ipady=5)
        
        # Status
        ttk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # History
        history_frame = ttk.LabelFrame(main_frame, text="Conversion History (last 20)")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                                    font=('Consolas', 9))
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # History buttons
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(history_btn_frame, text="Clear History", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_btn_frame, text="Save History", 
                  command=self.save_history).pack(side=tk.LEFT, padx=5)
        
        # Exit button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def toggle_currency_mode(self):
        """Toggle between regular and currency converter"""
        self.currency_mode = not self.currency_mode
        
        if self.currency_mode:
            self.mode_btn.config(text="Regular Converter", style='Normal.TButton')
            self.api_frame.pack(fill=tk.X, pady=5, before=self.conv_frame)
            
            # Hide categories and show only currencies
            self.category_label.grid_forget()
            self.category_combo.grid_forget()
            
            # Update units for currencies
            self.from_combo['values'] = list(self.currency_units.keys())
            self.to_combo['values'] = list(self.currency_units.keys())
            
            if not self.from_unit.get() or self.from_unit.get() not in self.currency_units:
                self.from_unit.set("USD (US Dollar)")
            if not self.to_unit.get() or self.to_unit.get() not in self.currency_units:
                self.to_unit.set("EUR (Euro)")
        else:
            self.mode_btn.config(text="Currency Converter", style='Currency.TButton')
            self.api_frame.pack_forget()
            
            # Show categories
            self.category_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            self.category_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Return to regular units
            self.update_units()
        
        # Update layout
        self.units_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)
        self.value_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        # Clear input field when switching modes
        self.input_value.set("1.0")
        self.result_value.set("")
    
    def initialize_data(self):
        """Initialize data on startup"""
        self.load_currency_rates()
        self.update_units()
        self.load_history()
        self.toggle_currency_mode()  # Start with regular mode
        self.toggle_currency_mode()  # Toggle back for proper initialization
    
    def update_units(self, event=None):
        """Update list of units"""
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
        """Load API key from file"""
        try:
            if os.path.exists(self.api_file):
                with open(self.api_file, 'r') as f:
                    data = json.load(f)
                    return data.get('api_key', "")
        except Exception as e:
            print(f"Error loading API key: {e}")
        return ""
    
    def save_api_key(self):
        """Save API key to file"""
        self.API_KEY = self.api_key_var.get().strip()
        try:
            with open(self.api_file, 'w') as f:
                json.dump({'api_key': self.API_KEY}, f)
            messagebox.showinfo("Success", "API key saved!")
            self.load_currency_rates()  # Try to load rates with new key
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save key: {str(e)}")
    
    def show_api_instructions(self):
        """Show API key instructions"""
        instructions = """
        To work with currencies, you need an API key:
        
        1. Go to: https://www.exchangerate-api.com/
        2. Click "Get Free Key"
        3. Register with your email
        4. You'll receive an API key via email
        5. Copy the key and paste it in the field above
        6. Click "Save API"
        
        The free tier allows 1500 requests per month.
        Click "Update Rates" to refresh currency rates.
        """
        messagebox.showinfo("API Key Instructions", instructions)
    
    def load_currency_rates(self):
        """Load currency rates from file or API"""
        try:
            # Try to load from file
            if os.path.exists(self.rates_file):
                with open(self.rates_file, 'r') as f:
                    data = json.load(f)
                    last_update = datetime.strptime(data['last_update'], '%Y-%m-%d')
                    
                    # If last update was less than 7 days ago
                    if datetime.now() - last_update < timedelta(days=7):
                        self.rates = data['rates']
                        self.last_update = last_update
                        self.status_var.set(f"Rates loaded from file ({last_update.strftime('%m/%d/%Y')})")
                        
                        # Update coefficients in currency_units
                        for curr, rate in self.rates.items():
                            # Find currency in currency_units by code (start of string)
                            for key in list(self.currency_units.keys()):
                                if key.startswith(curr + " "):
                                    self.currency_units[key] = rate
                                    break
                        return
            
            # If no file or data is stale, but we have API key - update
            if self.API_KEY:
                self.update_currency_rates()
            else:
                self.status_var.set("Using saved rates (not updated)")
                
        except Exception as e:
            self.status_var.set(f"Error loading rates: {str(e)}")
            # Use default saved values
    
    def update_currency_rates(self):
        """Update currency rates via API"""
        if not self.API_KEY:
            messagebox.showwarning("Error", "Enter API key to update rates")
            return
            
        try:
            self.status_var.set("Updating rates...")
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
                
                # Update coefficients in currency_units
                for curr, rate in self.rates.items():
                    for key in list(self.currency_units.keys()):
                        if key.startswith(curr + " "):
                            self.currency_units[key] = rate
                            break
                
                # Save to file
                self.last_update = datetime.now()
                with open(self.rates_file, 'w') as f:
                    json.dump({
                        'rates': self.rates,
                        'last_update': self.last_update.strftime('%Y-%m-%d')
                    }, f)
                
                self.status_var.set(f"Rates updated ({self.last_update.strftime('%m/%d/%Y')})")
                messagebox.showinfo("Success", "Currency rates updated successfully!")
            else:
                error_msg = data.get('error-type', 'Unknown error')
                self.status_var.set(f"API Error: {error_msg}")
                messagebox.showerror("API Error", f"Failed to update rates: {error_msg}")
                
        except Exception as e:
            self.status_var.set(f"Update error: {str(e)}")
            messagebox.showerror("Error", f"Failed to update rates: {str(e)}")
    
    def get_currency_name(self, code):
        """Get currency name by code"""
        names = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'RUB': 'Russian Ruble',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'CNY': 'Chinese Yuan',
            'AUD': 'Australian Dollar',
            'CAD': 'Canadian Dollar',
            'CHF': 'Swiss Franc',
            'INR': 'Indian Rupee',
            'BRL': 'Brazilian Real'
        }
        return names.get(code, code)
    
    def convert(self):
        """Perform conversion"""
        try:
            input_value = self.input_value.get()
            if not input_value:
                raise ValueError("Enter a value to convert")
            
            value = float(input_value)
            
            if self.currency_mode:
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Select currencies to convert")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                
                # Check if currencies exist in dictionary
                if from_unit not in self.currency_units or to_unit not in self.currency_units:
                    raise ValueError("Selected currencies not found")
                
                # Conversion using saved values
                result = value * (self.currency_units[to_unit] / self.currency_units[from_unit])
                self.add_to_history(f"{value} {from_unit} → {result:.6f} {to_unit} (Currency)")
            else:
                category = self.current_category.get()
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("Select units to convert")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                    
                if category == "Temperature":
                    result = self.convert_temperature(value, from_unit, to_unit)
                else:
                    # For other categories use standard logic
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
            
            # Format result (remove trailing zeros)
            formatted_result = "{0:.8f}".format(result).rstrip('0').rstrip('.') if '.' in "{0:.8f}".format(result) else str(result)
            self.result_value.set(formatted_result)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Input error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion error: {str(e)}")
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Convert temperature"""
        if from_unit == to_unit:
            return value
            
        # Convert to Celsius
        if "Fahrenheit" in from_unit:
            celsius = (value - 32) * 5/9
        elif "Kelvin" in from_unit:
            celsius = value - 273.15
        else:
            celsius = value
            
        # Convert from Celsius
        if "Fahrenheit" in to_unit:
            return celsius * 9/5 + 32
        elif "Kelvin" in to_unit:
            return celsius + 273.15
        else:
            return celsius
    
    def swap_units(self):
        """Swap units"""
        from_unit = self.from_unit.get()
        to_unit = self.to_unit.get()
        self.from_unit.set(to_unit)
        self.to_unit.set(from_unit)
        if self.result_value.get():
            self.convert()
    
    def add_to_history(self, entry):
        """Add entry to history"""
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
        """Clear history"""
        self.history = []
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def save_history(self):
        """Save history to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Conversion History"
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Conversion History:\n")
                    f.write("="*50 + "\n")
                    for i, item in enumerate(self.history, 1):
                        f.write(f"{i}. {item}\n")
                messagebox.showinfo("Success", "History saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_history(self):
        """Load history from file"""
        try:
            if os.path.exists("converter_history.json"):
                with open("converter_history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.add_to_history("History loaded")
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalConverter(root)
    root.mainloop()