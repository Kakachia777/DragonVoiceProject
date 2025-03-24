#!/usr/bin/env python3
"""
Script to run dragon_gui.py with detailed error output
"""
import sys
import os
import traceback
import logging

# Configure logging to show all messages
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def run_dragon_gui():
    """Run the DragonVoiceGUI application with detailed error handling"""
    try:
        print("Starting DragonVoiceGUI application...")
        
        # Add the src directory to the Python path
        sys.path.append(os.path.abspath("src"))
        
        # Import the dragon_gui module
        import dragon_gui
        
        # Call the main function
        print("Calling dragon_gui.main()...")
        dragon_gui.main()
        
    except Exception as e:
        print(f"Error running DragonVoiceGUI: {str(e)}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        
        # Print additional debugging information
        print("\nSystem information:")
        print(f"Python version: {sys.version}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        
        # Check if the required modules are available
        try:
            import tkinter
            print("tkinter is available")
        except ImportError:
            print("tkinter is NOT available")
        
        try:
            import customtkinter
            print("customtkinter is available")
        except ImportError:
            print("customtkinter is NOT available")
        
        try:
            import PIL
            print("PIL is available")
        except ImportError:
            print("PIL is NOT available")

if __name__ == "__main__":
    run_dragon_gui() 