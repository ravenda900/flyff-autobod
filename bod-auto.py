import time
import pytesseract
from PIL import ImageGrab, Image, ImageTk
import pyautogui
import sys, os
import cv2
import re
import numpy as np
import tkinter as tk
from tkinter import messagebox, scrolledtext
import customtkinter as ctk

# Version
VERSION = "v1.1.0"

# OPTIONAL: Set tesseract path if not in environment
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Helper: get correct path whether running from source or .exe
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Tesseract inside exe
pytesseract.pytesseract.tesseract_cmd = resource_path("tesseract/tesseract.exe")

# --- Load available stats from file ---
def load_stats_from_file():
    """Load available stats from stats.txt file"""
    stats_file = resource_path("stats.txt")
    try:
        with open(stats_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", f"stats.txt not found at {stats_file}")
        sys.exit()

# --- Snipping tool for region selection ---
def select_region_with_snipping_tool():
    """Allow user to select region by drawing a rectangle on screen"""
    class SnippingTool:
        def __init__(self):
            self.root = tk.Tk()
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-alpha', 0.3)
            self.root.configure(bg='grey')
            self.root.attributes('-topmost', True)
            
            self.canvas = tk.Canvas(self.root, cursor="cross", bg='grey')
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            self.start_x = None
            self.start_y = None
            self.rect = None
            self.region = None
            
            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)
            self.root.bind("<Escape>", lambda e: self.cancel())
            
            # Add instruction text
            self.canvas.create_text(
                self.root.winfo_screenwidth() // 2,
                50,
                text="Drag to select the BoD/BoG dialog region. Press ESC to cancel.",
                fill="white",
                font=('Segoe UI', 16, 'bold')
            )
            
        def on_press(self, event):
            self.start_x = event.x
            self.start_y = event.y
            if self.rect:
                self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline='red', width=3
            )
            
        def on_drag(self, event):
            if self.rect:
                self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
                
        def on_release(self, event):
            end_x, end_y = event.x, event.y
            
            # Calculate region (ensure left < right, top < bottom)
            left = min(self.start_x, end_x)
            right = max(self.start_x, end_x)
            top = min(self.start_y, end_y)
            bottom = max(self.start_y, end_y)
            
            # Only accept if region is big enough
            if (right - left) > 50 and (bottom - top) > 50:
                self.region = (left, top, right, bottom)
                self.root.quit()
                self.root.destroy()
            else:
                messagebox.showwarning("Too Small", "Please select a larger region")
                if self.rect:
                    self.canvas.delete(self.rect)
                    
        def cancel(self):
            self.region = None
            self.root.quit()
            self.root.destroy()
            
        def run(self):
            self.root.mainloop()
            return self.region
    
    tool = SnippingTool()
    return tool.run()

