#!/usr/bin/env python3
"""
DragonVoiceProject - Coordinate Finder Utility

This utility helps find the exact coordinates for chatbot input fields.
It allows users to position their mouse cursor over the input field
and record the absolute and relative coordinates for use in config.json.

Usage:
    python coordinate_finder.py [--chatbot CHATBOT_NAME]

Options:
    --chatbot CHATBOT_NAME     Specific chatbot to configure

Requirements:
    - pygetwindow
    - pyautogui
"""

import sys
import time
import argparse
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

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Coordinate Finder")
    
    parser.add_argument("--chatbot", type=str, default=None,
                        help="Specific chatbot to configure")
    
    return parser.parse_args()

def get_active_window():
    """Get the current active window."""
    try:
        return gw.getActiveWindow()
    except Exception as e:
        logger.error(f"Error getting active window: {e}")
        return None

def get_mouse_position():
    """Get the current mouse position."""
    try:
        return pyautogui.position()
    except Exception as e:
        logger.error(f"Error getting mouse position: {e}")
        return None

def calculate_relative_position(window, position):
    """Calculate the relative position (0.0-1.0) within the window."""
    try:
        if not window or not position:
            return None
        
        rel_x = (position[0] - window.left) / window.width
        rel_y = (position[1] - window.top) / window.height
        
        return (rel_x, rel_y)
    except Exception as e:
        logger.error(f"Error calculating relative position: {e}")
        return None

def update_config(chatbot_name, position, rel_position, window_title):
    """Update the config.json file with the new coordinates."""
    try:
        # Path to config file
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        if not os.path.exists(config_path):
            logger.warning(f"Config file not found at {config_path}")
            return False
        
        # Load existing config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Make sure chatbots section exists
        if "chatbots" not in config:
            config["chatbots"] = {}
        
        # Normalize chatbot name (convert to lowercase, remove spaces)
        normalized_name = chatbot_name.lower().replace(" ", "")
        
        # Create or update chatbot entry
        if normalized_name not in config["chatbots"]:
            config["chatbots"][normalized_name] = {}
        
        # Update the configuration
        config["chatbots"][normalized_name]["title_pattern"] = window_title
        config["chatbots"][normalized_name]["input_position"] = [position[0], position[1]]
        config["chatbots"][normalized_name]["relative_position"] = [rel_position[0], rel_position[1]]
        config["chatbots"][normalized_name]["send_method"] = "enter"
        
        # Save the updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info(f"Updated configuration for '{chatbot_name}' in {config_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return False

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()
    chatbot_name = args.chatbot
    
    print("=" * 60)
    print("DragonVoiceProject - Coordinate Finder Utility")
    print("=" * 60)
    print("\nThis utility helps you find the exact coordinates of chat input fields")
    print("for your medical AI chatbots.")
    print("\nInstructions:")
    print("1. Make sure the chatbot window is open")
    print("2. Follow the prompts to position your mouse and capture coordinates")
    print("3. The utility will save the coordinates to your config.json file")
    print("=" * 60)
    
    # If no chatbot name was provided, ask for one
    if not chatbot_name:
        chatbot_name = input("\nEnter chatbot name (e.g., Grok, HealthUniverse): ").strip()
        if not chatbot_name:
            print("Chatbot name cannot be empty.")
            return False
    
    print(f"\nFinding coordinates for: {chatbot_name}")
    print("\nStep 1: Switch to the browser window containing the chatbot")
    input("Press Enter when you're in the chatbot window...")
    
    # Get the active window
    window = get_active_window()
    if not window:
        print("Error: Could not get active window.")
        return False
    
    window_title = window.title
    print(f"\nActive window: {window_title}")
    print(f"Window position: Left={window.left}, Top={window.top}, Width={window.width}, Height={window.height}")
    
    print("\nStep 2: Position your mouse cursor over the chat input field")
    print("(Don't click, just hover over it)")
    input("Press Enter when your mouse is positioned correctly...")
    
    # Small countdown
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(0.5)
    
    # Get the mouse position
    position = get_mouse_position()
    if not position:
        print("Error: Could not get mouse position.")
        return False
    
    # Calculate relative position
    rel_position = calculate_relative_position(window, position)
    if not rel_position:
        print("Error: Could not calculate relative position.")
        return False
    
    # Display the results
    print("\nCoordinates captured successfully!")
    print(f"Absolute position: x={position[0]}, y={position[1]}")
    print(f"Relative position: x={rel_position[0]:.3f}, y={rel_position[1]:.3f}")
    
    # Ask to update config
    update = input("\nUpdate config.json with these coordinates? (y/n): ")
    if update.lower() == 'y':
        success = update_config(chatbot_name, position, rel_position, window_title)
        if success:
            print("\nConfiguration updated successfully!")
            print(f"Updated settings for '{chatbot_name}' with input position: [{position[0]}, {position[1]}]")
        else:
            print("\nError updating configuration. Please check the logs.")
    else:
        print("\nConfiguration not updated.")
    
    # Manual instructions
    print("\nTo manually add these coordinates to your config.json:")
    print(f"""
    "chatbots": {{
        "{chatbot_name.lower().replace(' ', '')}": {{
            "title_pattern": "{window_title}",
            "input_position": [{position[0]}, {position[1]}],
            "send_method": "enter",
            "typing_delay": 0.05
        }}
    }}
    """)
    
    print("\nFinished! You can now use these coordinates with the Dragon Voice Project.")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nExiting Coordinate Finder. Thank you for using DragonVoiceProject!") 