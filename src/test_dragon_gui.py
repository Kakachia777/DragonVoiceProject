#!/usr/bin/env python3
"""
Test script to verify that the fixed dragon_gui.py file can be imported without errors
"""
import os
import sys
import importlib.util
import traceback

def test_import(file_path):
    """Test importing a Python file"""
    try:
        print(f"Testing import of {file_path}...")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"✗ Error: File {file_path} does not exist.")
            return False
        
        print(f"File exists. Size: {os.path.getsize(file_path)} bytes")
        
        # Get the module name from the file path
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"Module name: {module_name}")
        
        # Import the module
        print("Importing module...")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        print("Executing module...")
        spec.loader.exec_module(module)
        print("Module executed successfully!")
        
        # Check if the DragonVoiceGUI class exists
        if hasattr(module, 'DragonVoiceGUI'):
            print("✓ DragonVoiceGUI class found")
            
            # Check for required methods
            required_methods = [
                'load_config', 
                'setup_theme',
                'toggle_voice_assistant',
                'create_dashboard_tab',
                'create_chatbots_tab',
                'create_about_tab',
                'start_manual_recording',
                'stop_manual_recording',
                'transcribe_last_recording'
            ]
            
            for method in required_methods:
                if hasattr(module.DragonVoiceGUI, method):
                    print(f"✓ DragonVoiceGUI.{method} method found")
                else:
                    print(f"✗ DragonVoiceGUI.{method} method NOT found")
        else:
            print("✗ DragonVoiceGUI class NOT found")
            
        # Check if the main function exists
        if hasattr(module, 'main'):
            print("✓ main function found")
        else:
            print("✗ main function NOT found")
            
        print("Import test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error importing {file_path}: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Test the fixed file
    fixed_file = "src/dragon_gui.py.fixed"
    
    # Add the src directory to the Python path
    sys.path.append(os.path.abspath("src"))
    print(f"Python path: {sys.path}")
    
    # Test the import
    success = test_import(fixed_file)
    
    if success:
        print("\nThe fixed file can be imported without errors!")
    else:
        print("\nThe fixed file has import errors. Please check the error messages above.") 