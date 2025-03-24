#!/usr/bin/env python3
"""
Test Chatbot Coordinates Script

This script tests the chatbot coordinates by writing "thank you" in each chatbot
and clicking enter. It helps verify that the coordinates are correctly configured.
"""

import os
import sys
import time
import json
import logging
import argparse
import pyautogui
from typing import Dict, List, Optional

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

class ChatbotCoordinateTester:
    """Tests chatbot coordinates by writing text and pressing enter"""
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """
        Initialize the tester
        
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
        
        logger.info("ChatbotCoordinateTester initialized")
    
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

def main():
    """Main entry point"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Test Chatbot Coordinates")
        parser.add_argument('--config', help='Path to config file', default=DEFAULT_CONFIG_PATH)
        parser.add_argument('--message', help='Message to type', default="thank you")
        parser.add_argument('--no-enter', help='Do not press enter after typing', action='store_true')
        parser.add_argument('--index', help='Test only the coordinate at this index (0-based)', type=int)
        args = parser.parse_args()
        
        # Create and run tester
        tester = ChatbotCoordinateTester(config_path=args.config)
        tester.message = args.message
        
        if args.index is not None:
            tester.test_single_coordinate(args.index, args.message, not args.no_enter)
        else:
            tester.test_coordinates(args.message, not args.no_enter)
        
    except KeyboardInterrupt:
        logger.info("Testing aborted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 