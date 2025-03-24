#!/usr/bin/env python3
"""
DragonVoiceProject - Batch Coordinate Finder Utility

This utility helps find the exact coordinates for all 12 chatbot input fields in sequence.
It allows users to configure all chatbots one after another in a single session,
recording coordinates for each chatbot and updating the config.json file.

Usage:
    python batch_coordinate_finder.py

Requirements:
    - pygetwindow
    - pyautogui
"""

import sys
import time
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

# List of all supported chatbots
CHATBOTS = [
    "Grok",
    "HealthUniverse", 
    "OpenEvidence",
    "Coral AI",
    "GlassHelp",
    "Bearly",
    "RobertLab",
    "Dr. Oracle",
    "DougallGPT",
    "ClinicalKey",
    "Pathway"
]

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
        
        # Add or update chatbot configuration
        config["chatbots"][normalized_name] = {
            "title_pattern": chatbot_name,
            "input_position": [position[0], position[1]],
            "send_method": "enter",
            "typing_delay": 0.05
        }
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info(f"Updated config for {chatbot_name} at {position}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return False

def configure_chatbot(chatbot_name):
    """Configure a single chatbot by recording mouse position."""
    print("\n" + "=" * 60)
    print(f"Configuring {chatbot_name}")
    print("=" * 60)
    
    print("\nPlease follow these steps:")
    print("1. Switch to the Chrome window containing the chatbot")
    print("2. Position your mouse cursor over the chat input field")
    print("3. Press Enter to record the coordinates")
    print("4. OR press Ctrl+C to skip this chatbot")
    
    input("\nPress Enter when ready...")
    
    try:
        # Give user time to position the mouse
        print("Recording in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        # Get window and mouse information
        window = get_active_window()
        position = get_mouse_position()
        
        if not window:
            print("Error: Could not detect active window.")
            return False
        
        if not position:
            print("Error: Could not detect mouse position.")
            return False
        
        # Print information
        print("\nCursor Information:")
        print(f"Window Title: {window.title}")
        print(f"Window Position: ({window.left}, {window.top}, {window.width}, {window.height})")
        print(f"Cursor Position (Absolute): ({position[0]}, {position[1]})")
        
        # Calculate relative position
        rel_position = calculate_relative_position(window, position)
        if rel_position:
            print(f"Cursor Position (Relative): ({rel_position[0]:.4f}, {rel_position[1]:.4f})")
        
        # Confirm with user
        confirm = input("\nSave these coordinates? (y/n): ").lower()
        if confirm == 'y':
            if update_config(chatbot_name, position, rel_position, window.title):
                print(f"Coordinates for {chatbot_name} saved to config.json.")
                return True
            else:
                print("Error: Could not update config.json.")
                return False
        else:
            print(f"Coordinates for {chatbot_name} not saved.")
            return False
    
    except KeyboardInterrupt:
        print(f"\nSkipping {chatbot_name}...")
        return False
    
    except Exception as e:
        logger.error(f"Error configuring chatbot: {e}")
        return False

def main():
    """Main function to run the batch coordinate finder."""
    print("\n" + "=" * 60)
    print("DragonVoiceProject - Batch Coordinate Finder Utility")
    print("=" * 60)
    
    print("\nThis utility will help you configure coordinates for all chatbots.")
    print("For each chatbot, you'll need to position the mouse cursor over its input field.")
    print("\nSupported chatbots:")
    for i, chatbot in enumerate(CHATBOTS, 1):
        print(f"{i}. {chatbot}")
    
    input("\nPress Enter to begin the configuration process...")
    
    configured_count = 0
    
    for chatbot in CHATBOTS:
        if configure_chatbot(chatbot):
            configured_count += 1
    
    print("\n" + "=" * 60)
    print(f"Configuration complete. Configured {configured_count}/{len(CHATBOTS)} chatbots.")
    print("=" * 60)
    
    print("\nYou can now use the DragonVoiceProject with the configured chatbots.")
    print("To test the configuration, run:")
    print("python src/quick_test.py")

if __name__ == "__main__":
    main() 