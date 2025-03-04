#!/usr/bin/env python3
"""
DragonVoiceProject - Client Component (Phase 2)

This script implements the client-side functionality for the Dragon Voice Project.
It polls the server for new search queries and types them into Chrome browser windows.

Usage:
    python client.py [--server SERVER_URL] [--interval SECONDS]

Options:
    --server SERVER_URL    URL of the server (default: http://localhost:5000)
    --interval SECONDS     Polling interval in seconds (default: 1.0)

Requirements:
    - requests
    - pygetwindow
    - pyautogui
"""

import os
import sys
import time
import json
import argparse
import threading
import traceback
from datetime import datetime

try:
    import requests
    import pygetwindow as gw
    import pyautogui
except ImportError:
    print("Error: Required packages not found.")
    print("Please install required packages using: pip install requests pygetwindow pyautogui")
    sys.exit(1)

# Configuration (defaults, can be overridden via command line args or config file)
config = {
    "server_url": "http://localhost:5000",
    "polling_interval": 1.0,  # seconds
    "typing_delay": 0.05,     # seconds between keystrokes
    "window_switch_delay": 0.5,  # seconds after switching windows
    "request_timeout": 5.0,   # seconds for network requests
    "browser_title_pattern": "Chrome",  # Pattern to match in window title
    "max_retries": 3,         # Maximum number of retry attempts for network requests
    "retry_delay": 1.0,       # Seconds to wait between retries
}

# Global variables
last_processed_query = None
stop_event = threading.Event()


class NetworkManager:
    """Handles communication with the server."""
    
    @staticmethod
    def get_latest_query():
        """
        Retrieve the latest query from the server.
        
        Returns:
            dict or None: Query data if successful, None if error or no query available
        """
        url = f"{config['server_url']}/get_query"
        retries = 0
        
        while retries < config["max_retries"]:
            try:
                response = requests.get(
                    url, 
                    timeout=config["request_timeout"]
                )
                
                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    return response.json()
                
                # No query available yet (status code 204)
                elif response.status_code == 204:
                    return None
                
                # Server error
                else:
                    print(f"Error retrieving query: Status code {response.status_code}")
                    print(f"Response: {response.text}")
                    
                    # Increment retry counter
                    retries += 1
                    
                    # Wait before retrying
                    if retries < config["max_retries"]:
                        time.sleep(config["retry_delay"])
            
            except requests.exceptions.RequestException as e:
                print(f"Network error retrieving query: {e}")
                
                # Increment retry counter
                retries += 1
                
                # Wait before retrying
                if retries < config["max_retries"]:
                    print(f"Retrying ({retries}/{config['max_retries']})...")
                    time.sleep(config["retry_delay"])
        
        # All retries failed
        print(f"Failed to retrieve query after {config['max_retries']} attempts")
        return None


