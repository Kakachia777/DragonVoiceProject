#!/usr/bin/env python3
"""
DragonVoiceProject - Quick Test Script (Phase 1)

This script demonstrates the core chatbot automation functionality on a single computer.
It prompts for a query and sends it to all open browser windows containing medical AI chatbots.

Usage:
    python quick_test.py [--browser BROWSER_PATTERN] [--delay DELAY] [--chatbot CHATBOT_NAME]

Options:
    --browser BROWSER_PATTERN  Browser window title pattern (default: Chrome)
    --delay DELAY              Typing delay in seconds (default: 0.05)
    --chatbot CHATBOT_NAME     Specific chatbot to target (e.g., 'Grok', 'HealthUniverse')

Requirements:
    - pygetwindow
    - pyautogui
"""

import sys
import time
import argparse
import traceback
import logging
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DragonVoiceProject')

try:
    import pygetwindow as gw
    import pyautogui
except ImportError as e:
    logger.error(f"Required package not found: {e}")
    logger.error("Please install required packages using: pip install pygetwindow pyautogui")
    sys.exit(1)

# Default configuration
TYPING_DELAY = 0.05  # Delay between keystrokes (seconds)
WINDOW_SWITCH_DELAY = 0.5  # Delay after switching windows (seconds)
BROWSER_TITLE_PATTERN = "Chrome"  # Pattern to match in window title
CHATBOT_NAME = None  # Specific chatbot to target

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Quick Test")
    
    parser.add_argument("--browser", type=str, default=BROWSER_TITLE_PATTERN,
                        help=f"Browser window title pattern (default: {BROWSER_TITLE_PATTERN})")
    
    parser.add_argument("--delay", type=float, default=TYPING_DELAY,
                        help=f"Typing delay in seconds (default: {TYPING_DELAY})")
    
    parser.add_argument("--chatbot", type=str, default=CHATBOT_NAME,
                        help="Specific chatbot to target (e.g., 'Grok', 'HealthUniverse')")
    
    return parser.parse_args()

def find_browser_windows(title_pattern=BROWSER_TITLE_PATTERN):
    """
    Find all browser windows matching the specified title pattern.
    
    Args:
        title_pattern: Pattern to match in window titles
        
    Returns:
        List of matching window objects
    """
    try:
        # Get all windows that match the pattern in their title
        browser_windows = gw.getWindowsWithTitle(title_pattern)
        
        if not browser_windows:
            logger.warning(f"No windows found matching pattern: '{title_pattern}'")
            return []
        
        logger.info(f"Found {len(browser_windows)} windows matching pattern: '{title_pattern}'")
        return browser_windows
    
    except Exception as e:
        logger.error(f"Error finding browser windows: {e}")
        traceback.print_exc()
        return []

