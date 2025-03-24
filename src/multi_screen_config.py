#!/usr/bin/env python3
"""
DragonVoiceProject - Multi-Screen Configuration Tool

This utility helps configure chatbot coordinates across multiple screens.
It provides a simple interface to record mouse positions for all chatbots
and distributes them intelligently across multiple monitors.

Usage:
    python multi_screen_config.py [--screens NUM_SCREENS]

Options:
    --screens NUM_SCREENS    Number of screens to configure for (default: auto-detect)

Requirements:
    - pygetwindow
    - pyautogui
"""

import os
import sys
import time
import json
import argparse
import logging
import ctypes

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

# Default configuration path
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def detect_screens():
    """Detect and return information about all connected screens."""
    try:
        # Start with default single screen using pyautogui
        screen_width, screen_height = pyautogui.size()
        screen_info = [
            {"width": screen_width, "height": screen_height, "left": 0, "top": 0}
        ]
        
        # On Windows, try to detect multiple monitors
        if sys.platform == 'win32':
            try:
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
                    logger.info(f"Detected {len(monitors)} monitors")
                    screen_info = monitors
            except Exception as e:
                logger.warning(f"Error detecting multiple monitors: {e}")
        
        return screen_info
    
    except Exception as e:
        logger.error(f"Error detecting screens: {e}")
        return [{"width": 1920, "height": 1080, "left": 0, "top": 0}]

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

