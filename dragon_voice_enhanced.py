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
import pyautogui
import logging
import pyaudio
import audioop

# Disable PyAutoGUI failsafe to allow moving to any screen coordinates
pyautogui.FAILSAFE = False

class ModernButton(ttk.Button):
    """Custom styled button with hover effect"""
    def __init__(self, master=None, **kwargs):
        self.style_name = kwargs.pop('style_name', 'ModernButton.TButton')
        super().__init__(master, style=self.style_name, **kwargs)

class RecordButton(tk.Button):
    """Custom button specifically for recording"""
    def __init__(self, master=None, **kwargs):
        self.command = kwargs.pop('command', None)
        super().__init__(
            master, 
            bg="#d32f2f", 
            fg="white", 
            activebackground="#b71c1c", 
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
            **kwargs
        )
        
        if self.command:
            self.config(command=self.command)
        
        # Add hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        """When mouse enters the button"""
        self.config(bg="#b71c1c")
    
    def _on_leave(self, e):
        """When mouse leaves the button"""
        self.config(bg="#d32f2f")
    
    def set_recording_state(self, is_recording):
        """Update button appearance based on recording state"""
        if is_recording:
            self.config(
                bg="#9e9d24", 
                activebackground="#827717",
                text="Recording... (Space to stop)"
            )
        else:
            self.config(
                bg="#d32f2f", 
                activebackground="#b71c1c",
                text="Record (Space)"
            )
            
class GreenButton(tk.Button):
    """Custom green button for sending text"""
    def __init__(self, master=None, **kwargs):
        self.command = kwargs.pop('command', None)
        super().__init__(
            master, 
            bg="#4CAF50",  # Green background
            fg="white",  # White text
            activebackground="#388E3C",  # Darker green on hover
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
            **kwargs
        )
        
        if self.command:
            self.config(command=self.command)
        
        # Add hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        """When mouse enters the button"""
        self.config(bg="#388E3C")  # Darker green
    
    def _on_leave(self, e):
        """When mouse leaves the button"""
        self.config(bg="#4CAF50")  # Original green
    
class DragonVoiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragon Voice A")
        self.root.geometry("600x750")
        self.root.minsize(600, 750)
        
        # Recording state tracking
        self.recording_active = False
        self.record_button = None
        
        # Text input focused flag
        self.text_input_focused = False
        
        # Sending flag to prevent multiple send operations
        self.sending_in_progress = False
        
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
        
        # Set up periodic check to ensure shortcuts are bound to new widgets
        self.root.after(1000, self.refresh_shortcuts)
    
    def refresh_shortcuts(self):
        """Periodically refresh shortcuts binding to catch any new widgets"""
        self.bind_space_to_widgets(self.root)
        # Schedule next check
        self.root.after(1000, self.refresh_shortcuts)
    
    def bind_space_to_widgets(self, parent):
        """Recursively bind space key to all widgets"""
        for child in parent.winfo_children():
            # Skip text widgets which need space for typing
            if not isinstance(child, tk.Text) and not isinstance(child, scrolledtext.ScrolledText):
                child.bind('<space>', lambda e: self.toggle_recording())
            # For text widgets, only allow spaces when deliberately focused
            elif not hasattr(self, 'text_input') or child != self.text_input:
                # For other text fields, not our main text input
                child.bind('<space>', lambda e: self.handle_text_input_space(e))
            
            # Recursively bind to children
            if child.winfo_children():
                self.bind_space_to_widgets(child)
    
    def bind_shortcuts(self):
        """Set up all keyboard shortcuts"""
        # Use Space to toggle recording on/off when the root window has focus
        # and the text input doesn't
        self.root.bind('<space>', self.handle_global_space)

        # Bind space key to all existing widgets (except text input initially)
        self.bind_space_to_widgets(self.root)
        
        # Use Enter to send to chatbots
        self.root.bind('<Return>', lambda e: self.send_to_chatbots())
        
        self.root.bind('<F10>', lambda e: self.quick_mode())
        self.root.bind('<F11>', lambda e: self.retry_failed())
        self.root.bind('<F12>', lambda e: self.open_settings())
        self.root.bind('<Control-v>', lambda e: self.paste_from_clipboard())
        
        # Add more keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.open_settings())
        self.root.bind('<Control-c>', lambda e: self.calibrate_chatbots())
        self.root.bind('<Control-r>', lambda e: self.toggle_recording())
        self.root.bind('<Control-q>', lambda e: self.quick_mode())
        self.root.bind('<Escape>', lambda e: self.on_closing())
    
    def toggle_recording(self):
        """Toggle recording on and off when space is pressed"""
        if self.recording_active:
            # Stop recording
            self.recording_active = False
            if isinstance(self.record_button, RecordButton):
                self.record_button.set_recording_state(False)
            elif self.record_button:
                self.record_button.config(text="Record (Space)")
            self.log("Recording stopped (Space key pressed)")
        else:
            # Start recording
            self.log("Starting recording (Space key pressed)")
            self.recording_active = True
            # Update button text
            if isinstance(self.record_button, RecordButton):
                self.record_button.set_recording_state(True)
            elif self.record_button:
                self.record_button.config(text="Recording... (Press Space to stop)")
            # Create a thread for recording
            recording_thread = threading.Thread(target=self._record_thread, daemon=True)
            recording_thread.start()
            
            # Start updating level display
            self.update_level_display()
        
        # Return "break" to prevent the space from being processed further
        return "break"
    
    def handle_text_input_space(self, event):
        """Handle space key in text box - only allow spaces when focused"""
        # Use our focused flag to determine if space should add text
        if hasattr(self, 'text_input_focused') and self.text_input_focused:
            # If deliberately focused, allow normal space behavior
            return None
        else:
            # Toggle recording instead if not focused
            self.toggle_recording()
            return "break"  # Prevents the default space behavior
    
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
        
        # Create record card frame
        record_card = ttk.Frame(buttons_container, style="Card.TFrame")
        record_card.columnconfigure(1, weight=1)
        record_card.grid(row=0, column=0, padx=(0, 5), pady=(0, 10), sticky="nsew")
        
        # Icon
        icon_label = ttk.Label(record_card, text="🎙️", style="CardIcon.TLabel")
        icon_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(record_card, text="Record Voice", style="CardTitle.TLabel")
        title_label.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(10, 0))
        
        # Description
        desc_label = ttk.Label(record_card, text="Press Space to start/stop recording", style="CardDesc.TLabel")
        desc_label.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 10))
        
        # Separator
        separator = ttk.Separator(record_card, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Colored record button
        self.record_button = RecordButton(record_card, text="Record (Space)", command=self.start_recording)
        self.record_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Quick Mode card
        quick_card = self.create_card(buttons_container,
                                    "Quick Mode",
                                    "Record and send to all chatbots",
                                    "⚡",
                                    lambda: self.quick_mode(),
                                    "Quick Mode (F10)")
        quick_card.grid(row=0, column=1, padx=(5, 0), pady=(0, 10), sticky="nsew")
        
        # Add text input box
        self.create_text_input_area()
    
    def create_text_input_area(self):
        """Create a text input area for typing messages"""
        input_frame = ttk.LabelFrame(self.main_container, text="Text Input", padding=(10, 5))
        input_frame.pack(fill=tk.X, expand=False, padx=15, pady=(0, 10))
        
        # Create a text entry with scrollbar
        text_input_container = ttk.Frame(input_frame)
        text_input_container.pack(fill=tk.X, expand=True, pady=(0, 5))
        
        self.text_input = scrolledtext.ScrolledText(text_input_container, height=3, 
                                               wrap=tk.WORD, font=("Segoe UI", 10))
        self.text_input.pack(fill=tk.X, expand=True)
        
        # Bind Enter key in the text input to send (Shift+Enter for new line)
        self.text_input.bind("<Return>", self.handle_text_input_enter)
        self.text_input.bind("<Shift-Return>", self.handle_text_input_shift_enter)
        
        # Prevent space key from adding spaces unless focused
        self.text_input.bind("<space>", self.handle_text_input_space)
        
        # Handle focus events
        self.text_input.bind("<FocusIn>", self.handle_text_focus_in)
        self.text_input.bind("<FocusOut>", self.handle_text_focus_out)
        
        # Create buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, expand=True)
        
        clear_btn = ttk.Button(btn_frame, text="Clear",
                             command=lambda: self.text_input.delete(1.0, tk.END), 
                             width=8)
        clear_btn.pack(side=tk.LEFT)
        
        # Use the custom GreenButton instead of ttk.Button for better styling
        send_btn = GreenButton(btn_frame, text="Send to Chatbots (Enter)",
                           command=self.send_text_to_chatbots,
                           width=25)
        send_btn.pack(side=tk.RIGHT)
    
    def handle_text_input_enter(self, event):
        """Handle Enter key in text input box"""
        self.send_text_to_chatbots()
        return "break"  # Prevents the default behavior (newline)
    
    def handle_text_input_shift_enter(self, event):
        """Handle Shift+Enter to insert new line in text box"""
        # Allow default behavior (newline)
        return None
    
    def handle_text_focus_in(self, event):
        """When text input gets focus, ensure any ongoing recording is stopped"""
        if self.recording_active:
            self.recording_active = False
            if isinstance(self.record_button, RecordButton):
                self.record_button.set_recording_state(False)
            else:
                self.record_button.config(text="Record (Space)")
            self.log("Recording stopped (text input focused)")
        
        # Set a flag to indicate the text box is deliberately focused
        self.text_input_focused = True
    
    def handle_text_focus_out(self, event):
        """When text input loses focus, update state"""
        # Clear the focus flag
        self.text_input_focused = False
        # Re-bind space in text input to toggle recording if focus is lost
        self.text_input.bind("<space>", self.handle_text_input_space_when_not_focused)

    def handle_text_input_space_when_not_focused(self, event):
        """Handle space key in text box only when it's NOT focused."""
        # This should only be active when the text box *doesn't* have focus
        # but somehow still receives the event. In this case, toggle recording.
        if not self.text_input_focused:
            self.toggle_recording()
            return "break" # Prevent default space behavior
        # If it somehow gets here while focused, allow normal space
        return None

    def handle_global_space(self, event):
        """Handle space key pressed when the main window has focus but not the text input."""
        # Check if the text input has focus
        if self.root.focus_get() != self.text_input:
            self.toggle_recording()
            return "break" # Prevent default space behavior
        # If text input has focus, do nothing here (let its own binding handle it)
        return None

    def send_text_to_chatbots(self):
        """Send text from input box to chatbots"""
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            self.log(f"Sending text to chatbots: {text[:50]}..." if len(text) > 50 else f"Sending text to chatbots: {text}")
            self.app.last_transcription = text
            
            # Minimize the window before sending to chatbots
            self.log("Minimizing Dragon Voice A window before sending to chatbots")
            self.root.iconify()  # Minimize the window
            self.root.update_idletasks()
            time.sleep(0.5)  # Give time for window to minimize
            
            # Create a thread for sending
            sending_thread = threading.Thread(target=self._send_thread, daemon=True)
            sending_thread.start()
            
            # Clear the input after sending
            self.text_input.delete(1.0, tk.END)
        else:
            self.log("No text to send")
    
    def send_to_chatbots(self):
        """Send current transcription to chatbots (Enter key shortcut)"""
        if hasattr(self.app, 'last_transcription') and self.app.last_transcription:
            # Create a thread for sending
            sending_thread = threading.Thread(target=self._send_thread, daemon=True)
            sending_thread.start()
        else:
            self.log("No text available to send to chatbots")
    
    def _send_thread(self):
        """Thread for sending to chatbots"""
        try:
            # Check if sending is already in progress
            if self.sending_in_progress:
                self.log("Send operation already in progress")
                return
                
            # Set flag to prevent multiple sends
            self.sending_in_progress = True
            
            # Check if this is from a voice command for special handling
            is_voice_command = False
            if hasattr(self.app, 'from_voice_command') and self.app.from_voice_command:
                is_voice_command = True
                self.log("Using voice command reliability mode")
                
            self.set_status("Sending to chatbots...", "📤")
            
            # Show progress bar
            self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
            self.root.update_idletasks()
            
            # Make sure the window is minimized (in case it wasn't already)
            if not self.root.winfo_ismapped():
                self.log("Window already minimized, proceeding with send operation")
            else:
                self.log("Minimizing window before sending to chatbots")
                self.root.iconify()  # Minimize the window
                self.root.update_idletasks()
                
                # Use longer delay for voice commands
                if is_voice_command:
                    time.sleep(0.8)  # Give more time for window to minimize
                else:
                    time.sleep(0.5)  # Standard delay
            
            # Always use the direct method with hardcoded coordinates
            try:
                # Copy text to clipboard for pasting
                if hasattr(self.app, 'last_transcription'):
                    # Add a small pause before clipboard operation
                    time.sleep(0.2)
                    
                    # Check if text exists
                    text_to_send = self.app.last_transcription
                    if not text_to_send or len(text_to_send.strip()) == 0:
                        self.log("No text available to send (empty transcription)")
                        self.set_status("Empty text to send", "⚠️")
                        return
                    
                    # Copy to clipboard with verification
                    pyperclip.copy(text_to_send)
                    
                    # Use longer wait for voice commands
                    if is_voice_command:
                        time.sleep(0.5)  # Longer wait for clipboard operations
                    else:
                        time.sleep(0.3)  # Standard wait
                    
                    # Verify clipboard content
                    clipboard_content = pyperclip.paste()
                    if clipboard_content != text_to_send:
                        self.log("Warning: Clipboard content doesn't match expected text")
                        # Try again
                        pyperclip.copy(text_to_send)
                        time.sleep(0.3)
                    
                    self.log("Text copied to clipboard, length: " + str(len(text_to_send)))
                    
                    # Special handling for voice commands - re-verify one more time and add an additional pause
                    if is_voice_command:
                        time.sleep(0.5)  # Additional stabilization delay
                        # One more verification
                        clipboard_content = pyperclip.paste()
                        if clipboard_content != text_to_send:
                            self.log("Second clipboard verification failed, trying once more")
                            pyperclip.copy(text_to_send)
                            time.sleep(0.5)
                    
                    # Click on all chatbot coordinates with special voice command flag
                    success_count = self.click_on_all_chatbots(is_voice_command)
                    
                    # Check if we were successful
                    if success_count > 0:
                        self.log(f"Sent to {success_count} chatbots via coordinates")
                        self.set_status(f"Sent to {success_count} chatbots", "✅")
                    else:
                        self.log("Failed to send to any chatbots")
                        self.set_status("Send failed", "❌")
                        
                        # Try one more time with a longer delay
                        self.log("Attempting one retry with longer delays...")
                        time.sleep(1.0)  # Wait a full second
                        pyperclip.copy(text_to_send)  # Ensure clipboard has text
                        time.sleep(0.5)
                        success_count = self.click_on_all_chatbots(True)  # Always use voice mode for retry
                        
                        if success_count > 0:
                            self.log(f"Retry succeeded: Sent to {success_count} chatbots")
                            self.set_status("Retry succeeded", "✅")
                        else:
                            self.log("Retry failed: Could not send to any chatbots")
                            self.set_status("Send failed", "❌")
                else:
                    self.log("No text available to send (no transcription)")
                    self.set_status("No text to send", "ℹ️")
            except Exception as e:
                self.log(f"Error sending text: {str(e)}")
                self.set_status("Send failed", "❌")
                
                # Restore window if there's an error
                self.root.deiconify()
            
            # Hide progress bar
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            
        except Exception as e:
            self.log(f"Error sending to chatbots: {str(e)}")
            self.set_status("Error", "🔴")
            # Hide progress bar
            self.progress_bar.pack_forget()
            
            # Restore window if there's an error
            self.root.deiconify()
        finally:
            # Reset sending flag
            self.sending_in_progress = False
            
            # Reset voice command flag if it exists
            if hasattr(self.app, 'from_voice_command'):
                self.app.from_voice_command = False
    
    def click_on_coordinates(self, coordinates):
        """Click on specific coordinates for chatbot interaction
        
        Args:
            coordinates (dict): Dictionary containing:
                - x, y: Screen coordinates to click
                - name: Optional name of the chatbot (for logging)
                - post_wait: Optional seconds to wait after clicking (default: 0.5)
                - press_enter: Optional boolean to control if Enter is pressed (default: True)
                - key_press: Optional string or list of strings for custom key press:
                    - String: Single key like "enter", "tab", "space"
                    - List: Key combination like ["ctrl", "enter"] or ["shift", "enter"]
                - post_clicks: Optional list of additional clicks to perform after
                  the main click, each with x, y and optional delay
                  
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if coordinates are valid
            if not coordinates or 'x' not in coordinates or 'y' not in coordinates:
                self.log("Invalid coordinates provided")
                return False
            
            # Log the action
            name = coordinates.get('name', 'Unnamed chatbot')
            self.log(f"Clicking on coordinates for {name} at x={coordinates['x']}, y={coordinates['y']}")
            
            # Ensure coordinates are within screen bounds if possible
            try:
                screen_width, screen_height = pyautogui.size()
                x = max(0, min(coordinates['x'], screen_width-1)) if coordinates['x'] >= 0 else coordinates['x']
                y = max(0, min(coordinates['y'], screen_height-1)) if coordinates['y'] >= 0 else coordinates['y']
            except Exception as e:
                # If there's any error, use the original coordinates
                x, y = coordinates['x'], coordinates['y']
            
            # Add a slight delay before moving to ensure system is ready
            time.sleep(0.2)
            
            # Move mouse to coordinates and click - use a slower duration for more reliability
            pyautogui.moveTo(x, y, duration=0.3)
            time.sleep(0.1)  # Brief pause before clicking
            pyautogui.click()
            
            # Longer delay to ensure focus
            time.sleep(0.3)
            
            # Paste text (Ctrl+V)
            pyautogui.hotkey('ctrl', 'v')
            
            # Increased delay after paste
            time.sleep(0.3)
            
            # Handle submit key(s)
            if 'key_press' in coordinates:
                # Handle specific keys or key combinations
                key_press = coordinates['key_press']
                if isinstance(key_press, str):
                    # Single key
                    self.log(f"Pressing {key_press} for {name}")
                    pyautogui.press(key_press)
                elif isinstance(key_press, list):
                    # Key combination (hotkey)
                    self.log(f"Pressing key combination {'+'.join(key_press)} for {name}")
                    pyautogui.hotkey(*key_press)
            elif coordinates.get('press_enter', True):
                # Default behavior: press Enter
                self.log(f"Pressing Enter for {name}")
                pyautogui.press('enter')
            
            # Wait after click if specified
            post_wait = coordinates.get('post_wait', 0.8)  # Increased default wait time
            time.sleep(post_wait)
            
            # Handle any post-clicks if specified
            if 'post_clicks' in coordinates and coordinates['post_clicks']:
                for post_click in coordinates['post_clicks']:
                    if 'x' in post_click and 'y' in post_click:
                        # Wait before post-click if specified
                        if 'delay' in post_click:
                            time.sleep(post_click['delay'])
                        else:
                            time.sleep(0.5)  # Default delay for post-clicks
                        
                        self.log(f"Performing post-click at x={post_click['x']}, y={post_click['y']}")
                        
                        # Apply same screen bounds check for post-clicks
                        try:
                            screen_width, screen_height = pyautogui.size()
                            post_x = max(0, min(post_click['x'], screen_width-1)) if post_click['x'] >= 0 else post_click['x']
                            post_y = max(0, min(post_click['y'], screen_height-1)) if post_click['y'] >= 0 else post_click['y']
                        except Exception as e:
                            post_x, post_y = post_click['x'], post_click['y']
                        
                        # Use slower movement for post-clicks as well
                        pyautogui.moveTo(post_x, post_y, duration=0.3)
                        time.sleep(0.1)  # Brief pause
                        pyautogui.click()
                        time.sleep(0.3)  # Wait after click
            
            return True
            
        except Exception as e:
            self.log(f"Error clicking on coordinates: {str(e)}")
            return False
    
    def click_on_all_chatbots(self, is_voice_command=False):
        """Click on all chatbot coordinates in the config"""
        # Use hardcoded coordinates directly instead of loading from config
        coordinates_list = [
            {
                "name": "Anara",
                "x": -1797,
                "y": -222,
                "post_wait": 0.5
            },
            {
                "name": "Answerr",
                "x": -1810,
                "y": 254,
                "post_wait": 0.5
            },
            {
                "name": "Generic Bot",
                "x": -1091,
                "y": -193,
                "post_wait": 0.5
            },
            {
                "name": "Abacus.AI (Claude Sonnet 3.7)",
                "x": -1166,
                "y": 244,
                "post_wait": 0.5,
                "key_press": "enter"
            },
            {
                "name": "ChatGPT 4.5",
                "x": -498,
                "y": -258,
                "post_clicks": [
                    {"x": -41, "y": -207, "delay": 1.0}
                ],
                "post_wait": 0.5,
                "press_enter": False
            },
            {
                "name": "Robert Lab (ChatGPT)",
                "x": -506,
                "y": 318,
                "post_wait": 0.5,
            },
            {
                "name": "Consensus AI - Search",
                "x": 36,
                "y": -1916,
                "post_wait": 0.5
            },
            {
                "name": "ClinicalKey AI",
                "x": -456,
                "y": -1340,
                "post_wait": 0.5
            },
            {
                "name": "ChatGPT 4.5",
                "x": 41,
                "y": -1705,
                "post_clicks": [
                    {"x": 530, "y": -1669, "delay": 1.0}
                ],
                "post_wait": 0.5
            },
            {
                "name": "Otio.ai",
                "x": 73,
                "y": -1201,
                "post_clicks": [
                    {"x": 530, "y": -1172, "delay": 1.0}
                ],
                "post_wait": 0.5
            },
            {
                "name": "ChatGPT 4.5",
                "x": 701,
                "y": -1716,
                "post_clicks": [
                    {"x": 1176, "y": -1670, "delay": 1.0}
                ],
                "post_wait": 0.5
            },
            {
                "name": "ReachRx",
                "x": 741,
                "y": -1231,
                "post_wait": 0.5
            },
            {
                "name": "Grok",
                "x": 298,
                "y": 449,
                "post_wait": 0.5
            },
            {
                "name": "Robert Lab (ChatGPT)",
                "x": 169,
                "y": 1047,
                "post_wait": 0.5
            },
            {
                "name": "Concierge AI",
                "x": 823,
                "y": 462,
                "post_wait": 0.5
            },
            {
                "name": "UPDF AI",
                "x": 732,
                "y": 932,
                "post_wait": 0.5
            },
            {
                "name": "TextCortex (Zeno)",
                "x": 1375,
                "y": 420,
                "post_wait": 0.5
            },
            {
                "name": "Pathway",
                "x": 1428,
                "y": 1015,
                "post_clicks": [
                    {"x": 1862, "y": 1018, "delay": 1.0}
                ],
                "post_wait": 0.5
            },
            {
                "name": "NotebookLM (Google)",
                "x": 1465,
                "y": -826,
                "post_wait": 0.5
            },
            {
                "name": "SciSpace",
                "x": 1657,
                "y": -565,
                "post_wait": 0.5
            },
            {
                "name": "NotebookLM (Google)",
                "x": 2206,
                "y": -842,
                "post_wait": 0.5
            },
            {
                "name": "HealthUniverse (Navigator)",
                "x": 2417,
                "y": -188,
                "post_wait": 0.5
            },
            {
                "name": "AskClair AI",
                "x": 3300,
                "y": -968,
                "post_wait": 0.5
            },
            {
                "name": "Yesil Health AI",
                "x": 3927,
                "y": -79,
                "post_wait": 0.5
            },
            {
                "name": "Medical Chat Data",
                "x": 4829,
                "y": -106,
                "post_wait": 0.5
            },
            {
                "name": "ChatHub",
                "x": 6032,
                "y": -82,
                "post_wait": 0.5
            }
        ]
        
        if not coordinates_list:
            self.log("No chatbot coordinates defined")
            return 0  # Return 0 for success count
        
        # If this is coming from voice, log special mode
        if is_voice_command:
            self.log("Using voice reliability mode with longer timeouts")
        
        # Make clipboard contents available again after each click in case it gets lost
        original_clipboard = pyperclip.paste()
        text_to_send = ""
        if hasattr(self.app, 'last_transcription'):
            text_to_send = self.app.last_transcription
        
        # Click on each set of coordinates
        success_count = 0
        total_count = len(coordinates_list)
        self.log(f"Starting to send text to {total_count} chatbots")
        
        # Update progress bar to show progress through all chatbots
        self.progress_var.set(0)
        self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
        self.root.update_idletasks()
        
        try:
            for i, coords in enumerate(coordinates_list):
                # Update progress bar
                progress_percent = (i / total_count) * 100
                self.progress_var.set(progress_percent)
                self.root.update_idletasks()
                
                # Ensure clipboard has the right text before each chatbot
                if text_to_send and text_to_send != pyperclip.paste():
                    self.log("Restoring text to clipboard")
                    pyperclip.copy(text_to_send)
                    
                    # Use longer delay for voice commands
                    if is_voice_command:
                        time.sleep(0.4)  # Longer delay for voice
                    else:
                        time.sleep(0.2)  # Standard delay after clipboard operation
                
                # For voice commands, use special handling with multiple attempts if needed
                if is_voice_command and i < 3:  # Only for first 3 chatbots - they're most important
                    # Try up to 3 times for important chatbots with voice commands
                    success = False
                    for attempt in range(3):
                        if attempt > 0:
                            self.log(f"Retry attempt {attempt+1} for {coords.get('name', 'unnamed chatbot')}")
                            # Re-copy to clipboard before retry
                            pyperclip.copy(text_to_send)
                            time.sleep(0.5)
                        
                        # Click on coordinates
                        if self.click_on_coordinates(coords):
                            success = True
                            success_count += 1
                            break
                        else:
                            self.log(f"Failed to click on {coords.get('name', 'unnamed chatbot')} (attempt {attempt+1})")
                            time.sleep(0.5)  # Wait before retry
                    
                    if not success:
                        self.log(f"All attempts failed for {coords.get('name', 'unnamed chatbot')}")
                else:
                    # Standard handling for non-voice or less important chatbots
                    if self.click_on_coordinates(coords):
                        success_count += 1
                    else:
                        self.log(f"Failed to click on {coords.get('name', 'unnamed chatbot')}")
                
                # Add delay between chatbots - use a slightly longer delay for voice-originated commands
                # to improve reliability
                if is_voice_command:
                    delay = 1.0  # Even longer delay for voice commands
                else:
                    delay = 0.8  # Standard increased default delay
                
                if hasattr(self.app, 'config') and 'chatbot_input' in self.app.config:
                    config_delay = self.app.config["chatbot_input"].get("delay_between_inputs", 0.5)
                    # Use the larger of our default or configured delay
                    delay = max(delay, config_delay)
                
                # Log the delay
                self.log(f"Waiting {delay:.1f} seconds before next chatbot")
                time.sleep(delay)
            
            # Set progress to 100% when done
            self.progress_var.set(100)
            self.root.update_idletasks()
            
        except Exception as e:
            self.log(f"Error during chatbot sequence: {str(e)}")
        finally:
            # Hide progress bar
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            
            # Restore original clipboard content if needed
            if original_clipboard and original_clipboard != pyperclip.paste():
                try:
                    pyperclip.copy(original_clipboard)
                except:
                    pass
        
        self.log(f"Clicked on {success_count} out of {len(coordinates_list)} chatbots")
        
        # Return success count for potential error handling
        return success_count
    
    def create_action_buttons(self):
        """Create secondary action buttons"""
        # Secondary buttons container
        actions_container = ttk.Frame(self.main_container, padding=(15, 0))
        actions_container.pack(fill=tk.BOTH, expand=False, pady=(0, 15))
        actions_container.columnconfigure(0, weight=1)
        actions_container.columnconfigure(1, weight=1)
        actions_container.columnconfigure(2, weight=1)
        actions_container.columnconfigure(3, weight=1)  # Add a 4th column
        
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
        calibrate_card.grid(row=0, column=2, padx=5, sticky="nsew")
        
        # Test coordinates card
        test_coords_card = self.create_small_card(actions_container,
                                              "Test Coords",
                                              "🔍",
                                              lambda: self.test_coordinates())
        test_coords_card.grid(row=0, column=3, padx=(5, 0), sticky="nsew")
    
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
                                 text="Shortcuts: Space=Toggle recording, Enter=Send, F10=Quick Mode, F11=Retry, F12=Settings",
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
        style.configure("Green.TButton", background="#4CAF50", foreground="white")
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
        
        # Button - use RecordButton for the primary action (recording)
        if is_primary:
            action_btn = RecordButton(card, text=button_text, command=command)
            action_btn.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        else:
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
• Record Voice: Press Space to start recording, press again to stop. Speak clearly, and the app will transcribe your speech.
• Quick Mode: Records and sends your spoken text to all configured chatbots in one step.
• Paste Text: Sends clipboard text directly to chatbots.
• Retry Failed: Retries sending to any chatbots that failed in previous attempts.
• Calibrate: Allows you to set up the positions of chatbot windows on your screen.

KEYBOARD SHORTCUTS:
------------------
Space - Press to start/stop recording
Enter - Send to chatbots
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
        # Use the toggle_recording function
        self.toggle_recording()
    
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
                
                # Set up audio stream directly for more control
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
                    
                    # Log the recording start
                    self.log("Recording started - press Space to stop")
                    
                    # Continue recording until space is pressed again (recording_active becomes False)
                    while self.recording_active:
                        time.sleep(0.05)  # Short sleep to avoid high CPU usage
                        
                        # Update volume level meter
                        if hasattr(self.app, 'current_volume'):
                            self.update_level_meter(self.app.current_volume)
                    
                    # Log that recording is stopping due to space key press
                    self.log("Recording stopped (Space key pressed)")
                    
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
                                        
                                        # Set a flag to indicate this is from voice (for extra reliability measures)
                                        self.app.from_voice_command = True
                                        
                                        if hasattr(self.app, 'input_to_chatbots'):
                                            self.log("\nSending transcription to chatbots...")
                                            
                                            # Minimize the window before sending to chatbots
                                            self.log("Minimizing Dragon Voice A window before sending")
                                            self.root.iconify()  # Minimize the window
                                            self.root.update_idletasks()
                                            time.sleep(0.8)  # Give more time for window to minimize with voice command
                                            
                                            # Add additional wait to ensure everything is stable
                                            time.sleep(0.5)
                                            
                                            # Use our direct coordinate method instead of app's method
                                            # Copy text to clipboard for pasting with extra verification
                                            pyperclip.copy(final_text)
                                            time.sleep(0.5)  # Longer wait for clipboard with voice
                                            
                                            # Verify clipboard
                                            clip_text = pyperclip.paste()
                                            if clip_text != final_text:
                                                self.log("Warning: Clipboard verification failed, trying again")
                                                # Try again
                                                pyperclip.copy(final_text)
                                                time.sleep(0.5)
                                            
                                            self.log("Text copied to clipboard for chatbots")
                                            
                                            # Create a thread for sending to ensure UI remains responsive
                                            sending_thread = threading.Thread(target=self._send_thread, daemon=True)
                                            sending_thread.start()
                                            
                                            # IMPORTANT: Don't update status here - the sending thread will do that
                                            # Wait for the sending thread to finish properly
                                            # self.set_status("Sent to chatbots", "✅")
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
                                    text="Review the transcription below. You can edit it if needed. Press Enter to confirm.",
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
        
        # Bind Enter key to confirm (but not when Shift is held)
        def handle_enter(event):
            # Only handle if Shift is not pressed (to allow multiline in text box)
            if not event.state & 0x1:  # Check if Shift is not pressed
                on_confirm()
                return "break"
            return None
        
        # Bind Enter key to dialog and text box
        dialog.bind("<Return>", handle_enter)
        text_box.bind("<Return>", handle_enter)
        
        # Buttons at bottom
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 0))
        
        confirm_btn = ttk.Button(btn_frame, text="Confirm & Send to Chatbots (Enter)", 
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
                
                # Start recording
                self.recording_active = True
                recording_duration = 5  # Maximum recording duration in seconds
                start_time = time.time()
                
                self.log("Quick mode recording started - maximum 5 seconds (press Space to stop)")
                
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
                    self.recording_active = False
                
                # Process the transcription
                if hasattr(self.app, 'last_transcription') and self.app.last_transcription:
                    transcript_text = self.app.last_transcription
                    self.log(f"Transcribed: {transcript_text}")
                    
                    # Minimize window before sending
                    self.log("Minimizing window before sending to chatbots")
                    self.root.iconify()  # Minimize the window
                    self.root.update_idletasks()
                    time.sleep(0.5)  # Give time for window to minimize
                    
                    # Use our direct sending method instead of app's method for more reliability
                    # Add a small pause before clipboard operation
                    time.sleep(0.2)
                    
                    # Ensure the text is in clipboard
                    pyperclip.copy(transcript_text)
                    time.sleep(0.3)  # Wait for clipboard to update
                    
                    # Send to chatbots using our direct click method
                    self.log("Sending quick mode transcription to chatbots")
                    success_count = self.click_on_all_chatbots()
                    
                    if success_count > 0:
                        self.log(f"Quick mode: Sent to {success_count} chatbots")
                        self.set_status("Quick mode completed", "✅")
                    else:
                        self.log("Quick mode: Failed to send to any chatbots")
                        self.set_status("Send failed", "❌")
                        
                        # Try one more time with longer delays
                        self.log("Attempting one retry with longer delays...")
                        time.sleep(1.0)
                        pyperclip.copy(transcript_text)
                        time.sleep(0.5)
                        success_count = self.click_on_all_chatbots()
                        
                        if success_count > 0:
                            self.log(f"Quick mode retry succeeded: Sent to {success_count} chatbots")
                            self.set_status("Quick mode completed", "✅")
                        else:
                            self.log("Quick mode retry failed")
                            self.set_status("Quick mode failed", "❌")
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
            
            # Minimize the window before sending to chatbots
            self.log("Minimizing window before sending to chatbots")
            self.root.iconify()  # Minimize the window
            self.root.update_idletasks()
            time.sleep(0.5)  # Give time for window to minimize
            
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
            # Restore window if there's an error
            self.root.deiconify()
    
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
            
            # Minimize the window before sending to chatbots
            self.log("Minimizing window before retrying chatbots")
            self.root.iconify()  # Minimize the window
            self.root.update_idletasks()
            time.sleep(0.5)  # Give time for window to minimize
            
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
            # Restore window if there's an error
            self.root.deiconify()
    
    def calibrate_chatbots(self):
        """Open the chatbot calibration tool"""
        # Show a message about using hardcoded coordinates
        messagebox.showinfo(
            "Hardcoded Coordinates", 
            "This application is using hardcoded coordinates directly from the script.\n\n" +
            "To modify coordinates, you'll need to edit the script directly in the click_on_all_chatbots method."
        )
        self.log("Using hardcoded coordinates - calibration not needed")
        self.set_status("Using hardcoded coordinates", "ℹ️")
        
        # Update chatbot count
        self.update_chatbot_count()
    
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

    def test_coordinates(self):
        """Test the coordinates in the config by clicking on them"""
        # Create a thread for coordinate testing
        coords_thread = threading.Thread(target=self._test_coordinates_thread, daemon=True)
        coords_thread.start()
    
    def _test_coordinates_thread(self):
        """Thread for testing coordinates"""
        try:
            self.set_status("Testing coordinates...", "🔍")
            
            # Show progress bar
            self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 5))
            self.root.update_idletasks()
            
            # Text for testing
            test_text = "This is a coordinate test message."
            pyperclip.copy(test_text)
            self.log(f"Testing with message: {test_text}")
            
            # Click on all chatbot coordinates
            self.click_on_all_chatbots()
            
            # Hide progress bar
            self.progress_bar.pack_forget()
            self.root.update_idletasks()
            
            self.set_status("Coordinate test completed", "✅")
            
        except Exception as e:
            self.log(f"Error testing coordinates: {str(e)}")
            self.set_status("Error", "🔴")
            # Hide progress bar
            self.progress_bar.pack_forget()

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