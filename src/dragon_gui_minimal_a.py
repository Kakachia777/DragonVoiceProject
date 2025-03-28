import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyperclip
from PIL import Image, ImageTk
import Dragon_cli2 as dragon_cli

class ModernButton(ttk.Button):
    """Custom styled button with hover effect"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'ModernButton.TButton')
        super().__init__(master, style=self.style_name, **kwargs)
        
class DragonVoiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragon Voice A")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Set up theme and styles
        self.setup_styles()
        
        # Set app icon
        try:
            self.root.iconbitmap("dragon_icon.ico")
        except:
            pass  # Icon not found, continue without it
        
        # Create CLI instance
        self.app = dragon_cli.DragonVoiceCLI()
        
        # Main frame
        main_frame = ttk.Frame(root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame with icon and title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Try to load and display icon
        try:
            img = Image.open("dragon_icon.ico")
            img = img.resize((48, 48), Image.LANCZOS)
            self.icon_img = ImageTk.PhotoImage(img)
            icon_label = ttk.Label(header_frame, image=self.icon_img)
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
        except:
            pass
        
        # Title and version info
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="Dragon Voice Assistant", 
                               font=("Segoe UI", 18, "bold"), foreground="#1a73e8")
        title_label.pack(anchor="w")
        
        version_label = ttk.Label(title_frame, text="Computer A Edition", 
                                font=("Segoe UI", 10), foreground="#5f6368")
        version_label.pack(anchor="w")
        
        # Status bar
        status_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_icon_var = tk.StringVar(value="🟢")
        
        status_icon = ttk.Label(status_frame, textvariable=self.status_icon_var, 
                               font=("Segoe UI", 12), padding=(10, 5))
        status_icon.pack(side=tk.LEFT)
        
        status_label = ttk.Label(status_frame, text="Status:", font=("Segoe UI", 10, "bold"), padding=(0, 5))
        status_label.pack(side=tk.LEFT)
        
        status_value = ttk.Label(status_frame, textvariable=self.status_var, 
                               foreground="#1a73e8", font=("Segoe UI", 10), padding=(5, 5))
        status_value.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Button cards container
        buttons_container = ttk.Frame(main_frame)
        buttons_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)
        
        # Record card
        record_card = self.create_card(buttons_container, 
                                     "Record Voice",
                                     "Speak now and transcribe your voice",
                                     "🎙️",
                                     lambda: self.start_recording(),
                                     "Record",
                                     is_primary=True)
        record_card.grid(row=0, column=0, padx=(0, 5), pady=(0, 10), sticky="nsew")
        
        # Quick Mode card
        quick_card = self.create_card(buttons_container,
                                    "Quick Mode",
                                    "Record and send to all chatbots",
                                    "⚡",
                                    lambda: self.quick_mode(),
                                    "Quick Mode")
        quick_card.grid(row=0, column=1, padx=(5, 0), pady=(0, 10), sticky="nsew")
        
        # Paste card
        paste_card = self.create_card(buttons_container,
                                    "Paste from Clipboard",
                                    "Send clipboard text to chatbots",
                                    "📋",
                                    lambda: self.paste_from_clipboard(),
                                    "Paste")
        paste_card.grid(row=1, column=0, padx=(0, 5), pady=(10, 0), sticky="nsew")
        
        # Retry card
        retry_card = self.create_card(buttons_container,
                                    "Retry Failed",
                                    "Retry sending to failed chatbots",
                                    "🔄",
                                    lambda: self.retry_failed(),
                                    "Retry")
        retry_card.grid(row=1, column=1, padx=(5, 0), pady=(10, 0), sticky="nsew")
        
        # Settings button
        settings_btn = ModernButton(main_frame, text="Settings", 
                                  command=self.open_settings, 
                                  style_name="Settings.TButton")
        settings_btn.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding=(10, 5))
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame to hold the text and scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=8, wrap=tk.WORD, 
                              state=tk.DISABLED, font=("Consolas", 9),
                              background="#f8f9fa", borderwidth=1, 
                              relief="solid")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_container, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Clear log button
        clear_btn = ttk.Button(log_frame, text="Clear Log", 
                             command=self.clear_log, width=15)
        clear_btn.pack(pady=(5, 0), anchor=tk.E)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        shortcut_label = ttk.Label(footer_frame, 
                                  text="Shortcuts: F9 = Record, F10 = Quick Mode",
                                  font=("Segoe UI", 8), foreground="#5f6368")
        shortcut_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(footer_frame, 
                                text="v1.0",
                                font=("Segoe UI", 8), foreground="#5f6368")
        version_label.pack(side=tk.RIGHT)
        
        # Override print function
        self.original_print = dragon_cli.print
        dragon_cli.print = self.custom_print
        
        # Set up a protocol for when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind keyboard shortcuts
        self.root.bind('<F9>', lambda e: self.start_recording())
        self.root.bind('<F10>', lambda e: self.quick_mode())
    
    def setup_styles(self):
        """Setup ttk styles for modern look"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Primary.TButton", background="#1a73e8", foreground="white")
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("CardDesc.TLabel", font=("Segoe UI", 9))
        style.configure("CardIcon.TLabel", font=("Segoe UI", 24))
        style.configure("Settings.TButton", font=("Segoe UI", 10))
        
        # Configure other elements
        style.configure("TLabelframe", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
    
    def create_card(self, parent, title, desc, icon, command, button_text, is_primary=False):
        """Create a card-like button with icon and description"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=0)
        
        # Content frame (left side)
        content = ttk.Frame(card)
        content.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Title and description
        title_label = ttk.Label(content, text=title, style="CardTitle.TLabel")
        title_label.pack(anchor="w")
        
        desc_label = ttk.Label(content, text=desc, style="CardDesc.TLabel")
        desc_label.pack(anchor="w", pady=(2, 0))
        
        # Icon (right side)
        icon_label = ttk.Label(card, text=icon, style="CardIcon.TLabel")
        icon_label.grid(row=0, column=1, padx=(0, 15), sticky="e")
        
        # Button
        button_style = "Primary.TButton" if is_primary else "TButton"
        button = ttk.Button(card, text=button_text, command=command, style=button_style)
        button.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")
        
        return card
    
    def set_status(self, status, icon="🟢"):
        """Set status with icon"""
        self.status_var.set(status)
        self.status_icon_var.set(icon)
    
    def custom_print(self, *args, **kwargs):
        """Override print to display in log"""
        message = " ".join(str(arg) for arg in args)
        
        # Update log text
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Also call original print
        self.original_print(*args, **kwargs)
    
    def get_timestamp(self):
        """Get current timestamp for logs"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def clear_log(self):
        """Clear the log text"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_recording(self):
        """Start recording audio"""
        self.set_status("Recording...", "🔴")
        
        # Run in a separate thread to avoid freezing UI
        threading.Thread(target=self._record_thread, daemon=True).start()
    
    def _record_thread(self):
        """Thread for recording to avoid freezing UI"""
        try:
            # Start recording
            self.app.start_recording()
            
            # After recording is done
            self.root.after(0, lambda: self.set_status("Ready"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error", "🔴"))
    
    def quick_mode(self):
        """Start quick mode recording"""
        self.set_status("Quick Mode...", "🟠")
        
        # Run in a separate thread to avoid freezing UI
        threading.Thread(target=self._quick_thread, daemon=True).start()
    
    def _quick_thread(self):
        """Thread for quick mode to avoid freezing UI"""
        try:
            # Run quick mode
            self.app.quick_mode()
            
            # After quick mode is done
            self.root.after(0, lambda: self.set_status("Ready"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error", "🔴"))
    
    def paste_from_clipboard(self):
        """Paste text from clipboard to chatbots"""
        self.set_status("Pasting from clipboard...", "🟠")
        
        # Run in a separate thread to avoid freezing UI
        threading.Thread(target=self._paste_thread, daemon=True).start()
    
    def _paste_thread(self):
        """Thread for pasting to avoid freezing UI"""
        try:
            # Get clipboard content
            clipboard_text = pyperclip.paste()
            
            if not clipboard_text:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "Clipboard is empty"))
                self.root.after(0, lambda: self.set_status("Ready"))
                return
            
            # Set as last transcription
            self.app.last_transcription = clipboard_text
            
            # Input to chatbots with confirmation
            self.app.input_to_chatbots(skip_confirmation=True)
            
            # After paste is done
            self.root.after(0, lambda: self.set_status("Ready"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error", "🔴"))
    
    def retry_failed(self):
        """Retry failed chatbots"""
        self.set_status("Retrying failed chatbots...", "🟠")
        
        # Run in a separate thread to avoid freezing UI
        threading.Thread(target=self._retry_thread, daemon=True).start()
    
    def _retry_thread(self):
        """Thread for retrying to avoid freezing UI"""
        try:
            # Retry failed chatbots
            self.app.retry_failed_chatbots()
            
            # After retry is done
            self.root.after(0, lambda: self.set_status("Ready"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error", "🔴"))
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("550x450")
        settings_window.resizable(False, False)
        settings_window.grab_set()  # Make window modal
        
        try:
            settings_window.iconbitmap("dragon_icon.ico")
        except:
            pass
        
        # Main frame
        main_frame = ttk.Frame(settings_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="Settings", 
                               font=("Segoe UI", 16, "bold"), foreground="#1a73e8")
        header_label.pack(anchor="w", pady=(0, 15))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Audio settings tab
        audio_frame = ttk.Frame(notebook, padding=15)
        notebook.add(audio_frame, text="Audio")
        
        # Create a nice frame for device selection
        device_frame = ttk.LabelFrame(audio_frame, text="Audio Device", padding=10)
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        current_device = self.app.config["audio"].get("device_name", "Default Device")
        device_label = ttk.Label(device_frame, text=f"Current: {current_device}", font=("Segoe UI", 10))
        device_label.pack(anchor="w", pady=(0, 10))
        
        device_btn = ttk.Button(device_frame, text="Select Device", 
                              command=lambda: threading.Thread(target=self._select_device_thread, 
                                                             args=(device_label,), daemon=True).start())
        device_btn.pack(fill=tk.X)
        
        # Gain setting
        gain_frame = ttk.LabelFrame(audio_frame, text="Gain Settings", padding=10)
        gain_frame.pack(fill=tk.X)
        
        gain_desc = ttk.Label(gain_frame, 
                            text="Adjust the recording sensitivity. Higher values make the microphone more sensitive.",
                            font=("Segoe UI", 9), wraplength=450)
        gain_desc.pack(anchor="w", pady=(0, 10))
        
        gain_val = self.app.config["audio"]["gain"]
        gain_var = tk.DoubleVar(value=gain_val)
        
        gain_value_label = ttk.Label(gain_frame, text=f"Gain: {gain_val:.1f}", font=("Segoe UI", 10, "bold"))
        gain_value_label.pack(anchor="w")
        
        gain_scale = ttk.Scale(gain_frame, from_=0.1, to=3.0, length=400,
                             variable=gain_var, command=lambda v: self._update_gain_label(float(v), gain_value_label))
        gain_scale.pack(fill=tk.X, pady=(5, 0))
        
        scale_labels = ttk.Frame(gain_frame)
        scale_labels.pack(fill=tk.X)
        
        ttk.Label(scale_labels, text="Low (0.1)", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Label(scale_labels, text="High (3.0)", font=("Segoe UI", 8)).pack(side=tk.RIGHT)
        
        # Chatbot settings tab
        chatbot_frame = ttk.Frame(notebook, padding=15)
        notebook.add(chatbot_frame, text="Chatbots")
        
        # Enabled setting
        enabled_frame = ttk.LabelFrame(chatbot_frame, text="Chatbot Input", padding=10)
        enabled_frame.pack(fill=tk.X, pady=(0, 15))
        
        chatbot_enabled = tk.BooleanVar(value=self.app.config["chatbot_input"]["enabled"])
        chatbot_check = ttk.Checkbutton(enabled_frame, text="Enable Chatbot Input", 
                                      variable=chatbot_enabled,
                                      command=lambda: self._toggle_chatbot_input(chatbot_enabled))
        chatbot_check.pack(anchor="w")
        
        enabled_desc = ttk.Label(enabled_frame, 
                               text="When enabled, transcribed text will be sent to configured chatbots automatically.",
                               font=("Segoe UI", 9), wraplength=450)
        enabled_desc.pack(anchor="w", pady=(5, 0))
        
        # Fast mode setting
        fast_frame = ttk.LabelFrame(chatbot_frame, text="Fast Mode", padding=10)
        fast_frame.pack(fill=tk.X, pady=(0, 15))
        
        fast_mode = tk.BooleanVar(value=self.app.config["chatbot_input"].get("fast_mode", True))
        fast_check = ttk.Checkbutton(fast_frame, text="Enable Fast Mode", 
                                   variable=fast_mode,
                                   command=lambda: self._toggle_fast_mode(fast_mode))
        fast_check.pack(anchor="w")
        
        fast_desc = ttk.Label(fast_frame, 
                            text="Fast mode skips confirmations and sends text directly to chatbots.",
                            font=("Segoe UI", 9), wraplength=450)
        fast_desc.pack(anchor="w", pady=(5, 0))
        
        # Calibration button
        cal_frame = ttk.LabelFrame(chatbot_frame, text="Calibration", padding=10)
        cal_frame.pack(fill=tk.X)
        
        cal_desc = ttk.Label(cal_frame, 
                           text="Calibrate the screen coordinates for each chatbot. You'll need to position each chatbot window before calibration.",
                           font=("Segoe UI", 9), wraplength=450)
        cal_desc.pack(anchor="w", pady=(0, 10))
        
        cal_btn = ttk.Button(cal_frame, text="Calibrate Chatbot Coordinates", 
                           command=lambda: threading.Thread(target=self.app.calibrate_chatbot_coordinates, daemon=True).start())
        cal_btn.pack(fill=tk.X)
        
        # Advanced tab
        advanced_frame = ttk.Frame(notebook, padding=15)
        notebook.add(advanced_frame, text="Advanced")
        
        # Config file location
        config_frame = ttk.LabelFrame(advanced_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        config_path = os.path.abspath(self.app.config_path if hasattr(self.app, 'config_path') else "config.json")
        config_label = ttk.Label(config_frame, text=f"Config file: {config_path}", font=("Segoe UI", 9))
        config_label.pack(anchor="w")
        
        # Open config button
        open_config_btn = ttk.Button(config_frame, text="Open Config File", 
                                   command=lambda: os.startfile(config_path) if os.path.exists(config_path) else None)
        open_config_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons at bottom
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_btn = ttk.Button(btn_frame, text="Save", width=12,
                            command=lambda: self._save_settings(settings_window, gain_var))
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", width=12,
                              command=settings_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)
    
    def _select_device_thread(self, label):
        """Thread for device selection"""
        try:
            self.app.select_device()
            # Update label with new device
            if hasattr(self.app, 'config') and 'audio' in self.app.config:
                device_name = self.app.config["audio"].get("device_name", "Default Device")
                self.root.after(0, lambda: label.config(text=f"Current: {device_name}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def _update_gain_label(self, value, label):
        """Update gain label when slider is moved"""
        rounded = round(value, 1)
        label.config(text=f"Gain: {rounded:.1f}")
    
    def _toggle_chatbot_input(self, var):
        """Toggle chatbot input enabled/disabled"""
        self.app.config["chatbot_input"]["enabled"] = var.get()
    
    def _toggle_fast_mode(self, var):
        """Toggle fast mode enabled/disabled"""
        self.app.config["chatbot_input"]["fast_mode"] = var.get()
    
    def _save_settings(self, window, gain_var=None):
        """Save settings to config file"""
        try:
            # Update gain if provided
            if gain_var is not None:
                self.app.config["audio"]["gain"] = round(gain_var.get(), 1)
            
            # Save config to file
            config_path = self.app.config_path if hasattr(self.app, 'config_path') else "config.json"
            with open(config_path, "w") as f:
                json.dump(self.app.config, f, indent=4)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def on_closing(self):
        """Called when window is closed"""
        # Restore original print function
        dragon_cli.print = self.original_print
        
        # Close the window
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set DPI awareness for better rendering on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = DragonVoiceGUI(root)
    root.mainloop() 