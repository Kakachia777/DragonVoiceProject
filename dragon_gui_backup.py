import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import pyperclip
import platform

# Root window
root = tk.Tk()
root.title("Dragon Voice Assistant")
root.geometry("500x400")
root.resizable(True, True)

# Try to set the window icon
try:
    # First, check if running as executable
    if getattr(sys, 'frozen', False):
        # If running as executable, use sys._MEIPASS to locate icon
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "dragon_icon.ico")
    else:
        # If running as script, use relative path
        icon_path = "dragon_icon.ico"
        
    root.iconbitmap(icon_path)
except Exception as e:
    print(f"Could not set icon: {e}")

# App class
class DragonVoiceApp:
    def __init__(self, root):
        self.root = root
        self.recording = False
        self.audio_data = []
        self.backend_module = None
        
        # Load config to determine which backend to use
        self.load_config()
        
        # Set up the CLI backend process
        self.setup_backend()
        
        # Global configuration
        padx = 10
        pady = 8
        
        # Frame for the main content
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        # Text Input Frame (NEW)
        text_input_frame = tk.Frame(main_frame)
        text_input_frame.pack(fill=tk.X, padx=padx, pady=pady)
        
        # Label for Text Input
        tk.Label(text_input_frame, text="Text Input").pack(anchor=tk.W)
        
        # Text Input Box with scrollbar
        self.text_input = scrolledtext.ScrolledText(text_input_frame, height=4, wrap=tk.WORD)
        self.text_input.pack(fill=tk.X, expand=True, padx=0, pady=5)
        
        # Text Input Controls - using a frame for button arrangement
        input_controls = tk.Frame(text_input_frame)
        input_controls.pack(fill=tk.X, padx=0, pady=5)
        
        # Clear button
        clear_btn = tk.Button(input_controls, text="Clear", command=self.clear_text)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Submit button - green with white text
        submit_btn = tk.Button(input_controls, text="Submit", 
                              background="#4CAF50", foreground="white",  # Green with white text
                              command=self.submit_text)
        submit_btn.pack(side=tk.RIGHT, padx=2)
        
        # Recording Controls section
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, padx=padx, pady=pady)
        
        # Label for Recording section
        tk.Label(controls_frame, text="Voice Recording").pack(anchor=tk.W)
        
        # Status indicator
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.status_emoji = tk.StringVar()
        self.status_emoji.set("ðŸŽ¤")
        
        status_frame = tk.Frame(controls_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_emoji_label = tk.Label(status_frame, textvariable=self.status_emoji, font=("Arial", 16))
        self.status_emoji_label.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Activity Log
        log_frame = tk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        tk.Label(log_frame, text="Activity Log").pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)
        
        # Set the initial hint message in the log
        self.log_text.insert(tk.END, "Dragon Voice Assistant started successfully\n")
        self.log("Using configuration from: " + self.config_path)
        self.log("Hold SPACE key to record your voice")
        
        # Keyboard binding for Space key
        self.root.bind("<KeyPress-space>", self.handle_space_press)
        self.root.bind("<KeyRelease-space>", self.handle_space_release)
        
        # Function keys for various commands
        self.root.bind("<F10>", self.handle_quick_mode)  # F10 for quick mode
        self.root.bind("<F11>", self.handle_retry)       # F11 for retry failed chatbots
        self.root.bind("<F12>", self.show_settings)      # F12 for settings
        
        # Setup automatic scrolling for the log
        self.log_text.see(tk.END)
        
        # Update UI state
        self.update_ui_state()
    
    def handle_space_press(self, event=None):
        """Handler for space key press with focus check"""
        # Check if the text input box has focus - if so, don't start recording
        if event.widget == self.text_input:
            return
            
        # Otherwise start recording
        if not self.recording:
            self.start_recording()
    
    def handle_space_release(self, event=None):
        """Handler for space key release with focus check"""
        # Check if the text input box has focus - if so, don't stop recording
        if event.widget == self.text_input:
            return
            
        # Otherwise stop recording if we were recording
        if self.recording:
            self.stop_recording()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            # First check for config.json in the same directory
            self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            
            # If running as executable, check in the executable's directory
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                self.config_path = os.path.join(base_dir, "config.json")
            
            # Check if the file exists
            if not os.path.exists(self.config_path):
                # Try looking in the current working directory
                self.config_path = "config.json"
                
            # Load the config
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                
            # Determine which backend module to use based on existence
            if os.path.exists("Dragon_cli2.py"):
                self.backend_script = "Dragon_cli2.py"
            else:
                self.backend_script = "dragon_cli.py"
                
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Error loading configuration: {str(e)}")
            self.config = {}
            self.backend_script = "dragon_cli.py"  # Default
    
    def setup_backend(self):
        """Set up the backend CLI process"""
        try:
            # Get the path to the Python executable
            python_exe = sys.executable
            
            # Get the path to the backend script
            if getattr(sys, 'frozen', False):
                # If running as executable, Dragon_cli2.py should be in the same directory
                script_path = os.path.join(os.path.dirname(sys.executable), self.backend_script)
            else:
                # If running as script, use the backend script in the current directory
                script_path = self.backend_script
                
            # Create temp directory if needed
            temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            # Create a unique config path for this session
            session_id = f"_{hex(id(self))[2:]}"
            self.session_config_path = os.path.join(temp_dir, f"_ME{session_id}")
            
            # Tell the user which backend script we're using
            self.log(f"Using backend configuration from: {self.config_path}")
                
        except Exception as e:
            self.log(f"Error setting up backend: {str(e)}")
            messagebox.showerror("Backend Error", f"Error setting up backend: {str(e)}")
    
    def log(self, message):
        """Add a message to the log"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            if hasattr(self, 'log_text') and self.log_text:
                self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
                self.log_text.see(tk.END)
            else:
                # Just print to console if log_text isn't available yet
                print(f"[{timestamp}] {message}")
        except Exception as e:
            # Fallback for early logging
            print(f"[LOG] {message}")
            print(f"Logging error: {e}")
    
    def clear_text(self):
        """Clear the text input box"""
        self.text_input.delete(1.0, tk.END)
    
    def submit_text(self):
        """Submit the text from the input box"""
        # Get the text from the input box
        text = self.text_input.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showinfo("Empty Text", "Please enter some text to submit.")
            return
        
        # Log the submission
        self.log(f"Submitting text: {text[:30]}..." if len(text) > 30 else f"Submitting text: {text}")
        
        # Copy to clipboard
        pyperclip.copy(text)
        
        # Run the command to paste to all chatbots
        self.run_command(["python", self.backend_script, "--paste"])
        
        # Clear the text box after submission
        self.clear_text()
    
    def update_ui_state(self):
        """Update the UI state based on recording status"""
        if self.recording:
            self.status_var.set("Recording...")
            self.status_emoji.set("ðŸ”´")
            self.status_emoji_label.config(foreground="red")
            self.status_label.config(foreground="red")
        else:
            self.status_var.set("Ready")
            self.status_emoji.set("ðŸŽ¤")
            self.status_emoji_label.config(foreground="black")
            self.status_label.config(foreground="black")
    
    def set_status(self, status, emoji=None):
        """Set the status text and emoji"""
        self.status_var.set(status)
        if emoji:
            self.status_emoji.set(emoji)
    
    def start_recording(self):
        """Start recording audio"""
        if self.recording:
            return
            
        self.recording = True
        self.update_ui_state()
        self.log("Started recording - release SPACE when finished")
        
        # Start recording thread
        self.record_thread = threading.Thread(target=self._record_thread)
        self.record_thread.daemon = True
        self.record_thread.start()
    
    def stop_recording(self):
        """Stop recording audio"""
        if not self.recording:
            return
            
        self.recording = False
        self.update_ui_state()
        self.log("Stopped recording")
        
        # Wait for recording thread to finish
        if hasattr(self, 'record_thread'):
            self.record_thread.join(timeout=1.0)
    
    def _record_thread(self):
        """Thread function to handle recording"""
        try:
            # Run the CLI command to record and process audio
            self.run_command(["python", self.backend_script, "--record"])
        except Exception as e:
            self.log(f"Error in recording thread: {str(e)}")
        finally:
            self.recording = False
            self.root.after(100, self.update_ui_state)
    
    def run_command(self, cmd):
        """Run a command and handle its output"""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # Start threads to read output
            def read_output(pipe, is_error=False):
                for line in iter(pipe.readline, ''):
                    if line.strip():
                        if is_error:
                            self.log(f"Error: {line.strip()}")
                        else:
                            self.log(line.strip())
            
            # Start threads for stdout and stderr
            stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, True))
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for the process to complete
            process.wait()
            
            # Wait for output threads to finish
            stdout_thread.join(timeout=0.5)
            stderr_thread.join(timeout=0.5)
            
            return process.returncode
            
        except Exception as e:
            self.log(f"Error running command: {str(e)}")
            return -1
    
    def handle_quick_mode(self, event=None):
        """Handle F10 key for quick mode"""
        self.log("Quick mode - starting recording and auto-sending")
        
        # Run the quick mode command
        self.run_command(["python", self.backend_script, "--quick"])
    
    def handle_retry(self, event=None):
        """Handle F11 key to retry failed chatbots"""
        self.log("Retrying failed chatbots")
        
        # Run the retry command
        self.run_command(["python", self.backend_script, "--retry"])
    
    def show_settings(self, event=None):
        """Show settings dialog (F12)"""
        self.log("Opening settings")
        
        # Create a settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Dragon Voice Assistant Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Simple settings display for now
        settings_text = scrolledtext.ScrolledText(settings_window, wrap=tk.WORD)
        settings_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add a message about settings
        settings_text.insert(tk.END, "Dragon Voice Assistant Settings\n\n")
        settings_text.insert(tk.END, "Configure through config.json file.\n\n")
        settings_text.insert(tk.END, f"Config path: {self.config_path}\n\n")
        
        # Add backend information
        settings_text.insert(tk.END, f"Backend script: {self.backend_script}\n\n")
        
        # Make it read-only
        settings_text.config(state=tk.DISABLED)
        
        # Add a close button
        close_btn = tk.Button(settings_window, text="Close", command=settings_window.destroy)
        close_btn.pack(pady=10)

# Create the app
app = DragonVoiceApp(root)

# Start the main loop
root.mainloop()

class DragonVoiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragon Voice A")
        self.root.geometry("600x750")
        self.root.minsize(600, 750)
        # ... rest of the DragonVoiceGUI class and its methods ... 