def type_query_in_window(window, query, typing_delay=TYPING_DELAY):
    """
    Type the query into a specific window using the standard method.
    This is a fallback for chatbots without specific configurations.
    
    Args:
        window: Window object to type into
        query: Query string to type
        typing_delay: Delay between keystrokes in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Store current mouse position
        original_mouse_pos = pyautogui.position()
        
        # Activate the window (bring it to the foreground)
        logger.info(f"Activating window: {window.title}")
        window.activate()
        
        # Wait for the window to come to the foreground
        time.sleep(WINDOW_SWITCH_DELAY)
        
        # Click near the bottom center of the window (common location for chat inputs)
        input_x = window.left + window.width // 2
        input_y = window.bottom - 50
        pyautogui.click(input_x, input_y)
        time.sleep(0.2)
        
        # Type the query character by character
        logger.info(f"Typing query: {query}")
        pyautogui.write(query, interval=typing_delay)
        
        # Press Enter to send the message
        pyautogui.press('enter')
        
        # Restore original mouse position
        pyautogui.moveTo(original_mouse_pos)
        
        return True
    
    except Exception as e:
        logger.error(f"Error typing in window: {e}")
        traceback.print_exc()
        return False

def get_chatbot_config(chatbot_name):
    """
    Get configuration for a specific chatbot from config.json.
    
    Args:
        chatbot_name: Name of the chatbot to get configuration for
        
    Returns:
        Dictionary with chatbot configuration or None if not found
    """
    try:
        # Look for config.json in the same directory
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        if not os.path.exists(config_path):
            logger.warning("config.json not found. Using default settings.")
            return None
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check for chatbots configuration
        chatbots = config.get("chatbots", {})
        
        if not chatbot_name:
            return None
        
        # Try to find the specific chatbot configuration
        for name, settings in chatbots.items():
            if name.lower() == chatbot_name.lower() or \
               settings.get("title_pattern", "").lower() == chatbot_name.lower():
                return settings
        
        return None
    
    except Exception as e:
        logger.error(f"Error loading chatbot configuration: {e}")
        return None

def type_query_in_chatbot(window, query, chatbot_config, typing_delay=TYPING_DELAY):
    """
    Type the query into a specific chatbot window using its configuration.
    
    Args:
        window: Window object to type into
        query: Query string to type
        chatbot_config: Configuration for the chatbot
        typing_delay: Default typing delay (may be overridden by config)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Store current mouse position
        original_mouse_pos = pyautogui.position()
        
        # Activate the window (bring it to the foreground)
        logger.info(f"Activating window: {window.title}")
        window.activate()
        
        # Wait for the window to come to the foreground
        time.sleep(WINDOW_SWITCH_DELAY)
        
        # Get input position from config
        input_position = chatbot_config.get("input_position", [])
        if len(input_position) == 2 and input_position[0] < 1 and input_position[1] < 1:
            # Relative position (0.0-1.0)
            input_x = window.left + int(window.width * input_position[0])
            input_y = window.top + int(window.height * input_position[1])
        elif len(input_position) == 2:
            # Absolute position
            input_x, input_y = input_position
        else:
            # Default to bottom center
            input_x = window.left + (window.width // 2)
            input_y = window.bottom - 50
        
        # Click in the input area
        pyautogui.click(input_x, input_y)
        time.sleep(0.3)
        
        # Use configured typing delay or default
        actual_typing_delay = chatbot_config.get("typing_delay", typing_delay)
        
        # Type the query character by character
        logger.info(f"Typing query: {query}")
        pyautogui.write(query, interval=actual_typing_delay)
        
        # Send based on method
        send_method = chatbot_config.get("send_method", "enter")
        if send_method == "enter":
            pyautogui.press('enter')
        elif send_method == "button":
            button_pos = chatbot_config.get("send_button_position", [input_x + 100, input_y])
            pyautogui.click(button_pos[0], button_pos[1])
        
        # Wait after sending if specified
        wait_time = chatbot_config.get("wait_time", 0)
        if wait_time > 0:
            time.sleep(wait_time)
        
        # Restore original mouse position
        pyautogui.moveTo(original_mouse_pos)
        
        return True
    
    except Exception as e:
        logger.error(f"Error typing in chatbot: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set configuration from arguments
    global BROWSER_TITLE_PATTERN, TYPING_DELAY, CHATBOT_NAME
    BROWSER_TITLE_PATTERN = args.browser
    TYPING_DELAY = args.delay
    CHATBOT_NAME = args.chatbot
    
    print("=" * 60)
    print("DragonVoiceProject - Quick Test (Chatbot Automation)")
    print("=" * 60)
    print("\nThis script will find all open browser windows matching your pattern")
    print("and send your query to the chatbots in each window.")
    print(f"\nBrowser pattern: '{BROWSER_TITLE_PATTERN}'")
    print(f"Typing delay: {TYPING_DELAY} seconds")
    if CHATBOT_NAME:
        print(f"Target chatbot: {CHATBOT_NAME}")
    print("\nPlease make sure you have one or more browser windows open with chatbots.")
    print("\nNote: Do not move your mouse or use your keyboard during the automation process.")
    print("=" * 60)
    
    # Get the chatbot query from the user
    query = input("\nEnter your chatbot query: ").strip()
    
    if not query:
        logger.error("Query cannot be empty.")
        return
    
    # Find browser windows
    browser_windows = find_browser_windows(BROWSER_TITLE_PATTERN)
    
    if not browser_windows:
        logger.error("No matching browser windows found. Please open at least one browser window.")
        return
    
    # If a specific chatbot was specified, filter windows
    if CHATBOT_NAME:
        filtered_windows = []
        for window in browser_windows:
            if CHATBOT_NAME.lower() in window.title.lower():
                filtered_windows.append(window)
        
        if filtered_windows:
            browser_windows = filtered_windows
            logger.info(f"Filtered to {len(browser_windows)} windows containing '{CHATBOT_NAME}'")
        else:
            logger.warning(f"No windows containing '{CHATBOT_NAME}' found. Will try all windows.")
    
    # Get chatbot configuration if a specific chatbot was specified
    chatbot_config = get_chatbot_config(CHATBOT_NAME)
    if chatbot_config:
        logger.info(f"Using configuration for chatbot: {CHATBOT_NAME}")
    
    # Ask for confirmation before proceeding
    confirmation = input(f"\nReady to send '{query}' to {len(browser_windows)} browser windows? (y/n): ")
    
    if confirmation.lower() != 'y':
        print("Operation cancelled by user.")
        return
    
    print("\nStarting automation in 3 seconds... Please don't move the mouse or use keyboard.")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Type the query into each browser window
    success_count = 0
    for i, window in enumerate(browser_windows, 1):
        print(f"\nWindow {i}/{len(browser_windows)}: {window.title}")
        
        if chatbot_config:
            # Use specific chatbot configuration
            if type_query_in_chatbot(window, query, chatbot_config, TYPING_DELAY):
                success_count += 1
        else:
            # Use standard method
            if type_query_in_window(window, query, TYPING_DELAY):
                success_count += 1
        
        # Brief pause between windows
        time.sleep(WINDOW_SWITCH_DELAY)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Automation complete. Successfully sent query to {success_count}/{len(browser_windows)} chatbots.")
    print("=" * 60)
    
    if success_count == 0:
        print("\nTroubleshooting tips:")
        print("1. Make sure browser windows are not minimized")
        print("2. Try increasing the typing delay with --delay option")
        print("3. Check if your browser window title contains the pattern you specified")
        print("4. Try running the script with a different browser pattern using --browser option")
        print("5. Use the coordinate finder utility to find the exact chat input position")

    return success_count > 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()
    finally:
        print("\nExiting script. Thank you for testing DragonVoiceProject!") 