class BrowserAutomation:
    """Handles browser automation."""
    
    @staticmethod
    def find_browser_windows():
        """
        Find all Chrome browser windows.
        
        Returns:
            list: List of window objects
        """
        try:
            # Get all windows that have the browser pattern in their title
            browser_windows = gw.getWindowsWithTitle(config["browser_title_pattern"])
            
            if not browser_windows:
                print(f"No {config['browser_title_pattern']} windows found.")
            else:
                print(f"Found {len(browser_windows)} {config['browser_title_pattern']} windows.")
            
            return browser_windows
        
        except Exception as e:
            print(f"Error finding browser windows: {e}")
            traceback.print_exc()
            return []
    
    @staticmethod
    def type_query_in_window(window, query):
        """
        Type the query into a specific window.
        
        Args:
            window: Window object to type into
            query (str): Query text to type
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Activate the window (bring it to the foreground)
            print(f"Activating window: {window.title}")
            window.activate()
            
            # Wait for the window to come to the foreground
            time.sleep(config["window_switch_delay"])
            
            # Select all existing text (Ctrl+A) and delete it
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.1)
            
            # Type the query character by character
            print(f"Typing query: {query}")
            pyautogui.write(query, interval=config["typing_delay"])
            
            # Press Enter to execute the search
            pyautogui.press('enter')
            
            return True
        
        except Exception as e:
            print(f"Error typing in window: {e}")
            traceback.print_exc()
            return False
    
    @staticmethod
    def process_query(query_text):
        """
        Process a query by typing it into all Chrome windows.
        
        Args:
            query_text (str): Query text to type
            
        Returns:
            bool: True if at least one window was successfully processed
        """
        global last_processed_query
        
        # Check if this is a new query
        if query_text == last_processed_query:
            # Already processed this query, skip
            return False
        
        # Update last processed query
        last_processed_query = query_text
        
        # Find browser windows
        browser_windows = BrowserAutomation.find_browser_windows()
        
        if not browser_windows:
            return False
        
        # Type the query into each browser window
        success_count = 0
        for i, window in enumerate(browser_windows, 1):
            print(f"\nWindow {i}/{len(browser_windows)}: {window.title}")
            
            if BrowserAutomation.type_query_in_window(window, query_text):
                success_count += 1
            
            # Brief pause between windows
            time.sleep(0.5)
        
        # Print summary
        print(f"\nAutomation complete. Successfully typed into {success_count}/{len(browser_windows)} windows.")
        
        return success_count > 0


def polling_thread_function():
    """
    Function to run in the polling thread.
    Continuously polls the server for new queries and processes them.
    """
    print(f"Polling thread started. Checking server {config['server_url']} every {config['polling_interval']} seconds.")
    
    while not stop_event.is_set():
        try:
            # Get the latest query from the server
            query_data = NetworkManager.get_latest_query()
            
            # Process the query if available
            if query_data and "query" in query_data:
                query_text = query_data["query"]
                timestamp = query_data.get("timestamp", "unknown time")
                
                print(f"\nNew query received: '{query_text}' (timestamp: {timestamp})")
                
                # Process the query (type into browser windows)
                BrowserAutomation.process_query(query_text)
            
            # Wait for the next polling interval
            stop_event.wait(config["polling_interval"])
            
        except Exception as e:
            print(f"Error in polling thread: {e}")
            traceback.print_exc()
            
            # Wait a bit before trying again
            stop_event.wait(config["retry_delay"])


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Dragon Voice Project Client')
    
    parser.add_argument('--server', type=str, default=config['server_url'],
                        help=f'URL of the server (default: {config["server_url"]})')
    
    parser.add_argument('--interval', type=float, default=config['polling_interval'],
                        help=f'Polling interval in seconds (default: {config["polling_interval"]})')
    
    return parser.parse_args()


def load_config_file():
    """
    Load configuration from a JSON file if available.
    The config file takes precedence over defaults but not over command line arguments.
    """
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_config.json')
    
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as f:
                file_config = json.load(f)
                
            # Update configuration with values from file
            config.update(file_config)
            print(f"Loaded configuration from {config_file_path}")
            
        except Exception as e:
            print(f"Error loading configuration file: {e}")


def main():
    """Main function."""
    global stop_event
    
    # Load configuration from file if available
    load_config_file()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Update configuration from arguments (highest priority)
    config['server_url'] = args.server
    config['polling_interval'] = args.interval
    
    # Print startup banner
    print("\n" + "=" * 60)
    print("DragonVoiceProject - Client (Browser Automation)")
    print("=" * 60)
    print(f"\nServer URL: {config['server_url']}")
    print(f"Polling interval: {config['polling_interval']} seconds")
    print(f"Browser pattern: {config['browser_title_pattern']}")
    print("\nThis client will:")
    print("1. Poll the server for new search queries")
    print("2. Find all Chrome browser windows")
    print("3. Type the query into each window and press Enter")
    print("\nPress Ctrl+C to stop the client")
    print("=" * 60)
    
    # Start the polling thread
    polling_thread = threading.Thread(target=polling_thread_function, daemon=True)
    polling_thread.start()
    
    try:
        # Keep the main thread alive until Ctrl+C
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping client...")
        stop_event.set()
        polling_thread.join(timeout=2.0)
        print("Client stopped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user (Ctrl+C).")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        traceback.print_exc()
    finally:
        print("\nExiting client. Thank you for using DragonVoiceProject!") 