# --- Enhanced UI for user input ---
class ConfigUI:
    def __init__(self, initial_stat1=None, initial_value1=None, initial_stat2=None, initial_value2=None, initial_region=None):
        ctk.set_appearance_mode("dark")  # Default to dark mode
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        
        self.root.title(f"BoD/BoG Auto-Reroll Tool - Setup - {VERSION}")
        self.root.geometry("650x900")
        self.root.resizable(True, True)
        
        self.current_theme = "dark"  # Track current theme
        
        # Store initial values for reconfiguration
        self.initial_stat1 = initial_stat1
        self.initial_value1 = initial_value1
        self.initial_stat2 = initial_stat2
        self.initial_value2 = initial_value2
        self.initial_region = initial_region
        
        # Stat possible values mapping based on game data
        self.stat_values = {
            'STR': [0, 1, 2, 3, 4, 5],
            'DEX': [0, 1, 2, 3, 4, 5],
            'INT': [0, 1, 2, 3, 4, 5],
            'STA': [0, 1, 2, 3, 4, 5],
            'CriticalChance': [0, 0.5, 1.0, 1.5, 2.0, 2.5],
            'CriticalDamage': [0, 0.5, 1.0, 1.5, 2.0, 2.5],
            'Speed': [0, 1.0, 2.0, 3.0],
            'AttackSpeed': [0, 1.0, 2.0, 3.0],
            'CastingSpeed': [0, 1.0, 2.0, 3.0],
            'Attack': [0, 5, 9, 13, 17, 21],
            'Defense': [0, 2, 6, 10, 14],
            'HP': [0, 12, 20, 28, 37],
            'MP': [0, 12, 20, 28, 37],
            'FP': [0, 12, 20, 28, 37],
            'MagicDefense': [0, 2, 6, 10, 14, 18],
            'Parry': [0, 1.0, 2.0, 3.0],
            'MeleeBlock': [0, 1.0, 2.0, 3.0],
            'RangedBlock': [0, 1.0, 2.0, 3.0],
            'PvEDamage': [0, 10, 15, 20, 25, 30],
            'PvEDmgResist': [0, 10, 15, 20, 25]
        }
        
        # Modern Color Palette
        self.colors = {
            'primary': '#1f6feb',
            'success': '#238636',
            'danger': '#da3633',
            'warning': '#e3b341',
            'info': '#58a6ff',
            'secondary': '#6e7681'
        }
        
        self.available_stats = load_stats_from_file()
        self.selected_stat1 = None
        self.selected_stat2 = None
        self.target_value1 = None
        self.target_value2 = None
        self.region = None
        
        # Initialize widget variables before create_widgets
        self.stat1_var = None
        self.stat2_var = None
        self.value1_var = None
        self.value2_var = None
        self.stat1_dropdown = None
        self.stat2_dropdown = None
        self.value1_dropdown = None
        self.value2_dropdown = None
        
        self.create_widgets()
        
    def create_card_frame(self, parent, title):
        """Create a modern card frame with title"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(fill="x", pady=(0, 15))
        
        if title:
            title_label = ctk.CTkLabel(card, text=title, 
                                      font=("Segoe UI", 14, "bold"),
                                      anchor="w")
            title_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        return content
        
    def create_widgets(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # Scrollable body (adds vertical scrollbar automatically when needed)
        body_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=25, pady=(25, 15))

        # Header with theme switcher
        header_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title section
        title_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_section.pack(side="left", fill="x", expand=True)
        
        title = ctk.CTkLabel(title_section, 
                           text="⚡ BoD/BoG Auto Reroll",
                           font=("Segoe UI", 24, "bold"))
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(title_section,
                              text="Automatic stat detection and optimization",
                              font=("Segoe UI", 12),
                              text_color="gray60")
        subtitle.pack(anchor="w")
        
        # Theme switcher
        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.pack(side="right", padx=(10, 0))
        
        ctk.CTkLabel(theme_frame, text="Theme:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 5))
        
        self.theme_var = tk.StringVar(value="Dark")
        theme_menu = ctk.CTkOptionMenu(theme_frame,
                                      values=["Light", "Dark", "System"],
                                      variable=self.theme_var,
                                      command=self.change_theme,
                                      width=100)
        theme_menu.pack(side="left")
        
        # Window Detection Card
        window_card = self.create_card_frame(body_frame, "📍 Select Dialog Region")
        
        info_label = ctk.CTkLabel(window_card, 
                                 text="✂️ Select the BoD/BoG dialog region using the selection tool",
                                 font=("Segoe UI", 12, "bold"))
        info_label.pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(window_card,
                    text="1. Open the BoD/BoG dialog in your game\n2. Click the button below\n3. Draw a rectangle around the entire dialog (include title and buttons)",
                    font=("Segoe UI", 11),
                    text_color="gray60",
                    justify="left").pack(anchor="w", pady=(0, 15))
        
        # Large, prominent selection button
        self.select_btn = ctk.CTkButton(window_card, 
                                      text="✂️  SELECT DIALOG REGION", 
                                      command=self.select_region,
                                      fg_color="#1f6feb",
                                      hover_color="#388bfd",
                                      corner_radius=10,
                                      height=50,
                                      font=("Segoe UI", 14, "bold"))
        self.select_btn.pack(fill="x", pady=(0, 10))
        
        # Status label
        self.region_status = ctk.CTkLabel(window_card, 
                                        text="⚫ Region not selected",
                                        font=("Segoe UI", 11, "bold"),
                                        text_color="#da3633")
        self.region_status.pack(pady=(10, 5))
        
        # Manual region input (optional)
        ctk.CTkLabel(window_card, 
                    text="Or enter coordinates manually (left,top,right,bottom):",
                    font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 5))
        
        self.region_entry = ctk.CTkEntry(window_card, 
                                        font=('Segoe UI', 11),
                                        placeholder_text="Example: 2070,680,2560,880",
                                        height=35)
        self.region_entry.pack(pady=5, fill="x")
        self.region_entry.bind('<KeyRelease>', lambda e: self.validate_region())
        
        # Stats Selection Card
        stats_card = self.create_card_frame(body_frame, "📊 Configure Target Stats")
        
        # Stat 1 Configuration
        stat1_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
        stat1_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(stat1_frame, text="⭐ Stat 1 (optional):", font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        stat1_input = ctk.CTkFrame(stat1_frame, fg_color="transparent")
        stat1_input.pack(fill="x")
        
        self.stat1_var = tk.StringVar()
        self.stat1_dropdown = ctk.CTkComboBox(stat1_input, 
                                             variable=self.stat1_var,
                                             values=['(None)'] + self.available_stats,
                                             state="readonly",
                                             width=200,
                                             command=self.on_stat1_change)
        self.stat1_dropdown.pack(side="left", padx=(0, 10))
        self.stat1_dropdown.set('(None)')
        
        ctk.CTkLabel(stat1_input, text="Value:", font=("Segoe UI", 11)).pack(side="left", padx=(10, 5))
        
        self.value1_var = tk.StringVar()
        self.value1_dropdown = ctk.CTkComboBox(stat1_input,
                                              variable=self.value1_var,
                                              state="disabled",
                                              width=100,
                                              values=[''])
        self.value1_dropdown.pack(side="left")
        self.update_stat1_values()
        
        # Divider
        ctk.CTkFrame(stats_card, height=2, fg_color="#6e7681").pack(fill="x", pady=15)
        
        # Stat 2 Configuration
        stat2_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
        stat2_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(stat2_frame, text="⭐ Stat 2 (optional):", font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        stat2_input = ctk.CTkFrame(stat2_frame, fg_color="transparent")
        stat2_input.pack(fill="x")
        
        self.stat2_var = tk.StringVar()
        self.stat2_dropdown = ctk.CTkComboBox(stat2_input, 
                                             variable=self.stat2_var,
                                             values=['(None)'] + self.available_stats,
                                             state="readonly",
                                             width=200,
                                             command=self.on_stat2_change)
        self.stat2_dropdown.pack(side="left", padx=(0, 10))
        self.stat2_dropdown.set('(None)')
        
        ctk.CTkLabel(stat2_input, text="Value:", font=("Segoe UI", 11)).pack(side="left", padx=(10, 5))
        
        self.value2_var = tk.StringVar()
        self.value2_dropdown = ctk.CTkComboBox(stat2_input,
                                              variable=self.value2_var,
                                              state="disabled",
                                              width=100,
                                              values=[''])
        self.value2_dropdown.pack(side="left")
        self.update_stat2_values()
        
        # Apply initial values if provided (for reconfiguration)
        self.apply_initial_values()
        
        # Info label
        info_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
        info_frame.pack(fill="x", pady=(15, 0), padx=5)
        
        info_text = ctk.CTkLabel(info_frame,
                                text="💡 Configure at least one stat (Stat 1 or Stat 2 or both).\n\nIf only ONE stat is configured and it appears in both panels,\nthe values will be SUMMED. If BOTH stats are configured,\neach is checked individually.\n\nStats can appear in either panel of the BoD/BoG window.",
                                font=('Segoe UI', 10),
                                text_color="gray60",
                                justify='left',
                                anchor='w')
        info_text.pack(anchor="w", fill="x")
        
        # Sticky footer for Start Button (always visible)
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", padx=25, pady=(0, 25))

        # Start Button - Large and prominent
        self.start_btn = ctk.CTkButton(footer_frame,
                         text="🚀 START AUTOMATION",
                         command=self.start,
                         fg_color="#238636",
                         hover_color="#2ea043",
                         corner_radius=10,
                         height=50,
                         font=("Segoe UI", 14, "bold"),
                         state="disabled")
        self.start_btn.pack(fill="x")
    
    def apply_initial_values(self):
        """Apply initial values if provided (for reconfiguration)"""
        # Restore region coordinates
        if self.initial_region:
            self.region = self.initial_region
            self.region_entry.delete(0, tk.END)
            self.region_entry.insert(0, f"{self.initial_region[0]},{self.initial_region[1]},{self.initial_region[2]},{self.initial_region[3]}")
            width = self.initial_region[2] - self.initial_region[0]
            height = self.initial_region[3] - self.initial_region[1]
            self.region_status.configure(text=f"✓ Region selected: {width}x{height} pixels", text_color="#238636")
        
        # Restore Stat 1 and its value
        if self.initial_stat1:
            # Set stat dropdown
            self.stat1_var.set(self.initial_stat1)
            self.stat1_dropdown.set(self.initial_stat1)
            
            # Update value dropdown options for this stat
            self.update_stat1_values()
            
            # Now set the value if provided
            if self.initial_value1 is not None:
                # Format value consistently
                if self.initial_value1 == int(self.initial_value1):
                    value_str = str(int(self.initial_value1))
                else:
                    value_str = str(self.initial_value1)
                
                # Set the value
                self.value1_var.set(value_str)
                self.value1_dropdown.set(value_str)
        
        # Restore Stat 2 and its value
        if self.initial_stat2:
            # Set stat dropdown
            self.stat2_var.set(self.initial_stat2)
            self.stat2_dropdown.set(self.initial_stat2)
            
            # Update value dropdown options for this stat
            self.update_stat2_values()
            
            # Now set the value if provided
            if self.initial_value2 is not None:
                # Format value consistently
                if self.initial_value2 == int(self.initial_value2):
                    value_str = str(int(self.initial_value2))
                else:
                    value_str = str(self.initial_value2)
                
                # Set the value
                self.value2_var.set(value_str)
                self.value2_dropdown.set(value_str)
        
        # Update start button state
        self.update_start_button()
    
    def change_theme(self, choice):
        """Change the application theme"""
        theme_map = {
            "Light": "light",
            "Dark": "dark",
            "System": "system"
        }
        ctk.set_appearance_mode(theme_map[choice])
        self.current_theme = theme_map[choice]
        
    def select_region(self):
        """Use snipping tool to select the BoD/BoG dialog region"""
        self.root.iconify()  # Minimize the config window
        time.sleep(0.3)  # Short delay for window to minimize
        
        region = select_region_with_snipping_tool()
        
        self.root.deiconify()  # Restore the config window
        
        if region:
            self.region = region
            self.region_entry.delete(0, tk.END)
            self.region_entry.insert(0, f"{region[0]},{region[1]},{region[2]},{region[3]}")
            width = region[2] - region[0]
            height = region[3] - region[1]
            self.region_status.configure(text=f"✓ Region selected: {width}x{height} pixels", text_color="#238636")
            self.update_start_button()
        else:
            self.region_status.configure(text="✗ Selection cancelled", text_color="#e3b341")
    
    def validate_region(self):
        """Validate manually entered region coordinates"""
        try:
            coords = self.region_entry.get().strip()
            if coords:
                parts = coords.split(',')
                if len(parts) == 4:
                    left, top, right, bottom = map(int, parts)
                    if right > left and bottom > top:
                        self.region = (left, top, right, bottom)
                        width = right - left
                        height = bottom - top
                        self.region_status.configure(text=f"✓ Region set: {width}x{height} pixels", text_color="#238636")
                        self.update_start_button()
                        return
            # If we get here, coordinates are invalid or incomplete
            if coords:
                self.region_status.configure(text="⚠️ Invalid coordinates format", text_color="#e3b341")
            else:
                self.region_status.configure(text="⚫ Region not selected", text_color="#da3633")
            self.region = None
            self.update_start_button()
        except ValueError:
            self.region_status.configure(text="⚠️ Coordinates must be numbers", text_color="#e3b341")
            self.region = None
            self.update_start_button()
    
    def add_stat(self):
        pass  # No longer needed
    
    def remove_stat(self):
        pass  # No longer needed
    
    def on_stat1_change(self, choice):
        """Handle Stat 1 dropdown change - updates value dropdown immediately"""
        # Explicitly update the variable
        self.stat1_var.set(choice)
        # Force widget to update
        self.stat1_dropdown.set(choice)
        # Update value dropdown based on new stat
        self.update_stat1_values()
    
    def on_stat2_change(self, choice):
        """Handle Stat 2 dropdown change - updates value dropdown immediately"""
        # Explicitly update the variable
        self.stat2_var.set(choice)
        # Force widget to update
        self.stat2_dropdown.set(choice)
        # Update value dropdown based on new stat
        self.update_stat2_values()
    
    def update_stat1_values(self):
        """Update value dropdown for Stat 1 based on selected stat"""
        stat = self.stat1_var.get()
        current_value = self.value1_var.get()
        
        if stat == '(None)' or not stat:
            # No stat selected - disable value dropdown
            self.value1_dropdown.configure(values=[''])
            self.value1_dropdown.configure(state='disabled')
            self.value1_var.set('')
            self.value1_dropdown.set('')
        elif stat in self.stat_values:
            # Valid stat - populate value dropdown
            values = self.stat_values[stat]
            formatted_values = [str(int(v)) if v == int(v) else str(v) for v in values]
            
            # Update dropdown options
            self.value1_dropdown.configure(values=formatted_values)
            self.value1_dropdown.configure(state='readonly')
            
            # Set value: preserve if valid, otherwise use first option
            if current_value and current_value in formatted_values:
                # Preserve valid value
                self.value1_var.set(current_value)
                self.value1_dropdown.set(current_value)
            else:
                # Set to first valid value
                if formatted_values:
                    self.value1_var.set(formatted_values[0])
                    self.value1_dropdown.set(formatted_values[0])
        else:
            # Unknown stat - disable dropdown
            self.value1_dropdown.configure(values=[''])
            self.value1_dropdown.configure(state='disabled')
            self.value1_var.set('')
            self.value1_dropdown.set('')
        
        # Update start button state
        self.update_start_button()
    
    def update_stat2_values(self):
        """Update value dropdown for Stat 2 based on selected stat"""
        stat = self.stat2_var.get()
        current_value = self.value2_var.get()
        
        if stat == '(None)' or not stat:
            # No stat selected - disable value dropdown
            self.value2_dropdown.configure(values=[''])
            self.value2_dropdown.configure(state='disabled')
            self.value2_var.set('')
            self.value2_dropdown.set('')
        elif stat in self.stat_values:
            # Valid stat - populate value dropdown
            values = self.stat_values[stat]
            formatted_values = [str(int(v)) if v == int(v) else str(v) for v in values]
            
            # Update dropdown options
            self.value2_dropdown.configure(values=formatted_values)
            self.value2_dropdown.configure(state='readonly')
            
            # Set value: preserve if valid, otherwise use first option
            if current_value and current_value in formatted_values:
                # Preserve valid value
                self.value2_var.set(current_value)
                self.value2_dropdown.set(current_value)
            else:
                # Set to first valid value
                if formatted_values:
                    self.value2_var.set(formatted_values[0])
                    self.value2_dropdown.set(formatted_values[0])
        else:
            # Unknown stat - disable dropdown
            self.value2_dropdown.configure(values=[''])
            self.value2_dropdown.configure(state='disabled')
            self.value2_var.set('')
            self.value2_dropdown.set('')
        
        # Update start button state
        self.update_start_button()
    
    def update_value_dropdown(self):
        pass  # No longer needed
    
    def update_start_button(self):
        # Check if all widget variables are initialized
        if not all([self.stat1_var, self.stat2_var, self.value1_var, self.value2_var]):
            return
        
        # Check if start button exists yet
        if not hasattr(self, 'start_btn') or self.start_btn is None:
            return
        
        # At least one stat must be configured
        stat1_selected = self.stat1_var.get() != '(None)' and self.stat1_var.get() != ''
        stat2_selected = self.stat2_var.get() != '(None)' and self.stat2_var.get() != ''
        
        # Need region and at least one stat configured
        if self.region and (stat1_selected or stat2_selected):
            # If stat1 is selected, it must have a value
            if stat1_selected and not self.value1_var.get():
                self.start_btn.configure(state='disabled')
                return
            # If stat2 is selected, it must have a value
            if stat2_selected and not self.value2_var.get():
                self.start_btn.configure(state='disabled')
                return
            # All selected stats have values
            self.start_btn.configure(state='normal')
        else:
            self.start_btn.configure(state='disabled')
    
    def start(self):
        self.selected_stat1 = self.stat1_var.get() if self.stat1_var.get() != '(None)' else None
        self.selected_stat2 = self.stat2_var.get() if self.stat2_var.get() != '(None)' else None
        
        try:
            if self.selected_stat1:
                self.target_value1 = float(self.value1_var.get())
            else:
                self.target_value1 = None
                
            if self.selected_stat2:
                self.target_value2 = float(self.value2_var.get())
            else:
                self.target_value2 = None
        except ValueError:
            messagebox.showerror("Error", "Please select valid values for the configured stats")
            return
        
        if not self.selected_stat1 and not self.selected_stat2:
            messagebox.showerror("Error", "Please configure at least one stat (Stat 1 or Stat 2)")
            return
        
        if not self.region:
            messagebox.showerror("Error", "Please select the BoD/BoG dialog region")
            return
        
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()
        return (self.selected_stat1, self.target_value1, 
                self.selected_stat2, self.target_value2, 
                self.region)

# Status Window for automation
class StatusWindow:
    def __init__(self, stat1_name, target_value1, stat2_name, target_value2):
        self.root = ctk.CTk()
        self.root.title(f"BoD/BoG Auto-Reroll Tool - Active - {VERSION}")
        self.root.geometry("850x800")
        self.root.resizable(True, True)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with reconfigure button
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, 
                    text="🤖 Automation Running",
                    font=("Segoe UI", 20, "bold")).pack(side="left")
        
        ctk.CTkButton(header_frame,
                     text="⚙️  Reconfigure",
                     command=self.reconfigure,
                     width=130,
                     height=35,
                     font=("Segoe UI", 12, "bold"),
                     fg_color=("#6e7681", "#484f58"),
                     hover_color=("#8b949e", "#6e7681"),
                     corner_radius=8).pack(side="right")
        
        # Config summary
        config_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        config_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(config_frame, 
                    text="📊 Configured Targets:",
                    font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        config_lines = []
        if stat1_name:
            config_lines.append(f"⭐ {stat1_name} ≥ {target_value1}")
        if stat2_name:
            config_lines.append(f"⭐ {stat2_name} ≥ {target_value2}")
        config_text = "\n".join(config_lines)
        
        ctk.CTkLabel(config_frame,
                    text=config_text,
                    font=("Segoe UI", 12),
                    justify="left").pack(anchor="w", padx=15, pady=(0, 15))
        
        # Status label
        self.status_label = ctk.CTkLabel(main_frame,
                                        text="🔍 Searching for button...",
                                        font=("Segoe UI", 13, "bold"),
                                        text_color="#58a6ff")
        self.status_label.pack(pady=(0, 10))
        
        # Log area label
        ctk.CTkLabel(main_frame,
                    text="📋 Activity Log:",
                    font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(5, 5))
        
        # Log text area - smaller to leave room for button
        self.log_text = scrolledtext.ScrolledText(main_frame,
                                                 height=12,
                                                 font=("Consolas", 9),
                                                 bg="#1e1e1e",
                                                 fg="#d4d4d4",
                                                 wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True, pady=(0, 15))
        
        # Separator
        ctk.CTkFrame(main_frame, height=2, fg_color="#6e7681").pack(fill="x", pady=(0, 15))
        
        # START/STOP BUTTON - ALWAYS AT BOTTOM with intuitive styling
        self.control_btn = ctk.CTkButton(main_frame,
                                        text="▶️  START AUTOMATION",
                                        command=self.toggle_automation,
                                        fg_color=("#2ea043", "#238636"),
                                        hover_color=("#3fb950", "#2ea043"),
                                        text_color=("white", "white"),
                                        height=70,
                                        font=("Segoe UI", 18, "bold"),
                                        border_width=0,
                                        corner_radius=12)
        self.control_btn.pack(fill="x", pady=(0, 0))
        
        self.running = False
        self.started = False
        self.reconfigure_requested = False
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle window close event"""
        if self.running:
            self.stop()
        self.log("👋 Window closed - terminating...")
        self.root.quit()
        self.root.destroy()
        sys.exit(0)
    
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def set_status(self, message, color="#58a6ff"):
        """Update status label"""
        self.status_label.configure(text=message, text_color=color)
        self.root.update()
    
    def toggle_automation(self):
        """Toggle automation on/off"""
        if not self.started:
            # Start automation
            self.started = True
            self.running = True
            # Make window always on top when automation starts
            self.root.attributes("-topmost", True)
            self.control_btn.configure(
                text="⏹️  STOP AUTOMATION",
                fg_color=("#da3633", "#c93632"),
                hover_color=("#e5534b", "#da3633")
            )
            self.log("🚀 Automation started by user")
            self.set_status("🔍 Searching for button...", "#58a6ff")
        else:
            # Stop automation
            self.stop()
        
    def stop(self):
        """Stop automation"""
        self.running = False
        self.started = False
        # Remove always on top when stopped
        self.root.attributes("-topmost", False)
        if hasattr(self, 'control_btn'):
            self.control_btn.configure(
                text="▶️  START AUTOMATION",
                fg_color=("#2ea043", "#238636"),
                hover_color=("#3fb950", "#2ea043")
            )
        self.log("🛑 Automation stopped")
        self.set_status("⏹️ Stopped", "#da3633")
    
    def reconfigure(self):
        """Return to configuration page"""
        if self.running:
            self.stop()
        self.log("🔄 Returning to configuration...")
        self.reconfigure_requested = True
        self.root.after(500, self.root.destroy)
        
    def update(self):
        """Update the window"""
        self.root.update()

