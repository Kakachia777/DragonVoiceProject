#!/usr/bin/env python3
"""
Chatbot Coordinate Manager

A comprehensive tool for managing and testing chatbot coordinates.
This script combines functionality to:
1. Update config.json with preset coordinates
2. Test coordinates by typing messages in chatbots
3. View current coordinates

Usage:
    python chatbot_coordinate_manager.py
"""

import os
import sys
import time
import json
import logging
import pyautogui
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

# Safety settings for pyautogui
pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort
pyautogui.PAUSE = 0.5  # Add pause between PyAutoGUI commands

# Preset coordinates
PRESET_COORDINATES = [
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
    {"name": "Unknown", "x": 7992, "y": 1350}
]

class ChatbotCoordinateManager:
    """Manages and tests chatbot coordinates"""
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """
        Initialize the manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self.load_config()
        
        # Default message to type
        self.message = "thank you"
        
        # Set mouse speed (lower is faster)
        self.mouse_speed = 0.3
        
        # Delay between actions
        self.action_delay = 0.5
        
        logger.info("ChatbotCoordinateManager initialized")
    
    def load_config(self) -> Dict:
        """
        Load configuration from file
        
        Returns:
            The configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
            else:
                logger.error(f"Configuration file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def save_config(self, config: Dict) -> bool:
        """
        Save configuration to file
        
        Args:
            config: The configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_chatbot_coordinates(self) -> List[Dict]:
        """
        Get chatbot coordinates from the configuration
        
        Returns:
            List of chatbot coordinates
        """
        try:
            # Check if chatbot input is enabled and coordinates are configured
            if not self.config.get("chatbot_input", {}).get("enabled", False):
                logger.warning("Chatbot input is not enabled in the configuration")
                return []
            
            coordinates = self.config.get("chatbot_input", {}).get("coordinates", [])
            if not coordinates:
                logger.warning("No chatbot coordinates configured")
                return []
            
            return coordinates
        except Exception as e:
            logger.error(f"Error getting chatbot coordinates: {e}")
            return []
    
    def update_coordinates(self, coordinates: List[Dict], clear_existing: bool = False) -> bool:
        """
        Update the chatbot coordinates in the configuration
        
        Args:
            coordinates: List of coordinate dictionaries
            clear_existing: Whether to clear existing coordinates before adding new ones
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create chatbot_input section if it doesn't exist
            if "chatbot_input" not in self.config:
                self.config["chatbot_input"] = {}
            
            # Enable chatbot input
            self.config["chatbot_input"]["enabled"] = True
            
            # Set delay between inputs
            if "delay_between_inputs" not in self.config["chatbot_input"]:
                self.config["chatbot_input"]["delay_between_inputs"] = 0.5
            
            # Update coordinates
            if clear_existing:
                self.config["chatbot_input"]["coordinates"] = coordinates
                logger.info(f"Replaced coordinates with {len(coordinates)} new coordinates")
            else:
                # Merge coordinates, avoiding duplicates by name
                existing_coords = self.config["chatbot_input"].get("coordinates", [])
                existing_names = {c.get("name", f"Unnamed-{i}"): i 
                                 for i, c in enumerate(existing_coords) 
                                 if "name" in c}
                
                for coord in coordinates:
                    name = coord.get("name", "")
                    if name and name in existing_names:
                        # Replace existing coordinate with same name
                        existing_coords[existing_names[name]] = coord
                        logger.info(f"Updated coordinate for '{name}'")
                    else:
                        # Add new coordinate
                        existing_coords.append(coord)
                        logger.info(f"Added new coordinate for '{name}'")
                
                self.config["chatbot_input"]["coordinates"] = existing_coords
                logger.info(f"Updated configuration with {len(existing_coords)} total coordinates")
            
            # Save configuration
            return self.save_config(self.config)
            
        except Exception as e:
            logger.error(f"Error updating coordinates: {e}")
            return False
    
    def test_coordinates(self, message: Optional[str] = None, press_enter: bool = True):
        """
        Test chatbot coordinates by writing text and optionally pressing enter
        
        Args:
            message: Message to type (defaults to self.message)
            press_enter: Whether to press enter after typing
        """
        if message is None:
            message = self.message
        
        coordinates = self.get_chatbot_coordinates()
        if not coordinates:
            logger.error("No coordinates to test")
            return
        
        logger.info(f"Testing {len(coordinates)} chatbot coordinates")
        logger.info(f"Message to type: '{message}'")
        logger.info("Press Ctrl+C to abort")
        
        # Give user time to switch to the browser window
        logger.info("Starting in 5 seconds... Switch to your browser window!")
        for i in range(5, 0, -1):
            logger.info(f"{i}...")
            time.sleep(1)
        
        # Test each coordinate
        for i, coord in enumerate(coordinates):
            try:
                name = coord.get("name", f"Chatbot {i+1}")
                x, y = coord.get("x"), coord.get("y")
                
                logger.info(f"Testing {name} at ({x}, {y})")
                
                # Move to coordinate
                pyautogui.moveTo(x, y, duration=self.mouse_speed)
                time.sleep(self.action_delay)
                
                # Click to focus
                pyautogui.click()
                time.sleep(self.action_delay)
                
                # Clear any existing text (Ctrl+A then Delete)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.2)
                pyautogui.press('delete')
                time.sleep(0.2)
                
                # Type the message
                pyautogui.write(message)
                time.sleep(self.action_delay)
                
                # Press enter if requested
                if press_enter:
                    pyautogui.press('enter')
                
                logger.info(f"Successfully tested {name}")
                
                # Wait before moving to the next chatbot
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error testing {name}: {e}")
        
        logger.info("Testing completed")
    
    def test_single_coordinate(self, index: int, message: Optional[str] = None, press_enter: bool = True):
        """
        Test a single chatbot coordinate by index
        
        Args:
            index: Index of the coordinate to test (0-based)
            message: Message to type (defaults to self.message)
            press_enter: Whether to press enter after typing
        """
        if message is None:
            message = self.message
        
        coordinates = self.get_chatbot_coordinates()
        if not coordinates:
            logger.error("No coordinates to test")
            return
        
        if index < 0 or index >= len(coordinates):
            logger.error(f"Invalid index: {index}. Valid range: 0-{len(coordinates)-1}")
            return
        
        coord = coordinates[index]
        name = coord.get("name", f"Chatbot {index+1}")
        x, y = coord.get("x"), coord.get("y")
        
        logger.info(f"Testing {name} at ({x}, {y})")
        logger.info(f"Message to type: '{message}'")
        logger.info("Press Ctrl+C to abort")
        
        # Give user time to switch to the browser window
        logger.info("Starting in 5 seconds... Switch to your browser window!")
        for i in range(5, 0, -1):
            logger.info(f"{i}...")
            time.sleep(1)
        
        try:
            # Move to coordinate
            pyautogui.moveTo(x, y, duration=self.mouse_speed)
            time.sleep(self.action_delay)
            
            # Click to focus
            pyautogui.click()
            time.sleep(self.action_delay)
            
            # Clear any existing text (Ctrl+A then Delete)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)
            
            # Type the message
            pyautogui.write(message)
            time.sleep(self.action_delay)
            
            # Press enter if requested
            if press_enter:
                pyautogui.press('enter')
            
            logger.info(f"Successfully tested {name}")
            
        except Exception as e:
            logger.error(f"Error testing {name}: {e}")
        
        logger.info("Testing completed")
    
    def view_coordinates(self):
        """Display the current chatbot coordinates"""
        coordinates = self.get_chatbot_coordinates()
        if not coordinates:
            logger.info("No chatbot coordinates configured")
            return
        
        logger.info(f"Current chatbot coordinates ({len(coordinates)} total):")
        print("\n" + "="*60)
        print(f"{'Index':<6}{'Name':<25}{'X':<10}{'Y':<10}")
        print("-"*60)
        
        for i, coord in enumerate(coordinates):
            name = coord.get("name", f"Chatbot {i+1}")
            x, y = coord.get("x"), coord.get("y")
            print(f"{i:<6}{name:<25}{x:<10}{y:<10}")
        
        print("="*60 + "\n")
        
        # Check if chatbot input is enabled
        enabled = self.config.get("chatbot_input", {}).get("enabled", False)
        delay = self.config.get("chatbot_input", {}).get("delay_between_inputs", 0.5)
        
        print(f"Chatbot input enabled: {enabled}")
        print(f"Delay between inputs: {delay} seconds\n")

def get_user_confirmation(prompt: str, default: bool = True) -> bool:
    """
    Get confirmation from the user
    
    Args:
        prompt: The prompt to display
        default: Default value if user just presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response.startswith('y')

def interactive_menu() -> Tuple[str, Dict]:
    """
    Display an interactive menu and get user selection
    
    Returns:
        Tuple of (command, args)
    """
    print("\n" + "="*60)
    print("Chatbot Coordinate Manager - Interactive Menu")
    print("="*60)
    print("1. Update with preset coordinates")
    print("2. Test all coordinates")
    print("3. Test a specific coordinate")
    print("4. View current coordinates")
    print("5. Exit")
    print("="*60)
    
    choice = input("Enter your choice (1-5): ").strip()
    
    args = {}
    
    if choice == "1":
        clear = get_user_confirmation("Clear existing coordinates?", False)
        args["clear"] = clear
        return "update", args
    elif choice == "2":
        message = input("Enter message to type (default: 'thank you'): ").strip()
        if message:
            args["message"] = message
        
        press_enter = get_user_confirmation("Press Enter after typing?", True)
        args["press_enter"] = press_enter
        
        return "test", args
    elif choice == "3":
        index = input("Enter coordinate index to test: ").strip()
        try:
            args["index"] = int(index)
        except ValueError:
            print("Invalid index. Using index 0.")
            args["index"] = 0
        
        message = input("Enter message to type (default: 'thank you'): ").strip()
        if message:
            args["message"] = message
        
        press_enter = get_user_confirmation("Press Enter after typing?", True)
        args["press_enter"] = press_enter
        
        return "test_single", args
    elif choice == "4":
        return "view", args
    elif choice == "5":
        return "exit", args
    else:
        print("Invalid choice. Please try again.")
        return interactive_menu()

def main():
    """Main entry point"""
    try:
        # Create manager
        manager = ChatbotCoordinateManager()
        
        # Run interactive menu
        while True:
            command, command_args = interactive_menu()
            
            if command == "exit":
                logger.info("Exiting")
                break
            elif command == "update":
                logger.info("Updating coordinates with presets")
                if manager.update_coordinates(PRESET_COORDINATES, command_args.get("clear", False)):
                    logger.info("Preset coordinates have been successfully added to the configuration")
                else:
                    logger.error("Failed to update coordinates")
            elif command == "test":
                logger.info("Testing all coordinates")
                manager.test_coordinates(
                    command_args.get("message", "thank you"),
                    command_args.get("press_enter", True)
                )
            elif command == "test_single":
                index = command_args.get("index", 0)
                logger.info(f"Testing coordinate at index {index}")
                manager.test_single_coordinate(
                    index,
                    command_args.get("message", "thank you"),
                    command_args.get("press_enter", True)
                )
            elif command == "view":
                manager.view_coordinates()
            
            # Pause before showing menu again
            input("\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        logger.info("Operation aborted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
