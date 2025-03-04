#!/usr/bin/env python3
"""
DragonVoiceProject - Quick Test Script (Phase 1)

This script demonstrates the core browser automation functionality on a single computer.
It prompts for a search query and types it into all open Chrome browser windows.

Usage:
    python quick_test.py [--browser BROWSER_PATTERN] [--delay DELAY]

Options:
    --browser BROWSER_PATTERN  Browser window title pattern (default: Chrome)
    --delay DELAY              Typing delay in seconds (default: 0.05)

Requirements:
    - pygetwindow
    - pyautogui
"""

import sys
import time
import argparse
import traceback
import logging

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

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Quick Test")
    
    parser.add_argument("--browser", type=str, default=BROWSER_TITLE_PATTERN,
                        help=f"Browser window title pattern (default: {BROWSER_TITLE_PATTERN})")
    
    parser.add_argument("--delay", type=float, default=TYPING_DELAY,
                        help=f"Typing delay in seconds (default: {TYPING_DELAY})")
    
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
    Type the query into a specific window.
    
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
        
        # Click in the window to ensure focus (at the center of the window)
        window_center_x = window.left + window.width // 2
        window_center_y = window.top + 100  # Typically where the search bar might be
        pyautogui.click(window_center_x, window_center_y)
        time.sleep(0.1)
        
        # Select all existing text (Ctrl+A) and delete it
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        
        # Type the query character by character
        logger.info(f"Typing query: {query}")
        pyautogui.write(query, interval=typing_delay)
        
        # Press Enter to execute the search
        pyautogui.press('enter')
        
        # Restore original mouse position
        pyautogui.moveTo(original_mouse_pos)
        
        return True
    
    except Exception as e:
        logger.error(f"Error typing in window: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set configuration from arguments
    global BROWSER_TITLE_PATTERN, TYPING_DELAY
    BROWSER_TITLE_PATTERN = args.browser
    TYPING_DELAY = args.delay
    
    print("=" * 60)
    print("DragonVoiceProject - Quick Test (Single Computer Browser Automation)")
    print("=" * 60)
    print("\nThis script will find all open browser windows matching your pattern")
    print("and type your query into each one.")
    print(f"\nBrowser pattern: '{BROWSER_TITLE_PATTERN}'")
    print(f"Typing delay: {TYPING_DELAY} seconds")
    print("\nPlease make sure you have one or more browser windows open with search bars visible.")
    print("\nNote: Do not move your mouse or use your keyboard during the automation process.")
    print("=" * 60)
    
    # Get the search query from the user
    query = input("\nEnter your search query: ").strip()
    
    if not query:
        logger.error("Query cannot be empty.")
        return
    
    # Find browser windows
    browser_windows = find_browser_windows(BROWSER_TITLE_PATTERN)
    
    if not browser_windows:
        logger.error("No matching browser windows found. Please open at least one browser window.")
        return
    
    # Ask for confirmation before proceeding
    confirmation = input(f"\nReady to type '{query}' into {len(browser_windows)} browser windows? (y/n): ")
    
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
        
        if type_query_in_window(window, query, TYPING_DELAY):
            success_count += 1
        
        # Brief pause between windows
        time.sleep(WINDOW_SWITCH_DELAY)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Automation complete. Successfully typed into {success_count}/{len(browser_windows)} windows.")
    print("=" * 60)
    
    if success_count == 0:
        print("\nTroubleshooting tips:")
        print("1. Make sure browser windows are not minimized")
        print("2. Try increasing the typing delay with --delay option")
        print("3. Check if your browser window title contains the pattern you specified")
        print("4. Try running the script with a different browser pattern using --browser option")

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