# Path to the image to look for when text is not found
fallback_image = resource_path("button_image.png")  # Replace with your image file

def capture_and_check():
    """Capture screen region and check if stat(s) meet their target values.
    Stats can appear in either Stat 1 or Stat 2 panel of the BoD/BoG window.
    """
    # Grab screenshot of the region
    screenshot = ImageGrab.grab(bbox=region)

    # Convert PIL Image to OpenCV format (numpy array)
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

    # Resize to improve OCR accuracy
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # Apply inverted binary thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Optional: clean small noise
    thresh = cv2.medianBlur(thresh, 3)

    # Optional: slight dilation to make thin characters thicker
    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.erode(thresh, kernel, iterations=1)

    # Use Tesseract with custom config
    config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+.% '

    text = pytesseract.image_to_string(thresh, config=config)

    status_window.log(f"OCR: {text.strip()[:80]}..." if len(text.strip()) > 80 else f"OCR: {text.strip()}")
    print("\nDetected text:", text.strip())

    # Build normalized target stats for exact matching by stat label
    def normalize_stat_name(name):
        return re.sub(r"[^A-Za-z]", "", name).lower()

    target_stats = {}
    if stat1_name:
        target_stats[normalize_stat_name(stat1_name)] = stat1_name
    if stat2_name:
        target_stats[normalize_stat_name(stat2_name)] = stat2_name

    if not target_stats:
        return False

    # Regex: capture full OCR label before +/#, then parse number (int/decimal), optional %
    # Example matches: "Speed+3", "Attack Speed + 2.0", "CriticalChance#0.5%"
    pattern = re.compile(r"([A-Za-z][A-Za-z ]{0,40}?)\s*[+#]\s*(\d+(?:\.\d+)?)(%?)", re.IGNORECASE)

    # Dictionary to store all occurrences of each stat
    stat_occurrences = {}
    if stat1_name:
        stat_occurrences[stat1_name] = []
    if stat2_name:
        stat_occurrences[stat2_name] = []
    
    # Find all matches
    for m in pattern.finditer(text):
        detected_label, num_str, percent = m.groups()
        normalized_detected = normalize_stat_name(detected_label)
        if normalized_detected not in target_stats:
            continue

        stat = target_stats[normalized_detected]
        value = float(num_str)
        
        # Avoid duplicates by checking if value already exists
        if stat in stat_occurrences and value not in stat_occurrences[stat]:
            stat_occurrences[stat].append(value)
            status_window.log(f"Found: {stat}+{value}")
            print(f"Matched: {stat}+{value}")
    
    # Check if required stat(s) meet their target values
    print(f"\nChecking requirements:")
    
    # Determine if we should use sum logic (only one stat configured)
    only_one_stat = (stat1_name and not stat2_name) or (stat2_name and not stat1_name)
    
    if stat1_name and stat2_name:
        print(f"Looking for: {stat1_name} ≥ {target_value1} AND {stat2_name} ≥ {target_value2}")
    elif stat1_name:
        print(f"Looking for: {stat1_name} ≥ {target_value1}")
        if only_one_stat:
            print(f"Note: If {stat1_name} appears in both panels, values will be summed")
    elif stat2_name:
        print(f"Looking for: {stat2_name} ≥ {target_value2}")
        if only_one_stat:
            print(f"Note: If {stat2_name} appears in both panels, values will be summed")
    
    stat1_found = True if not stat1_name else False
    stat2_found = True if not stat2_name else False
    
    # Check stat1 if configured
    if stat1_name and stat1_name in stat_occurrences:
        if stat_occurrences[stat1_name]:
            # If only stat1 is configured and appears in both panels, sum them
            if only_one_stat and len(stat_occurrences[stat1_name]) >= 2:
                total_value = sum(stat_occurrences[stat1_name][:2])
                status_window.log(f"Found {stat1_name} in both panels: {stat_occurrences[stat1_name][:2]}")
                status_window.log(f"Sum: {total_value}")
                print(f"Found {stat1_name} in both panels: {stat_occurrences[stat1_name][:2]}, sum = {total_value}")
                if total_value >= target_value1:
                    status_window.log(f"✓ {stat1_name} sum = {total_value} ≥ {target_value1}")
                    print(f"✓ {stat1_name} sum = {total_value} meets target {target_value1}")
                    stat1_found = True
                else:
                    status_window.log(f"✗ {stat1_name} sum {total_value} < {target_value1}")
                    print(f"✗ {stat1_name} sum {total_value} below target {target_value1}")
            else:
                # Check individual values
                for value in stat_occurrences[stat1_name]:
                    if value >= target_value1:
                        status_window.log(f"✓ {stat1_name} = {value} ≥ {target_value1}")
                        print(f"✓ {stat1_name} = {value} meets target {target_value1}")
                        stat1_found = True
                        break
                if not stat1_found:
                    status_window.log(f"✗ {stat1_name} values {stat_occurrences[stat1_name]} < {target_value1}")
                    print(f"✗ {stat1_name} values below target {target_value1}")
        else:
            status_window.log(f"✗ {stat1_name} not detected")
            print(f"✗ {stat1_name} not found in window")
    
    # Check stat2 if configured
    if stat2_name and stat2_name in stat_occurrences:
        if stat_occurrences[stat2_name]:
            # If only stat2 is configured and appears in both panels, sum them
            if only_one_stat and len(stat_occurrences[stat2_name]) >= 2:
                total_value = sum(stat_occurrences[stat2_name][:2])
                status_window.log(f"Found {stat2_name} in both panels: {stat_occurrences[stat2_name][:2]}")
                status_window.log(f"Sum: {total_value}")
                print(f"Found {stat2_name} in both panels: {stat_occurrences[stat2_name][:2]}, sum = {total_value}")
                if total_value >= target_value2:
                    status_window.log(f"✓ {stat2_name} sum = {total_value} ≥ {target_value2}")
                    print(f"✓ {stat2_name} sum = {total_value} meets target {target_value2}")
                    stat2_found = True
                else:
                    status_window.log(f"✗ {stat2_name} sum {total_value} < {target_value2}")
                    print(f"✗ {stat2_name} sum {total_value} below target {target_value2}")
            else:
                # Check individual values
                for value in stat_occurrences[stat2_name]:
                    if value >= target_value2:
                        status_window.log(f"✓ {stat2_name} = {value} ≥ {target_value2}")
                        print(f"✓ {stat2_name} = {value} meets target {target_value2}")
                        stat2_found = True
                        break
                if not stat2_found:
                    status_window.log(f"✗ {stat2_name} values {stat_occurrences[stat2_name]} < {target_value2}")
                    print(f"✗ {stat2_name} values below target {target_value2}")
        else:
            status_window.log(f"✗ {stat2_name} not detected")
            print(f"✗ {stat2_name} not found in window")
    
    # All configured stats must meet their targets
    if stat1_found and stat2_found:
        if stat1_name and stat2_name:
            status_window.log("🎉 BOTH STATS MEET TARGETS!")
            status_window.set_status("🎉 TARGET STATS FOUND!", "#238636")
            print("\n🎉 BOTH STATS MEET TARGETS!")
        else:
            status_window.log("🎉 STAT MEETS TARGET!")
            status_window.set_status("🎉 TARGET STAT FOUND!", "#238636")
            print("\n🎉 STAT MEETS TARGET!")
        return True
    else:
        print("\n❌ Requirements not met")
        return False

