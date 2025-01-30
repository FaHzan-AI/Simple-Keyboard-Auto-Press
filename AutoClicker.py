import tkinter as tk
from tkinter import ttk
import keyboard
import mouse
import threading
import time
from random import uniform

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Auto Clicker By FaHzan")
        self.root.resizable(False, False)
        
        # Variables
        self.is_clicking = False
        self.click_thread = None
        self.hotkey = tk.StringVar(value="F6")
        self.is_infinite = tk.BooleanVar(value=True)
        
        # Main frame
        main_frame = ttk.Frame(root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Hotkey section
        hotkey_frame = ttk.LabelFrame(main_frame, text="Keyboard Shortcut Key to Start / Stop Clicking", padding="5")
        hotkey_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey, width=10)
        self.hotkey_entry.grid(row=0, column=0, padx=5)
        
        ttk.Button(hotkey_frame, text="Save Keyboard Key", command=self.save_hotkey).grid(row=0, column=1, padx=5)
        ttk.Button(hotkey_frame, text="Remove Key", command=self.remove_hotkey).grid(row=0, column=2, padx=5)
        
        # Click settings section
        click_settings_frame = ttk.LabelFrame(main_frame, text="Auto Clicking Time Delay, Location, Distance, Number of Clicks etc", padding="5")
        click_settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Click interval settings
        ttk.Label(click_settings_frame, text="Minutes:").grid(row=0, column=0, padx=5)
        self.minutes_entry = ttk.Entry(click_settings_frame, width=5)
        self.minutes_entry.insert(0, "0")
        self.minutes_entry.grid(row=0, column=1)
        
        ttk.Label(click_settings_frame, text="Seconds:").grid(row=0, column=2, padx=5)
        self.seconds_entry = ttk.Entry(click_settings_frame, width=5)
        self.seconds_entry.insert(0, "0")
        self.seconds_entry.grid(row=0, column=3)
        
        ttk.Label(click_settings_frame, text="Mili Seconds:").grid(row=0, column=4, padx=5)
        self.milliseconds_entry = ttk.Entry(click_settings_frame, width=5)
        self.milliseconds_entry.insert(0, "10")
        self.milliseconds_entry.grid(row=0, column=5)

        # Infinite clicking checkbox and number of clicks
        click_count_frame = ttk.Frame(click_settings_frame)
        click_count_frame.grid(row=1, column=0, columnspan=6, pady=5)
        
        self.infinite_check = ttk.Checkbutton(click_count_frame, text="Infinite Clicking", 
                                            variable=self.is_infinite, 
                                            command=self.toggle_clicks_entry)
        self.infinite_check.grid(row=0, column=0, padx=5)
        
        ttk.Label(click_count_frame, text="Number of Clicks:").grid(row=0, column=1, padx=5)
        self.clicks_entry = ttk.Entry(click_count_frame, width=8)
        self.clicks_entry.insert(0, "1000")
        self.clicks_entry.grid(row=0, column=2, padx=5)
        
        # Initially disable clicks entry since infinite is default
        self.toggle_clicks_entry()
        
        # Mouse button selection
        mouse_frame = ttk.LabelFrame(main_frame, text="Mouse Button to Click", padding="5")
        mouse_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.mouse_button = tk.StringVar(value="left")
        ttk.Radiobutton(mouse_frame, text="Left", variable=self.mouse_button, value="left").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mouse_frame, text="Middle", variable=self.mouse_button, value="middle").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(mouse_frame, text="Right", variable=self.mouse_button, value="right").grid(row=0, column=2, padx=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start Clicking", command=self.start_clicking)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Clicking", command=self.stop_clicking, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Current Status: Stopped")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Bind hotkey
        keyboard.on_press_key(self.hotkey.get(), self.toggle_clicking)

    def toggle_clicks_entry(self):
        if self.is_infinite.get():
            self.clicks_entry.state(['disabled'])
        else:
            self.clicks_entry.state(['!disabled'])

    def save_hotkey(self):
        new_hotkey = self.hotkey.get().upper()
        keyboard.unhook_all()
        keyboard.on_press_key(new_hotkey, self.toggle_clicking)
        
    def remove_hotkey(self):
        self.hotkey.set("")
        keyboard.unhook_all()
        
    def toggle_clicking(self, e=None):
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def start_clicking(self):
        if not self.is_clicking:
            self.is_clicking = True
            self.start_button.state(['disabled'])
            self.stop_button.state(['!disabled'])
            self.status_label.config(text="Current Status: Running")
            
            self.click_thread = threading.Thread(target=self.clicking_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
    
    def stop_clicking(self):
        self.is_clicking = False
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.status_label.config(text="Current Status: Stopped")
    
    def clicking_loop(self):
        minutes = int(self.minutes_entry.get())
        seconds = int(self.seconds_entry.get())
        milliseconds = int(self.milliseconds_entry.get())
        
        # Calculate total delay in seconds
        delay = (minutes * 60) + seconds + (milliseconds / 1000)
        
        if self.is_infinite.get():
            while self.is_clicking:
                mouse.click(button=self.mouse_button.get())
                time.sleep(delay)
        else:
            clicks_remaining = int(self.clicks_entry.get())
            while self.is_clicking and clicks_remaining > 0:
                mouse.click(button=self.mouse_button.get())
                time.sleep(delay)
                clicks_remaining -= 1

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()