#!/usr/bin/env python3
"""
DragonVoice CLI - Terminal-based voice assistant with chatbot integration
"""

import os
import sys
import json
import time
import logging
import argparse
import threading
import platform
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
import pyautogui  # Added for chatbot automation
import pyperclip
import subprocess

# Try to import win32gui and win32con for window minimization
try:
    import win32gui
    import win32con
    has_pywin32 = True
except ImportError:
    has_pywin32 = False

# Add keyboard library for global hotkeys
try:
    import keyboard
    has_keyboard = True
except ImportError:
    has_keyboard = False
    print("Warning: keyboard module not found. Global hotkeys will not be available.")
    print("Install with: pip install keyboard")

# Load environment variables at startup
load_dotenv()

# Try to import optional colorama for Windows color support
try:
    from colorama import init, Fore, Back, Style
    has_colorama = True
    init()
except ImportError:
    has_colorama = False

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

# Get the script directory for absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

# Constants with absolute paths
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
RECORDINGS_DIR = os.path.join(PROJECT_DIR, "recordings")
TRANSCRIPTS_DIR = os.path.join(PROJECT_DIR, "transcripts")
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")

class DragonVoiceCLI:
    """Terminal-based voice assistant with chatbot integration"""
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """Initialize the CLI application"""
        self.config_path = config_path
        
        # Set up directories
        self.setup_directories()
        
        # Configure logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize state variables
        self.recording = False
        self.is_paused = False
        self.continuous_mode = False
        self.current_chatbot = None
        self.audio_data = []
        self.stop_level_meter_event = threading.Event()  # Add event for level meter control
        self.last_transcription = ""  # Store the last transcription for confirmation/editing
        self.failed_chatbots = []  # Track failed chatbots for retry
        
        # API configuration
        self.api_key = "j3ydNXEmQFyDKwl5mWxSzcvdZcTLJw1t"  # Hardcoded API key
        self.api_url = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3"
        
        # Set up global hotkeys if available
        self.setup_hotkeys()
        
        # Print welcome message
        self.print_welcome()
        
        logger.info("DragonVoice CLI initialized")
    
    def setup_directories(self):
        """Create necessary directories"""
        for dir_name in [RECORDINGS_DIR, TRANSCRIPTS_DIR, LOGS_DIR]:
            os.makedirs(dir_name, exist_ok=True)
    
    def setup_logging(self):
        """Configure logging with rotation"""
        global logger
        
        log_file = os.path.join(LOGS_DIR, "dragon_cli.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configure logger
        logger = logging.getLogger('DragonVoice')
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info("Configuration loaded from file")
            else:
                config = self.create_default_config()
                logger.info("Created default configuration")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.create_default_config()
    
    def create_default_config(self) -> Dict:
        """Create default configuration"""
        config = {
            "audio": {
                "samplerate": 16000,
                "channels": 1,
                "device": None,
                "chunk_size": 1024,
                "gain": 1.0,
                "noise_gate": 0.01,
                "noise_reduction": {
                    "enabled": False,
                    "strength": 0.5
                }
            },
            "recording": {
                "auto_save": True,
                "save_path": RECORDINGS_DIR,
                "max_duration": 300,
                "silence_threshold": 0.01,
                "silence_duration": 2.0,
                "auto_transcribe": True,
                "quality": "high"
            },
            "transcription": {
                "save_path": TRANSCRIPTS_DIR,
                "task": "transcribe",
                "language": "en",
                "temperature": 0,
                "chunk_level": "segment",
                "chunk_length_s": 30
            },
            "interface": {
                "level_meter_width": 50,
                "level_meter_chars": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"],
                "colors_enabled": has_colorama,
                "status_refresh_rate": 0.1
            },
            "chatbot_input": {
                "enabled": True,
                "coordinates": [],
                "delay_between_inputs": 0.5,
                "mouse_speed": 0.2,  # Speed for mouse movements (seconds)
                "action_delay": 0.1,  # Delay between actions (seconds)
                "fast_mode": True,    # Use fast mode by default
                "profiles": {}
            }
        }
        
        # Save default config
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Default configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving default configuration: {e}")
        
        return config
    
    def print_welcome(self):
        """Print welcome message with color if available"""
        if has_colorama:
            print(f"\n{Fore.CYAN}DragonVoice CLI{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}")
        else:
            print("\nDragonVoice CLI")
            print("=" * 50)
    
    def print_colored(self, text: str, color: Optional[str] = None,
                     style: Optional[str] = None, **kwargs):
        """Print colored text if colorama is available"""
        if has_colorama and self.config["interface"]["colors_enabled"]:
            color_code = getattr(Fore, color.upper(), "") if color else ""
            style_code = getattr(Style, style.upper(), "") if style else ""
            print(f"{color_code}{style_code}{text}{Style.RESET_ALL}", **kwargs)
        else:
            print(text, **kwargs)
    
    def start_recording(self):
        """Start recording audio"""
        if self.recording:
            self.print_colored("Already recording!", "yellow")
            return
        
        try:
            self.print_colored("Starting recording... Press Enter when finished.", "green")
            self.recording = True
            self.is_paused = False
            self.recording_start_time = time.time()  # Initialize recording start time
            self.audio_data = []  # Reset audio data
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            # Wait for Enter key to stop recording
            input()
            self.stop_recording()
            
        except Exception as e:
            self.print_colored(f"Error starting recording: {str(e)}", "red")
            logging.error(f"Error starting recording: {str(e)}")
            self.recording = False
    
    def _record_audio(self):
        """Record audio in a separate thread"""
        try:
            # Set up audio stream
            stream = sd.InputStream(
                device=self.config["audio"]["device"],
                channels=self.config["audio"]["channels"],
                samplerate=self.config["audio"]["samplerate"],
                dtype=np.float32,
                blocksize=self.config["audio"]["chunk_size"],
                callback=self._audio_callback
            )
            
            with stream:
                while self.recording:
                    time.sleep(0.1)  # Prevent busy waiting
                    
        except Exception as e:
            logger.error(f"Error in recording thread: {e}")
            self.recording = False
    
    def _audio_callback(self, indata: np.ndarray, frames: int,
                       time_info: Dict, status: Any) -> None:
        """Process audio data from the input stream"""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        try:
            # Apply gain
            data = indata * self.config["audio"]["gain"]
            
            # Calculate current volume (RMS)
            rms = np.sqrt(np.mean(data**2))
            
            # Apply noise gate
            if rms < self.config["audio"]["noise_gate"]:
                data = np.zeros_like(data)
                rms = 0.0
            
            # Update volume with smoothing
            alpha = 0.1
            self.current_volume = (alpha * rms) + ((1 - alpha) * getattr(self, 'current_volume', 0.0))
            
            # Store audio data if recording and not paused
            if self.recording and not (hasattr(self, 'is_paused') and self.is_paused):
                self.audio_data.append(data.copy())
                
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
    
    def display_level_meter(self):
        """Display a real-time audio level meter"""
        try:
            # Create a more visible recording indicator
            if self.is_paused:
                status_text = "⏸️  RECORDING PAUSED"
                status_color = "yellow"
            else:
                status_text = "🔴 RECORDING IN PROGRESS"
                status_color = "red"
                
            # Clear any previous output
            print("\r" + " " * 80, end="\r", flush=True)
            
            # Display recording status with color
            self.print_colored(status_text, status_color, "bright")
            
            # Show instructions
            if self.is_paused:
                print("\nPress Enter to stop recording or '3' to resume.")
            else:
                print("\nPress Enter to stop recording and transcribe.")
                print("Use '3' to pause recording.")
                
            # Show estimated recording time
            if hasattr(self, 'recording_start_time'):
                elapsed = time.time() - self.recording_start_time
                print(f"Recording time: {elapsed:.1f} seconds")
                
        except Exception as e:
            logger.error(f"Error in display_level_meter: {e}")
            # Don't show the error to avoid cluttering the display
    
    def stop_recording(self) -> bool:
        """Stop recording audio"""
        if not self.recording:
            self.print_colored("Not recording", "yellow")
            return False
        
        try:
            # Stop recording
            self.recording = False
            
            # Wait for recording thread to finish
            if hasattr(self, 'recording_thread'):
                self.recording_thread.join(timeout=0.5)
            
            # Clear any terminal mess
            print("\r" + " " * 80 + "\r", end='', flush=True)
            
            # Calculate recording duration
            if hasattr(self, 'recording_start_time'):
                duration = time.time() - self.recording_start_time
                self.print_colored(f"Recording stopped (duration: {duration:.1f}s)", "green")
            else:
                self.print_colored("Recording stopped", "green")
            
            # Save the recorded audio to a file
            if hasattr(self, 'audio_data') and self.audio_data:
                self.save_audio()
                
                # Auto-transcribe if enabled
                if self.config.get("auto_transcribe", True):
                    self.transcribe_audio()
            else:
                self.print_colored("No audio data recorded", "yellow")
            
            return True
            
        except Exception as e:
            self.print_colored(f"Error stopping recording: {str(e)}", "red")
            logging.error(f"Error stopping recording: {str(e)}")
            return False
    
    def save_audio(self) -> Optional[str]:
        """Save recorded audio to a file"""
        try:
            if not self.audio_data:
                self.print_colored("No audio data to save", "yellow")
                return None
                
            # Create a timestamp for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(RECORDINGS_DIR, f"recording_{timestamp}.wav")
            
            # Concatenate audio data and save to file
            audio_data = np.concatenate(self.audio_data)
            sf.write(filename, audio_data, self.config["audio"]["samplerate"])
            
            self.print_colored(f"Recording saved to {filename}", "green")
            logger.info(f"Recording saved to {filename}")
            
            return filename
            
        except Exception as e:
            self.print_colored(f"Error saving audio: {str(e)}", "red")
            logger.error(f"Error saving audio: {str(e)}")
            return None
    
    def transcribe_audio(self) -> Optional[str]:
        """Transcribe the recorded audio using Deepinfra API"""
        try:
            if not self.audio_data:
                self.print_colored("No audio data to transcribe", "red")
                return None
            
            self.print_colored("\nTranscribing audio...", "cyan")
            
            # Save audio to temporary file
            temp_file = os.path.join(tempfile.gettempdir(), "temp_audio.mp3")
            audio_data = np.concatenate(self.audio_data)
            
            # Check if we have actual audio data
            if np.all(audio_data == 0) or len(audio_data) < 100:
                self.print_colored("No audio detected - recording was empty or too short", "yellow")
                return None
                
            # Save the audio file
            sf.write(temp_file, audio_data, self.config["audio"]["samplerate"])
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            
            data = {
                "model": "whisper-large-v3",
                "task": "transcribe",
                "language": "en"
            }
            
            # Print debug info
            print(f"API URL: {self.api_url}")
            print(f"Audio file size: {os.path.getsize(temp_file)} bytes")
            
            # Open the file for the request
            files = {
                'audio': (temp_file, open(temp_file, 'rb'), 'audio/mpeg')
            }
            
            try:
                # Make API request
                self.print_colored("Sending request to API...", "cyan")
                response = requests.post(self.api_url, headers=headers, data=data, files=files)
                
                # Close file handle
                files['audio'][1].close()
                
                # Process response
                if response.status_code == 200:
                    result = response.json()
                    
                    # Print transcription
                    self.print_colored("\nTranscription:", "green")
                    transcript_text = result.get('text', '')
                    print(transcript_text)
                    
                    # Store the transcription for confirmation/editing
                    self.last_transcription = transcript_text
                    
                    # Save transcript if auto-save is enabled
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    transcript_file = os.path.join(
                        TRANSCRIPTS_DIR,
                        f"transcript_{timestamp}.txt"
                    )
                    
                    with open(transcript_file, 'w') as f:
                        f.write(transcript_text)
                    
                    self.print_colored(f"\nTranscript saved to: {transcript_file}", "blue")
                    
                    # Confirm or edit the transcription
                    confirmed = self.confirm_or_edit_transcription()
                    if confirmed:
                        # If confirmed, automatically send to chatbots without asking
                        if "chatbot_input" in self.config and self.config["chatbot_input"]["enabled"]:
                            # Send directly to chatbots without confirmation
                            self.print_colored("\nSending transcription to chatbots...", "cyan")
                            self.input_to_chatbots(skip_confirmation=True)
                            self.print_colored("\nReady for next recording. Enter command or '1' to record again.", "cyan")
                        else:
                            self.print_colored("\nChatbot input is not enabled. Use command '12' to configure.", "yellow")
                            self.print_colored("Ready for next command.", "cyan")
                    else:
                        self.print_colored("\nTranscription process cancelled. Ready for next command.", "yellow")
                        return None  # Return None when cancelled
                    
                    return transcript_text
                else:
                    self.print_colored("Transcription failed", "red")
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.print_colored(f"API request error: {e}", "red")
                return None
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            self.print_colored(f"Error: {e}", "red")
            return None
        finally:
            # Clean up temp file
            if 'temp_file' in locals() and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def confirm_or_edit_transcription(self) -> bool:
        """Presents the user with the transcription and options to confirm or edit."""
        try:
            while True:
                print("\nCurrent transcription:")
                self.print_colored(self.last_transcription, "cyan")
                print("\nOptions:")
                print("1. Confirm and proceed")
                print("2. Edit transcription")
                print("3. Cancel")
                choice = input("Enter choice (1-3): ").strip()

                if choice == "1":
                    self.print_colored("Transcription confirmed.", "green")
                    return True  # User confirmed
                elif choice == "2":
                    print("\nEdit the text below:")
                    print("Current text: " + self.last_transcription)
                    
                    # Copy the text to clipboard for easy editing
                    pyperclip.copy(self.last_transcription)
                    self.print_colored("Text copied to clipboard for easy editing.", "green")
                    self.print_colored("Paste it (Ctrl+V), edit as needed, then press Enter:", "yellow")
                    
                    # Get user's edited text
                    new_text = input("> ")
                    
                    # If user entered something, use that as the new text
                    if new_text:
                        self.last_transcription = new_text  # Update the transcription
                        self.print_colored("Transcription updated:", "green")
                        self.print_colored(self.last_transcription, "cyan")
                    else:
                        self.print_colored("Keeping original transcription:", "green")
                        self.print_colored(self.last_transcription, "cyan")
                    return True
                elif choice == "3":
                    self.print_colored("Operation cancelled.", "yellow")
                    return False
                else:
                    self.print_colored("Invalid choice. Please enter 1, 2, or 3.", "yellow")
        except KeyboardInterrupt:
            self.print_colored("\nOperation cancelled by user.", "yellow")
            return False
        except Exception as e:
            logger.error(f"Error in confirm_or_edit_transcription: {e}")
            self.print_colored(f"Error: {e}", "red")
            return False
    
    def input_to_chatbots(self, skip_confirmation=False):
        """Inputs the confirmed transcription into the chatbot windows."""
        try:
            if not self.last_transcription:
                self.print_colored("No transcription to input.", "yellow")
                return
            
            # Check if chatbot input is configured
            if "chatbot_input" not in self.config or not self.config["chatbot_input"]["enabled"]:
                self.print_colored("Chatbot input is not enabled in configuration.", "yellow")
                return
            
            # Get coordinates and delay from config
            coordinates = self.config["chatbot_input"]["coordinates"]
            delay = self.config["chatbot_input"]["delay_between_inputs"]
            
            # Get speed settings from config
            mouse_speed = self.config["chatbot_input"].get("mouse_speed", 0.2)
            action_delay = self.config["chatbot_input"].get("action_delay", 0.1)
            fast_mode = self.config["chatbot_input"].get("fast_mode", True)
            
            # Apply fast mode settings if enabled
            if fast_mode:
                mouse_speed = min(mouse_speed, 0.1)
                action_delay = min(action_delay, 0.05)
                delay = min(delay, 0.2)
            
            if not coordinates:
                self.print_colored("No chatbot coordinates configured.", "yellow")
                return
            
            # Copy text to clipboard for pasting
            pyperclip.copy(self.last_transcription)
            
            # Create a progress bar
            total_bots = len(coordinates)
            self.print_colored(f"\n[CHATBOT INPUT] Starting input to {total_bots} chatbots...", "cyan")
            self.print_colored("DO NOT MOVE YOUR MOUSE during this process!", "yellow", "bright")
            
            # Show speed settings
            if fast_mode:
                self.print_colored(f"Using fast mode: mouse_speed={mouse_speed}s, action_delay={action_delay}s, delay={delay}s", "cyan")
            
            # Always proceed without confirmation, regardless of skip_confirmation parameter
            # Removed the confirmation prompt here
            
            # Minimize Command Prompt window so it doesn't get in the way
            try:
                self.print_colored("Attempting to minimize Command Prompt window...", "cyan")
                
                if has_pywin32:
                    # Create a standalone function to minimize windows
                    def minimize_windows():
                        """Minimizes Command Prompt windows as a separate function."""
                        # Define window enumeration callback function
                        def window_enum_handler(hwnd, results):
                            """Callback function for EnumWindows."""
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd)
                                # Look for cmd.exe or command prompt windows
                                if title and ("cmd.exe" in title or 
                                             "Command Prompt" in title or 
                                             "C:\\WINDOWS\\system32\\cmd.exe" in title):
                                    results.append((hwnd, title))
                        
                        # Find and minimize Command Prompt windows
                        windows = []
                        win32gui.EnumWindows(window_enum_handler, windows)
                        
                        if windows:
                            for hwnd, title in windows:
                                self.print_colored(f"Minimizing window: '{title}' (HWND: {hwnd})", "cyan")
                                # Add some time between finding the window and minimizing it
                                time.sleep(0.1)  
                                try:
                                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                                    # Wait a bit after minimizing
                                    time.sleep(0.1)
                                except Exception as e:
                                    self.print_colored(f"Error minimizing window {hwnd}: {e}", "red")
                                    
                            return len(windows)
                        return 0
                    
                    # Call the function and get the count of minimized windows
                    count = minimize_windows()
                    if count > 0:
                        self.print_colored(f"Minimized {count} Command Prompt window(s) using pywin32.", "green")
                    else:
                        self.print_colored("No Command Prompt windows found with pywin32.", "yellow")
                        # Try as a fallback to minimize active window
                        try:
                            active_hwnd = win32gui.GetForegroundWindow()
                            if active_hwnd:
                                active_title = win32gui.GetWindowText(active_hwnd)
                                self.print_colored(f"Minimizing active window: '{active_title}'", "cyan")
                                win32gui.ShowWindow(active_hwnd, win32con.SW_MINIMIZE)
                        except Exception as e:
                            self.print_colored(f"Error minimizing active window: {e}", "red")
                else:
                    self.print_colored("pywin32 is not available. Cannot minimize Command Prompt windows.", "yellow")
                    self.print_colored("Install pywin32 for window minimization: pip install pywin32", "yellow")
            except Exception as e:
                logger.error(f"Error minimizing Command Prompt window: {e}")
                self.print_colored(f"Could not minimize Command Prompt window: {e}", "yellow")
                self.print_colored("Continuing with chatbot input...", "cyan")
            
            # Add a small pause after window minimization
            time.sleep(0.5)
            
            # Create a progress bar
            progress_width = 40
            
            # Save original mouse position to restore at the end
            original_mouse_pos = pyautogui.position()
            
            # Track success count and failed chatbots
            success_count = 0
            self.failed_chatbots = []  # Reset failed chatbots list
            
            # Configure pyautogui for faster operation
            original_pause = pyautogui.PAUSE
            pyautogui.PAUSE = 0.01  # Set minimal pause between PyAutoGUI commands
            
            # Input to each chatbot
            for i, coords in enumerate(coordinates):
                try:
                    # Get chatbot name if available
                    chatbot_name = coords.get("name", f"Chatbot {i+1}")
                    
                    # Calculate progress
                    progress = int((i / total_bots) * progress_width)
                    remaining = progress_width - progress
                    
                    # Display progress bar with chatbot number and name
                    progress_bar = f"[{'#' * progress}{' ' * remaining}] {i+1}/{total_bots}"
                    
                    # Clear line and print progress
                    print(f"\r{' ' * 100}", end='', flush=True)  # Clear line with more space for names
                    print(f"\r[{chatbot_name}] {progress_bar}", end='', flush=True)
                    
                    # Check if there's a special sequence for this chatbot (like DocuAsk)
                    if "special_sequence" in coords:
                        self.print_colored(f"\nExecuting special sequence for {chatbot_name}...", "cyan")
                        
                        # Execute each action in the sequence
                        for step in coords["special_sequence"]:
                            action = step.get("action", "")
                            
                            if action == "click":
                                # Move to and click on the specified coordinates
                                pyautogui.moveTo(step["x"], step["y"], duration=mouse_speed)
                                pyautogui.click()
                                time.sleep(action_delay * 2)  # Double delay after clicks in sequence
                            elif action == "scroll":
                                # Scroll down by the specified amount (multiple wheel movements)
                                amount = step.get("amount", 1)
                                self.print_colored(f"Scrolling down {amount} times...", "cyan")
                                
                                # Scroll in small increments with small delays for reliability
                                for _ in range(amount):
                                    pyautogui.scroll(-3)  # Negative values scroll down
                                    time.sleep(0.1)  # Small delay between scrolls
                                
                                # Pause after scrolling to let page settle
                                time.sleep(0.5)
                        
                        # After sequence, move to final input position
                        pyautogui.moveTo(coords["x"], coords["y"], duration=mouse_speed)
                        pyautogui.click()
                        time.sleep(action_delay * 2)  # Extra delay after special sequence
                    else:
                        # Move to and click on the input field - use configured speed
                        pyautogui.moveTo(coords["x"], coords["y"], duration=mouse_speed)
                        pyautogui.click()
                    time.sleep(action_delay)  # Use configured action delay
                    
                    # Paste the text
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(action_delay)  # Use configured action delay
                    
                    # Check if there's a special submit method
                    if "submit_with" in coords:
                        submit_method = coords["submit_with"]
                        self.print_colored(f"\nUsing special submit method for {chatbot_name}: {submit_method}", "cyan")
                        
                        if submit_method == "ctrl+enter":
                            # Use Ctrl+Enter to submit - use explicit keyDown/keyUp for more reliability
                            time.sleep(0.5)  # Add a longer delay before sending Ctrl+Enter
                            self.print_colored(f"Sending Ctrl+Enter to {chatbot_name}...", "cyan")
                            
                            # Method using explicit keyDown/keyUp
                            pyautogui.keyDown('ctrl')
                            time.sleep(0.2)  # Wait a bit with ctrl pressed
                            pyautogui.press('enter')
                            time.sleep(0.2)  # Wait a bit before releasing ctrl
                            pyautogui.keyUp('ctrl')
                            
                            # Add extra delay after sending Ctrl+Enter
                            time.sleep(0.5)
                        elif submit_method == "shift+enter":
                            # Use Shift+Enter to submit
                            time.sleep(0.5)
                            pyautogui.keyDown('shift')
                            time.sleep(0.2)
                            pyautogui.press('enter')
                            time.sleep(0.2)
                            pyautogui.keyUp('shift')
                            time.sleep(0.5)
                        else:
                            # Use the specified key or key combination
                            pyautogui.press(submit_method)
                    else:
                        # Default: Press Enter to send
                        pyautogui.press('enter')
                    
                    time.sleep(action_delay)  # Use configured action delay
                    
                    # Increment success counter
                    success_count += 1
                    
                    # Wait before moving to next chatbot (only if not the last one)
                    if i < total_bots - 1:
                        time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Error inputting to chatbot {i+1}: {e}")
                    
                    # Get chatbot name if available
                    chatbot_name = coords.get("name", f"Chatbot {i+1}")
                    
                    # Add to failed chatbots list
                    self.failed_chatbots.append(i)
                    
                    # Clear line and print error
                    print(f"\r{' ' * 100}", end='', flush=True)  # Clear line
                    self.print_colored(f"\r[ERROR] Failed to input to {chatbot_name}: {str(e)}", "red")
                    
                    # Provide recovery options
                    print("\nOptions:")
                    print("1. Retry this chatbot")
                    print("2. Skip to next chatbot")
                    print("3. Abort all remaining inputs")
                    
                    choice = input("Choose option (1-3): ").strip()
                    
                    if choice == '1':
                        i -= 1  # Retry this chatbot
                        # continue is handled at end of loop
                    elif choice == '2':
                        pass  # Skip to next chatbot
                    elif choice == '3':
                        self.print_colored("Aborting remaining chatbot inputs.", "yellow")
                        return  # Exit function instead of break
                    else:
                        self.print_colored("Invalid choice. Skipping to next chatbot.", "yellow")
            
            # Restore original PyAutoGUI pause
            pyautogui.PAUSE = original_pause
            
            # Try to restore original mouse position
            try:
                pyautogui.moveTo(original_mouse_pos.x, original_mouse_pos.y, duration=mouse_speed)
            except:
                pass  # Ignore errors when restoring mouse position
            
            # Clear line and print completion message
            print(f"\r{' ' * 100}", end='', flush=True)  # Clear line
            
            # Show success rate
            if success_count == total_bots:
                self.print_colored(f"\r[COMPLETE] Successfully input text to all {total_bots} chatbots! ✅", "green")
            else:
                self.print_colored(f"\r[PARTIAL] Input text to {success_count}/{total_bots} chatbots.", 
                                 "yellow" if success_count > 0 else "red")
                
                # Offer to retry failed chatbots
                if self.failed_chatbots:
                    self.print_colored(f"Failed to input to {len(self.failed_chatbots)} chatbots.", "yellow")
                    retry = input("Would you like to retry the failed chatbots? (y/n): ").strip().lower()
                    if retry == 'y':
                        self.retry_failed_chatbots()
            
            # Provide a summary of what was input
            truncated_text = self.last_transcription[:50] + "..." if len(self.last_transcription) > 50 else self.last_transcription
            self.print_colored(f"Text: \"{truncated_text}\"", "cyan")
            
            # Return to ready state
            self.print_colored("\nReady for next recording. Press 'r' to record again or 'q' for quick mode.", "cyan")
            
        except Exception as e:
            logger.error(f"Error during chatbot input: {e}")
            self.print_colored(f"Error: {e}", "red")
            
            # Restore original PyAutoGUI pause if it was changed
            if 'original_pause' in locals():
                pyautogui.PAUSE = original_pause
            
            # Try to restore original mouse position on error
            try:
                if 'original_mouse_pos' in locals():
                    pyautogui.moveTo(original_mouse_pos.x, original_mouse_pos.y, duration=mouse_speed)
            except:
                pass  # Ignore errors when restoring mouse position

    def list_devices(self):
        """List available audio devices"""
        try:
            devices = sd.query_devices()
            
            self.print_colored("\nAvailable audio devices:", "cyan")
            print("-" * 60)
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    # Highlight default device
                    is_default = i == sd.default.device[0]
                    prefix = "* " if is_default else "  "
                    
                    if has_colorama:
                        name_color = Fore.GREEN if is_default else Fore.WHITE
                        info_color = Fore.CYAN if is_default else Fore.LIGHTBLACK_EX
                    else:
                        name_color = info_color = ""
                    
                    print(f"{prefix}{name_color}{i}: {device['name']}")
                    print(f"    {info_color}Channels: {device['max_input_channels']}")
                    print(f"    Sample Rate: {device['default_samplerate']:.0f} Hz")
            
            print("-" * 60)
            
        except Exception as e:
            logger.error(f"Error listing audio devices: {e}")
            self.print_colored(f"Error: {e}", "red")
    
    def select_device(self):
        """Select input device"""
        try:
            # List available devices
            self.list_devices()
            
            # Get user selection
            device = input("\nSelect device number (or Enter for default): ").strip()
            
            if device:
                try:
                    device = int(device)
                    # Update config
                    self.config["audio"]["device"] = device
                    self.print_colored(f"Selected device {device}", "green")
                    
                    # If recording, restart with new device
                    if self.recording:
                        self.stop_recording()
                        self.start_recording()
                except ValueError:
                    self.print_colored("Invalid device number", "red")
            else:
                # Reset to default device
                self.config["audio"]["device"] = None
                self.print_colored("Using default device", "green")
                
                # If recording, restart with default device
                if self.recording:
                    self.stop_recording()
                    self.start_recording()
                    
        except Exception as e:
            logger.error(f"Error selecting device: {e}")
            self.print_colored(f"Error: {e}", "red")

    def configure(self):
        """Configure application settings"""
        try:
            while True:
                print("\nConfiguration Menu:")
                print("1. Audio Settings")
                print("2. Recording Settings")
                print("3. Transcription Settings")
                print("4. Hotkey Settings")  # Add hotkey settings option
                print("5. Chatbot Input Settings")  # Add chatbot input settings option
                print("6. Save and Exit")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self.configure_audio()
                elif choice == "2":
                    self.configure_recording()
                elif choice == "3":
                    self.configure_transcription()
                elif choice == "4":
                    self.configure_hotkeys()  # Add hotkey configuration
                elif choice == "5":
                    self.configure_chatbot_input()
                elif choice == "6":
                    # Save configuration
                    with open(self.config_path, 'w') as f:
                        json.dump(self.config, f, indent=4)
                    self.print_colored("Settings saved", "green")
                    break
                else:
                    self.print_colored("Invalid option", "yellow")
                    
        except Exception as e:
            logger.error(f"Error in configuration menu: {e}")
            self.print_colored(f"Error: {e}", "red")

    def configure_audio(self):
        """Configure audio settings"""
        try:
            while True:
                print("\nAudio Settings:")
                print("1. Select Input Device")
                print("2. Adjust Gain")
                print("3. Noise Reduction")
                print("4. Back")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self.select_device()
                elif choice == "2":
                    self.adjust_gain()
                elif choice == "3":
                    self.configure_noise_reduction()
                elif choice == "4":
                    break
                else:
                    self.print_colored("Invalid option", "yellow")
                    
        except Exception as e:
            logger.error(f"Error in audio settings: {e}")
            self.print_colored(f"Error: {e}", "red")

    def configure_recording(self):
        """Configure recording settings"""
        try:
            while True:
                print("\nRecording Settings:")
                print("1. Recording Quality")
                print("2. Silence Detection")
                print("3. Auto-transcribe")
                print("4. Back")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self.set_recording_quality()
                elif choice == "2":
                    self.configure_silence_detection()
                elif choice == "3":
                    self.config["recording"]["auto_transcribe"] = not self.config["recording"]["auto_transcribe"]
                    status = "enabled" if self.config["recording"]["auto_transcribe"] else "disabled"
                    self.print_colored(f"Auto-transcribe {status}", "green")
                elif choice == "4":
                    break
                else:
                    self.print_colored("Invalid option", "yellow")
                    
        except Exception as e:
            logger.error(f"Error in recording settings: {e}")
            self.print_colored(f"Error: {e}", "red")

    def configure_transcription(self):
        """Configure transcription settings"""
        try:
            while True:
                print("\nTranscription Settings:")
                print("1. Recognition Language")
                print("2. Real-time Transcription")
                print("3. Translation Settings")
                print("4. Output Format")
                print("5. Custom Prompt")
                print("6. Back")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self.set_language()
                elif choice == "2":
                    self.toggle_realtime_transcription()
                elif choice == "3":
                    self.configure_translation()
                elif choice == "4":
                    self.set_output_format()
                elif choice == "5":
                    self.set_custom_prompt()
                elif choice == "6":
                    break
                else:
                    self.print_colored("Invalid option", "yellow")
                    
        except Exception as e:
            logger.error(f"Error in transcription settings: {e}")
            self.print_colored(f"Error: {e}", "red")

    def adjust_gain(self):
        """Adjust input gain"""
        try:
            current_gain = self.config["audio"]["gain"]
            print(f"\nCurrent gain: {current_gain:.1f}")
            new_gain = input("Enter new gain (0.1-10.0): ").strip()
            
            try:
                new_gain = float(new_gain)
                if 0.1 <= new_gain <= 10.0:
                    self.config["audio"]["gain"] = new_gain
                    self.print_colored(f"Gain set to {new_gain:.1f}", "green")
                else:
                    self.print_colored("Gain must be between 0.1 and 10.0", "yellow")
            except ValueError:
                self.print_colored("Invalid gain value", "red")
                
        except Exception as e:
            logger.error(f"Error adjusting gain: {e}")
            self.print_colored(f"Error: {e}", "red")

    def configure_noise_reduction(self):
        """Configure noise reduction settings"""
        try:
            noise_config = self.config["audio"]["noise_reduction"]
            print("\nNoise Reduction Settings:")
            print(f"1. Enabled: {noise_config['enabled']}")
            print(f"2. Strength: {noise_config['strength']:.1f}")
            print("3. Back")
            
            choice = input("\nSelect option to change: ").strip()
            
            if choice == "1":
                noise_config["enabled"] = not noise_config["enabled"]
                status = "enabled" if noise_config["enabled"] else "disabled"
                self.print_colored(f"Noise reduction {status}", "green")
                
            elif choice == "2":
                strength = input("Enter strength (0.0-1.0): ").strip()
                try:
                    strength = float(strength)
                    if 0.0 <= strength <= 1.0:
                        noise_config["strength"] = strength
                        self.print_colored(f"Noise reduction strength set to {strength:.1f}", "green")
                    else:
                        self.print_colored("Strength must be between 0.0 and 1.0", "yellow")
                except ValueError:
                    self.print_colored("Invalid strength value", "red")
                    
        except Exception as e:
            logger.error(f"Error configuring noise reduction: {e}")
            self.print_colored(f"Error: {e}", "red")

    def toggle_realtime_transcription(self):
        """Toggle real-time transcription"""
        try:
            self.config["transcription"]["real_time"] = not self.config["transcription"]["real_time"]
            status = "enabled" if self.config["transcription"]["real_time"] else "disabled"
            self.print_colored(f"Real-time transcription {status}", "green")
            
        except Exception as e:
            logger.error(f"Error toggling real-time transcription: {e}")
            self.print_colored(f"Error: {e}", "red")

    def configure_translation(self):
        """Configure translation settings"""
        try:
            trans_config = self.config["transcription"]["translation"]
            print("\nTranslation Settings:")
            print(f"1. Enabled: {trans_config['enabled']}")
            print(f"2. Target Language: {trans_config['target_language']}")
            print("3. Back")
            
            choice = input("\nSelect option to change: ").strip()
            
            if choice == "1":
                trans_config["enabled"] = not trans_config["enabled"]
                status = "enabled" if trans_config["enabled"] else "disabled"
                self.print_colored(f"Translation {status}", "green")
                
            elif choice == "2":
                lang = input("Enter target language code (e.g., en, es, fr): ").strip()
                if lang:
                    trans_config["target_language"] = lang
                    self.print_colored(f"Target language set to {lang}", "green")
                    
        except Exception as e:
            logger.error(f"Error configuring translation: {e}")
            self.print_colored(f"Error: {e}", "red")

    def set_output_format(self):
        """Set transcription output format"""
        try:
            print("\nAvailable formats:")
            print("1. text - Plain text")
            print("2. json - Detailed JSON with metadata")
            print("3. srt - Subtitle format")
            print("4. vtt - WebVTT format")
            print("5. Back")
            
            choice = input("\nSelect format: ").strip()
            
            formats = {
                "1": "text",
                "2": "json",
                "3": "srt",
                "4": "vtt"
            }
            
            if choice in formats:
                self.config["transcription"]["response_format"] = formats[choice]
                self.print_colored(f"Output format set to {formats[choice]}", "green")
                
        except Exception as e:
            logger.error(f"Error setting output format: {e}")
            self.print_colored(f"Error: {e}", "red")

    def set_custom_prompt(self):
        """Set custom transcription prompt"""
        try:
            current = self.config["transcription"]["prompt"]
            print(f"\nCurrent prompt: {current or 'None'}")
            
            prompt = input("Enter new prompt (empty to clear): ").strip()
            self.config["transcription"]["prompt"] = prompt if prompt else None
            
            if prompt:
                self.print_colored(f"Prompt set: {prompt}", "green")
            else:
                self.print_colored("Prompt cleared", "green")
                
        except Exception as e:
            logger.error(f"Error setting prompt: {e}")
            self.print_colored(f"Error: {e}", "red")

    def set_language(self):
        """Set recognition language"""
        try:
            current = self.config["transcription"]["language"]
            print(f"\nCurrent language: {current}")
            
            lang = input("Enter language code (e.g., en, es, fr): ").strip()
            if lang:
                self.config["transcription"]["language"] = lang
                self.print_colored(f"Language set to {lang}", "green")
                
        except Exception as e:
            logger.error(f"Error setting language: {e}")
            self.print_colored(f"Error: {e}", "red")

    def set_recording_quality(self):
        """Set recording quality"""
        try:
            current = self.config["recording"]["quality"]
            print("\nRecording Quality:")
            print("1. Low (16kHz, 16-bit)")
            print("2. Medium (32kHz, 16-bit)")
            print("3. High (48kHz, 24-bit)")
            print(f"\nCurrent: {current}")
            
            choice = input("\nSelect quality: ").strip()
            
            qualities = {
                "1": "low",
                "2": "medium",
                "3": "high"
            }
            
            if choice in qualities:
                self.config["recording"]["quality"] = qualities[choice]
                self.print_colored(f"Quality set to {qualities[choice]}", "green")
                
        except Exception as e:
            logger.error(f"Error setting quality: {e}")
            self.print_colored(f"Error: {e}", "red")

    def configure_silence_detection(self):
        """Configure silence detection settings"""
        try:
            print("\nSilence Detection Settings:")
            print(f"1. Threshold: {self.config['recording']['silence_threshold']:.3f}")
            print(f"2. Duration: {self.config['recording']['silence_duration']:.1f}s")
            print("3. Back")
            
            choice = input("\nSelect option to change: ").strip()
            
            if choice == "1":
                threshold = input("Enter threshold (0.001-0.1): ").strip()
                try:
                    threshold = float(threshold)
                    if 0.001 <= threshold <= 0.1:
                        self.config["recording"]["silence_threshold"] = threshold
                        self.print_colored(f"Threshold set to {threshold:.3f}", "green")
                    else:
                        self.print_colored("Threshold must be between 0.001 and 0.1", "yellow")
                except ValueError:
                    self.print_colored("Invalid threshold value", "red")
                    
            elif choice == "2":
                duration = input("Enter duration in seconds (0.5-10.0): ").strip()
                try:
                    duration = float(duration)
                    if 0.5 <= duration <= 10.0:
                        self.config["recording"]["silence_duration"] = duration
                        self.print_colored(f"Duration set to {duration:.1f}s", "green")
                    else:
                        self.print_colored("Duration must be between 0.5 and 10.0", "yellow")
                except ValueError:
                    self.print_colored("Invalid duration value", "red")
                    
        except Exception as e:
            logger.error(f"Error configuring silence detection: {e}")
            self.print_colored(f"Error: {e}", "red")

    def show_status(self):
        """Show system status"""
        try:
            print("\nSystem Status:")
            print("-" * 50)
            
            # Recording status
            status = "Recording" if self.recording else "Idle"
            if self.recording and self.is_paused:
                status = "Paused"
            
            self.print_colored(f"Status: {status}", "cyan")
            
            # Continuous mode
            continuous = "Enabled" if self.continuous_mode else "Disabled"
            self.print_colored(f"Continuous Mode: {continuous}", "cyan")
            
            # Audio settings
            print("\nAudio Settings:")
            print(f"Device: {self.config['audio']['device'] or 'Default'}")
            print(f"Gain: {self.config['audio']['gain']:.1f}")
            print(f"Noise Reduction: {'Enabled' if self.config['audio']['noise_reduction']['enabled'] else 'Disabled'}")
            
            # Recording settings
            print("\nRecording Settings:")
            print(f"Quality: {self.config['recording']['quality']}")
            print(f"Auto-transcribe: {'Enabled' if self.config['recording']['auto_transcribe'] else 'Disabled'}")
            
            # Transcription settings
            print("\nTranscription Settings:")
            print(f"Language: {self.config['transcription']['language']}")
            if "real_time" in self.config["transcription"]:
                print(f"Real-time: {'Enabled' if self.config['transcription']['real_time'] else 'Disabled'}")
            if "translation" in self.config["transcription"]:
                print(f"Translation: {'Enabled' if self.config['transcription']['translation']['enabled'] else 'Disabled'}")
            
            # Chatbot input settings
            if "chatbot_input" in self.config:
                print("\nChatbot Input Settings:")
                print(f"Enabled: {'Yes' if self.config['chatbot_input']['enabled'] else 'No'}")
                print(f"Configured Chatbots: {len(self.config['chatbot_input']['coordinates'])}")
                print(f"Delay Between Inputs: {self.config['chatbot_input']['delay_between_inputs']}s")
            
            print("-" * 50)
            
        except Exception as e:
            logger.error(f"Error showing status: {e}")
            self.print_colored(f"Error: {e}", "red")

    def show_help(self):
        """Show help information"""
        help_text = """
DragonVoice CLI Commands:
------------------------
Recording Controls:
  1. record           - Start recording audio
  2. stop            - Stop recording
  3. pause           - Pause/resume recording
  4. device          - Select input device
  5. gain            - Adjust input gain
  6. noise           - Configure noise reduction
  c. continuous      - Toggle continuous recording mode
  q. quick           - Quick mode: record, transcribe, and send to all chatbots
  p. paste           - Paste text from clipboard to all chatbots

Transcription:
  7. transcribe      - Transcribe last recording
  8. realtime        - Toggle real-time transcription
  9. translate       - Translate transcription
  10. format         - Set output format
  11. prompt         - Set custom prompt

Chatbot Integration:
  12. chatbot        - Configure chatbot input settings
  13. calibrate      - Calibrate chatbot coordinates
  14. profile        - Load a saved chatbot profile
  23. retry          - Retry sending to failed chatbots
  24. add_preset     - Add preset chatbot coordinates

Settings:
  15. config         - Configure settings
  16. language       - Set recognition language
  17. quality        - Set recording quality
  18. silence        - Configure silence detection

System:
  19. devices        - List audio devices
  20. status         - Show system status
  21. help           - Show this help message
  22. exit           - Exit application

Hotkeys (if enabled):
  F9               - Toggle recording (customizable)
  F10              - Quick mode (customizable)
  F11              - Paste from clipboard (customizable)

Tips:
- Use quick mode (q) for fastest workflow: record, transcribe, and send to all chatbots
- Use paste mode (p) to send text from clipboard to all chatbots without recording
- Save different chatbot configurations as profiles for different setups
- Use continuous mode (c) to automatically start recording after each transcription
- Press Enter to stop recording and transcribe
- Use pause (3) to temporarily pause recording without stopping
- After transcription, you can confirm, edit, or cancel the text
- Confirmed/edited text will be sent to configured chatbots
- If sending to some chatbots fails, use retry (23) to try again
"""
        if has_colorama:
            print(f"{Fore.CYAN}{help_text}{Style.RESET_ALL}")
        else:
            print(help_text)

    def configure_hotkeys(self):
        """Configure global hotkey settings"""
        if not has_keyboard:
            self.print_colored("Keyboard module not available. Please install with: pip install keyboard", "yellow")
            return
            
        try:
            # Initialize hotkey settings if not present
            if "hotkeys" not in self.config:
                self.config["hotkeys"] = {
                    "enabled": True,
                    "record_key": "f9",
                    "quick_mode_key": "f10",
                    "paste_key": "f11"  # Add paste from clipboard key
                }
                
            hotkeys = self.config["hotkeys"]
            
            while True:
                print("\nHotkey Settings:")
                print(f"1. Enabled: {hotkeys['enabled']}")
                print(f"2. Record Toggle Key: {hotkeys['record_key']}")
                print(f"3. Quick Mode Key: {hotkeys['quick_mode_key']}")
                print(f"4. Paste from Clipboard Key: {hotkeys.get('paste_key', 'f11')}")
                print("5. Back")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    hotkeys["enabled"] = not hotkeys["enabled"]
                    status = "enabled" if hotkeys["enabled"] else "disabled"
                    self.print_colored(f"Hotkeys {status}", "green")
                    
                    # Re-register or unregister hotkeys
                    if hotkeys["enabled"]:
                        # Clear existing hotkeys
                        keyboard.unhook_all()
                        # Register hotkeys
                        keyboard.add_hotkey(hotkeys["record_key"], self.hotkey_toggle_recording)
                        keyboard.add_hotkey(hotkeys["quick_mode_key"], self.quick_mode)
                        keyboard.add_hotkey(hotkeys.get("paste_key", "f11"), self.paste_from_clipboard)
                        self.print_colored("Hotkeys registered", "green")
                    else:
                        # Unregister all hotkeys
                        keyboard.unhook_all()
                        self.print_colored("Hotkeys unregistered", "yellow")
                        
                elif choice == "2":
                    print("\nPress the key you want to use for toggling recording...")
                    key = keyboard.read_hotkey(suppress=False)
                    hotkeys["record_key"] = key
                    self.print_colored(f"Record toggle key set to: {key}", "green")
                    
                    # Re-register hotkeys
                    if hotkeys["enabled"]:
                        keyboard.unhook_all()
                        keyboard.add_hotkey(hotkeys["record_key"], self.hotkey_toggle_recording)
                        keyboard.add_hotkey(hotkeys["quick_mode_key"], self.quick_mode)
                        keyboard.add_hotkey(hotkeys.get("paste_key", "f11"), self.paste_from_clipboard)
                        
                elif choice == "3":
                    print("\nPress the key you want to use for quick mode...")
                    key = keyboard.read_hotkey(suppress=False)
                    hotkeys["quick_mode_key"] = key
                    self.print_colored(f"Quick mode key set to: {key}", "green")
                    
                    # Re-register hotkeys
                    if hotkeys["enabled"]:
                        keyboard.unhook_all()
                        keyboard.add_hotkey(hotkeys["record_key"], self.hotkey_toggle_recording)
                        keyboard.add_hotkey(hotkeys["quick_mode_key"], self.quick_mode)
                        keyboard.add_hotkey(hotkeys.get("paste_key", "f11"), self.paste_from_clipboard)
                
                elif choice == "4":
                    print("\nPress the key you want to use for pasting from clipboard...")
                    key = keyboard.read_hotkey(suppress=False)
                    hotkeys["paste_key"] = key
                    self.print_colored(f"Paste from clipboard key set to: {key}", "green")
                    
                    # Re-register hotkeys
                    if hotkeys["enabled"]:
                        keyboard.unhook_all()
                        keyboard.add_hotkey(hotkeys["record_key"], self.hotkey_toggle_recording)
                        keyboard.add_hotkey(hotkeys["quick_mode_key"], self.quick_mode)
                        keyboard.add_hotkey(hotkeys["paste_key"], self.paste_from_clipboard)
                        
                elif choice == "5":
                    break
                else:
                    self.print_colored("Invalid option", "yellow")
                    
        except Exception as e:
            logger.error(f"Error configuring hotkeys: {e}")
            self.print_colored(f"Error: {e}", "red")
            
    def paste_from_clipboard(self):
        """Get text from clipboard and send to all chatbots"""
        try:
            # Check if chatbot input is configured
            if "chatbot_input" not in self.config or not self.config["chatbot_input"]["enabled"]:
                self.print_colored("\n[CLIPBOARD] Chatbot input is not enabled. Please configure it first with command '12'.", "yellow")
                return
                
            if not self.config["chatbot_input"]["coordinates"]:
                self.print_colored("\n[CLIPBOARD] No chatbot coordinates configured. Please calibrate with command '13'.", "yellow")
                return
                
            # Get text from clipboard
            clipboard_text = pyperclip.paste()
            
            if not clipboard_text:
                self.print_colored("\n[CLIPBOARD] Clipboard is empty. Copy some text first.", "yellow")
                return
                
            # Store as last transcription
            self.last_transcription = clipboard_text
            
            # Show what will be sent
            self.print_colored(f"\n[CLIPBOARD] Sending clipboard text to {len(self.config['chatbot_input']['coordinates'])} chatbots:", "green")
            truncated_text = clipboard_text[:100] + "..." if len(clipboard_text) > 100 else clipboard_text
            self.print_colored(truncated_text, "cyan")
            
            # Quick confirmation (with 3-second timeout)
            print("Sending in 3 seconds... Press Ctrl+C to cancel.")
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                self.print_colored("\n[CLIPBOARD] Sending cancelled.", "yellow")
                return
            
            # Input to chatbots
            self.input_to_chatbots(skip_confirmation=True)
            
        except Exception as e:
            logger.error(f"Error in paste_from_clipboard: {e}")
            self.print_colored(f"\n[CLIPBOARD] Error: {e}", "red")
            
    def setup_hotkeys(self):
        """Set up global hotkeys for quick recording"""
        if not has_keyboard:
            return
            
        try:
            # Initialize hotkey settings if not present
            if "hotkeys" not in self.config:
                self.config["hotkeys"] = {
                    "enabled": True,
                    "record_key": "f9",
                    "quick_mode_key": "f10",
                    "paste_key": "f11"  # Add paste from clipboard key
                }
                
            # Register hotkeys if enabled
            if self.config["hotkeys"]["enabled"]:
                record_key = self.config["hotkeys"]["record_key"]
                quick_key = self.config["hotkeys"]["quick_mode_key"]
                paste_key = self.config["hotkeys"].get("paste_key", "f11")
                
                # Register hotkeys
                keyboard.add_hotkey(record_key, self.hotkey_toggle_recording)
                keyboard.add_hotkey(quick_key, self.quick_mode)
                keyboard.add_hotkey(paste_key, self.paste_from_clipboard)
                
                logger.info(f"Global hotkeys registered: {record_key} for recording, {quick_key} for quick mode, {paste_key} for clipboard paste")
                
        except Exception as e:
            logger.error(f"Error setting up hotkeys: {e}")
            self.print_colored(f"Error setting up hotkeys: {e}", "red")

    def process_command(self, command: str) -> bool:
        """Process a command"""
        command_aliases = {
            'rec': 'record',
            'stp': 'stop',
            'trs': 'transcribe',
            'cfg': 'config',
            'dev': 'device',
            'hlp': 'help',
            'ext': 'exit',
            'q': 'quick',  # Add quick mode alias
            'p': 'paste',   # Add paste from clipboard alias
            'prof': 'profile',  # Add profile alias
            'preset': 'add_preset'  # Add preset coordinates alias
        }
        # Apply any aliases to the command
        command = command_aliases.get(command, command)
        
        # Recording controls
        if command in ['1', 'record', 'r']:
            self.start_recording()
        elif command in ['2', 'stop', 's']:
            self.stop_recording()
        elif command in ['3', 'pause', 'p']:
            self.toggle_pause()
        elif command in ['4', 'device', 'd']:
            self.select_device()
        elif command in ['5', 'gain', 'g']:
            self.adjust_gain()
        elif command in ['6', 'noise', 'n']:
            self.configure_noise_reduction()
        elif command in ['continuous', 'cont', 'c']:
            self.toggle_continuous_mode()
            
        # Transcription controls
        elif command in ['7', 'transcribe', 't']:
            self.transcribe_audio()
        elif command in ['8', 'realtime', 'rt']:
            self.toggle_realtime_transcription()
        elif command in ['9', 'translate', 'tr']:
            self.configure_translation()
        elif command in ['10', 'format', 'f']:
            self.set_output_format()
        elif command in ['11', 'prompt', 'pr']:
            self.set_custom_prompt()
        elif command in ['10', 'clear_coordinates']:
            self.clear_coordinates()
        elif command in ['24', 'add_preset']:
            self.add_preset_coordinates()
            
        # Chatbot integration
        elif command in ['12', 'chatbot', 'cb']:
            self.configure_chatbot_input()
        elif command in ['13', 'calibrate', 'cal']:
            self.calibrate_chatbot_coordinates()
        elif command in ['quick', 'q']:  # Add quick mode command
            self.quick_mode()
        elif command in ['paste', 'p']:  # Add paste from clipboard command
            self.paste_from_clipboard()
        elif command in ['profile', 'prof', '14']:  # Add profile command
            self.load_profile_command()
            
        # Settings
        elif command in ['15', 'config', 'cf']:
            self.configure()
        elif command in ['16', 'language', 'l']:
            self.set_language()
        elif command in ['17', 'quality', 'q']:
            self.set_recording_quality()
        elif command in ['18', 'silence', 'si']:
            self.configure_silence_detection()
            
        # System commands
        elif command in ['19', 'devices']:
            self.list_devices()
        elif command in ['20', 'status']:
            self.show_status()
        elif command in ['21', 'help', '?']:
            self.show_help()
        elif command in ['22', 'exit', 'quit', 'q']:
            return False
        elif command in ['23', 'retry']:  # Add retry command
            self.retry_failed_chatbots()
        else:
            self.print_colored("Unknown command. Type '21' or 'help' for available commands.", "yellow")
        
        return True

    def main_loop(self):
        """Main application loop - handles continuous operation."""
        self.print_colored("\nDragonVoice CLI ready. Press and hold Enter to record.", "green")
        self.show_help()  # Show help on startup
        
        # Automatically start in "ready to record" mode
        self.print_colored("\nReady to record. Press and hold Enter to start recording, release to stop.", "cyan")
        
        while True:  # Loop forever until explicitly quit
            try:
                # Show prompt with current status
                status = "READY"
                continuous_status = "CONT_OFF"
                chatbot_status = f"CHATBOTS: {len(self.config.get('chatbot_input', {}).get('coordinates', []))}"
                prompt = f"[{status} | {continuous_status} | {chatbot_status}] Press Enter to record (or type command, 21=help, 22=quit): "
                
                # Get input from user
                user_input = input(prompt).strip().lower()
                
                # If Enter was pressed (empty input), start recording with Enter key control
                if not user_input:
                    self.record_with_enter_key()
                else:
                    # Process command if something was typed
                    if not self.process_command(user_input):
                        break  # Exit the loop if process_command returns False (quit)
                
            except KeyboardInterrupt:
                self.print_colored("\nInterrupted by user. Exiting...", "yellow")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.print_colored(f"Error: {e}", "red")
        
        self.print_colored("Exiting DragonVoice CLI...", "green")

    def record_with_enter_key(self):
        """Record audio while Enter key is held down"""
        try:
            import keyboard  # We already have this imported at the top
            
            self.print_colored("Press and hold Enter to start recording. Release to stop.", "green")
            self.print_colored("Waiting for Enter key press...", "cyan")
            
            # Wait for Enter key to be pressed
            keyboard.wait('enter', suppress=True)
            
            # Start recording
            self.print_colored("Recording started... Release Enter to stop.", "green", "bright")
            self.recording = True
            self.is_paused = False
            self.recording_start_time = time.time()
            self.audio_data = []
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            # Wait for Enter key to be released
            keyboard.wait('enter', suppress=True, trigger_on_release=True)
            
            # Stop recording when Enter is released
            self.stop_recording()
            
            # Process the recording
            if self.save_audio():
                self.transcribe_audio()
            
        except Exception as e:
            self.print_colored(f"Error in recording with Enter key: {str(e)}", "red")
            logger.error(f"Error in recording with Enter key: {str(e)}")
            if self.recording:
                self.stop_recording()

    def hotkey_toggle_recording(self):
        """Toggle recording state when hotkey is pressed"""
        try:
            if self.recording:
                # If recording, stop and transcribe
                self.print_colored("\n[HOTKEY] Stopping recording...", "cyan")
                self.stop_recording()
            else:
                # If not recording, start
                self.print_colored("\n[HOTKEY] Starting recording...", "cyan")
                self.start_recording()
                
        except Exception as e:
            logger.error(f"Error in hotkey_toggle_recording: {e}")

    def calibrate_chatbot_coordinates(self):
        """Calibrate chatbot coordinates by capturing mouse positions"""
        try:
            self.print_colored("\nChatbot Coordinate Calibration", "cyan")
            print("This will help you set up coordinates for multiple chatbot windows.")
            print("You'll need to position your mouse over each chatbot input field.")
            
            # Ask if user wants to use auto-detection
            print("\nCalibration Options:")
            print("1. Manual calibration (position mouse over each chatbot)")
            print("2. Auto-detect browser tabs (experimental)")
            print("3. Cancel")
            
            option = input("\nSelect option: ").strip()
            
            if option == "1":
                self._manual_calibration()
            elif option == "2":
                self._auto_detect_browser_tabs()
            else:
                self.print_colored("Calibration cancelled.", "yellow")
                return
                
        except Exception as e:
            logger.error(f"Error in chatbot calibration: {e}")
            self.print_colored(f"Error: {e}", "red")
            
    def _manual_calibration(self):
        """Manual calibration of chatbot coordinates"""
        try:
            # Ask how many chatbots to configure
            num_chatbots = input("\nHow many chatbot windows do you want to configure? (1-12): ").strip()
            try:
                num_chatbots = int(num_chatbots)
                if not (1 <= num_chatbots <= 12):
                    self.print_colored("Number must be between 1 and 12", "yellow")
                    return
            except ValueError:
                self.print_colored("Invalid number", "red")
                return
            
            # Ask if user wants to clear existing coordinates
            if self.config.get("chatbot_input", {}).get("coordinates", []):
                clear = input(f"You already have {len(self.config['chatbot_input']['coordinates'])} coordinates configured. Clear them? (y/n): ").strip().lower()
                if clear == 'y':
                    self.config["chatbot_input"]["coordinates"] = []
                    self.print_colored("Existing coordinates cleared.", "green")
                else:
                    self.print_colored("Keeping existing coordinates.", "yellow")
                    return
            else:
                # Initialize chatbot_input if it doesn't exist
                if "chatbot_input" not in self.config:
                    self.config["chatbot_input"] = {
                        "enabled": True,
                        "delay_between_inputs": 1.0,
                        "coordinates": []
                    }
                else:
                    self.config["chatbot_input"]["coordinates"] = []
            
            self.print_colored("\nCalibration Instructions:", "green")
            self.print_colored("1. Position your mouse over a chatbot input field", "cyan")
            self.print_colored("2. Press Enter to start the countdown", "cyan")
            self.print_colored("3. DO NOT MOVE YOUR MOUSE during the countdown", "yellow")
            self.print_colored("4. After capture, verify the position is correct", "cyan")
            
            input("\nPress Enter when ready to begin calibration...")
            
            # Capture coordinates for each chatbot
            for i in range(num_chatbots):
                self.print_colored(f"\nChatbot {i+1} of {num_chatbots}:", "cyan")
                self.print_colored("Move your mouse to the chatbot input field and DO NOT MOVE IT", "yellow")
                input(f"When your mouse is positioned over chatbot {i+1}'s input field, press Enter...")
                
                # Countdown
                for j in range(5, 0, -1):
                    print(f"Capturing in {j} seconds... DO NOT MOVE MOUSE!", end="\r")
                    time.sleep(1)
                
                # Capture position
                pos = pyautogui.position()
                x, y = pos.x, pos.y
                
                # Add to config
                self.config["chatbot_input"]["coordinates"].append({"x": x, "y": y})
                self.print_colored(f"Captured position {i+1}: X={x}, Y={y}", "green")
                
                # Verify the position
                verify = input("Is this position correct? (y/n): ").strip().lower()
                if verify != 'y':
                    # Remove the last added coordinate
                    self.config["chatbot_input"]["coordinates"].pop()
                    self.print_colored("Position discarded. Let's try again.", "yellow")
                    i -= 1  # Repeat this position
            
            # Enable chatbot input
            self.config["chatbot_input"]["enabled"] = True
            
            # Set delay between inputs
            delay = input("\nEnter delay between chatbot inputs in seconds (0.5-5.0): ").strip()
            try:
                delay = float(delay)
                if 0.5 <= delay <= 5.0:
                    self.config["chatbot_input"]["delay_between_inputs"] = delay
                    self.print_colored(f"Delay set to {delay}s", "green")
                else:
                    self.print_colored("Using default delay of 1.0s", "yellow")
                    self.config["chatbot_input"]["delay_between_inputs"] = 1.0
            except ValueError:
                self.print_colored("Using default delay of 1.0s", "yellow")
                self.config["chatbot_input"]["delay_between_inputs"] = 1.0
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.print_colored(f"\nCalibration complete! {len(self.config['chatbot_input']['coordinates'])} chatbot positions configured.", "green")
            
            # Test the coordinates
            self._test_coordinates()
            
        except Exception as e:
            logger.error(f"Error in manual calibration: {e}")
            self.print_colored(f"Error: {e}", "red")
            
    def _auto_detect_browser_tabs(self):
        """Attempt to automatically detect browser tabs with chatbots"""
        try:
            self.print_colored("\nAuto-detecting browser tabs...", "cyan")
            self.print_colored("This feature will help you quickly set up coordinates for multiple browser tabs.", "cyan")
            self.print_colored("It works best with Chrome/Edge browser tabs arranged in a grid.", "yellow")
            
            # Ask if user wants to clear existing coordinates
            if self.config.get("chatbot_input", {}).get("coordinates", []):
                clear = input(f"You already have {len(self.config['chatbot_input']['coordinates'])} coordinates configured. Clear them? (y/n): ").strip().lower()
                if clear == 'y':
                    self.config["chatbot_input"]["coordinates"] = []
                    self.print_colored("Existing coordinates cleared.", "green")
                else:
                    self.print_colored("Keeping existing coordinates.", "yellow")
                    return
            else:
                # Initialize chatbot_input if it doesn't exist
                if "chatbot_input" not in self.config:
                    self.config["chatbot_input"] = {
                        "enabled": True,
                        "delay_between_inputs": 1.0,
                        "coordinates": []
                    }
                else:
                    self.config["chatbot_input"]["coordinates"] = []
            
            # Get screen resolution
            screen_width, screen_height = pyautogui.size()
            self.print_colored(f"Detected screen resolution: {screen_width}x{screen_height}", "cyan")
            
            # Ask for browser window position
            self.print_colored("\nFirst, we need to locate your browser window.", "cyan")
            self.print_colored("Please make sure your browser window is visible and in focus.", "yellow")
            input("Press Enter when ready...")
            
            # Ask user to click on the browser window
            self.print_colored("\nPlease click on the browser window title bar and press Enter.", "cyan")
            input("Press Enter after clicking on the browser window...")
            
            # Get active window position (this is platform-specific and may need adjustment)
            # For now, we'll use a simplified approach
            self.print_colored("\nNow, please click on the first chatbot input field (bottom of the page).", "cyan")
            input("Position your mouse over the first chatbot input field and press Enter...")
            
            # Countdown
            for j in range(3, 0, -1):
                print(f"Capturing in {j} seconds... DO NOT MOVE MOUSE!", end="\r")
                time.sleep(1)
                
            # Capture first position
            first_pos = pyautogui.position()
            first_x, first_y = first_pos.x, first_pos.y
            
            self.print_colored(f"Captured first position: X={first_x}, Y={first_y}", "green")
            
            # Ask for number of tabs and arrangement
            self.print_colored("\nHow many browser tabs with chatbots do you have open?", "cyan")
            num_tabs = input("Number of tabs (1-12): ").strip()
            try:
                num_tabs = int(num_tabs)
                if not (1 <= num_tabs <= 12):
                    self.print_colored("Number must be between 1 and 12", "yellow")
                    return
            except ValueError:
                self.print_colored("Invalid number", "red")
                return
                
            # Ask for tab arrangement
            self.print_colored("\nHow are your tabs arranged?", "cyan")
            print("1. Single row (horizontal)")
            print("2. Single column (vertical)")
            print("3. Grid (multiple rows and columns)")
            
            arrangement = input("Select arrangement (1-3): ").strip()
            
            if arrangement == "1":  # Horizontal
                # Ask for tab width
                tab_width = input("Approximate width between tab centers (in pixels, e.g., 300): ").strip()
                try:
                    tab_width = int(tab_width)
                except ValueError:
                    tab_width = 300  # Default
                    
                # Generate coordinates
                for i in range(num_tabs):
                    x = first_x + (i * tab_width)
                    y = first_y
                    self.config["chatbot_input"]["coordinates"].append({"x": x, "y": y})
                    self.print_colored(f"Added position {i+1}: X={x}, Y={y}", "green")
                    
            elif arrangement == "2":  # Vertical
                # Ask for tab height
                tab_height = input("Approximate height between tab centers (in pixels, e.g., 200): ").strip()
                try:
                    tab_height = int(tab_height)
                except ValueError:
                    tab_height = 200  # Default
                    
                # Generate coordinates
                for i in range(num_tabs):
                    x = first_x
                    y = first_y + (i * tab_height)
                    self.config["chatbot_input"]["coordinates"].append({"x": x, "y": y})
                    self.print_colored(f"Added position {i+1}: X={x}, Y={y}", "green")
                    
            elif arrangement == "3":  # Grid
                # Ask for grid dimensions
                cols = input("Number of columns in the grid: ").strip()
                try:
                    cols = int(cols)
                    if cols < 1:
                        cols = 1
                except ValueError:
                    cols = 2  # Default
                    
                # Calculate rows
                rows = (num_tabs + cols - 1) // cols  # Ceiling division
                
                # Ask for spacing
                col_spacing = input("Horizontal spacing between tabs (in pixels, e.g., 300): ").strip()
                try:
                    col_spacing = int(col_spacing)
                except ValueError:
                    col_spacing = 300  # Default
                    
                row_spacing = input("Vertical spacing between tabs (in pixels, e.g., 200): ").strip()
                try:
                    row_spacing = int(row_spacing)
                except ValueError:
                    row_spacing = 200  # Default
                    
                # Generate coordinates
                tab_count = 0
                for row in range(rows):
                    for col in range(cols):
                        if tab_count < num_tabs:
                            x = first_x + (col * col_spacing)
                            y = first_y + (row * row_spacing)
                            self.config["chatbot_input"]["coordinates"].append({"x": x, "y": y})
                            self.print_colored(f"Added position {tab_count+1}: X={x}, Y={y}", "green")
                            tab_count += 1
            else:
                self.print_colored("Invalid arrangement selection", "red")
                return
                
            # Enable chatbot input
            self.config["chatbot_input"]["enabled"] = True
            
            # Set delay between inputs
            delay = input("\nEnter delay between chatbot inputs in seconds (0.5-5.0): ").strip()
            try:
                delay = float(delay)
                if 0.5 <= delay <= 5.0:
                    self.config["chatbot_input"]["delay_between_inputs"] = delay
                    self.print_colored(f"Delay set to {delay}s", "green")
                else:
                    self.print_colored("Using default delay of 1.0s", "yellow")
                    self.config["chatbot_input"]["delay_between_inputs"] = 1.0
            except ValueError:
                self.print_colored("Using default delay of 1.0s", "yellow")
                self.config["chatbot_input"]["delay_between_inputs"] = 1.0
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.print_colored(f"\nAuto-detection complete! {len(self.config['chatbot_input']['coordinates'])} chatbot positions configured.", "green")
            
            # Test the coordinates
            self._test_coordinates()
            
        except Exception as e:
            logger.error(f"Error in auto-detect browser tabs: {e}")
            self.print_colored(f"Error: {e}", "red")
            
            # Restore original PyAutoGUI pause if it was changed
            if 'original_pause' in locals():
                pyautogui.PAUSE = original_pause

    def configure_chatbot_input(self):
        """Configure chatbot input settings"""
        try:
            # Ensure chatbot_input section exists in config
            if "chatbot_input" not in self.config:
                self.config["chatbot_input"] = {
                    "enabled": False,
                    "delay_between_inputs": 0.5,
                    "coordinates": [],
                    "profiles": {},  # Add profiles section
                    "mouse_speed": 0.2,  # Speed for mouse movements (seconds)
                    "action_delay": 0.1,  # Delay between actions (seconds)
                    "fast_mode": True     # Use fast mode by default
                }
            
            # Ensure all settings exist
            if "mouse_speed" not in self.config["chatbot_input"]:
                self.config["chatbot_input"]["mouse_speed"] = 0.2
            if "action_delay" not in self.config["chatbot_input"]:
                self.config["chatbot_input"]["action_delay"] = 0.1
            if "fast_mode" not in self.config["chatbot_input"]:
                self.config["chatbot_input"]["fast_mode"] = True
            
            while True:
                print("\nChatbot Input Settings:")
                print(f"1. Enabled: {self.config['chatbot_input']['enabled']}")
                print(f"2. Delay between inputs: {self.config['chatbot_input']['delay_between_inputs']}s")
                print(f"3. Configured chatbots: {len(self.config['chatbot_input']['coordinates'])}")
                print(f"4. Mouse movement speed: {self.config['chatbot_input']['mouse_speed']}s")
                print(f"5. Action delay: {self.config['chatbot_input']['action_delay']}s")
                print(f"6. Fast mode: {self.config['chatbot_input']['fast_mode']}")
                print("7. Calibrate coordinates")
                print("8. Manage profiles")
                print("9. Back")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self.config["chatbot_input"]["enabled"] = not self.config["chatbot_input"]["enabled"]
                    status = "enabled" if self.config["chatbot_input"]["enabled"] else "disabled"
                    self.print_colored(f"Chatbot input {status}", "green")
                    
                elif choice == "2":
                    delay = input("Enter delay between inputs (0.1-5.0 seconds): ").strip()
                    try:
                        delay = float(delay)
                        if 0.1 <= delay <= 5.0:
                            self.config["chatbot_input"]["delay_between_inputs"] = delay
                            self.print_colored(f"Delay set to {delay}s", "green")
                        else:
                            self.print_colored("Delay must be between 0.1 and 5.0 seconds", "yellow")
                    except ValueError:
                        self.print_colored("Invalid delay value", "red")
                        
                elif choice == "3":
                    self.print_colored("\nConfigured chatbot coordinates:", "cyan")
                    coords = self.config["chatbot_input"]["coordinates"]
                    for i, coord in enumerate(coords):
                        name = coord.get("name", f"Chatbot {i+1}")
                        submit = f", submit with: {coord['submit_with']}" if "submit_with" in coord else ""
                        self.print_colored(f"{i+1}: {name} - X={coord['x']}, Y={coord['y']}{submit}", "white")
                    
                    print("\nOptions:")
                    print("1. Add new coordinate")
                    print("2. Remove coordinate")
                    print("3. Clear all coordinates")
                    print("4. Back")
                    
                    subchoice = input("\nSelect option: ").strip()
                    
                    if subchoice == "1":
                        self.add_chatbot_coordinate()
                    elif subchoice == "2":
                        self.remove_chatbot_coordinate()
                    elif subchoice == "3":
                        confirm = input("Are you sure you want to clear all coordinates? (y/n): ").strip().lower()
                        if confirm == 'y':
                            self.config["chatbot_input"]["coordinates"] = []
                            self.print_colored("All coordinates cleared", "green")
                    
                elif choice == "4":
                    speed = input("Enter mouse movement speed (0.05-1.0 seconds): ").strip()
                    try:
                        speed = float(speed)
                        if 0.05 <= speed <= 1.0:
                            self.config["chatbot_input"]["mouse_speed"] = speed
                            self.print_colored(f"Mouse speed set to {speed}s", "green")
                        else:
                            self.print_colored("Speed must be between 0.05 and 1.0 seconds", "yellow")
                    except ValueError:
                        self.print_colored("Invalid speed value", "red")
                    
                elif choice == "5":
                    delay = input("Enter action delay (0.05-1.0 seconds): ").strip()
                    try:
                        delay = float(delay)
                        if 0.05 <= delay <= 1.0:
                            self.config["chatbot_input"]["action_delay"] = delay
                            self.print_colored(f"Action delay set to {delay}s", "green")
                        else:
                            self.print_colored("Delay must be between 0.05 and 1.0 seconds", "yellow")
                    except ValueError:
                        self.print_colored("Invalid delay value", "red")
                
                elif choice == "6":
                    self.config["chatbot_input"]["fast_mode"] = not self.config["chatbot_input"]["fast_mode"]
                    status = "enabled" if self.config["chatbot_input"]["fast_mode"] else "disabled"
                    self.print_colored(f"Fast mode {status}", "green")
                    
                    if self.config["chatbot_input"]["fast_mode"]:
                        self.print_colored("Fast mode will use minimal delays for PyAutoGUI actions.", "cyan")
                    else:
                        self.print_colored("Fast mode disabled. Will use configured delays.", "cyan")
                    
                elif choice == "7":
                    self.calibrate_chatbot_coordinates()
                    
                elif choice == "8":
                    self.manage_chatbot_profiles()
                    
                elif choice == "9":
                    # Save configuration
                    with open(self.config_path, 'w') as f:
                        json.dump(self.config, f, indent=4)
                    self.print_colored("Settings saved", "green")
                    break
                    
        except Exception as e:
            logger.error(f"Error in chatbot input settings: {e}")
            self.print_colored(f"Error: {e}", "red")

    def manage_chatbot_profiles(self):
        """Manage saved chatbot configuration profiles"""
        try:
            # Ensure profiles section exists
            if "profiles" not in self.config["chatbot_input"]:
                self.config["chatbot_input"]["profiles"] = {}
                
            profiles = self.config["chatbot_input"]["profiles"]
            
            while True:
                print("\nChatbot Configuration Profiles:")
                if profiles:
                    for i, (name, profile) in enumerate(profiles.items(), 1):
                        print(f"{i}. {name} ({len(profile['coordinates'])} chatbots)")
                else:
                    print("No saved profiles.")
                    
                print("\nOptions:")
                print("1. Save current configuration as profile")
                print("2. Load profile")
                print("3. Delete profile")
                print("4. Back")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    # Save current configuration
                    name = input("Enter profile name: ").strip()
                    if not name:
                        self.print_colored("Profile name cannot be empty", "yellow")
                        continue
                        
                    # Check if profile exists
                    if name in profiles:
                        confirm = input(f"Profile '{name}' already exists. Overwrite? (y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                            
                    # Save profile
                    profiles[name] = {
                        "coordinates": self.config["chatbot_input"]["coordinates"].copy(),
                        "delay_between_inputs": self.config["chatbot_input"]["delay_between_inputs"]
                    }
                    
                    self.print_colored(f"Profile '{name}' saved with {len(self.config['chatbot_input']['coordinates'])} chatbot positions", "green")
                    
                elif choice == "2":
                    # Load profile
                    if not profiles:
                        self.print_colored("No profiles to load", "yellow")
                        continue
                        
                    print("\nSelect profile to load:")
                    for i, name in enumerate(profiles.keys(), 1):
                        print(f"{i}. {name}")
                        
                    profile_choice = input("\nEnter profile number: ").strip()
                    try:
                        profile_idx = int(profile_choice) - 1
                        if 0 <= profile_idx < len(profiles):
                            profile_name = list(profiles.keys())[profile_idx]
                            profile = profiles[profile_name]
                            
                            # Confirm load
                            confirm = input(f"Load profile '{profile_name}'? This will replace your current configuration. (y/n): ").strip().lower()
                            if confirm == 'y':
                                # Load profile
                                self.config["chatbot_input"]["coordinates"] = profile["coordinates"].copy()
                                self.config["chatbot_input"]["delay_between_inputs"] = profile["delay_between_inputs"]
                                self.config["chatbot_input"]["enabled"] = True
                                
                                self.print_colored(f"Profile '{profile_name}' loaded with {len(profile['coordinates'])} chatbot positions", "green")
                        else:
                            self.print_colored("Invalid profile number", "yellow")
                    except ValueError:
                        self.print_colored("Invalid input", "yellow")
                        
                elif choice == "3":
                    # Delete profile
                    if not profiles:
                        self.print_colored("No profiles to delete", "yellow")
                        continue
                        
                    print("\nSelect profile to delete:")
                    for i, name in enumerate(profiles.keys(), 1):
                        print(f"{i}. {name}")
                        
                    profile_choice = input("\nEnter profile number: ").strip()
                    try:
                        profile_idx = int(profile_choice) - 1
                        if 0 <= profile_idx < len(profiles):
                            profile_name = list(profiles.keys())[profile_idx]
                            
                            # Confirm delete
                            confirm = input(f"Delete profile '{profile_name}'? This cannot be undone. (y/n): ").strip().lower()
                            if confirm == 'y':
                                # Delete profile
                                del profiles[profile_name]
                                self.print_colored(f"Profile '{profile_name}' deleted", "green")
                        else:
                            self.print_colored("Invalid profile number", "yellow")
                    except ValueError:
                        self.print_colored("Invalid input", "yellow")
                        
                elif choice == "4":
                    # Save configuration
                    with open(self.config_path, 'w') as f:
                        json.dump(self.config, f, indent=4)
                    self.print_colored("Profiles saved", "green")
                    break
                else:
                    self.print_colored("Invalid option", "yellow")
                    
        except Exception as e:
            logger.error(f"Error managing chatbot profiles: {e}")
            self.print_colored(f"Error: {e}", "red")
    
    def add_chatbot_coordinate(self):
        """Add a new chatbot coordinate"""
        try:
            print("\nAdding new chatbot coordinate")
            
            # Get chatbot name
            name = input("Enter chatbot name (optional): ").strip()
            
            print("Enter X coordinate (or 'c' to capture current mouse position):")
            x_input = input("> ").strip().lower()
            
            if x_input == 'c':
                # Get current mouse position
                self.print_colored("Positioning mouse in 3 seconds...", "yellow")
                time.sleep(3)  # Give user time to position mouse
                pos = pyautogui.position()
                x, y = pos.x, pos.y
                self.print_colored(f"Captured position: X={x}, Y={y}", "green")
            else:
                try:
                    x = int(x_input)
                    y = int(input("Enter Y coordinate: ").strip())
                except ValueError:
                    self.print_colored("Invalid coordinates", "red")
                    return
            
            # Ask for submit method
            submit_with = input("Enter submit method (leave empty for default Enter, or type ctrl+enter, shift+enter, etc): ").strip().lower()
            
            # Create coordinate object
            coordinate = {"x": x, "y": y}
            
            # Add name if provided
            if name:
                coordinate["name"] = name
                
            # Add submit_with if provided
            if submit_with:
                coordinate["submit_with"] = submit_with
            
            # Add to config
            self.config["chatbot_input"]["coordinates"].append(coordinate)
            
            details = f"X={x}, Y={y}"
            if name:
                details = f"{name}: {details}"
            if submit_with:
                details += f", submit with: {submit_with}"
                
            self.print_colored(f"Added coordinate: {details}", "green")
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error adding chatbot coordinate: {e}")
            self.print_colored(f"Error: {e}", "red")
    
    def remove_chatbot_coordinate(self):
        """Remove a chatbot coordinate"""
        try:
            coords = self.config["chatbot_input"]["coordinates"]
            if not coords:
                self.print_colored("No coordinates to remove", "yellow")
                return
            
            print("\nSelect coordinate to remove:")
            for i, coord in enumerate(coords):
                print(f"{i+1}: X={coord['x']}, Y={coord['y']}")
            
            choice = input("\nEnter number to remove (or 'c' to cancel): ").strip().lower()
            
            if choice == 'c':
                return
                
            try:
                index = int(choice) - 1
                if 0 <= index < len(coords):
                    removed = coords.pop(index)
                    self.print_colored(f"Removed coordinate: X={removed['x']}, Y={removed['y']}", "green")
                    
                    # Save configuration
                    with open(self.config_path, 'w') as f:
                        json.dump(self.config, f, indent=4)
                else:
                    self.print_colored("Invalid selection", "red")
            except ValueError:
                self.print_colored("Invalid selection", "red")
                
        except Exception as e:
            logger.error(f"Error removing chatbot coordinate: {e}")
            self.print_colored(f"Error: {e}", "red")
    
    def load_profile_command(self):
        """Command to quickly load a chatbot profile"""
        try:
            # Check if profiles exist
            if "profiles" not in self.config["chatbot_input"] or not self.config["chatbot_input"]["profiles"]:
                self.print_colored("No chatbot profiles found. Create profiles in the chatbot settings menu (command '12').", "yellow")
                return
                
            profiles = self.config["chatbot_input"]["profiles"]
            
            # List available profiles
            print("\nAvailable Chatbot Profiles:")
            for i, (name, profile) in enumerate(profiles.items(), 1):
                print(f"{i}. {name} ({len(profile['coordinates'])} chatbots)")
                
            # Get user selection
            profile_choice = input("\nSelect profile to load (or 'c' to cancel): ").strip()
            
            if profile_choice.lower() == 'c':
                    return
                
            try:
                profile_idx = int(profile_choice) - 1
                if 0 <= profile_idx < len(profiles):
                    profile_name = list(profiles.keys())[profile_idx]
                    profile = profiles[profile_name]
                    
                    # Load profile
                    self.config["chatbot_input"]["coordinates"] = profile["coordinates"].copy()
                    self.config["chatbot_input"]["delay_between_inputs"] = profile["delay_between_inputs"]
                    self.config["chatbot_input"]["enabled"] = True
                    
                    self.print_colored(f"Profile '{profile_name}' loaded with {len(profile['coordinates'])} chatbot positions", "green")
                    
                    # Save configuration
                    with open(self.config_path, 'w') as f:
                        json.dump(self.config, f, indent=4)
                else:
                    self.print_colored("Invalid profile number", "yellow")
            except ValueError:
                self.print_colored("Invalid input", "yellow")
                
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            self.print_colored(f"Error: {e}", "red")

    def toggle_pause(self) -> bool:
        """Toggle pause/resume recording"""
        try:
            if not self.recording:
                self.print_colored("Not recording", "yellow")
                return False
            
            # Toggle pause state
            if hasattr(self, 'is_paused') and self.is_paused:
                self.is_paused = False
                self.print_colored("Recording resumed", "green")
                # Track pause duration for accurate timing
                if hasattr(self, 'pause_start_time'):
                    pause_duration = time.time() - self.pause_start_time
                    self.recording_start_time += pause_duration  # Adjust start time to account for pause
                    delattr(self, 'pause_start_time')
            else:
                self.is_paused = True
                self.print_colored("Recording paused", "yellow")
                # Track when pause started
                self.pause_start_time = time.time()
            
            # Update the display
            self.display_level_meter()
            
            return True
            
        except Exception as e:
            logger.error(f"Error toggling pause: {e}")
            self.print_colored(f"Error: {e}", "red")
            return False

    def toggle_continuous_mode(self) -> bool:
        """Toggle continuous recording mode"""
        try:
            self.continuous_mode = not self.continuous_mode
            status = "enabled" if self.continuous_mode else "disabled"
            self.print_colored(f"Continuous recording mode {status}", "green")
            
            if self.continuous_mode:
                self.print_colored("After each transcription, recording will automatically start again.", "cyan")
                self.print_colored("Press Ctrl+C to exit continuous mode.", "cyan")
            
            return True
            
        except Exception as e:
            logger.error(f"Error toggling continuous mode: {e}")
            self.print_colored(f"Error: {e}", "red")
            return False

    def quick_mode(self):
        """Quick mode: Record, transcribe, and send to all chatbots with minimal prompts"""
        try:
            # Check if chatbot input is configured
            if "chatbot_input" not in self.config or not self.config["chatbot_input"]["enabled"]:
                self.print_colored("Chatbot input is not enabled. Please configure it first with command '12'.", "yellow")
                return
            # End of quick_mode
        except Exception as e:
            logger.error(f"Error in manual fix: {e}")
    # End of quick_mode method

    def retry_failed_chatbots(self):
        """Retry sending to chatbots that failed in the previous attempt"""
        try:
            if not hasattr(self, 'failed_chatbots') or not self.failed_chatbots:
                self.print_colored("No failed chatbot inputs to retry.", "yellow")
                return
            
            if not self.last_transcription:
                self.print_colored("No transcription to input.", "yellow")
                return
                
            if not self.last_transcription:
                self.print_colored("No transcription to input.", "yellow")
                return
                
            if not self.last_transcription:
                self.print_colored("No transcription to input.", "yellow")
                return
                
            # Get coordinates and delay from config
            coordinates = self.config["chatbot_input"]["coordinates"]
            delay = self.config["chatbot_input"]["delay_between_inputs"]
            
            # Get speed settings from config
            mouse_speed = self.config["chatbot_input"].get("mouse_speed", 0.2)
            action_delay = self.config["chatbot_input"].get("action_delay", 0.1)
            fast_mode = self.config["chatbot_input"].get("fast_mode", True)
            
            # Apply fast mode settings if enabled
            if fast_mode:
                mouse_speed = min(mouse_speed, 0.1)
                action_delay = min(action_delay, 0.05)
                delay = min(delay, 0.2)
            
            # Copy text to clipboard for pasting
            pyperclip.copy(self.last_transcription)
            
            # Create a progress bar
            total_retries = len(self.failed_chatbots)
            self.print_colored(f"\n[RETRY] Retrying input to {total_retries} chatbots...", "cyan")
            self.print_colored("DO NOT MOVE YOUR MOUSE during this process!", "yellow", "bright")
            
            # Show speed settings
            if fast_mode:
                self.print_colored(f"Using fast mode: mouse_speed={mouse_speed}s, action_delay={action_delay}s, delay={delay}s", "cyan")
            
            # Verify before proceeding
            proceed = input("Ready to retry failed chatbots? (y/n): ").strip().lower()
            if proceed != 'y':
                self.print_colored("Retry cancelled.", "yellow")
                return
                
            # Save original mouse position to restore at the end
            original_mouse_pos = pyautogui.position()
            
            # Track success count
            success_count = 0
            new_failed_chatbots = []
            
            # Progress bar width
            progress_width = 40
            
            # Configure pyautogui for faster operation
            original_pause = pyautogui.PAUSE
            pyautogui.PAUSE = 0.01  # Set minimal pause between PyAutoGUI commands
            
            # Retry each failed chatbot
            for i, chatbot_idx in enumerate(self.failed_chatbots):
                try:
                    # Get coordinates for this chatbot
                    if chatbot_idx >= len(coordinates):
                        self.print_colored(f"Invalid chatbot index: {chatbot_idx}", "red")
                        continue
                        
                    coords = coordinates[chatbot_idx]
                    
                    # Get chatbot name if available
                    chatbot_name = coords.get("name", f"Chatbot {chatbot_idx+1}")
                    
                    # Calculate progress
                    progress = int((i / total_retries) * progress_width)
                    remaining = progress_width - progress
                    
                    # Display progress bar
                    progress_bar = f"[{'#' * progress}{' ' * remaining}] {i+1}/{total_retries}"
                    
                    # Clear line and print progress
                    print(f"\r{' ' * 100}", end='', flush=True)  # Clear line with more space for names
                    print(f"\r[RETRY {chatbot_name}] {progress_bar}", end='', flush=True)
                    
                    # Move to and click on the input field - use configured speed
                    pyautogui.moveTo(coords["x"], coords["y"], duration=mouse_speed)
                    pyautogui.click()
                    time.sleep(action_delay)  # Use configured action delay
                    
                    # Paste the text
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(action_delay)  # Use configured action delay
                    
                    # Check if there's a special submit method
                    if "submit_with" in coords:
                        submit_method = coords["submit_with"]
                        self.print_colored(f"\nUsing special submit method for {chatbot_name}: {submit_method}", "cyan")
                        
                        if submit_method == "ctrl+enter":
                            # Use Ctrl+Enter to submit - use explicit keyDown/keyUp for more reliability
                            time.sleep(0.5)  # Add a longer delay before sending Ctrl+Enter
                            self.print_colored(f"Sending Ctrl+Enter to {chatbot_name}...", "cyan")
                            
                            # Method using explicit keyDown/keyUp
                            pyautogui.keyDown('ctrl')
                            time.sleep(0.2)  # Wait a bit with ctrl pressed
                            pyautogui.press('enter')
                            time.sleep(0.2)  # Wait a bit before releasing ctrl
                            pyautogui.keyUp('ctrl')
                            
                            # Add extra delay after sending Ctrl+Enter
                            time.sleep(0.5)
                        elif submit_method == "shift+enter":
                            # Use Shift+Enter to submit
                            time.sleep(0.5)
                            pyautogui.keyDown('shift')
                            time.sleep(0.2)
                            pyautogui.press('enter')
                            time.sleep(0.2)
                            pyautogui.keyUp('shift')
                            time.sleep(0.5)
                        else:
                            # Use the specified key or key combination
                            pyautogui.press(submit_method)
                    else:
                        # Default: Press Enter to send
                        pyautogui.press('enter')
                    
                    time.sleep(action_delay)  # Use configured action delay
                    
                    # Increment success counter
                    success_count += 1
                    
                    # Wait before moving to next chatbot (only if not the last one)
                    if i < total_retries - 1:
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"Error retrying chatbot {chatbot_idx+1}: {e}")
                    
                    # Get chatbot name if available
                    chatbot_name = coords.get("name", f"Chatbot {chatbot_idx+1}")
                    
                    # Add to new failed list
                    new_failed_chatbots.append(chatbot_idx)
                    
                    # Clear line and print error
                    print(f"\r{' ' * 100}", end='', flush=True)  # Clear line
                    self.print_colored(f"\r[ERROR] Failed to retry {chatbot_name}: {str(e)}", "red")
                    
                    # Provide recovery options
                    print("\nOptions:")
                    print("1. Retry this chatbot again")
                    print("2. Skip to next chatbot")
                    print("3. Abort all remaining retries")
                    
                    choice = input("Choose option (1-3): ").strip()
                    
                    if choice == '1':
                        i -= 1  # Retry this chatbot
                        # continue is handled at end of loop
                    elif choice == '2':
                        pass  # Skip to next chatbot
                    elif choice == '3':
                        self.print_colored("Aborting remaining retries.", "yellow")
                        return  # Exit function instead of break
                    else:
                        self.print_colored("Invalid choice. Skipping to next chatbot.", "yellow")
            
            # Restore original PyAutoGUI pause
            pyautogui.PAUSE = original_pause
            
            # Try to restore original mouse position
            try:
                pyautogui.moveTo(original_mouse_pos.x, original_mouse_pos.y, duration=mouse_speed)
            except:
                pass  # Ignore errors when restoring mouse position
                
            # Clear line and print completion message
            print(f"\r{' ' * 100}", end='', flush=True)  # Clear line
            
            # Show success rate
            if success_count == total_retries:
                self.print_colored(f"\r[COMPLETE] Successfully retried all {total_retries} chatbots! ✅", "green")
                # Clear the failed chatbots list
                self.failed_chatbots = []
        else:
            self.print_colored(f"\r[PARTIAL] Successfully retried {success_count}/{total_retries} chatbots.", 
                                 "yellow" if success_count > 0 else "red")
                # Update the failed chatbots list
                self.failed_chatbots = new_failed_chatbots
                
            # Return to ready state
            self.print_colored("\nReady for next command.", "cyan")
            
        except Exception as e:
            logger.error(f"Error during retry: {e}")
            self.print_colored(f"Error: {e}", "red")
            
            # Restore original PyAutoGUI pause if it was changed
            if 'original_pause' in locals():
                pyautogui.PAUSE = original_pause
            
            # Try to restore original mouse position on error
            try:
                if 'original_mouse_pos' in locals():
                    pyautogui.moveTo(original_mouse_pos.x, original_mouse_pos.y, duration=mouse_speed)
            except:
                pass  # Ignore errors when restoring mouse position

    def _test_coordinates(self):
        """Test the configured chatbot coordinates"""
        try:
            # Test the coordinates
            test = input("\nWould you like to test the coordinates? (y/n): ").strip().lower()
            if test == 'y':
                test_text = "This is a test message from DragonVoice CLI."
                pyperclip.copy(test_text)
                
                self.print_colored("\nTesting coordinates with a test message...", "cyan")
                self.print_colored("The test will move your mouse to each configured position.", "yellow")
                self.print_colored("Press Ctrl+C to cancel the test at any time.", "yellow")
                
                input("Press Enter to begin the test...")
                
                # Configure pyautogui for faster operation
                original_pause = pyautogui.PAUSE
                pyautogui.PAUSE = 0.01  # Set minimal pause between PyAutoGUI commands
                
                # Save original mouse position
                original_mouse_pos = pyautogui.position()
                
                for i, coords in enumerate(self.config["chatbot_input"]["coordinates"]):
                    try:
                        self.print_colored(f"Testing position {i+1}: X={coords['x']}, Y={coords['y']}", "cyan")
                        
                        # Move to position - faster movement
                        pyautogui.moveTo(coords["x"], coords["y"], duration=0.3)
                        time.sleep(0.5)
                        
                        # Ask if user wants to click and paste
                        click_paste = input("Click and paste test text here? (y/n): ").strip().lower()
                        if click_paste == 'y':
                            pyautogui.click()
                            time.sleep(0.2)
                            pyautogui.hotkey('ctrl', 'v')
                            time.sleep(0.2)
                            pyautogui.press('enter')
                            self.print_colored("Test text pasted and sent.", "green")
                        
                    except KeyboardInterrupt:
                        self.print_colored("\nTest cancelled.", "yellow")
                        break
                
                # Restore original PyAutoGUI pause
                pyautogui.PAUSE = original_pause
                
                # Try to restore original mouse position
                try:
                    pyautogui.moveTo(original_mouse_pos.x, original_mouse_pos.y, duration=0.3)
                except:
                    pass  # Ignore errors when restoring mouse position
                
                self.print_colored("\nTest complete. Did the mouse move to the correct positions? (y/n): ", "cyan")
                result = input().strip().lower()
                
                if result == 'y':
                    self.print_colored("Great! Your chatbot coordinates are configured correctly.", "green")
                else:
                    self.print_colored("You may want to recalibrate the coordinates.", "yellow")
            
        except Exception as e:
            logger.error(f"Error testing coordinates: {e}")
            self.print_colored(f"Error: {e}", "red")

            # Restore original PyAutoGUI pause if it was changed
            if 'original_pause' in locals():
                pyautogui.PAUSE = original_pause

    def add_multiple_coordinates(self, coordinates_list):
        """Add multiple chatbot coordinates at once from a list"""
        try:
            # Ensure chatbot_input section exists in config
            if "chatbot_input" not in self.config:
                self.config["chatbot_input"] = {
                    "enabled": True,
                    "delay_between_inputs": 0.5,
                    "coordinates": [],
                    "profiles": {},
                    "mouse_speed": 0.2,
                    "action_delay": 0.1,
                    "fast_mode": True
                }
            
            # Get current coordinates
            current_coords = self.config["chatbot_input"]["coordinates"]
            added_count = 0
            
            # Add each coordinate
            for name, x, y in coordinates_list:
                current_coords.append({"x": x, "y": y, "name": name})
                added_count += 1
                self.print_colored(f"Added {name}: X={x}, Y={y}", "green")
            
            # Update config
            self.config["chatbot_input"]["coordinates"] = current_coords
            self.config["chatbot_input"]["enabled"] = True
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.print_colored(f"Successfully added {added_count} chatbot coordinates", "green")
            
            # Ask if user wants to test the coordinates
            test = input("\nWould you like to test the coordinates? (y/n): ").strip().lower()
            if test == 'y':
                self._test_coordinates()
            
        except Exception as e:
            logger.error(f"Error adding multiple coordinates: {e}")
            self.print_colored(f"Error: {e}", "red")

    def add_preset_coordinates(self):
        """Add preset coordinates for common chatbots"""
        try:
            # Define preset coordinates with names
            preset_coordinates = [
                {"name": "Health Universe", "x": 413, "y": 641},
                {"name": "Glass Health", "x": 1315, "y": 460},
                {"name": "Hugging Chat", "x": 164, "y": 1896},
                {"name": "Bearly.AI", "x": 1238, "y": 1949},
                {"name": "OpenEvidence", "x": 2237, "y": 2038},
                {"name": "ReachRx", "x": 3053, "y": 966},
                {"name": "RobertLab", "x": -2773, "y": 1496},
                {"name": "Dr. Oracle", "x": -1702, "y": 411},
                {"name": "Dougall GPT", "x": -810, "y": 692},
                {"name": "ClinicalKey AI", "x": 6005, "y": 1496},
                {"name": "Pathway", "x": 6798, "y": 813},
                {"name": "Claude", "x": 500, "y": 500, "submit_with": "ctrl+enter"},
                {"name": "?", "x": 7992, "y": 1350}
            ]
            
            # Ensure chatbot_input section exists in config
            if "chatbot_input" not in self.config:
                self.config["chatbot_input"] = {
                    "enabled": True,
                    "delay_between_inputs": 0.5,
                    "coordinates": [],
                    "profiles": {},
                    "mouse_speed": 0.2,
                    "action_delay": 0.1,
                    "fast_mode": True
                }
            
            # Check if there are existing coordinates
            if self.config["chatbot_input"]["coordinates"]:
                clear = input(f"You already have {len(self.config['chatbot_input']['coordinates'])} coordinates configured. Clear them? (y/n): ").strip().lower()
                if clear == 'y':
                    self.config["chatbot_input"]["coordinates"] = []
                    self.print_colored("Existing coordinates cleared.", "green")
                else:
                    self.print_colored("Keeping existing coordinates.", "yellow")
            
            # Add preset coordinates
            self.print_colored("\nAdding preset coordinates for common chatbots...", "cyan")
            
            # Add each preset coordinate
            for preset in preset_coordinates:
                self.config["chatbot_input"]["coordinates"].append(preset)
                self.print_colored(f"Added {preset['name']}: X={preset['x']}, Y={preset['y']}", "green")
            
            # Enable fast mode for better performance
            self.config["chatbot_input"]["fast_mode"] = True
            self.config["chatbot_input"]["mouse_speed"] = 0.1
            self.config["chatbot_input"]["action_delay"] = 0.05
            self.config["chatbot_input"]["delay_between_inputs"] = 0.2
            
            # Enable chatbot input
            self.config["chatbot_input"]["enabled"] = True
            
            # Create a profile for all chatbots
            if "profiles" not in self.config["chatbot_input"]:
                self.config["chatbot_input"]["profiles"] = {}
                
            self.config["chatbot_input"]["profiles"]["All Chatbots"] = {
                "coordinates": self.config["chatbot_input"]["coordinates"].copy(),
                "delay_between_inputs": self.config["chatbot_input"]["delay_between_inputs"]
            }
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            self.print_colored(f"\nAdded {len(preset_coordinates)} preset coordinates and created 'All Chatbots' profile.", "green")
            self.print_colored("You may need to adjust these coordinates for your specific screen setup.", "yellow")
            self.print_colored("Use command '13' to calibrate coordinates for your specific setup.", "cyan")
            
        except Exception as e:
            logger.error(f"Error adding preset coordinates: {e}")
            self.print_colored(f"Error: {e}", "red")

    def handle_docuask(self, mouse_speed, action_delay):
        """Special handler for DocuAsk which needs a complex interaction sequence."""
        try:
            self.print_colored("\nProcessing DocuAsk with special sequence...", "cyan")
            
            # First click (top navigation)
            self.print_colored("1. Clicking top navigation...", "cyan")
            pyautogui.moveTo(6345, 390, duration=mouse_speed)
            pyautogui.click()
            time.sleep(action_delay * 2)
            
            # Scroll down a lot
            self.print_colored("2. Scrolling down deeply...", "cyan")
            for _ in range(10):  # Scroll down 10 times
                pyautogui.scroll(-5)  # Negative values scroll down
                time.sleep(0.1)  # Small delay between scrolls
            
            # Pause after scrolling to let page settle
            time.sleep(0.5)
            
            # Final click on input field
            self.print_colored("3. Clicking input field...", "cyan")
            pyautogui.moveTo(6279, 1227, duration=mouse_speed)
            pyautogui.click()
            time.sleep(action_delay * 2)
            
            return True
        except Exception as e:
            self.print_colored(f"Error in DocuAsk sequence: {e}", "red")
            return False

def main():
    """Main entry point"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="DragonVoice CLI")
        parser.add_argument('--config', help='Path to config file',
                          default=DEFAULT_CONFIG_PATH)
        args = parser.parse_args()
        
        # Create and run application
        app = DragonVoiceCLI(config_path=args.config)
        
        # Start the main application loop
        app.main_loop()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
