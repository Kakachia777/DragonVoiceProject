#!/usr/bin/env python3
"""
Simple test script to check if dragon_gui.py can be imported
"""
import sys
import os

print("Starting test...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    print("Attempting to import dragon_gui...")
    sys.path.append(os.path.abspath("src"))
    import dragon_gui
    print("Import successful!")
    
    # Check if the DragonVoiceGUI class exists
    if hasattr(dragon_gui, 'DragonVoiceGUI'):
        print("DragonVoiceGUI class found")
        
        # Check for required methods
        required_methods = [
            'start_manual_recording',
            'stop_manual_recording',
            'transcribe_last_recording'
        ]
        
        for method in required_methods:
            if hasattr(dragon_gui.DragonVoiceGUI, method):
                print(f"Method '{method}' found")
            else:
                print(f"Method '{method}' NOT found")
    else:
        print("DragonVoiceGUI class NOT found")
    
except Exception as e:
    print(f"Error importing dragon_gui: {str(e)}")
    import traceback
    traceback.print_exc()

print("Test completed") 