def click_image(image_path):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=0.9)
        if location:
            status_window.log("🎯 Button found, checking stats...")
            status_window.set_status("🔍 Analyzing stats...", "#e3b341")
            print("Checking awakes...")
            if capture_and_check():
                print("AWAKE FOUND!!!")
                status_window.set_status("🎉 Target found! Awaiting decision...", "#238636")
                
                # Show dialog in the app instead of terminal
                status_window.root.attributes("-topmost", True)  # Bring window to front
                result = messagebox.askyesno(
                    "🎉 Target Stats Found!",
                    "Your target stats have been achieved!\n\nDo you want to continue re-awakening?",
                    parent=status_window.root
                )
                
                if not result:  # User clicked "No"
                    status_window.log("🛑 User chose to stop automation")
                    status_window.stop()
                    print("User stopped automation")
                    return False  # Signal to stop checking
                else:  # User clicked "Yes"
                    status_window.log("🔄 Continuing re-awakening...")
                    status_window.set_status("🔄 Re-awakening...", "#58a6ff")
                    pyautogui.click(location)
                    return True
            else:
                status_window.log("📋 Stats below target, clicking button...")
                status_window.set_status("🔄 Rerolling...", "#58a6ff")
                pyautogui.click(location)
                return True
        else:
            status_window.set_status("🔍 Searching for button...", "#58a6ff")
    except Exception as e:
        pass

