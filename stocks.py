import customtkinter as ctk
from settings import *
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG_COLOR)
        self.geometry('900x700')
        self.title('')
        icon_path = Path(__file__).parent / 'empty.ico'
        self.iconbitmap(icon_path)
        self.title_bar_color()
        ctk.set_appearance_mode('dark')

        # data
        self.input_string = ctk.StringVar(value='AAPL')
        self.time_string = ctk.StringVar(value=TIME_OPTIONS[0])
        self.time_string.trace('w', self.create_graph)
        self.has_data = False
        
        # widgets
        self.graph_panel = None
        InputPanel(self, self.input_string, self.time_string)
    
        # events
        self.bind('<Return>', self.input_handler)        
        
        self.mainloop()
        
    def create_graph(self, *args):
        if self.graph_panel : self.graph_panel.pack_forget()
        
        if not self.has_data:
            return
        
        match self.time_string.get():
            case 'Max' : data = self.max
            case '1 Year' : data = self.year
            case '6 Months' : data = self.six_month
            case 'Month' : data = self.one_month
            case 'Week' : data = self.one_week
                
            
        self.graph_panel = GraphPanel(self, data)
        
    def input_handler(self, event=None):
        ticker = yf.Ticker(self.input_string.get())
        start = datetime(1950, 1, 1)
        end = datetime.today()

        try:
            self.max = ticker.history(start=start, end=end)

            if self.max.empty:
                print("No data found")
                return

        except Exception as e:
            print("Error fetching data:", e)
            return

        self.year = self.max.iloc[-260:]
        self.six_month = self.max.iloc[-120:]
        self.one_month = self.max.iloc[-22:]
        self.one_week = self.max.iloc[-5:]
        self.has_data = True

        self.create_graph()
    def title_bar_color(self):
        try:
            HWMD = windll.user32.GetParent(self.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(HWMD, 35, byref(c_int(TITLE_HEX_COLOR)), sizeof(c_int))
        except:
            pass 
        
class InputPanel(ctk.CTkFrame):
    def __init__(self, parent, input_string , time_string):
        super().__init__(parent, fg_color=INPUT_BG_COLOR, corner_radius=0)
        self.pack(fill='both', side='bottom')
        self.time_string = time_string
        
        # widgets
        ctk.CTkEntry(self, textvariable=input_string, fg_color=BG_COLOR, border_color=TEXT_COLOR, border_width=1).pack(side='left', padx=10, pady=10)
        self.buttons = [TextButton(self, text=text, time_string=self.time_string) for text in TIME_OPTIONS ]
        
        time_string.trace('w', self.unselect_all_buttons)
        
    def unselect_all_buttons(self, *args):
        for button in self.buttons:
            button.unselect()
    
class TextButton(ctk.CTkLabel):
    def __init__(self, parent, text, time_string):
        super().__init__(parent, text=text, text_color=TEXT_COLOR)
        self.pack(side='right', padx=10, pady=10)
        self.time_string = time_string
        self.text = text
        
        if time_string.get() == text:
           self.select_handler()
        
        self.bind('<Button>', self.select_handler)

    def select_handler(self, event=None):
        self.time_string.set(self.text)
        self.configure(text_color=HIGHLIGHT_COLOR)

    def unselect(self):
        self.configure(text_color=TEXT_COLOR)        

class GraphPanel(ctk.CTkFrame):
    def __init__(self, parent, data):
        super().__init__(parent, fg_color=BG_COLOR)
        self.pack(expand=True, fill='both')
        
        figure = plt.Figure()
        figure.subplots_adjust(left=0, right=1, bottom=0, top=0.98)
        figure.patch.set_facecolor(BG_COLOR)
        
        #graph 
        ax = figure.add_subplot(111)
        ax.set_facecolor(BG_COLOR)
        for side in ['top', 'left', 'bottom', 'right']:
            ax.spines[side].set_color(BG_COLOR)
        
        line = ax.plot(data['Close'])[0]
        line.set_color(HIGHLIGHT_COLOR)
        
        # ticks
        ax.tick_params(axis='x', direction='in', pad=-14, colors=TICK_COLOR)
        ax.yaxis.tick_right()
        ax.tick_params(axis='y', direction='in', pad=-22, colors=HIGHLIGHT_COLOR)
        
        
        # widgets
        figure_widget = FigureCanvasTkAgg(figure, self)
        figure_widget.get_tk_widget().pack(fill='both', expand=True)
        
App()
        