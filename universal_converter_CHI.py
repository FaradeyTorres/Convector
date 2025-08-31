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
        self.root.title("万能转换器 V1")  # 改为V1
        self.root.geometry("1000x750")
        
        # API设置
        self.api_file = "converter_api.json"
        self.rates_file = "currency_rates.json"
        self.API_KEY = self.load_api_key()
        self.BASE_URL = "https://v6.exchangerate-api.com/v6/"
        self.rates = {}
        self.last_update = None
        self.currency_mode = False

        # 样式设置
        self.setup_styles()
        
        # 所有可转换单位
        self.units = self.load_units()
        
        # 变量初始化
        self.setup_variables()
        
        # 创建界面
        self.create_interface()
        
        # 初始化数据
        self.initialize_data()

    def setup_styles(self):
        """设置界面样式"""
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f8ff')
        self.style.configure('TLabel', background='#f0f8ff', font=('Microsoft YaHei', 10))
        self.style.configure('Header.TLabel', background='#4682b4', foreground='white', 
                           font=('Microsoft YaHei', 14, 'bold'))
        self.style.configure('TButton', font=('Microsoft YaHei', 10), foreground='black')
        self.style.configure('Symbol.TButton', font=('Arial', 12, 'bold'))
        self.style.configure('Api.TFrame', background='#e6f7ff', relief='groove', borderwidth=2)
        self.style.configure('Currency.TButton', background='#90EE90', font=('Microsoft YaHei', 10, 'bold'))
        self.style.configure('Normal.TButton', background='#ADD8E6', font=('Microsoft YaHei', 10, 'bold'))
    
    def load_units(self):
        """加载所有单位"""
        units = {
            # 质量
            "质量": {
                "千克 (kg)": 1.0,
                "克 (g)": 0.001,
                "毫克 (mg)": 1e-6,
                "吨 (t)": 1000.0,
                "磅 (lb)": 0.453592,
                "盎司 (oz)": 0.0283495,
                "克拉 (ct)": 0.0002
            },
            
            # 长度
            "长度": {
                "米 (m)": 1.0,
                "千米 (km)": 1000.0,
                "厘米 (cm)": 0.01,
                "毫米 (mm)": 0.001,
                "微米 (µm)": 1e-6,
                "英寸 (in)": 0.0254,
                "英尺 (ft)": 0.3048,
                "码 (yd)": 0.9144,
                "英里 (mi)": 1609.34,
                "海里 (nmi)": 1852.0
            },
            
            # 体积
            "体积": {
                "升 (L)": 1.0,
                "毫升 (mL)": 0.001,
                "加仑 (gal)": 3.78541,
                "品脱 (pt)": 0.473176,
                "立方米 (m³)": 1000.0,
                "立方英寸 (in³)": 0.0163871,
                "茶匙 (tsp)": 0.00492892,
                "汤匙 (tbsp)": 0.0147868,
                "杯 (cup)": 0.236588
            },
            
            # 温度
            "温度": {
                "摄氏度 (°C)": "celsius",
                "华氏度 (°F)": "fahrenheit",
                "开尔文 (K)": "kelvin"
            },
            
            # 面积
            "面积": {
                "平方米 (m²)": 1.0,
                "平方千米 (km²)": 1e6,
                "平方厘米 (cm²)": 0.0001,
                "公顷 (ha)": 10000.0,
                "英亩 (ac)": 4046.86,
                "平方英里 (mi²)": 2.59e6,
                "平方英尺 (ft²)": 0.092903
            },
            
            # 速度
            "速度": {
                "米/秒 (m/s)": 1.0,
                "千米/小时 (km/h)": 0.277778,
                "英里/小时 (mph)": 0.44704,
                "节 (knots)": 0.514444,
                "马赫 (Mach)": 343.0
            },
            
            # 数据存储
            "数据存储": {
                "比特 (bit)": 1.0,
                "字节 (B)": 8.0,
                "千字节 (KB)": 8192.0,
                "兆字节 (MB)": 8388608.0,
                "千兆字节 (GB)": 8589934592.0,
                "太字节 (TB)": 8796093022208.0
            },
            
            # 能量
            "能量": {
                "焦耳 (J)": 1.0,
                "千焦 (kJ)": 1000.0,
                "卡路里 (cal)": 4.184,
                "千卡 (kcal)": 4184.0,
                "千瓦时 (kWh)": 3600000.0,
                "电子伏特 (eV)": 1.60218e-19
            },
            
            # 压力
            "压力": {
                "帕斯卡 (Pa)": 1.0,
                "巴 (bar)": 100000.0,
                "标准大气压 (atm)": 101325.0,
                "毫米汞柱 (mmHg)": 133.322,
                "磅力/平方英寸 (PSI)": 6894.76
            },
            
            # 时间
            "时间": {
                "秒 (s)": 1.0,
                "分钟 (min)": 60.0,
                "小时 (h)": 3600.0,
                "天": 86400.0,
                "周": 604800.0,
                "年": 31536000.0
            },
            
            # 辐射
            "辐射": {
                "西弗 (Sv)": 1.0,
                "雷姆 (rem)": 0.01,
                "拉德 (rad)": 0.01,
                "戈瑞 (Gy)": 1.0,
                "伦琴 (R)": 0.00933
            },
            
            # 天文
            "天文": {
                "光年 (ly)": 1.0,
                "天文单位 (AU)": 63241.1,
                "秒差距 (pc)": 3.26156,
                "千米 (km)": 9.461e12,
                "月球距离 (LD)": 384400.0
            },
            
            # 烹饪
            "烹饪": {
                "克 (g)": 1.0,
                "千克 (kg)": 1000.0,
                "盎司 (oz)": 28.3495,
                "磅 (lb)": 453.592,
                "茶匙 (tsp)": 5.0,
                "汤匙 (tbsp)": 15.0,
                "杯 (cup)": 240.0,
                "毫升 (mL)": 1.0,
                "升 (L)": 1000.0
            },
            
            # 角度
            "角度": {
                "度 (°)": 1.0,
                "弧度 (rad)": 57.2958,
                "百分度 (grad)": 0.9,
                "转 (rev)": 360.0
            }
        }
        
        # 货币单位单独处理
        self.currency_units = {
            "USD (美元)": 1.0,
            "EUR (欧元)": 0.85,
            "RUB (俄罗斯卢布)": 75.0,
            "GBP (英镑)": 0.75,
            "JPY (日元)": 110.0,
            "CNY (人民币)": 6.5,
            "AUD (澳元)": 1.35,
            "CAD (加元)": 1.25,
            "CHF (瑞士法郎)": 0.92,
            "INR (印度卢比)": 75.0,
            "BRL (巴西雷亚尔)": 5.25
        }
        
        return units
    
    def setup_variables(self):
        """初始化变量"""
        self.current_category = tk.StringVar(value="质量")
        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        self.input_value = tk.StringVar(value="1.0")
        self.result_value = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="准备就绪")
        self.api_key_var = tk.StringVar(value=self.API_KEY or "")
        self.history = []
    
    def create_interface(self):
        """创建界面"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题栏
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="万能转换器 V1",
                 style='Header.TLabel').pack(fill=tk.X, ipady=10)
        
        # 模式切换按钮
        self.mode_btn = ttk.Button(
            main_frame, 
            text="货币转换器", 
            style='Currency.TButton',
            command=self.toggle_currency_mode
        )
        self.mode_btn.pack(fill=tk.X, pady=5)
        
        # API框架(仅货币模式显示)
        self.api_frame = ttk.Frame(main_frame, style='Api.TFrame')
        
        ttk.Label(self.api_frame, text="API密钥:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        api_entry = ttk.Entry(self.api_frame, textvariable=self.api_key_var, width=40)
        api_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="保存API", 
                  command=self.save_api_key).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="更新汇率", 
                  command=self.update_currency_rates).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(self.api_frame, text="使用说明", 
                  command=self.show_api_instructions).grid(row=0, column=4, padx=5, pady=5)
        
        # 转换框架
        self.conv_frame = ttk.LabelFrame(main_frame, text="单位转换")
        self.conv_frame.pack(fill=tk.X, pady=5)
        
        # 类别(货币模式下隐藏)
        self.category_label = ttk.Label(self.conv_frame, text="类别:")
        self.category_combo = ttk.Combobox(
            self.conv_frame, 
            textvariable=self.current_category, 
            values=list(self.units.keys()), 
            state="readonly", 
            width=25
        )
        self.category_combo.bind("<<ComboboxSelected>>", self.update_units)
        
        # 单位选择
        self.units_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.units_frame, text="从:").pack(side=tk.LEFT, padx=5)
        self.from_combo = ttk.Combobox(self.units_frame, textvariable=self.from_unit, width=30)
        self.from_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.units_frame, text="↔", style='Symbol.TButton',
                  command=self.swap_units, width=3).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.units_frame, text="到:").pack(side=tk.LEFT, padx=5)
        self.to_combo = ttk.Combobox(self.units_frame, textvariable=self.to_unit, width=30)
        self.to_combo.pack(side=tk.LEFT, padx=5)
        
        # 数值输入
        self.value_frame = ttk.Frame(self.conv_frame)
        
        ttk.Label(self.value_frame, text="数值:").pack(side=tk.LEFT, padx=5)
        self.input_entry = ttk.Entry(self.value_frame, textvariable=self.input_value, width=20)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.value_frame, text="执行转换", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        
        # 结果
        result_frame = ttk.LabelFrame(main_frame, text="转换结果")
        result_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(result_frame, textvariable=self.result_value, 
                 font=('Microsoft YaHei', 12, 'bold'), state='readonly').pack(fill=tk.X, padx=5, pady=5, ipady=5)
        
        # 状态栏
        ttk.Label(main_frame, textvariable=self.status_var, font=('Microsoft YaHei', 9)).pack(anchor=tk.W)
        
        # 历史记录
        history_frame = ttk.LabelFrame(main_frame, text="转换历史(最近20条)")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                                    font=('Consolas', 9))
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # 历史记录按钮
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(history_btn_frame, text="清除历史", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_btn_frame, text="保存历史", 
                  command=self.save_history).pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="退出", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def toggle_currency_mode(self):
        """切换普通/货币转换模式"""
        self.currency_mode = not self.currency_mode
        
        if self.currency_mode:
            self.mode_btn.config(text="普通转换器", style='Normal.TButton')
            self.api_frame.pack(fill=tk.X, pady=5, before=self.conv_frame)
            
            # 隐藏类别选择
            self.category_label.grid_forget()
            self.category_combo.grid_forget()
            
            # 更新货币单位
            self.from_combo['values'] = list(self.currency_units.keys())
            self.to_combo['values'] = list(self.currency_units.keys())
            
            if not self.from_unit.get() or self.from_unit.get() not in self.currency_units:
                self.from_unit.set("USD (美元)")
            if not self.to_unit.get() or self.to_unit.get() not in self.currency_units:
                self.to_unit.set("EUR (欧元)")
        else:
            self.mode_btn.config(text="货币转换器", style='Currency.TButton')
            self.api_frame.pack_forget()
            
            # 显示类别选择
            self.category_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            self.category_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            
            # 恢复普通单位
            self.update_units()
        
        # 更新布局
        self.units_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)
        self.value_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        # 切换模式时清空输入
        self.input_value.set("1.0")
        self.result_value.set("")
    
    def initialize_data(self):
        """初始化数据"""
        self.load_currency_rates()
        self.update_units()
        self.load_history()
        self.toggle_currency_mode()  # 从普通模式开始
        self.toggle_currency_mode()  # 切换回货币模式完成初始化
    
    def update_units(self, event=None):
        """更新单位列表"""
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
        """从文件加载API密钥"""
        try:
            if os.path.exists(self.api_file):
                with open(self.api_file, 'r') as f:
                    data = json.load(f)
                    return data.get('api_key', "")
        except Exception as e:
            print(f"加载API密钥错误: {e}")
        return ""
    
    def save_api_key(self):
        """保存API密钥到文件"""
        self.API_KEY = self.api_key_var.get().strip()
        try:
            with open(self.api_file, 'w') as f:
                json.dump({'api_key': self.API_KEY}, f)
            messagebox.showinfo("成功", "API密钥已保存!")
            self.load_currency_rates()  # 尝试用新密钥加载汇率
        except Exception as e:
            messagebox.showerror("错误", f"保存密钥失败: {str(e)}")
    
    def show_api_instructions(self):
        """显示API密钥获取说明"""
        instructions = """
        货币转换功能需要API密钥:
        
        1. 访问: https://www.exchangerate-api.com/
        2. 点击"Get Free Key"
        3. 使用邮箱注册
        4. 您将收到包含API密钥的邮件
        5. 复制密钥并粘贴到上方输入框
        6. 点击"保存API"
        
        免费版本每月提供1500次请求。
        点击"更新汇率"可手动刷新汇率数据。
        """
        messagebox.showinfo("API密钥获取说明", instructions)
    
    def load_currency_rates(self):
        """从文件或API加载汇率"""
        try:
            # 尝试从文件加载
            if os.path.exists(self.rates_file):
                with open(self.rates_file, 'r') as f:
                    data = json.load(f)
                    last_update = datetime.strptime(data['last_update'], '%Y-%m-%d')
                    
                    # 如果上次更新在7天内
                    if datetime.now() - last_update < timedelta(days=7):
                        self.rates = data['rates']
                        self.last_update = last_update
                        self.status_var.set(f"汇率已从文件加载({last_update.strftime('%Y年%m月%d日')})")
                        
                        # 更新currency_units中的系数
                        for curr, rate in self.rates.items():
                            # 通过货币代码(字符串开头)在currency_units中查找
                            for key in list(self.currency_units.keys()):
                                if key.startswith(curr + " "):
                                    self.currency_units[key] = rate
                                    break
                        return
            
            # 如果没有文件或数据过期，但有API密钥 - 更新
            if self.API_KEY:
                self.update_currency_rates()
            else:
                self.status_var.set("使用保存的汇率(未更新)")
                
        except Exception as e:
            self.status_var.set(f"加载汇率错误: {str(e)}")
            # 使用默认保存值
    
    def update_currency_rates(self):
        """通过API更新汇率"""
        if not self.API_KEY:
            messagebox.showwarning("错误", "请输入API密钥以更新汇率")
            return
            
        try:
            self.status_var.set("正在更新汇率...")
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
                
                # 更新currency_units中的系数
                for curr, rate in self.rates.items():
                    for key in list(self.currency_units.keys()):
                        if key.startswith(curr + " "):
                            self.currency_units[key] = rate
                            break
                
                # 保存到文件
                self.last_update = datetime.now()
                with open(self.rates_file, 'w') as f:
                    json.dump({
                        'rates': self.rates,
                        'last_update': self.last_update.strftime('%Y-%m-%d')
                    }, f)
                
                self.status_var.set(f"汇率已更新({self.last_update.strftime('%Y年%m月%d日')})")
                messagebox.showinfo("成功", "汇率更新成功!")
            else:
                error_msg = data.get('error-type', '未知错误')
                self.status_var.set(f"API错误: {error_msg}")
                messagebox.showerror("API错误", f"更新汇率失败: {error_msg}")
                
        except Exception as e:
            self.status_var.set(f"更新错误: {str(e)}")
            messagebox.showerror("错误", f"更新汇率失败: {str(e)}")
    
    def get_currency_name(self, code):
        """根据代码获取货币名称"""
        names = {
            'USD': '美元',
            'EUR': '欧元',
            'RUB': '俄罗斯卢布',
            'GBP': '英镑',
            'JPY': '日元',
            'CNY': '人民币',
            'AUD': '澳元',
            'CAD': '加元',
            'CHF': '瑞士法郎',
            'INR': '印度卢比',
            'BRL': '巴西雷亚尔'
        }
        return names.get(code, code)
    
    def convert(self):
        """执行转换"""
        try:
            input_value = self.input_value.get()
            if not input_value:
                raise ValueError("请输入要转换的值")
            
            value = float(input_value)
            
            if self.currency_mode:
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("请选择要转换的货币")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                
                # 检查货币是否在字典中
                if from_unit not in self.currency_units or to_unit not in self.currency_units:
                    raise ValueError("选择的货币不存在")
                
                # 使用保存的值进行转换
                result = value * (self.currency_units[to_unit] / self.currency_units[from_unit])
                self.add_to_history(f"{value} {from_unit} → {result:.6f} {to_unit} (货币)")
            else:
                category = self.current_category.get()
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                
                if not from_unit or not to_unit:
                    raise ValueError("请选择要转换的单位")
                
                if from_unit == to_unit:
                    self.result_value.set(value)
                    return
                    
                if category == "温度":
                    result = self.convert_temperature(value, from_unit, to_unit)
                else:
                    # 其他类别使用标准逻辑
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
            
            # 格式化结果(去除多余的零)
            formatted_result = "{0:.8f}".format(result).rstrip('0').rstrip('.') if '.' in "{0:.8f}".format(result) else str(result)
            self.result_value.set(formatted_result)
            
        except ValueError as e:
            messagebox.showerror("错误", f"输入错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"转换错误: {str(e)}")
    
    def convert_temperature(self, value, from_unit, to_unit):
        """温度转换"""
        if from_unit == to_unit:
            return value
            
        # 转换为摄氏度
        if "华氏度" in from_unit:
            celsius = (value - 32) * 5/9
        elif "开尔文" in from_unit:
            celsius = value - 273.15
        else:
            celsius = value
            
        # 从摄氏度转换
        if "华氏度" in to_unit:
            return celsius * 9/5 + 32
        elif "开尔文" in to_unit:
            return celsius + 273.15
        else:
            return celsius
    
    def swap_units(self):
        """交换单位"""
        from_unit = self.from_unit.get()
        to_unit = self.to_unit.get()
        self.from_unit.set(to_unit)
        self.to_unit.set(from_unit)
        if self.result_value.get():
            self.convert()
    
    def add_to_history(self, entry):
        """添加到历史记录"""
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
        """清除历史记录"""
        self.history = []
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def save_history(self):
        """保存历史记录到文件"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                title="保存转换历史"
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("转换历史记录:\n")
                    f.write("="*50 + "\n")
                    for i, item in enumerate(self.history, 1):
                        f.write(f"{i}. {item}\n")
                messagebox.showinfo("成功", "历史记录保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def load_history(self):
        """从文件加载历史记录"""
        try:
            if os.path.exists("converter_history.json"):
                with open("converter_history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.add_to_history("历史记录已加载")
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalConverter(root)
    root.mainloop()