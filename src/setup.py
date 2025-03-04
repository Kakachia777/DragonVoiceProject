#!/usr/bin/env python3
"""
DragonVoiceProject - Setup Script

This script helps set up the Dragon Voice Project by:
1. Checking and installing required dependencies
2. Creating and configuring the Dragon output file
3. Testing the system components
4. Setting up autostart (optional)

Usage:
    python setup.py

Requirements:
    - Python 3.x
"""

import os
import sys
import json
import shutil
import subprocess
import traceback

# Required packages for the project
REQUIRED_PACKAGES = [
    "pygetwindow",
    "pyautogui",
    "pyperclip",
    "win10toast"  # For notifications
]

# Default configuration
DEFAULT_CONFIG = {
    "integration": {
        "mode": "file",
        "file_path": "C:/dragon_query.txt",
        "polling_interval": 1.0,
        "command_prefix": "search for"
    },
    "browser": {
        "window_title_pattern": "Chrome",
        "typing_delay": 0.05,
        "window_switch_delay": 0.5
    },
    "feedback": {
        "audio_enabled": True,
        "popup_enabled": True,
        "log_queries": True,
        "log_file": "dragon_voice_queries.log"
    },
    "advanced": {
        "max_retries": 3,
        "retry_delay": 1.0,
        "search_timeout": 5.0
    }
}

