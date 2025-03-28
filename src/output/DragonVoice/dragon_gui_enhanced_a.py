import os
import sys
import json
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pyperclip
from PIL import Image, ImageTk
import Dragon_cli2 as dragon_cli
from datetime import datetime
import sounddevice as sd
import numpy as np
import tempfile
import requests
import soundfile as sf

class ModernButton(ttk.Button):
    """Custom styled button with hover effect"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'ModernButton.TButton')
        super().__init__(master, style=self.style_name, **kwargs)

class DragonVoiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragon Voice A")
        self.root.geometry("600x750")
        self.root.minsize(600, 750)
        
        # Recording state tracking
        self.recording_active = False
        self.record_button = None
        
        # Set up theme and styles
        self.setup_styles()
        
        # Set app icon
        try:
            self.root.iconbitmap("dragon_icon.ico")
        except:
            pass  # Icon not found, continue without it
        
        # Create CLI instance
        self.app = dragon_cli.DragonVoiceCLI()
        
        # Main container 
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self.create_header_frame()
        self.create_status_bar()
        self.create_main_buttons()
        self.create_action_buttons()
        self.create_log_area()
        self.create_footer()
        
        # Add progress indicator
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(self.main_container, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
        self.progress_bar.pack_forget()  # Hide until needed
        
        # Override print function using a more reliable approach
        # Save the original print function
        self.original_print = print
        
        # Create a custom print function that will intercept output
        def custom_print(*args, **kwargs):
            # Get the message as a string
            message = " ".join(str(arg) for arg in args)
            # Log the message to our GUI
            self.log(message)
            # Also print to console using the original print
            self.original_print(*args, **kwargs)
        
        # Replace built-in print in the module
        import builtins
        builtins.print = custom_print
        
        # Set up a protocol for when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Set initial status
        self.set_status("Ready")
        
        # Create settings menu
        self.settings_menu = None
        
        # Timer for level meter updates
        self.level_timer_id = None
        
        # Log initial message
        self.log("Dragon Voice Assistant started successfully")
        self.log(f"Using configuration from: {os.path.abspath(self.app.config_path)}")
        
        # Check for mic
        mic_name = self.app.config["audio"].get("device_name", "Default")
        self.log(f"Microphone: {mic_name}")
    
    def bind_shortcuts(self):
        """Set up all keyboard shortcuts"""
        # Change F9 to Enter for recording
        self.root.bind('<Return>', lambda e: self.start_recording_key(True))
        self.root.bind('<KeyRelease-Return>', lambda e: self.start_recording_key(False))
        
        self.root.bind('<F10>', lambda e: self.quick_mode())
        self.root.bind('<F11>', lambda e: self.retry_failed())
        self.root.bind('<F12>', lambda e: self.open_settings())
        self.root.bind('<Control-v>', lambda e: self.paste_from_clipboard())
        
        # Add more keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.open_settings())
        self.root.bind('<Control-c>', lambda e: self.calibrate_chatbots())
        self.root.bind('<Control-r>', lambda e: self.start_recording())
        self.root.bind('<Control-q>', lambda e: self.quick_mode())
        self.root.bind('<Escape>', lambda e: self.on_closing())
    
    def start_recording_key(self, is_pressed):
        """Handle key press/release for recording"""
        if is_pressed:
            # Start recording only if not already recording
            if not self.recording_active:
                self.log("Starting recording (key pressed)")
                self.recording_active = True
                # Update button text
                if self.record_button:
                    self.record_button.config(text="Recording... (Release Enter to stop)")
                # Create a thread for recording
                recording_thread = threading.Thread(target=self._record_thread, daemon=True)
                recording_thread.start()
                
                # Start updating level meter
                self.update_level_display()
        else:
            # Stop recording on key release if we're recording
            if self.recording_active:
                self.recording_active = False
                # Update button text
                if self.record_button:
                    self.record_button.config(text="Record (Enter)")
    
    def create_header_frame(self):
        """Create the header with logo and title"""
        header_frame = ttk.Frame(self.main_container, padding=15)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Try to load and display icon
        try:
            img = Image.open("dragon_icon.ico")
            img = img.resize((48, 48), Image.LANCZOS)
            self.icon_img = ImageTk.PhotoImage(img)
            icon_label = ttk.Label(header_frame, image=self.icon_img)
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"Error loading icon: {e}")
            pass
        
        # Title and version info
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        title_label = ttk.Label(title_frame, text="Dragon Voice Assistant", 
                               font=("Segoe UI", 18, "bold"), foreground="#1a73e8")
        title_label.pack(anchor="w")
        
        version_label = ttk.Label(title_frame, text="Computer A Edition", 
                                font=("Segoe UI", 10), foreground="#5f6368")
        version_label.pack(anchor="w")
        
        # Quick access buttons on the right
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        help_btn = ttk.Button(button_frame, text="Help", width=8, 
                            command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=2)
        
        settings_btn = ttk.Button(button_frame, text="Settings", width=8,
                                command=self.open_settings)
        settings_btn.pack(side=tk.LEFT, padx=2)
    
    def create_status_bar(self):
        """Create enhanced status bar with more information"""
        status_frame = ttk.Frame(self.main_container, relief="solid", borderwidth=1)
        status_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
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
        
        # Add mic level indicator
        self.level_var = tk.StringVar(value="🔈 ▁▁▁▁▁▁▁▁")
        level_indicator = ttk.Label(status_frame, textvariable=self.level_var,
                                  font=("Segoe UI", 10), padding=(5, 5))
        level_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Add chatbot info
        self.chatbot_count_var = tk.StringVar(value="Chatbots: 0")
        chatbot_indicator = ttk.Label(status_frame, textvariable=self.chatbot_count_var,
                                    font=("Segoe UI", 9), padding=(5, 5))
        chatbot_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Update chatbot count
        self.update_chatbot_count()
    
    def update_chatbot_count(self):
        """Update the chatbot count in the status bar"""
        if hasattr(self.app, 'config') and 'chatbot_input' in self.app.config:
            count = len(self.app.config["chatbot_input"]["coordinates"])
            self.chatbot_count_var.set(f"Chatbots: {count}")
    
    def update_level_meter(self, level=0):
        """Update the microphone level meter"""
        if level < 0:
            level = 0
        elif level > 1:
            level = 1
            
        # Create level meter display
        bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        meter_width = 10
        
        # Calculate how many bars to fill
        filled_bars = int(level * meter_width)
        
        # Create the meter string
        meter = ""
        for i in range(meter_width):
            if i < filled_bars:
                idx = int((level * 8) % 8) if i == filled_bars - 1 else 7
                meter += bars[idx]
            else:
                meter += "▁"
        
        # Set the level meter text
        self.level_var.set(f"🔈 {meter}")
    
    def create_main_buttons(self):
        """Create the main button cards with actions"""
        # Button cards container
        buttons_container = ttk.Frame(self.main_container, padding=(15, 0))
        buttons_container.pack(fill=tk.BOTH, expand=False, pady=(0, 5))
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)
        
        # Record card - primary action
        record_card = self.create_card(buttons_container, 
                                     "Record Voice",
                                     "Press and hold Enter to record",
                                     "🎙️",
                                     lambda: self.start_recording(),
                                     "Record (Enter)",
                                     is_primary=True)
        record_card.grid(row=0, column=0, padx=(0, 5), pady=(0, 10), sticky="nsew")
        
        # Find and store the record button for later updates
        for child in record_card.winfo_children():
            if isinstance(child, ttk.Button):
                self.record_button = child
                break
        
        # Quick Mode card
        quick_card = self.create_card(buttons_container,
                                    "Quick Mode",
                                    "Record and send to all chatbots",
                                    "⚡",
                                    lambda: self.quick_mode(),
                                    "Quick Mode (F10)")
        quick_card.grid(row=0, column=1, padx=(5, 0), pady=(0, 10), sticky="nsew")
    
    def create_action_buttons(self):
        """Create secondary action buttons"""
        # Secondary buttons container
        actions_container = ttk.Frame(self.main_container, padding=(15, 0))
        actions_container.pack(fill=tk.BOTH, expand=False, pady=(0, 15))
        actions_container.columnconfigure(0, weight=1)
        actions_container.columnconfigure(1, weight=1)
        actions_container.columnconfigure(2, weight=1)
        
        # Paste card
        paste_card = self.create_small_card(actions_container,
                                          "Paste Text",
                                          "📋",
                                          lambda: self.paste_from_clipboard())
        paste_card.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        
        # Retry card
        retry_card = self.create_small_card(actions_container,
                                          "Retry Failed",
                                          "🔄",
                                          lambda: self.retry_failed())
        retry_card.grid(row=0, column=1, padx=5, sticky="nsew")
        
        # Calibrate card
        calibrate_card = self.create_small_card(actions_container,
                                              "Calibrate",
                                              "🎯",
                                              lambda: self.calibrate_chatbots())
        calibrate_card.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
    
    def create_log_area(self):
        """Create the log display area"""
        log_frame = ttk.LabelFrame(self.main_container, text="Activity Log", padding=(10, 5))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Create a frame to hold the text and scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        # Use scrolledtext widget for better performance
        self.log_text = scrolledtext.ScrolledText(log_container, height=10, wrap=tk.WORD, 
                                               state=tk.DISABLED, font=("Consolas", 9),
                                               background="#f8f9fa", borderwidth=1, 
                                               relief="solid")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Log control buttons
        btn_frame = ttk.Frame(log_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        copy_btn = ttk.Button(btn_frame, text="Copy Log", 
                            command=self.copy_log, width=12)
        copy_btn.pack(side=tk.LEFT)
        
        save_btn = ttk.Button(btn_frame, text="Save Log", 
                            command=self.save_log, width=12)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Clear Log", 
                             command=self.clear_log, width=12)
        clear_btn.pack(side=tk.RIGHT)
    
    def create_footer(self):
        """Create the footer with shortcuts and version"""
        footer_frame = ttk.Frame(self.main_container, padding=(15, 5))
        footer_frame.pack(fill=tk.X, pady=(0, 5))
        
        shortcut_label = ttk.Label(footer_frame, 
                                 text="Shortcuts: Enter=Record (hold), F10=Quick Mode, F11=Retry, F12=Settings",
                                 font=("Segoe UI", 8), foreground="#5f6368")
        shortcut_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(footer_frame, 
                                text="v2.0",
                                font=("Segoe UI", 8), foreground="#5f6368")
        version_label.pack(side=tk.RIGHT)
    
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
        
        # Configure tab styles
        style.configure("TNotebook", background="#f8f9fa")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10))
        
        # Configure other elements
        style.configure("TLabelframe", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
    
    def create_card(self, parent, title, desc, icon, command, button_text, is_primary=False):
        """Create a card-like button with icon and description"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ttk.Label(card, text=icon, style="CardIcon.TLabel")
        icon_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(card, text=title, style="CardTitle.TLabel")
        title_label.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(10, 0))
        
        # Description
        desc_label = ttk.Label(card, text=desc, style="CardDesc.TLabel")
        desc_label.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 10))
        
        # Separator
        separator = ttk.Separator(card, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Button
        button_style = "Primary.TButton" if is_primary else "TButton"
        action_btn = ModernButton(card, text=button_text, command=command, style_name=button_style)
        action_btn.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        return card
    
    def create_small_card(self, parent, title, icon, command):
        """Create a smaller action card with just icon and title"""
        card = ttk.Frame(parent, style="Card.TFrame")
        
        # Icon
        icon_label = ttk.Label(card, text=icon, style="CardIcon.TLabel")
        icon_label.pack(pady=(10, 5))
        
        # Title
        title_label = ttk.Label(card, text=title, style="CardTitle.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Make the whole card clickable
        card.bind("<Button-1>", lambda e: command())
        icon_label.bind("<Button-1>", lambda e: command())
        title_label.bind("<Button-1>", lambda e: command())
        
        return card
    
    def set_status(self, status, icon="🟢"):
        """Update the status display"""
        self.status_var.set(status)
        self.status_icon_var.set(icon)
        
        # Add to log in certain cases
        if status not in ["Ready", "Listening..."]:
            self.log(f"Status: {status}")
    
    def get_timestamp(self):
        """Get a formatted timestamp for logs"""
        return datetime.now().strftime("%H:%M:%S")
    
    def log(self, message):
        """Add a message to the log with timestamp"""
        timestamp = self.get_timestamp()
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Scroll to end
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Log cleared")
    
    def copy_log(self):
        """Copy log contents to clipboard"""
        log_content = self.log_text.get(1.0, tk.END)
        pyperclip.copy(log_content)
        self.log("Log copied to clipboard")
    
    def save_log(self):
        """Save log contents to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Log As"
            )
            if filename:
                log_content = self.log_text.get(1.0, tk.END)
                with open(filename, "w") as f:
                    f.write(log_content)
                self.log(f"Log saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {str(e)}")
    
    def show_help(self):
        """Show help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Dragon Voice Assistant Help")
        help_window.geometry("600x500")
        help_window.minsize(600, 500)
        help_window.grab_set()
        
        try:
            help_window.iconbitmap("dragon_icon.ico")
        except:
            pass
        
        # Main frame
        main_frame = ttk.Frame(help_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Dragon Voice Assistant Help", 
                             font=("Segoe UI", 16, "bold"), foreground="#1a73e8")
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Create scrollable text area
        help_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                           font=("Segoe UI", 10))
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Help content
        help_content = """
Dragon Voice Assistant Help

MAIN FEATURES:
--------------
• Record Voice: Press and hold Enter to record. Speak clearly, and the app will transcribe your speech.
• Quick Mode: Records and sends your spoken text to all configured chatbots in one step.
• Paste Text: Sends clipboard text directly to chatbots.
• Retry Failed: Retries sending to any chatbots that failed in previous attempts.
• Calibrate: Allows you to set up the positions of chatbot windows on your screen.

KEYBOARD SHORTCUTS:
------------------
Enter - Press and hold to record (release to stop)
F10 - Quick mode (record and send)
F11 - Retry failed chatbots
F12 - Open settings
Ctrl+V - Paste text from clipboard
Ctrl+S - Open settings
Ctrl+C - Open chatbot calibration
Ctrl+R - Start recording
Esc - Close application

SETTINGS:
---------
• Audio: Configure microphone, adjust gain, and noise reduction.
• Chatbots: Enable/disable chatbot input and configure fast mode.
• Profiles: Save and load different chatbot window configurations.
• Advanced: Access to configuration file and additional options.

CALIBRATION:
-----------
To set up chatbot coordinates:
1. Click "Calibrate" or press Ctrl+C
2. Position your browser windows with chatbots open
3. Follow the prompts to click on the input area of each chatbot
4. Save the configuration when done

TROUBLESHOOTING:
---------------
• If recording doesn't work, check your microphone in Settings
• If text isn't sent to chatbots, recalibrate the coordinates
• Check the Activity Log for detailed error messages
• Try running the application as administrator if you have permission issues

For more help, visit: https://dragonvoice.example.com/help
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", 
                             command=help_window.destroy, width=15)
        close_btn.pack(pady=(15, 0), anchor=tk.E)
    
    def start_recording(self):
        """Handle recording button click"""
        # This function is called when the record button is clicked
        # Toggle between start/stop
        if self.recording_active:
            # Stop recording
            self.recording_active = False
            if self.record_button:
                self.record_button.config(text="Record (Enter)")
            self.log("Recording stopped (button click)")
        else:
            # Start recording
            self.log("Starting recording (button click)")
            self.recording_active = True
            # Update button text
            if self.record_button:
                self.record_button.config(text="Recording... (Click to stop)")
            # Create a thread for recording
            recording_thread = threading.Thread(target=self._record_thread, daemon=True)
            recording_thread.start()
            
            # Start updating level meter
            self.update_level_display()
    
    def update_level_display(self):
        """Update the level meter display periodically"""
        if hasattr(self.app, 'recording') and self.app.recording:
            # Get the current level from the app if available
            level = 0
            if hasattr(self.app, 'current_level'):
                level = self.app.current_level
            
            # Update the meter
            self.update_level_meter(level)
            
            # Schedule next update
            self.level_timer_id = self.root.after(100, self.update_level_display)
        else:
            # Stop updating when not recording
            self.update_level_meter(0)
            
            # Cancel any pending timer
            if self.level_timer_id:
                self.root.after_cancel(self.level_timer_id)
                self.level_timer_id = None
    
    def _record_thread(self):
        """Thread for recording audio"""
        try:
            self.set_status("Recording...", "🎙️")
            
            # Show progress bar while recording
            self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
            self.root.update_idletasks()
            
            # Initialize recording manually - more direct approach to work with underlying API
            if hasattr(self.app, '_record_audio'):
                # Clear any previous audio data
                if hasattr(self.app, 'audio_data'):
                    self.app.audio_data = []
                
                # Reset recording start time
                self.app.recording_start_time = time.time()
                
                # Set recording flag
                self.app.recording = True
                
                # Set up audio stream - copied from _record_audio but executed directly
                # This is more reliable than calling _record_audio
                try:
                    # Set up audio stream with the same parameters as in the CLI
                    stream = sd.InputStream(
                        device=self.app.config["audio"]["device"],
                        channels=self.app.config["audio"]["channels"],
                        samplerate=self.app.config["audio"]["samplerate"],
                        dtype=np.float32,
                        blocksize=self.app.config["audio"]["chunk_size"],
                        callback=self.app._audio_callback
                    )
                    
                    # Start the stream
                    stream.start()
                    
                    # Set our active flag to true
                    self.recording_active = True
                    
                    # The recording will continue until key is released
                    # We'll wait here until recording_active becomes False
                    while self.recording_active:
                        time.sleep(0.05)  # Short sleep to avoid cpu usage
                        
                        # Update volume level meter
                        if hasattr(self.app, 'current_volume'):
                            self.update_level_meter(self.app.current_volume)
                        
                    # Log that recording is stopping due to key release
                    self.log("Recording stopped (key released)")
                    
                    # Stop the stream and clean up
                    stream.stop()
                    stream.close()
                    
                    # Set recording flag to false
                    self.app.recording = False
                    
                    # Save the recorded audio
                    if self.app.audio_data:
                        filename = self.app.save_audio()
                        if filename:
                            self.log(f"Recording saved to: {filename}")
                            
                            # Transcribe the audio - do this directly instead of calling app.transcribe_audio
                            # to avoid the CLI's confirmation dialog
                            try:
                                # Save audio to temporary file
                                temp_file = os.path.join(tempfile.gettempdir(), "temp_audio.mp3")
                                audio_data = np.concatenate(self.app.audio_data)
                                
                                # Check if we have actual audio data
                                if np.all(audio_data == 0) or len(audio_data) < 100:
                                    self.log("No audio detected - recording was empty or too short")
                                    self.set_status("Recording empty", "⚠️")
                                    return
                                    
                                # Save the audio file
                                sf.write(temp_file, audio_data, self.app.config["audio"]["samplerate"])
                                
                                # Prepare API request
                                headers = {
                                    "Authorization": f"Bearer {self.app.api_key}",
                                }
                                
                                data = {
                                    "model": "whisper-large-v3",
                                    "task": "transcribe",
                                    "language": "en"
                                }
                                
                                # Log debug info
                                self.log(f"API URL: {self.app.api_url}")
                                self.log(f"Audio file size: {os.path.getsize(temp_file)} bytes")
                                
                                # Open the file for the request
                                files = {
                                    'audio': (temp_file, open(temp_file, 'rb'), 'audio/mpeg')
                                }
                                
                                # Make API request
                                self.log("Sending request to API...")
                                response = requests.post(self.app.api_url, headers=headers, data=data, files=files)
                                
                                # Close file handle
                                files['audio'][1].close()
                                
                                # Process response
                                if response.status_code == 200:
                                    result = response.json()
                                    
                                    # Print transcription
                                    self.log("\nTranscription:")
                                    transcript_text = result.get('text', '')
                                    self.log(transcript_text)
                                    
                                    # Store the transcription in app
                                    self.app.last_transcription = transcript_text
                                    
                                    # Save transcript if auto-save is enabled
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    transcript_file = os.path.join(
                                        self.app.config["transcription"]["save_path"],
                                        f"transcript_{timestamp}.txt"
                                    )
                                    
                                    with open(transcript_file, 'w') as f:
                                        f.write(transcript_text)
                                    
                                    self.log(f"\nTranscript saved to: {transcript_file}")
                                    
                                    # Show GUI confirmation dialog instead of using CLI's input function
                                    confirmed, final_text = self.gui_confirm_transcription(transcript_text)
                                    
                                    # If confirmed, send to chatbots
                                    if confirmed:
                                        self.app.last_transcription = final_text
                                        if hasattr(self.app, 'input_to_chatbots'):
                                            self.log("\nSending transcription to chatbots...")
                                            self.app.input_to_chatbots(skip_confirmation=True)
                                            self.set_status("Sent to chatbots", "✅")
                                        else:
                                            self.log("Could not send to chatbots - function not available")
                                    else:
                                        self.log("Transcription process cancelled.")
                                    
                                else:
                                    self.log("Transcription failed")
                                    self.log(f"Status Code: {response.status_code}")
                                    self.log(f"Response: {response.text}")
                                    self.set_status("Transcription failed", "❌")
                            
                            except Exception as e:
                                self.log(f"Transcription error: {e}")
                                self.set_status("Transcription error", "❌")
                            
                            finally:
                                # Clean up temp file
                                if 'temp_file' in locals() and os.path.exists(temp_file):
                                    try:
                                        os.remove(temp_file)
                                    except:
                                        pass
                    else:
                        self.log("No audio data recorded")
                        self.set_status("Recording empty", "⚠️")
                    
                except Exception as e:
                    self.log(f"Audio stream error: {str(e)}")
                    if hasattr(self.app, 'recording'):
                        self.app.recording = False
            else:
                self.log("Recording method not available")
                self.set_status("Recording unavailable", "⚠️")
            
            # Hide progress bar when done
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            
            # Reset recording state
            self.recording_active = False
            
        except Exception as e:
            self.log(f"Recording error: {str(e)}")
            self.set_status("Error", "🔴")
            # Hide progress bar on error
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            # Reset recording state
            self.recording_active = False
            if hasattr(self.app, 'recording'):
                self.app.recording = False
    
    def gui_confirm_transcription(self, text):
        """GUI version of confirm or edit transcription dialog"""
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Confirm Transcription")
        dialog.geometry("500x400")
        dialog.minsize(500, 400)
        dialog.grab_set()  # Make modal
        
        # Set icon if available
        try:
            dialog.iconbitmap("dragon_icon.ico")
        except:
            pass
        
        # Main frame with padding
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Confirm Transcription", 
                             font=("Segoe UI", 16, "bold"), foreground="#1a73e8")
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Label for instructions
        instruction_label = ttk.Label(main_frame, 
                                    text="Review the transcription below. You can edit it if needed.",
                                    font=("Segoe UI", 10), wraplength=470)
        instruction_label.pack(anchor="w", pady=(0, 10))
        
        # Text box for transcription with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create scrolled text widget
        text_box = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                          font=("Segoe UI", 10), height=10)
        text_box.pack(fill=tk.BOTH, expand=True)
        
        # Insert the transcription
        text_box.insert(tk.END, text)
        
        # Copy button
        copy_btn = ttk.Button(main_frame, text="Copy to Clipboard", 
                           command=lambda: [pyperclip.copy(text_box.get(1.0, tk.END)), 
                                           self.log("Text copied to clipboard")])
        copy_btn.pack(side=tk.LEFT, pady=(0, 10))
        
        # Create result variables
        result = {"confirmed": False, "text": text}
        
        # Function to set result and close
        def on_confirm():
            result["confirmed"] = True
            result["text"] = text_box.get(1.0, tk.END).strip()
            dialog.destroy()
            
        def on_cancel():
            result["confirmed"] = False
            dialog.destroy()
        
        # Buttons at bottom
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 0))
        
        confirm_btn = ttk.Button(btn_frame, text="Confirm & Send to Chatbots", 
                              command=on_confirm, width=25)
        confirm_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", 
                             command=on_cancel, width=12)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        # Return result
        return result["confirmed"], result["text"]
    
    def quick_mode(self):
        """Record and send to chatbots in one step"""
        # Create a thread for quick mode
        quick_thread = threading.Thread(target=self._quick_thread, daemon=True)
        quick_thread.start()
    
    def _quick_thread(self):
        """Thread for quick mode"""
        try:
            self.set_status("Quick Mode Active", "⚡")
            
            # Show progress bar
            self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
            self.root.update_idletasks()
            
            # Initialize recording manually similar to _record_thread
            if hasattr(self.app, '_record_audio'):
                # Set recording flag
                self.app.recording = True
                
                # Start audio stream
                self.app._record_audio()
                
                # Start a short recording
                self.recording_active = True
                recording_duration = 5  # Maximum recording duration in seconds
                start_time = time.time()
                
                # Wait until stopped manually or timeout reached
                while self.recording_active and self.app.recording:
                    # Check if we've reached max duration
                    if time.time() - start_time > recording_duration:
                        self.log("Recording time limit reached")
                        break
                    time.sleep(0.1)
                
                # Stop recording
                if self.app.recording:
                    self.app.stop_recording()
                
                # Process the transcription
                if hasattr(self.app, 'last_transcription') and self.app.last_transcription:
                    self.log(f"Transcribed: {self.app.last_transcription}")
                    
                    # Send to chatbots
                    if hasattr(self.app, 'input_to_chatbots'):
                        self.app.input_to_chatbots(skip_confirmation=True)
                        self.log("Sent to chatbots")
                    else:
                        self.log("Could not send to chatbots - function not available")
                else:
                    self.set_status("Transcription failed", "❌")
            else:
                self.log("Quick mode function not available")
                self.set_status("Quick mode unavailable", "⚠️")
            
            # Hide progress bar
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            
            # Reset recording state
            self.recording_active = False
            
            self.set_status("Quick mode completed", "✅")
            
        except Exception as e:
            self.log(f"Quick mode error: {str(e)}")
            self.set_status("Error", "🔴")
            # Hide progress bar
            self.progress_bar.pack_forget()
            # Reset recording state
            self.recording_active = False
    
    def paste_from_clipboard(self):
        """Paste text from clipboard to chatbots"""
        # Create a thread for paste operation
        paste_thread = threading.Thread(target=self._paste_thread, daemon=True)
        paste_thread.start()
    
    def _paste_thread(self):
        """Thread for paste from clipboard"""
        try:
            self.set_status("Pasting from clipboard...", "📋")
            
            # Show progress bar
            self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
            self.root.update_idletasks()
            
            # Get clipboard text
            clipboard_text = pyperclip.paste()
            
            if not clipboard_text:
                self.log("Clipboard is empty")
                self.set_status("Clipboard empty", "⚠️")
                self.progress_bar.pack_forget()
                return
            
            # Truncate text for display in log
            display_text = clipboard_text[:50] + "..." if len(clipboard_text) > 50 else clipboard_text
            self.log(f"Pasting text: {display_text}")
            
            # Set clipboard text to last transcription and send to chatbots
            self.app.last_transcription = clipboard_text
            self.app.input_to_chatbots(skip_confirmation=True)
            
            # Hide progress bar
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            
            self.set_status("Paste completed", "✅")
            
        except Exception as e:
            self.log(f"Paste error: {str(e)}")
            self.set_status("Error", "🔴")
            # Hide progress bar
            self.progress_bar.pack_forget()
    
    def retry_failed(self):
        """Retry sending to failed chatbots"""
        # Create a thread for retry operation
        retry_thread = threading.Thread(target=self._retry_thread, daemon=True)
        retry_thread.start()
    
    def _retry_thread(self):
        """Thread for retry failed chatbots"""
        try:
            self.set_status("Retrying failed chatbots...", "🔄")
            
            # Show progress bar
            self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
            self.root.update_idletasks()
            
            # Retry
            if hasattr(self.app, 'retry_failed_chatbots'):
                self.app.retry_failed_chatbots()
                self.set_status("Retry completed", "✅")
            else:
                self.log("Retry function not available")
                self.set_status("Retry not available", "⚠️")
            
            # Hide progress bar
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            
        except Exception as e:
            self.log(f"Retry error: {str(e)}")
            self.set_status("Error", "🔴")
            # Hide progress bar
            self.progress_bar.pack_forget()
    
    def calibrate_chatbots(self):
        """Open the chatbot calibration tool"""
        # Create a thread for calibration
        calibrate_thread = threading.Thread(
            target=lambda: self.app.calibrate_chatbot_coordinates(), 
            daemon=True
        )
        calibrate_thread.start()
        self.log("Starting chatbot calibration...")
        self.set_status("Calibrating chatbots...", "🎯")
        
        # Update chatbot count when done (on a timer)
        self.root.after(5000, self.update_chatbot_count)
    
    def open_settings(self):
        """Open enhanced settings dialog"""
        if self.settings_menu:
            self.settings_menu.lift()
            return
            
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Dragon Voice Assistant Settings")
        settings_window.geometry("650x550")
        settings_window.minsize(650, 550)
        settings_window.grab_set()  # Make window modal
        
        # Track this window
        self.settings_menu = settings_window
        
        # Set protocol for when this window is closed
        settings_window.protocol("WM_DELETE_WINDOW", 
                               lambda: self.on_settings_closed(settings_window))
        
        try:
            settings_window.iconbitmap("dragon_icon.ico")
        except:
            pass
        
        # Main frame
        main_frame = ttk.Frame(settings_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="Dragon Voice Assistant Settings", 
                              font=("Segoe UI", 16, "bold"), foreground="#1a73e8")
        header_label.pack(anchor="w", pady=(0, 15))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        audio_frame = self.create_audio_settings_tab(notebook)
        chatbot_frame = self.create_chatbot_settings_tab(notebook)
        profiles_frame = self.create_profiles_tab(notebook)
        advanced_frame = self.create_advanced_settings_tab(notebook)
        
        # Add tabs to notebook
        notebook.add(audio_frame, text="Audio")
        notebook.add(chatbot_frame, text="Chatbots")
        notebook.add(profiles_frame, text="Profiles")
        notebook.add(advanced_frame, text="Advanced")
        
        # Buttons at bottom
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_btn = ttk.Button(btn_frame, text="Save", width=12,
                          command=lambda: self._save_all_settings(settings_window))
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", width=12,
                              command=settings_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)

    def create_audio_settings_tab(self, notebook):
        """Create the audio settings tab"""
        audio_frame = ttk.Frame(notebook, padding=15)
        
        # Device selection section
        device_frame = ttk.LabelFrame(audio_frame, text="Audio Device", padding=10)
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Current device info
        current_device = self.app.config["audio"].get("device_name", "Default Device")
        device_label = ttk.Label(device_frame, text=f"Current: {current_device}", 
                               font=("Segoe UI", 10))
        device_label.pack(anchor="w", pady=(0, 10))
        
        # Device selection button
        device_btn = ttk.Button(device_frame, text="Select Audio Device", 
                              command=lambda: threading.Thread(
                                  target=self._select_device_thread, 
                                  args=(device_label,), 
                                  daemon=True).start())
        device_btn.pack(fill=tk.X)
        
        # Test button
        test_btn = ttk.Button(device_frame, text="Test Microphone", 
                            command=lambda: threading.Thread(
                                target=self._test_microphone, 
                                daemon=True).start())
        test_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Gain settings section
        gain_frame = ttk.LabelFrame(audio_frame, text="Input Gain", padding=10)
        gain_frame.pack(fill=tk.X, pady=(0, 15))
        
        gain_desc = ttk.Label(gain_frame, 
                           text="Adjust recording sensitivity. Higher values make the microphone more sensitive.",
                           font=("Segoe UI", 9), wraplength=550)
        gain_desc.pack(anchor="w", pady=(0, 10))
        
        # Current gain value
        gain_val = self.app.config["audio"]["gain"]
        self.gain_var = tk.DoubleVar(value=gain_val)
        
        gain_value_label = ttk.Label(gain_frame, text=f"Gain: {gain_val:.1f}", 
                                   font=("Segoe UI", 10, "bold"))
        gain_value_label.pack(anchor="w")
        
        # Gain slider
        gain_scale = ttk.Scale(gain_frame, from_=0.1, to=3.0, length=550,
                            variable=self.gain_var, 
                            command=lambda v: self._update_gain_label(float(v), gain_value_label))
        gain_scale.pack(fill=tk.X, pady=(5, 0))
        
        # Scale labels
        scale_labels = ttk.Frame(gain_frame)
        scale_labels.pack(fill=tk.X)
        
        ttk.Label(scale_labels, text="Low (0.1)", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Label(scale_labels, text="High (3.0)", font=("Segoe UI", 8)).pack(side=tk.RIGHT)
        
        # Noise reduction section
        noise_frame = ttk.LabelFrame(audio_frame, text="Noise Reduction", padding=10)
        noise_frame.pack(fill=tk.X)
        
        # Noise reduction enabled checkbox
        noise_enabled = tk.BooleanVar(
            value=self.app.config["audio"]["noise_reduction"]["enabled"])
        noise_check = ttk.Checkbutton(noise_frame, text="Enable Noise Reduction", 
                                    variable=noise_enabled)
        noise_check.pack(anchor="w")
        
        # Noise reduction strength
        noise_strength = tk.DoubleVar(
            value=self.app.config["audio"]["noise_reduction"]["strength"])
        
        strength_frame = ttk.Frame(noise_frame)
        strength_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(strength_frame, text="Strength:", 
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        strength_value_label = ttk.Label(strength_frame, text=f"{noise_strength.get():.1f}", 
                                      font=("Segoe UI", 9, "bold"))
        strength_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Strength slider
        strength_scale = ttk.Scale(noise_frame, from_=0.1, to=1.0, length=550,
                                variable=noise_strength, 
                                command=lambda v: strength_value_label.config(
                                    text=f"{float(v):.1f}"))
        strength_scale.pack(fill=tk.X, pady=(5, 0))
        
        # Store variables for saving
        audio_frame.noise_enabled = noise_enabled
        audio_frame.noise_strength = noise_strength
        
        return audio_frame
    
    def create_chatbot_settings_tab(self, notebook):
        """Create the chatbot settings tab"""
        chatbot_frame = ttk.Frame(notebook, padding=15)
        
        # Enabled setting
        enabled_frame = ttk.LabelFrame(chatbot_frame, text="Chatbot Input", padding=10)
        enabled_frame.pack(fill=tk.X, pady=(0, 15))
        
        chatbot_enabled = tk.BooleanVar(value=self.app.config["chatbot_input"]["enabled"])
        chatbot_check = ttk.Checkbutton(enabled_frame, text="Enable Chatbot Input", 
                                      variable=chatbot_enabled)
        chatbot_check.pack(anchor="w")
        
        enabled_desc = ttk.Label(enabled_frame, 
                              text="When enabled, transcribed text will be sent to configured chatbots automatically.",
                              font=("Segoe UI", 9), wraplength=550)
        enabled_desc.pack(anchor="w", pady=(5, 0))
        
        # Fast mode setting
        fast_frame = ttk.LabelFrame(chatbot_frame, text="Fast Mode", padding=10)
        fast_frame.pack(fill=tk.X, pady=(0, 15))
        
        fast_mode = tk.BooleanVar(value=self.app.config["chatbot_input"].get("fast_mode", True))
        fast_check = ttk.Checkbutton(fast_frame, text="Enable Fast Mode", 
                                   variable=fast_mode)
        fast_check.pack(anchor="w")
        
        fast_desc = ttk.Label(fast_frame, 
                           text="Fast mode skips confirmations and sends text directly to chatbots.",
                           font=("Segoe UI", 9), wraplength=550)
        fast_desc.pack(anchor="w", pady=(5, 0))
        
        # Delay settings
        delay_frame = ttk.LabelFrame(chatbot_frame, text="Timing Settings", padding=10)
        delay_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Input delay
        input_delay = tk.DoubleVar(
            value=self.app.config["chatbot_input"]["delay_between_inputs"])
        
        delay_label_frame = ttk.Frame(delay_frame)
        delay_label_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(delay_label_frame, text="Delay between inputs (seconds):", 
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        delay_value_label = ttk.Label(delay_label_frame, text=f"{input_delay.get():.1f}", 
                                    font=("Segoe UI", 9, "bold"))
        delay_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Delay slider
        delay_scale = ttk.Scale(delay_frame, from_=0.1, to=3.0, length=550,
                              variable=input_delay, 
                              command=lambda v: delay_value_label.config(text=f"{float(v):.1f}"))
        delay_scale.pack(fill=tk.X)
        
        # Mouse speed
        mouse_speed = tk.DoubleVar(
            value=self.app.config["chatbot_input"]["mouse_speed"])
        
        speed_label_frame = ttk.Frame(delay_frame)
        speed_label_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(speed_label_frame, text="Mouse movement speed (seconds):", 
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        speed_value_label = ttk.Label(speed_label_frame, text=f"{mouse_speed.get():.1f}", 
                                    font=("Segoe UI", 9, "bold"))
        speed_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Speed slider
        speed_scale = ttk.Scale(delay_frame, from_=0.05, to=1.0, length=550,
                              variable=mouse_speed, 
                              command=lambda v: speed_value_label.config(text=f"{float(v):.2f}"))
        speed_scale.pack(fill=tk.X)
        
        # Calibration button
        cal_frame = ttk.LabelFrame(chatbot_frame, text="Calibration", padding=10)
        cal_frame.pack(fill=tk.X)
        
        cal_desc = ttk.Label(cal_frame, 
                          text="Calibrate the screen coordinates for each chatbot. You'll need to position each chatbot window before calibration.",
                          font=("Segoe UI", 9), wraplength=550)
        cal_desc.pack(anchor="w", pady=(0, 10))
        
        cal_btn = ttk.Button(cal_frame, text="Calibrate Chatbot Coordinates", 
                          command=self.calibrate_chatbots)
        cal_btn.pack(fill=tk.X)
        
        # Store variables for saving
        chatbot_frame.chatbot_enabled = chatbot_enabled
        chatbot_frame.fast_mode = fast_mode
        chatbot_frame.input_delay = input_delay
        chatbot_frame.mouse_speed = mouse_speed
        
        return chatbot_frame
    
    def create_profiles_tab(self, notebook):
        """Create the profiles management tab"""
        profiles_frame = ttk.Frame(notebook, padding=15)
        
        # Profiles explanation
        desc_label = ttk.Label(profiles_frame, 
                            text="Profiles allow you to save different chatbot configurations for different window arrangements. Create a profile after you've calibrated your chatbot positions.",
                            font=("Segoe UI", 9), wraplength=550)
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Current profiles section
        profiles_list_frame = ttk.LabelFrame(profiles_frame, text="Saved Profiles", padding=10)
        profiles_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Get existing profiles
        existing_profiles = list(self.app.config["chatbot_input"].get("profiles", {}).keys())
        
        if existing_profiles:
            # Create a listbox for profiles
            profiles_container = ttk.Frame(profiles_list_frame)
            profiles_container.pack(fill=tk.BOTH, expand=True)
            
            profiles_listbox = tk.Listbox(profiles_container, font=("Segoe UI", 10),
                                       height=6, selectmode=tk.SINGLE)
            profiles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(profiles_container, command=profiles_listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            profiles_listbox.config(yscrollcommand=scrollbar.set)
            
            # Populate the listbox
            for profile in existing_profiles:
                profiles_listbox.insert(tk.END, profile)
            
            # Buttons for profile actions
            btn_frame = ttk.Frame(profiles_list_frame)
            btn_frame.pack(fill=tk.X)
            
            load_btn = ttk.Button(btn_frame, text="Load", width=12,
                               command=lambda: self._load_profile(profiles_listbox))
            load_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            delete_btn = ttk.Button(btn_frame, text="Delete", width=12,
                                 command=lambda: self._delete_profile(profiles_listbox))
            delete_btn.pack(side=tk.LEFT)
            
            # Store the listbox for later use
            profiles_frame.profiles_listbox = profiles_listbox
        else:
            # No profiles message
            no_profiles_label = ttk.Label(profiles_list_frame, 
                                       text="No profiles have been saved yet.",
                                       font=("Segoe UI", 10))
            no_profiles_label.pack(pady=20)
        
        # Create new profile section
        new_profile_frame = ttk.LabelFrame(profiles_frame, text="Create New Profile", padding=10)
        new_profile_frame.pack(fill=tk.X)
        
        # Profile name entry
        name_frame = ttk.Frame(new_profile_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(name_frame, text="Profile Name:", 
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        profile_name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=profile_name_var, width=30)
        name_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Save button
        save_profile_btn = ttk.Button(new_profile_frame, text="Save Current Configuration as Profile", 
                                    command=lambda: self._save_profile(profile_name_var))
        save_profile_btn.pack(fill=tk.X)
        
        # Store variables
        profiles_frame.profile_name_var = profile_name_var
        
        return profiles_frame
    
    def create_advanced_settings_tab(self, notebook):
        """Create the advanced settings tab"""
        advanced_frame = ttk.Frame(notebook, padding=15)
        
        # Warning label
        warning_label = ttk.Label(advanced_frame, 
                               text="Advanced settings should only be modified if you understand their effects.",
                               font=("Segoe UI", 9, "bold"), foreground="#ff0000", wraplength=550)
        warning_label.pack(anchor="w", pady=(0, 15))
        
        # Config file location
        config_frame = ttk.LabelFrame(advanced_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        config_path = os.path.abspath(self.app.config_path if hasattr(self.app, 'config_path') else "config.json")
        config_label = ttk.Label(config_frame, text=f"Config file: {config_path}", 
                              font=("Segoe UI", 9), wraplength=550)
        config_label.pack(anchor="w")
        
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Open config button
        open_config_btn = ttk.Button(btn_frame, text="Open Config File", 
                                  command=lambda: os.startfile(config_path) if os.path.exists(config_path) else None)
        open_config_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Reload config button
        reload_config_btn = ttk.Button(btn_frame, text="Reload Config", 
                                    command=self._reload_config)
        reload_config_btn.pack(side=tk.LEFT)
        
        # Recording quality section
        quality_frame = ttk.LabelFrame(advanced_frame, text="Recording Quality", padding=10)
        quality_frame.pack(fill=tk.X, pady=(0, 15))
        
        quality_var = tk.StringVar(value=self.app.config["recording"]["quality"])
        
        ttk.Radiobutton(quality_frame, text="High (Better quality, more resource usage)", 
                     variable=quality_var, value="high").pack(anchor="w")
        ttk.Radiobutton(quality_frame, text="Medium (Balanced option)", 
                     variable=quality_var, value="medium").pack(anchor="w")
        ttk.Radiobutton(quality_frame, text="Low (Less resource usage, lower quality)", 
                     variable=quality_var, value="low").pack(anchor="w")
        
        # Silence detection section
        silence_frame = ttk.LabelFrame(advanced_frame, text="Silence Detection", padding=10)
        silence_frame.pack(fill=tk.X)
        
        silence_desc = ttk.Label(silence_frame, 
                              text="Configure automatic stop when silence is detected.",
                              font=("Segoe UI", 9), wraplength=550)
        silence_desc.pack(anchor="w", pady=(0, 10))
        
        # Threshold setting
        threshold_frame = ttk.Frame(silence_frame)
        threshold_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(threshold_frame, text="Silence Threshold:", 
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        threshold_var = tk.DoubleVar(value=self.app.config["recording"]["silence_threshold"])
        threshold_label = ttk.Label(threshold_frame, text=f"{threshold_var.get():.3f}", 
                                 font=("Segoe UI", 9, "bold"))
        threshold_label.pack(side=tk.LEFT, padx=(5, 0))
        
        threshold_scale = ttk.Scale(silence_frame, from_=0.001, to=0.1, length=550,
                                 variable=threshold_var, 
                                 command=lambda v: threshold_label.config(text=f"{float(v):.3f}"))
        threshold_scale.pack(fill=tk.X)
        
        # Duration setting
        duration_frame = ttk.Frame(silence_frame)
        duration_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(duration_frame, text="Silence Duration (seconds):", 
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        duration_var = tk.DoubleVar(value=self.app.config["recording"]["silence_duration"])
        duration_label = ttk.Label(duration_frame, text=f"{duration_var.get():.1f}", 
                                font=("Segoe UI", 9, "bold"))
        duration_label.pack(side=tk.LEFT, padx=(5, 0))
        
        duration_scale = ttk.Scale(silence_frame, from_=0.5, to=5.0, length=550,
                                variable=duration_var, 
                                command=lambda v: duration_label.config(text=f"{float(v):.1f}"))
        duration_scale.pack(fill=tk.X)
        
        # Store variables for saving
        advanced_frame.quality_var = quality_var
        advanced_frame.threshold_var = threshold_var
        advanced_frame.duration_var = duration_var
        
        return advanced_frame
    
    def _select_device_thread(self, label):
        """Thread for device selection"""
        try:
            self.app.select_device()
            # Update label with new device
            if hasattr(self.app, 'config') and 'audio' in self.app.config:
                device_name = self.app.config["audio"].get("device_name", "Default Device")
                self.root.after(0, lambda: label.config(text=f"Current: {device_name}"))
                self.log(f"Audio device changed to: {device_name}")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.log(f"Error selecting audio device: {str(e)}")
    
    def _test_microphone(self):
        """Test the microphone by recording a short sample"""
        try:
            self.log("Testing microphone...")
            self.set_status("Testing microphone...", "🎙️")
            
            # Record for 3 seconds to test
            if hasattr(self.app, 'start_recording') and hasattr(self.app, 'stop_recording'):
                # Show progress bar
                self.root.after(0, lambda: self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5)))
                self.root.update_idletasks()
                
                # Start recording
                self.app.recording = True
                self.app._record_audio()
                
                # Start level meter updates
                self.root.after(0, self.update_level_display)
                
                # Wait 3 seconds
                time.sleep(3)
                
                # Stop recording
                self.app.stop_recording()
                
                # Hide progress bar
                self.root.after(0, lambda: self.progress_bar.pack_forget())
                self.root.update_idletasks()
                
                self.log("Microphone test completed")
                self.set_status("Mic test complete", "✅")
            else:
                self.log("Microphone test function not available")
                self.set_status("Test unavailable", "⚠️")
        except Exception as e:
            self.log(f"Microphone test error: {str(e)}")
            self.set_status("Test failed", "❌")
            self.root.after(0, lambda: self.progress_bar.pack_forget())
    
    def _update_gain_label(self, value, label):
        """Update gain label when slider is moved"""
        rounded = round(value, 1)
        label.config(text=f"Gain: {rounded:.1f}")
    
    def _save_all_settings(self, window):
        """Save all settings from all tabs"""
        try:
            # Get the notebook widget
            notebook = None
            for child in window.winfo_children():
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.Notebook):
                        notebook = grandchild
                        break
            
            if not notebook:
                messagebox.showerror("Error", "Could not find settings notebook")
                return
            
            # Get the tab frames
            tabs = notebook.tabs()
            
            # Audio tab settings
            audio_frame = notebook.nametowidget(tabs[0])
            if hasattr(audio_frame, 'noise_enabled') and hasattr(audio_frame, 'noise_strength'):
                self.app.config["audio"]["gain"] = round(self.gain_var.get(), 1)
                self.app.config["audio"]["noise_reduction"]["enabled"] = audio_frame.noise_enabled.get()
                self.app.config["audio"]["noise_reduction"]["strength"] = round(audio_frame.noise_strength.get(), 1)
            
            # Chatbot tab settings
            chatbot_frame = notebook.nametowidget(tabs[1])
            if (hasattr(chatbot_frame, 'chatbot_enabled') and 
                hasattr(chatbot_frame, 'fast_mode') and
                hasattr(chatbot_frame, 'input_delay') and
                hasattr(chatbot_frame, 'mouse_speed')):
                self.app.config["chatbot_input"]["enabled"] = chatbot_frame.chatbot_enabled.get()
                self.app.config["chatbot_input"]["fast_mode"] = chatbot_frame.fast_mode.get()
                self.app.config["chatbot_input"]["delay_between_inputs"] = round(chatbot_frame.input_delay.get(), 1)
                self.app.config["chatbot_input"]["mouse_speed"] = round(chatbot_frame.mouse_speed.get(), 2)
            
            # Profiles tab - nothing to save directly
            
            # Advanced tab settings
            advanced_frame = notebook.nametowidget(tabs[3])
            if (hasattr(advanced_frame, 'quality_var') and 
                hasattr(advanced_frame, 'threshold_var') and
                hasattr(advanced_frame, 'duration_var')):
                self.app.config["recording"]["quality"] = advanced_frame.quality_var.get()
                self.app.config["recording"]["silence_threshold"] = round(advanced_frame.threshold_var.get(), 3)
                self.app.config["recording"]["silence_duration"] = round(advanced_frame.duration_var.get(), 1)
            
            # Save config to file
            config_path = self.app.config_path if hasattr(self.app, 'config_path') else "config.json"
            with open(config_path, "w") as f:
                json.dump(self.app.config, f, indent=4)
            
            self.log("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully!")
            window.destroy()
        except Exception as e:
            self.log(f"Error saving settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def _load_profile(self, listbox):
        """Load a selected profile"""
        try:
            # Get selected profile
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showinfo("Info", "Please select a profile first")
                return
            
            profile_name = listbox.get(selected_indices[0])
            
            # Check if profile exists
            if profile_name not in self.app.config["chatbot_input"].get("profiles", {}):
                messagebox.showerror("Error", f"Profile '{profile_name}' not found")
                return
            
            # Confirm load
            confirm = messagebox.askyesno("Confirm", 
                                       f"Load profile '{profile_name}'? This will replace your current chatbot coordinates.")
            if not confirm:
                return
            
            # Load profile
            profile_data = self.app.config["chatbot_input"]["profiles"][profile_name]
            self.app.config["chatbot_input"]["coordinates"] = profile_data
            
            # Save config to file
            config_path = self.app.config_path if hasattr(self.app, 'config_path') else "config.json"
            with open(config_path, "w") as f:
                json.dump(self.app.config, f, indent=4)
            
            self.log(f"Loaded profile: {profile_name}")
            messagebox.showinfo("Success", f"Profile '{profile_name}' loaded successfully!")
            
            # Update chatbot count
            self.update_chatbot_count()
            
        except Exception as e:
            self.log(f"Error loading profile: {str(e)}")
            messagebox.showerror("Error", f"Failed to load profile: {str(e)}")
    
    def _delete_profile(self, listbox):
        """Delete a selected profile"""
        try:
            # Get selected profile
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showinfo("Info", "Please select a profile first")
                return
            
            profile_name = listbox.get(selected_indices[0])
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm", 
                                       f"Delete profile '{profile_name}'? This cannot be undone.")
            if not confirm:
                return
            
            # Delete profile
            if "profiles" in self.app.config["chatbot_input"]:
                if profile_name in self.app.config["chatbot_input"]["profiles"]:
                    del self.app.config["chatbot_input"]["profiles"][profile_name]
                    
                    # Save config to file
                    config_path = self.app.config_path if hasattr(self.app, 'config_path') else "config.json"
                    with open(config_path, "w") as f:
                        json.dump(self.app.config, f, indent=4)
                    
                    # Remove from listbox
                    listbox.delete(selected_indices[0])
                    
                    self.log(f"Deleted profile: {profile_name}")
                    messagebox.showinfo("Success", f"Profile '{profile_name}' deleted successfully!")
                else:
                    messagebox.showerror("Error", f"Profile '{profile_name}' not found")
            else:
                messagebox.showerror("Error", "No profiles exist")
            
        except Exception as e:
            self.log(f"Error deleting profile: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete profile: {str(e)}")
    
    def _save_profile(self, name_var):
        """Save current configuration as a new profile"""
        try:
            profile_name = name_var.get().strip()
            
            if not profile_name:
                messagebox.showinfo("Info", "Please enter a profile name")
                return
            
            # Check if profile already exists
            if profile_name in self.app.config["chatbot_input"].get("profiles", {}):
                confirm = messagebox.askyesno("Confirm", 
                                          f"Profile '{profile_name}' already exists. Overwrite?")
                if not confirm:
                    return
            
            # Make sure profiles dict exists
            if "profiles" not in self.app.config["chatbot_input"]:
                self.app.config["chatbot_input"]["profiles"] = {}
            
            # Save current coordinates as profile
            self.app.config["chatbot_input"]["profiles"][profile_name] = \
                self.app.config["chatbot_input"]["coordinates"]
            
            # Save config to file
            config_path = self.app.config_path if hasattr(self.app, 'config_path') else "config.json"
            with open(config_path, "w") as f:
                json.dump(self.app.config, f, indent=4)
            
            self.log(f"Saved profile: {profile_name}")
            messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully!")
            
            # Clear the entry
            name_var.set("")
            
        except Exception as e:
            self.log(f"Error saving profile: {str(e)}")
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def _reload_config(self):
        """Reload configuration from file"""
        try:
            if hasattr(self.app, 'load_config'):
                self.app.config = self.app.load_config()
                self.log("Configuration reloaded from file")
                messagebox.showinfo("Success", "Configuration reloaded successfully!")
                
                # Update chatbot count
                self.update_chatbot_count()
            else:
                self.log("Reload config function not available")
                messagebox.showinfo("Info", "Reload function not available")
        except Exception as e:
            self.log(f"Error reloading config: {str(e)}")
            messagebox.showerror("Error", f"Failed to reload configuration: {str(e)}")
    
    def on_settings_closed(self, window):
        """Called when settings window is closed"""
        self.settings_menu = None
        window.destroy()
    
    def on_closing(self):
        """Called when main window is closed"""
        # Restore original print function
        import builtins
        builtins.print = self.original_print
        
        # Save configuration
        try:
            config_path = self.app.config_path if hasattr(self.app, 'config_path') else "config.json"
            with open(config_path, "w") as f:
                json.dump(self.app.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config on exit: {e}")
        
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