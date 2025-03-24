#!/usr/bin/env python3
"""
DragonVoiceProject - Voice Assistant Integration

This script enhances the DragonVoiceProject with direct voice command integration.
It listens for voice input, then distributes the command to all configured chatbots
across multiple monitors. It supports manual coordinate configuration and works
with the existing Dragon Medical One integration.

Usage:
    python voice_assistant.py [--mode {direct,dragon}]

Options:
    --mode {direct,dragon}    Voice input mode (default: dragon)

Requirements:
    - pyperclip
    - pygetwindow
    - pyautogui
"""

import os
import sys
import time
import json
import argparse
import logging
import threading
import pyperclip
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('voice_assistant.log')
    ]
)
logger = logging.getLogger('DragonVoiceProject')

try:
    import pyperclip
    import pygetwindow as gw
    import pyautogui
except ImportError as e:
    logger.error(f"Required package not found: {e}")
    logger.error("Please install required packages using: pip install pyperclip pygetwindow pyautogui")
    sys.exit(1)

# Default configuration
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class MultiScreenVoiceAssistant:
    """Handles voice input and distributes it to chatbots across multiple screens."""
    
    def __init__(self, config_path=DEFAULT_CONFIG_PATH, mode="dragon"):
        """Initialize the voice assistant."""
        self.config_path = config_path
        self.mode = mode
        self.load_config()
        self.last_clipboard_content = None
        self.last_file_content = None
        self.running = False
        
        # Initialize screen information
        self.screen_info = self.get_screen_info()
        logger.info(f"Detected {len(self.screen_info)} screens")
        for i, screen in enumerate(self.screen_info):
            logger.info(f"Screen {i+1}: {screen}")
    
    def load_config(self):
        """Load configuration from the config file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info("Configuration loaded successfully")
            
            # Log configuration details
            logger.info(f"Integration mode: {self.config['integration']['mode']}")
            logger.info(f"Command prefix: {self.config['integration']['command_prefix']}")
            logger.info(f"Number of chatbots configured: {len(self.config['chatbots'])}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            self.config = {
                "integration": {
                    "mode": "clipboard",
                    "file_path": "./dragon_query.txt",
                    "polling_interval": 1.0,
                    "command_prefix": "ask"
                },
                "browser": {
                    "window_title_pattern": "Chrome",
                    "typing_delay": 0.05,
                    "window_switch_delay": 0.5
                },
                "chatbots": {}
            }
    
    def get_screen_info(self):
        """Get information about all connected screens."""
        try:
            # This is a simple approach using pyautogui to get screen size
            screen_width, screen_height = pyautogui.size()
            
            # For a more sophisticated multi-monitor solution, we would use
            # platform-specific libraries. For now, we'll simulate with a simple approach
            screen_info = [
                {"width": screen_width, "height": screen_height, "left": 0, "top": 0}
            ]
            
            # If on Windows, try to get more detailed multi-monitor info
            if sys.platform == 'win32':
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    monitors = []
                    
                    def callback(monitor, dc, rect, data):
                        monitors.append({
                            "left": rect.contents.left,
                            "top": rect.contents.top,
                            "width": rect.contents.right - rect.contents.left,
                            "height": rect.contents.bottom - rect.contents.top
                        })
                        return 1
                    
                    callback_type = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, 
                                                     ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double)
                    user32.EnumDisplayMonitors(None, None, callback_type(callback), 0)
                    
                    if monitors:
                        screen_info = monitors
                
                except Exception as e:
                    logger.warning(f"Error getting detailed multi-monitor info: {e}")
            
            return screen_info
        
        except Exception as e:
            logger.error(f"Error detecting screens: {e}")
            # Return a default single screen configuration
            return [{"width": 1920, "height": 1080, "left": 0, "top": 0}]
    
    def check_clipboard(self):
        """Check clipboard for new commands."""
        try:
            current_content = pyperclip.paste()
            
            # Skip if content hasn't changed
            if current_content == self.last_clipboard_content:
                return None
            
            self.last_clipboard_content = current_content
            
            # Check if content starts with command prefix
            prefix = self.config["integration"]["command_prefix"].lower()
            if current_content.lower().startswith(prefix):
                # Extract the query part (after the prefix)
                query = current_content[len(prefix):].strip()
                logger.info(f"Voice command detected in clipboard: {query}")
                return query
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking clipboard: {e}")
            return None
    
    def check_file(self):
        """Check file for new commands."""
        try:
            file_path = self.config["integration"]["file_path"]
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                current_content = f.read().strip()
            
            # Skip if content hasn't changed
            if current_content == self.last_file_content:
                return None
            
            self.last_file_content = current_content
            
            # Check if content starts with command prefix
            prefix = self.config["integration"]["command_prefix"].lower()
            if current_content.lower().startswith(prefix):
                # Extract the query part (after the prefix)
                query = current_content[len(prefix):].strip()
                logger.info(f"Voice command detected in file: {query}")
                return query
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking file: {e}")
            return None
    
    def process_command(self, query):
        """Process a voice command by distributing it to all chatbots."""
        if not query:
            return
        
        logger.info(f"Processing command: {query}")
        
        # Find browser windows
        browser_pattern = self.config["browser"]["window_title_pattern"]
        typing_delay = self.config["browser"]["typing_delay"]
        window_switch_delay = self.config["browser"]["window_switch_delay"]
        
        try:
            # Get all windows that match the pattern in their title
            browser_windows = gw.getWindowsWithTitle(browser_pattern)
            
            if not browser_windows:
                logger.warning(f"No windows found matching pattern: '{browser_pattern}'")
                return
            
            logger.info(f"Found {len(browser_windows)} windows matching pattern: '{browser_pattern}'")
            
            # Process each window
            successful_count = 0
            
            for i, window in enumerate(browser_windows):
                logger.info(f"Processing window {i+1}/{len(browser_windows)}: {window.title}")
                
                # Find which chatbot this window belongs to
                chatbot_name = None
                for name, config in self.config["chatbots"].items():
                    if config["title_pattern"].lower() in window.title.lower():
                        chatbot_name = name
                        break
                
                if not chatbot_name:
                    logger.warning(f"No matching chatbot found for window: {window.title}")
                    continue
                
                try:
                    # Get chatbot specific config
                    chatbot_config = self.config["chatbots"][chatbot_name]
                    input_position = chatbot_config["input_position"]
                    send_method = chatbot_config.get("send_method", "enter")
                    chatbot_typing_delay = chatbot_config.get("typing_delay", typing_delay)
                    
                    # Activate window
                    logger.info(f"Activating window: {window.title}")
                    window.activate()
                    time.sleep(window_switch_delay)
                    
                    # Click on the input field
                    x, y = input_position
                    logger.info(f"Clicking at position: ({x}, {y})")
                    pyautogui.click(x, y)
                    time.sleep(0.5)
                    
                    # Type the query
                    logger.info(f"Typing query with delay: {chatbot_typing_delay}")
                    pyautogui.write(query, interval=chatbot_typing_delay)
                    time.sleep(0.5)
                    
                    # Send the query
                    if send_method.lower() == "enter":
                        logger.info("Pressing Enter to send")
                        pyautogui.press('enter')
                    else:
                        logger.info("Clicking send button")
                        # If send method is not "enter", assume it's a click on a button
                        # would need additional coordinates for the button, for now just use Enter
                        pyautogui.press('enter')
                    
                    successful_count += 1
                    time.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"Error processing window {window.title}: {e}")
                    continue
            
            logger.info(f"Successfully sent query to {successful_count}/{len(browser_windows)} windows")
            
            # Provide feedback if enabled
            if self.config.get("feedback", {}).get("popup_enabled", False):
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(
                        "DragonVoiceProject",
                        f"Query sent to {successful_count} chatbots",
                        duration=3,
                        threaded=True
                    )
                except ImportError:
                    pass
        
        except Exception as e:
            logger.error(f"Error in command processing: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop for voice commands."""
        logger.info(f"Starting voice command monitoring (mode: {self.mode})")
        
        polling_interval = self.config["integration"]["polling_interval"]
        
        while self.running:
            query = None
            
            # Check for new voice commands
            if self.config["integration"]["mode"] == "clipboard" or self.mode == "direct":
                query = self.check_clipboard()
            elif self.config["integration"]["mode"] == "file":
                query = self.check_file()
            
            # Process any detected commands
            if query:
                self.process_command(query)
            
            # Wait before checking again
            time.sleep(polling_interval)
    
    def start(self):
        """Start the voice assistant."""
        if self.running:
            logger.warning("Voice assistant is already running")
            return
        
        self.running = True
        
        # Start the monitoring loop in a separate thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Voice assistant started")
        
        print("\n" + "=" * 60)
        print("DragonVoiceProject - Voice Assistant")
        print("=" * 60)
        print("\nVoice assistant is now running.")
        print(f"Mode: {self.mode}")
        print(f"Command prefix: {self.config['integration']['command_prefix']}")
        print(f"Number of chatbots: {len(self.config['chatbots'])}")
        print(f"Number of screens: {len(self.screen_info)}")
        print("\nTo use:")
        if self.config["integration"]["mode"] == "clipboard":
            print("1. Dictate your command with Dragon Medical One")
            print("2. Make sure it includes the command prefix")
            print("3. Copy the text to clipboard")
        else:
            print("1. Dictate your command with Dragon Medical One")
            print("2. Make sure it includes the command prefix")
            print(f"3. Dragon should save to file: {self.config['integration']['file_path']}")
        
        print("\nPress Ctrl+C to stop")
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the voice assistant."""
        logger.info("Stopping voice assistant")
        self.running = False
        
        # Wait for the monitor thread to stop
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        logger.info("Voice assistant stopped")
        print("\nVoice assistant stopped")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Voice Assistant")
    
    parser.add_argument("--mode", choices=["direct", "dragon"], default="dragon",
                      help="Voice input mode (default: dragon)")
    
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH,
                      help=f"Path to config file (default: {DEFAULT_CONFIG_PATH})")
    
    return parser.parse_args()

def main():
    """Main function to run the voice assistant."""
    args = parse_arguments()
    
    # Create and start the voice assistant
    assistant = MultiScreenVoiceAssistant(config_path=args.config, mode=args.mode)
    assistant.start()

if __name__ == "__main__":
    main() 