def save_with_incremental_name(base_name, image):
    # Split extension
    name, ext = os.path.splitext(base_name)
    counter = 1
    filename = base_name

    # Keep incrementing until a free filename is found
    while os.path.exists(filename):
        filename = f"{name}_{counter}{ext}"
        counter += 1

    cv2.imwrite(filename, image)
    print(f"Saved: {filename}")

def main():
    print("Status window ready...")
    while True:
        try:
            status_window.update()
            
            # Check if reconfiguration was requested
            if status_window.reconfigure_requested:
                break
            
            # Only run automation if started
            if status_window.started and status_window.running:
                clicked = click_image(fallback_image)
                if clicked:
                    status_window.log("✓ Button clicked")
                    print("Start button clicked.")
                time.sleep(1)  # Wait before checking again
            else:
                time.sleep(0.1)  # Small delay when not running
                
        except tk.TclError:
            # Window was closed
            print("Window closed - terminating process")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            status_window.log(f"❌ Error: {e}")
            break

# Main loop to allow reconfiguration
# Initialize with no previous config
prev_stat1, prev_value1, prev_stat2, prev_value2, prev_region = None, None, None, None, None

while True:
    # Create and run UI with previous configuration (if reconfiguring)
    ui = ConfigUI(prev_stat1, prev_value1, prev_stat2, prev_value2, prev_region)
    stat1_name, target_value1, stat2_name, target_value2, region = ui.run()
    
    # At least one stat and region must be configured
    if not region or (not stat1_name and not stat2_name):
        sys.exit()
    
    # Store current configuration for potential reconfiguration
    prev_stat1, prev_value1, prev_stat2, prev_value2, prev_region = stat1_name, target_value1, stat2_name, target_value2, region
    
    # Create status window
    status_window = StatusWindow(stat1_name, target_value1, stat2_name, target_value2)
    status_window.log(f"✓ Configuration loaded")
    status_window.log(f"✓ Target region: {region}")
    status_window.log(f"💡 Click START AUTOMATION to begin")
    status_window.set_status("⏸️ Ready to start", "#e3b341")
    
    # Run main loop and handle reconfiguration
    try:
        main()
    except KeyboardInterrupt:
        print("\nAutomation stopped by user")
    
    # Check if we should reconfigure or exit
    if not status_window.reconfigure_requested:
        # Exit if not reconfiguring
        break