def load_config():
    """Load the existing configuration file."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        
        # Return default config if file doesn't exist
        return {
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
            "chatbots": {},
            "feedback": {
                "audio_enabled": True,
                "popup_enabled": True,
                "log_queries": True,
                "log_file": "dragon_voice_queries.log"
            }
        }
    
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None

def save_config(config):
    """Save the configuration to the config file."""
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Configuration saved to {CONFIG_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def assign_chatbots_to_screens(chatbots, screens):
    """
    Assign chatbots to screens in a balanced way.
    
    Args:
        chatbots: List of chatbot names
        screens: List of screen info dictionaries
    
    Returns:
        Dictionary mapping chatbot names to screen indices
    """
    if not chatbots or not screens:
        return {}
    
    # Simple round-robin assignment
    assignments = {}
    screen_index = 0
    
    for chatbot in chatbots:
        assignments[chatbot] = screen_index
        screen_index = (screen_index + 1) % len(screens)
    
    return assignments

def configure_chatbot(chatbot_name, screen_info):
    """Configure a single chatbot by recording mouse position."""
    print("\n" + "=" * 60)
    print(f"Configuring {chatbot_name}")
    if screen_info:
        screen_left = screen_info["left"]
        screen_top = screen_info["top"]
        screen_width = screen_info["width"]
        screen_height = screen_info["height"]
        print(f"Target Screen: Left={screen_left}, Top={screen_top}, Width={screen_width}, Height={screen_height}")
    print("=" * 60)
    
    print("\nPlease follow these steps:")
    print("1. Position your mouse cursor over the chat input field for this chatbot")
    print("2. Press Enter to record the coordinates")
    print("3. OR press Ctrl+C to skip this chatbot")
    
    input("\nPress Enter when ready...")
    
    try:
        # Give user time to position the mouse
        print("Recording in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        # Get mouse information
        position = get_mouse_position()
        window = get_active_window()
        
        if not position:
            print("Error: Could not detect mouse position.")
            return None
        
        # Print information
        print("\nCursor Information:")
        print(f"Cursor Position (Absolute): ({position[0]}, {position[1]})")
        
        if window:
            print(f"Active Window: {window.title}")
            print(f"Window Position: ({window.left}, {window.top}, {window.width}, {window.height})")
        
        # Verify position is in the correct screen
        if screen_info:
            in_screen = (
                screen_info["left"] <= position[0] < screen_info["left"] + screen_info["width"] and
                screen_info["top"] <= position[1] < screen_info["top"] + screen_info["height"]
            )
            
            if not in_screen:
                print(f"Warning: Cursor position is not in the target screen!")
                if input("Continue anyway? (y/n): ").lower() != 'y':
                    return None
        
        # Confirm with user
        if input("\nSave these coordinates? (y/n): ").lower() == 'y':
            return position
        else:
            print(f"Coordinates for {chatbot_name} not saved.")
            return None
    
    except KeyboardInterrupt:
        print(f"\nSkipping {chatbot_name}...")
        return None
    
    except Exception as e:
        logger.error(f"Error configuring chatbot: {e}")
        return None

def main():
    """Main function to run the multi-screen configuration tool."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Multi-Screen Configuration Tool")
    parser.add_argument("--screens", type=int, default=0,
                      help="Number of screens to configure for (default: auto-detect)")
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("DragonVoiceProject - Multi-Screen Configuration Tool")
    print("=" * 60)
    
    # Detect screens
    screens = detect_screens()
    if args.screens > 0:
        print(f"User requested {args.screens} screens")
        # Use only the specified number of screens
        screens = screens[:args.screens]
    
    print(f"\nDetected {len(screens)} screens:")
    for i, screen in enumerate(screens):
        print(f"Screen {i+1}: Left={screen['left']}, Top={screen['top']}, Width={screen['width']}, Height={screen['height']}")
    
    # Load existing config
    config = load_config()
    if not config:
        print("Error loading configuration. Please check the log for details.")
        sys.exit(1)
    
    # Ask user which chatbots to configure
    print("\nAvailable chatbots:")
    for i, chatbot in enumerate(CHATBOTS, 1):
        print(f"{i}. {chatbot}")
    
    selected_indices = input("\nEnter the numbers of chatbots to configure (comma-separated, or 'all'): ")
    
    if selected_indices.lower() == 'all':
        selected_chatbots = CHATBOTS
    else:
        try:
            indices = [int(idx.strip()) for idx in selected_indices.split(',')]
            selected_chatbots = [CHATBOTS[i-1] for i in indices if 1 <= i <= len(CHATBOTS)]
        except ValueError:
            print("Invalid input. Using all chatbots.")
            selected_chatbots = CHATBOTS
    
    print(f"\nConfiguring {len(selected_chatbots)} chatbots across {len(screens)} screens")
    
    # Assign chatbots to screens
    screen_assignments = assign_chatbots_to_screens(selected_chatbots, screens)
    
    # Configure each chatbot
    configured_count = 0
    
    for chatbot in selected_chatbots:
        screen_index = screen_assignments.get(chatbot, 0)
        screen_info = screens[screen_index] if 0 <= screen_index < len(screens) else None
        
        print(f"\nChatbot {chatbot} assigned to Screen {screen_index + 1}")
        position = configure_chatbot(chatbot, screen_info)
        
        if position:
            # Normalize chatbot name
            normalized_name = chatbot.lower().replace(" ", "")
            
            # Make sure chatbots section exists
            if "chatbots" not in config:
                config["chatbots"] = {}
                
            # Add or update chatbot configuration
            config["chatbots"][normalized_name] = {
                "title_pattern": chatbot,
                "input_position": [position[0], position[1]],
                "send_method": "enter",
                "typing_delay": 0.05
            }
            
            configured_count += 1
            print(f"Configured {chatbot} with position {position}")
    
    # Save the updated configuration
    if configured_count > 0:
        if save_config(config):
            print(f"\nSuccessfully configured {configured_count}/{len(selected_chatbots)} chatbots")
        else:
            print("\nError saving configuration. Please check the log for details.")
    else:
        print("\nNo chatbots were configured. Configuration not saved.")
    
    print("\n" + "=" * 60)
    print("Configuration complete")
    print("=" * 60)
    
    print("\nYou can now use the DragonVoiceProject voice assistant:")
    print("python src/voice_assistant.py")

if __name__ == "__main__":
    main() 