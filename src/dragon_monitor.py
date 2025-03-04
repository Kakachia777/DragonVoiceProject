#!/usr/bin/env python3
"""
DragonVoiceProject - Dragon Medical One Monitor (Phase 3)

This script monitors Dragon Medical One output and triggers browser automation.
It supports monitoring both text files and the clipboard.

Usage:
    python dragon_monitor.py [--mode {file,clipboard}] [--file FILE_PATH] [--interval SECONDS] [--verbose]

Options:
    --mode {file,clipboard}  Integration mode (default: file)
    --file FILE_PATH         Path to Dragon output text file (default: C:/dragon_query.txt)
    --interval SECONDS       Monitoring interval in seconds (default: 1.0)
    --verbose                Enable verbose logging

Requirements:
    - pyperclip
    - pygetwindow
    - pyautogui
    - win10toast (optional, for notifications)
"""

import os
import sys
import time
import json
import argparse
import traceback
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dragon_monitor.log')
    ]
)
logger = logging.getLogger('DragonVoiceProject')

# Try to import required packages
try:
    import pyperclip
    import pygetwindow as gw
    import pyautogui
except ImportError as e:
    logger.error(f"Required package not found: {e}")
    logger.error("Please install required packages using: pip install pyperclip pygetwindow pyautogui")
    sys.exit(1)

# Import our browser automation module from quick_test.py
try:
    from quick_test import find_browser_windows, type_query_in_window
except ImportError:
    logger.error("Could not import from quick_test.py.")
    logger.error("Make sure quick_test.py is in the same directory as dragon_monitor.py.")
    sys.exit(1)

# Default configuration
DEFAULT_CONFIG = {
    "integration": {
        "mode": "file",
        "file_path": "C:/dragon_query.txt",
        "polling_interval": 1.0,
        "command_prefix": "search for"
    },
    "browser": {
        "window_title_pattern": "Chrome",
        "typing_delay": 0.05,
        "window_switch_delay": 0.5
    },
    "feedback": {
        "audio_enabled": True,
        "popup_enabled": True,
        "log_queries": True,
        "log_file": "dragon_voice_queries.log"
    },
    "advanced": {
        "max_retries": 3,
        "retry_delay": 1.0,
        "search_timeout": 5.0
    }
}

# Global variables
config = {}
last_file_content = None
last_clipboard_content = None
last_processed_query = None
log_file = None


def load_config():
    """
    Load configuration from the config.json file.
    Falls back to default configuration if the file is not found or invalid.
    """
    global config
    
    # Path to config file
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    
    try:
        # Check if config file exists
        if os.path.exists(config_path):
            logger.info(f"Loading configuration from {config_path}")
            
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Validate and merge with defaults
            if not isinstance(loaded_config, dict):
                logger.warning("Invalid configuration format. Using defaults.")
                config = DEFAULT_CONFIG
            else:
                # Start with default config and update with loaded values
                config = DEFAULT_CONFIG.copy()
                
                # Update each section if it exists in the loaded config
                for section in config:
                    if section in loaded_config and isinstance(loaded_config[section], dict):
                        config[section].update(loaded_config[section])
            
            logger.info("Configuration loaded successfully.")
        else:
            logger.warning(f"Configuration file not found at {config_path}. Using defaults.")
            config = DEFAULT_CONFIG
    
    except json.JSONDecodeError:
        logger.error(f"Error parsing configuration file: {config_path}")
        logger.warning("Using default configuration.")
        config = DEFAULT_CONFIG
    
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        logger.warning("Using default configuration.")
        config = DEFAULT_CONFIG


def setup_logging():
    """
    Set up logging based on configuration.
    """
    global log_file
    
    # Check for verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Configure query logging if enabled
    if config["feedback"]["log_queries"]:
        log_path = config["feedback"]["log_file"]
        try:
            log_file = open(log_path, 'a')
            logger.info(f"Query logging enabled: {log_path}")
        except Exception as e:
            logger.error(f"Error opening query log file: {e}")


def monitor_file():
    """
    Monitor the Dragon Medical One output file for changes.
    Returns new content if detected, None otherwise.
    """
    global last_file_content
    
    try:
        file_path = config["integration"]["file_path"]
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.warning(f"Dragon output file not found at {file_path}")
            return None
        
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read().strip()
        
        # Check if content has changed since last check
        if content and content != last_file_content:
            last_file_content = content
            logger.debug(f"New file content detected: '{content}'")
            return content
        
        return None
    
    except Exception as e:
        logger.error(f"Error monitoring file: {e}")
        if args.verbose:
            traceback.print_exc()
        return None


def monitor_clipboard():
    """
    Monitor the clipboard for changes.
    Returns new content if detected, None otherwise.
    """
    global last_clipboard_content
    
    try:
        # Get current clipboard content
        content = pyperclip.paste().strip()
        
        # Check if content has changed since last check
        if content and content != last_clipboard_content:
            last_clipboard_content = content
            logger.debug(f"New clipboard content detected: '{content}'")
            return content
        
        return None
    
    except Exception as e:
        logger.error(f"Error monitoring clipboard: {e}")
        if args.verbose:
            traceback.print_exc()
        return None


def extract_search_query(text):
    """
    Extract the search query from the Dragon Medical One output.
    If a command prefix is configured, only process text starting with that prefix.
    Now supports multiple command prefixes separated by semicolons.
    """
    if not text:
        return None
    
    text = text.strip()
    
    # Get command prefix from config
    command_prefix = config["integration"]["command_prefix"]
    
    # If no prefix is defined, treat all text as a query
    if not command_prefix:
        return text
    
    # Support multiple prefixes by splitting the command_prefix on semicolons
    prefixes = [p.strip().lower() for p in command_prefix.split(';')]
    
    # Check if text starts with any of the defined prefixes
    text_lower = text.lower()
    for prefix in prefixes:
        if prefix and text_lower.startswith(prefix):
            # Remove the prefix and return the rest as the query
            return text[len(prefix):].strip()
    
    # No matching prefix found
    return None


