import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import time

class AutoKeyboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Keyboard Presser v2.0")
        self.is_running = False
        self.actions = []
        self.hotkeys = {'start': '[', 'stop': ']'}
        self.hotkey_handles = {}
        
        self.create_widgets()
        self.setup_hotkeys()
        
    def setup_hotkeys(self):
        for handle in self.hotkey_handles.values():
            keyboard.remove_hotkey(handle)
            
        self.hotkey_handles['start'] = keyboard.add_hotkey(
            self.hotkeys['start'], 
            self.start_pressing
        )
        self.hotkey_handles['stop'] = keyboard.add_hotkey(
            self.hotkeys['stop'], 
            self.stop_pressing
        )
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Hotkey Display
        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkeys", padding=10)
        hotkey_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(hotkey_frame, text="Start: [ ").grid(row=0, column=0)
        ttk.Label(hotkey_frame, text="Stop: ] ").grid(row=1, column=0)

        # Action List
        action_frame = ttk.LabelFrame(main_frame, text="Action List", padding=10)
        action_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.action_list = tk.Listbox(action_frame, width=40, height=8)
        self.action_list.pack()

        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, pady=5, sticky="ew")
        
        self.start_btn = ttk.Button(
            control_frame, 
            text="Start ([)", 
            command=self.start_pressing
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(
            control_frame, 
            text="Stop (])", 
            command=self.stop_pressing, 
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5)

        # Add/Delete Actions
        action_control_frame = ttk.Frame(main_frame)
        action_control_frame.grid(row=3, column=0, pady=5, sticky="ew")
        
        ttk.Label(action_control_frame, text="Key:").grid(row=0, column=0)
        self.key_entry = ttk.Entry(action_control_frame, width=5)
        self.key_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(action_control_frame, text="Add", command=self.add_action).grid(row=0, column=2, padx=5)
        ttk.Button(action_control_frame, text="Delete", command=self.delete_action).grid(row=0, column=3, padx=5)

        # Settings
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding=10)
        settings_frame.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        
        # Delay Setting
        ttk.Label(settings_frame, text="Delay (ms):").grid(row=0, column=0)
        self.delay_entry = ttk.Entry(settings_frame, width=10)
        self.delay_entry.insert(0, "300")
        self.delay_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Repeat Settings
        self.repeat_mode = tk.StringVar(value="continuous")
        ttk.Radiobutton(
            settings_frame, 
            text="Continuous", 
            variable=self.repeat_mode, 
            value="continuous",
            command=self.toggle_repeat_mode
        ).grid(row=1, column=0, sticky="w")
        
        ttk.Radiobutton(
            settings_frame, 
            text="Repeat Times:", 
            variable=self.repeat_mode, 
            value="fixed",
            command=self.toggle_repeat_mode
        ).grid(row=2, column=0, sticky="w")
        
        self.repeat_entry = ttk.Spinbox(
            settings_frame, 
            from_=1, 
            to=999, 
            width=8,
            state="disabled"
        )
        self.repeat_entry.grid(row=2, column=1, sticky="w", padx=5)

    def toggle_repeat_mode(self):
        if self.repeat_mode.get() == "fixed":
            self.repeat_entry.config(state="normal")
        else:
            self.repeat_entry.config(state="disabled")

    def add_action(self):
        key = self.key_entry.get()
        if key:
            self.actions.append(key)
            self.action_list.insert(tk.END, f"{len(self.actions)}. {key}")
            self.key_entry.delete(0, tk.END)

    def delete_action(self):
        try:
            selected_index = self.action_list.curselection()[0]
            self.action_list.delete(selected_index)
            del self.actions[selected_index]
            # Update numbering
            self.action_list.delete(0, tk.END)
            for idx, action in enumerate(self.actions, 1):
                self.action_list.insert(tk.END, f"{idx}. {action}")
        except IndexError:
            messagebox.showwarning("Warning", "Please select an action to delete!")

    def start_pressing(self):
        if not self.actions:
            messagebox.showwarning("Warning", "Please add at least one action!")
            return
            
        try:
            self.delay = int(self.delay_entry.get()) / 1000
            if self.repeat_mode.get() == "fixed":
                repeat_times = int(self.repeat_entry.get())
                if repeat_times < 1:
                    raise ValueError
            else:
                repeat_times = 0
        except ValueError:
            messagebox.showwarning("Warning", "Invalid settings value!")
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        threading.Thread(
            target=self.auto_press, 
            args=(repeat_times,), 
            daemon=True
        ).start()

    def stop_pressing(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def auto_press(self, repeat_times):
        current_repeat = 0
        while self.is_running and (repeat_times == 0 or current_repeat < repeat_times):
            for key in self.actions:
                if not self.is_running:
                    return
                keyboard.press_and_release(key)
                time.sleep(self.delay)
            current_repeat += 1
        
        self.stop_pressing()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoKeyboardApp(root)
    root.mainloop()