# Path to config file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def print_header(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def check_python_version():
    """Check if the Python version is compatible."""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("Error: Python 3.6 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"Python version OK: {sys.version}")
    return True


def check_install_packages():
    """Check and install required packages."""
    print("\nChecking required packages...")
    
    missing_packages = []
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nInstalling missing packages...")
        try:
            for package in missing_packages:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            print("Please install the missing packages manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True


def setup_dragon_file():
    """Set up the Dragon output file."""
    print("\nSetting up Dragon output file...")
    
    # Load configuration
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = DEFAULT_CONFIG
    
    file_path = config["integration"]["file_path"]
    print(f"Dragon output file path: {file_path}")
    
    # Check if file already exists
    if os.path.exists(file_path):
        print(f"Dragon output file already exists: {file_path}")
        overwrite = input("Do you want to reset the file? (y/n): ").lower() == 'y'
        
        if overwrite:
            try:
                with open(file_path, 'w') as f:
                    f.write("")
                print(f"Dragon output file reset: {file_path}")
            except Exception as e:
                print(f"Error resetting file: {e}")
                return False
    else:
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create an empty file
            with open(file_path, 'w') as f:
                f.write("")
            
            print(f"Dragon output file created: {file_path}")
        except Exception as e:
            print(f"Error creating file: {e}")
            print(f"Please create the file manually at: {file_path}")
            return False
    
    return True


def update_configuration():
    """Update the configuration file."""
    print("\nChecking configuration...")
    
    # Check if config file exists
    if os.path.exists(CONFIG_FILE):
        print(f"Configuration file found: {CONFIG_FILE}")
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            print("Configuration loaded successfully.")
        except json.JSONDecodeError:
            print("Error: Configuration file is invalid.")
            create_new = input("Create a new default configuration file? (y/n): ").lower() == 'y'
            
            if create_new:
                config = DEFAULT_CONFIG
            else:
                return False
    else:
        print("Configuration file not found.")
        config = DEFAULT_CONFIG
        print("Created default configuration.")
    
    # Ask user if they want to modify the configuration
    modify = input("\nDo you want to modify the configuration? (y/n): ").lower() == 'y'
    
    if modify:
        # Integration settings
        print("\nIntegration Settings:")
        mode_options = {
            "1": "file",
            "2": "clipboard"
        }
        print("Integration mode:")
        print("  1. File monitoring (recommended)")
        print("  2. Clipboard monitoring")
        mode_choice = input(f"Choose mode [1-2, default: {1 if config['integration']['mode'] == 'file' else 2}]: ").strip()
        
        if mode_choice in mode_options:
            config["integration"]["mode"] = mode_options[mode_choice]
        
        if config["integration"]["mode"] == "file":
            file_path = input(f"Dragon output file path [default: {config['integration']['file_path']}]: ").strip()
            if file_path:
                config["integration"]["file_path"] = file_path
        
        interval = input(f"Polling interval in seconds [default: {config['integration']['polling_interval']}]: ").strip()
        if interval and interval.replace('.', '', 1).isdigit():
            config["integration"]["polling_interval"] = float(interval)
        
        prefix = input(f"Command prefix [default: '{config['integration']['command_prefix']}'] (leave empty for none): ").strip()
        config["integration"]["command_prefix"] = prefix
        
        # Browser settings
        print("\nBrowser Settings:")
        pattern = input(f"Browser window title pattern [default: '{config['browser']['window_title_pattern']}']: ").strip()
        if pattern:
            config["browser"]["window_title_pattern"] = pattern
        
        delay = input(f"Typing delay in seconds [default: {config['browser']['typing_delay']}]: ").strip()
        if delay and delay.replace('.', '', 1).isdigit():
            config["browser"]["typing_delay"] = float(delay)
        
        # Feedback settings
        print("\nFeedback Settings:")
        config["feedback"]["audio_enabled"] = input(f"Enable audio feedback? (y/n) [default: {'y' if config['feedback']['audio_enabled'] else 'n'}]: ").lower() == 'y'
        config["feedback"]["popup_enabled"] = input(f"Enable popup notifications? (y/n) [default: {'y' if config['feedback']['popup_enabled'] else 'n'}]: ").lower() == 'y'
        config["feedback"]["log_queries"] = input(f"Log queries? (y/n) [default: {'y' if config['feedback']['log_queries'] else 'n'}]: ").lower() == 'y'
    
    # Save the configuration
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"\nConfiguration saved to: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def test_system_components():
    """Test the system components."""
    print_header("System Component Tests")
    
    # Test if quick_test.py exists
    quick_test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quick_test.py")
    if not os.path.exists(quick_test_path):
        print("Error: quick_test.py not found.")
        return False
    
    # Test if dragon_monitor.py exists
    dragon_monitor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dragon_monitor.py")
    if not os.path.exists(dragon_monitor_path):
        print("Error: dragon_monitor.py not found.")
        return False
    
    print("All required components found.")
    
    # Ask if user wants to run quick_test.py
    run_quick_test = input("\nDo you want to run a quick browser automation test? (y/n): ").lower() == 'y'
    
    if run_quick_test:
        print("\nRunning quick_test.py...")
        print("Please follow the instructions in the terminal.")
        
        try:
            subprocess.run([sys.executable, quick_test_path], check=True)
            print("\nQuick test completed.")
        except subprocess.CalledProcessError as e:
            print(f"Error running quick_test.py: {e}")
            return False
    
    return True


def setup_autostart():
    """Set up autostart for Dragon Voice Project."""
    print_header("Autostart Setup")
    
    setup_auto = input("Do you want to set up Dragon Voice Project to start automatically? (y/n): ").lower() == 'y'
    
    if not setup_auto:
        print("Autostart setup skipped.")
        return True
    
    # Get the path to the dragon_monitor.py script
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dragon_monitor.py")
    
    # Create a batch file to run the script
    batch_content = f"""@echo off
echo Starting Dragon Voice Project...
cd /d "{os.path.dirname(os.path.abspath(__file__))}"
"{sys.executable}" "{script_path}"
"""
    
    batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_dragon_voice.bat")
    
    try:
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        print(f"Batch file created: {batch_path}")
    except Exception as e:
        print(f"Error creating batch file: {e}")
        return False
    
    # Create a shortcut in the startup folder
    try:
        import winshell
        from win32com.client import Dispatch
        
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Dragon Voice Project.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = batch_path
        shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print(f"Shortcut created in startup folder: {shortcut_path}")
        print("Dragon Voice Project will start automatically when you log in.")
        
        return True
    
    except ImportError:
        print("Note: winshell or pywin32 not installed. Please add the program to autostart manually.")
        print(f"To start the program, run: {batch_path}")
        
        # Copy the batch file to the desktop for convenience
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            desktop_batch = os.path.join(desktop, "Start Dragon Voice Project.bat")
            shutil.copy2(batch_path, desktop_batch)
            print(f"Batch file copied to desktop: {desktop_batch}")
        except:
            pass
        
        return True
    
    except Exception as e:
        print(f"Error setting up autostart: {e}")
        print(f"To start the program, run: {batch_path}")
        return False


def main():
    """Main function."""
    print_header("Dragon Voice Project - Setup")
    print("This script will help you set up the Dragon Voice Project.")
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check and install required packages
    if not check_install_packages():
        input("Press Enter to continue anyway...")
    
    # Update configuration
    if not update_configuration():
        print("Configuration setup failed.")
        input("Press Enter to continue anyway...")
    
    # Set up Dragon output file
    if not setup_dragon_file():
        print("Dragon output file setup failed.")
        input("Press Enter to continue anyway...")
    
    # Test system components
    if not test_system_components():
        print("System component tests failed.")
        input("Press Enter to continue anyway...")
    
    # Set up autostart
    if not setup_autostart():
        print("Autostart setup failed.")
        input("Press Enter to continue anyway...")
    
    print_header("Setup Complete")
    print("""
Dragon Voice Project setup is complete! Here's what you can do now:

1. Test basic functionality:
   - Run 'python quick_test.py' to test browser automation

2. Start Dragon integration:
   - Run 'python dragon_monitor.py' to start monitoring
   - Or use the batch file/shortcut created during setup

3. Configure Dragon Medical One:
   - Set up Dragon to output dictation to the configured file
   - Use the command prefix (e.g., "search for") to trigger searches

For more information, refer to the documentation.
""")
    
    input("Press Enter to exit setup...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...") 