def log_query(query):
    """
    Log a processed query to the query log file.
    """
    if not log_file:
        return
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} | {query}\n")
        log_file.flush()
    except Exception as e:
        logger.error(f"Error logging query: {e}")


def provide_feedback(query):
    """
    Provide feedback when a query is detected and processed.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Console feedback
    print("\n" + "=" * 60)
    print(f"QUERY DETECTED ({timestamp}): '{query}'")
    print("=" * 60)
    
    # Log the query
    if config["feedback"]["log_queries"]:
        log_query(query)
    
    # Audio feedback (beep sound)
    if config["feedback"]["audio_enabled"]:
        try:
            # Use Windows built-in beep (frequency, duration in ms)
            import winsound
            winsound.Beep(880, 200)  # 880Hz for 200ms
        except Exception as e:
            logger.debug(f"Audio feedback failed: {e}")
            # Fall back to print statement if audio fails
            print("\a")  # ASCII bell character (might work on some terminals)
    
    # Visual feedback (pop-up notification)
    if config["feedback"]["popup_enabled"]:
        try:
            # This requires having 'win10toast' installed (Windows only)
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                "Dragon Voice Project",
                f"Processing query: {query}",
                duration=3,
                threaded=True
            )
        except ImportError:
            logger.debug("win10toast package not installed - popup notifications disabled")
        except Exception as e:
            logger.error(f"Error showing popup: {e}")


def process_query(query):
    """
    Process a search query by typing it into all Chrome windows.
    """
    global last_processed_query
    
    # Extract the actual query from the text
    search_query = extract_search_query(query)
    
    if not search_query:
        logger.debug(f"No valid search query found in: '{query}'")
        return False
    
    # Check if this is a new query
    if search_query == last_processed_query:
        logger.debug(f"Already processed this query: '{search_query}'")
        return False
    
    # Update last processed query
    last_processed_query = search_query
    
    # Provide feedback
    provide_feedback(search_query)
    
    # Find browser windows
    window_title_pattern = config["browser"]["window_title_pattern"]
    browser_windows = find_browser_windows(window_title_pattern)
    
    if not browser_windows:
        logger.warning(f"No browser windows found matching pattern: '{window_title_pattern}'")
        return False
    
    # Type the query into each browser window
    typing_delay = config["browser"]["typing_delay"]
    window_switch_delay = config["browser"]["window_switch_delay"]
    max_retries = config["advanced"]["max_retries"]
    retry_delay = config["advanced"]["retry_delay"]
    
    success_count = 0
    for i, window in enumerate(browser_windows, 1):
        logger.info(f"Window {i}/{len(browser_windows)}: {window.title}")
        
        # Try typing with retries
        success = False
        for attempt in range(1, max_retries + 1):
            try:
                if type_query_in_window(window, search_query, typing_delay):
                    success = True
                    break
                else:
                    logger.warning(f"Failed to type in window, attempt {attempt}/{max_retries}")
                    if attempt < max_retries:
                        time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Error typing in window: {e}")
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        
        if success:
            success_count += 1
        
        # Brief pause between windows
        time.sleep(window_switch_delay)
    
    # Print summary
    logger.info(f"Automation complete. Successfully typed into {success_count}/{len(browser_windows)} windows.")
    
    return success_count > 0


def monitor_loop():
    """
    Main monitoring loop.
    Continuously checks for Dragon Medical One output and processes it.
    """
    mode = config["integration"]["mode"]
    polling_interval = config["integration"]["polling_interval"]
    command_prefix = config["integration"]["command_prefix"]
    
    logger.info(f"Monitoring {mode} for Dragon Medical One output...")
    logger.info(f"Checking every {polling_interval} seconds.")
    logger.info(f"Command prefix: '{command_prefix}'")
    logger.info("Press Ctrl+C to stop monitoring.\n")
    
    while True:
        try:
            # Check for new content based on selected mode
            if mode == "file":
                new_content = monitor_file()
            else:  # clipboard mode
                new_content = monitor_clipboard()
            
            # Process new content if found
            if new_content:
                process_query(new_content)
            
            # Wait for the next check
            time.sleep(polling_interval)
        
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user.")
            break
        
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            if args.verbose:
                traceback.print_exc()
            
            # Wait a moment before continuing
            time.sleep(1)


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Dragon Medical One Monitor")
    
    parser.add_argument("--mode", choices=["file", "clipboard"],
                        help="Integration mode (default: file)")
    
    parser.add_argument("--file", dest="file_path",
                        help="Path to Dragon output text file")
    
    parser.add_argument("--interval", type=float, dest="polling_interval",
                        help="Monitoring interval in seconds")
    
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    
    return parser.parse_args()


def main():
    """
    Main function.
    """
    global args
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    load_config()
    
    # Override config with command line arguments if provided
    if args.mode:
        config["integration"]["mode"] = args.mode
    
    if args.file_path:
        config["integration"]["file_path"] = args.file_path
    
    if args.polling_interval:
        config["integration"]["polling_interval"] = args.polling_interval
    
    # Setup logging
    setup_logging()
    
    try:
        # Start monitoring
        monitor_loop()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1
    
    finally:
        # Close the query log file if it's open
        if log_file:
            log_file.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 