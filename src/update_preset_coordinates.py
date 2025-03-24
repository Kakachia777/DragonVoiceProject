#!/usr/bin/env python3
"""
Update Preset Coordinates Script

This script updates the config.json file with preset chatbot coordinates.
"""

import os
import sys
import json
import logging
from typing import Dict, List

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

def load_config(config_path: str) -> Dict:
    """
    Load configuration from file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        The configuration dictionary
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        else:
            logger.error(f"Configuration file not found: {config_path}")
            return {}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def save_config(config_path: str, config: Dict) -> bool:
    """
    Save configuration to file
    
    Args:
        config_path: Path to the configuration file
        config: The configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

def update_coordinates(config: Dict, coordinates: List[Dict]) -> Dict:
    """
    Update the chatbot coordinates in the configuration
    
    Args:
        config: The configuration dictionary
        coordinates: List of coordinate dictionaries
        
    Returns:
        The updated configuration dictionary
    """
    try:
        # Create chatbot_input section if it doesn't exist
        if "chatbot_input" not in config:
            config["chatbot_input"] = {}
        
        # Enable chatbot input
        config["chatbot_input"]["enabled"] = True
        
        # Set delay between inputs
        if "delay_between_inputs" not in config["chatbot_input"]:
            config["chatbot_input"]["delay_between_inputs"] = 0.5
        
        # Update coordinates
        config["chatbot_input"]["coordinates"] = coordinates
        
        logger.info(f"Updated configuration with {len(coordinates)} coordinates")
        return config
    except Exception as e:
        logger.error(f"Error updating coordinates: {e}")
        return config

def main():
    """Main entry point"""
    try:
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description="Update Preset Coordinates")
        parser.add_argument('--config', help='Path to config file', default=DEFAULT_CONFIG_PATH)
        parser.add_argument('--clear', help='Clear existing coordinates before adding presets', action='store_true')
        args = parser.parse_args()
        
        # Load configuration
        config = load_config(args.config)
        
        # Check if we should clear existing coordinates
        if args.clear:
            logger.info("Clearing existing coordinates")
            if "chatbot_input" in config and "coordinates" in config["chatbot_input"]:
                config["chatbot_input"]["coordinates"] = []
        
        # Update coordinates
        config = update_coordinates(config, PRESET_COORDINATES)
        
        # Save configuration
        if save_config(args.config, config):
            logger.info("Preset coordinates have been successfully added to the configuration")
            logger.info(f"Total coordinates: {len(PRESET_COORDINATES)}")
            
            # Print coordinates
            for i, coord in enumerate(PRESET_COORDINATES):
                logger.info(f"{i+1}. {coord.get('name', 'Unnamed')} at ({coord['x']}, {coord['y']})")
        else:
            logger.error("Failed to save configuration")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 