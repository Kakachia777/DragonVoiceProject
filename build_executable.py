import os
import sys
import subprocess
import shutil
import platform

def install_requirements():
    """Install required packages for the application"""
    print("Installing required packages...")
    
    requirements = [
        "pyinstaller",  # For creating the executable
        "numpy",
        "pyaudio",
        "sounddevice",
        "soundfile",
        "requests",
        "pyperclip",
        "keyboard",
        "pillow",  # For PIL.Image
        "python-dotenv",
        "pywin32",  # For Windows-specific functionality
        "pyautogui"
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}. Please install it manually with: pip install {package}")
            return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Determine the script name
    script_name = "dragon_gui_enhanced_a.py"
    if not os.path.exists(script_name):
        print(f"Error: {script_name} not found. Make sure you're in the correct directory.")
        return False
    
    # Check if icon exists
    icon_path = "dragon_icon.ico"
    if not os.path.exists(icon_path):
        print("Warning: Icon file not found. Creating executable without custom icon.")
        pyinstaller_cmd = [
            "pyinstaller",
            "--name=DragonVoiceAssistant",
            "--onefile",  # Create a single executable
            "--windowed",  # Don't show console window
            "--clean",
            "--add-data=Dragon_cli2.py;.",  # Include CLI module
            script_name
        ]
    else:
        pyinstaller_cmd = [
            "pyinstaller",
            "--name=DragonVoiceAssistant",
            "--onefile",  # Create a single executable
            "--windowed",  # Don't show console window
            f"--icon={icon_path}",  # Use the icon file
            "--clean",
            "--add-data=Dragon_cli2.py;.",  # Include CLI module
            script_name
        ]
    
    try:
        subprocess.check_call(pyinstaller_cmd)
        print("Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

def setup_app_for_exe():
    """Make modifications to the app for better executable behavior"""
    # Create folders that may be needed at runtime
    os.makedirs("recordings", exist_ok=True)
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Copy the executable to a convenient location
    if os.path.exists("dist/DragonVoiceAssistant.exe"):
        dest_path = os.path.expanduser("~/Desktop/DragonVoiceAssistant.exe")
        try:
            shutil.copy2("dist/DragonVoiceAssistant.exe", dest_path)
            print(f"Executable copied to Desktop: {dest_path}")
        except Exception as e:
            print(f"Error copying executable to Desktop: {e}")
    
    # Create shortcut for pinning (Windows only)
    if platform.system() == "Windows":
        try:
            import win32com.client
            desktop = os.path.expanduser("~/Desktop")
            shortcut_path = os.path.join(desktop, "DragonVoiceAssistant.lnk")
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = os.path.abspath("dist/DragonVoiceAssistant.exe")
            shortcut.WorkingDirectory = os.path.abspath("dist")
            
            if os.path.exists("dragon_icon.ico"):
                shortcut.IconLocation = os.path.abspath("dragon_icon.ico")
                
            shortcut.save()
            print(f"Shortcut created at: {shortcut_path}")
            print("You can now pin this shortcut to your taskbar.")
            
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            print("Please create a shortcut manually and pin it to your taskbar.")

def main():
    """Main function to build the executable"""
    print("==== Dragon Voice Assistant - Executable Builder ====")
    
    # Install requirements
    if not install_requirements():
        print("Failed to install all required packages. Continuing anyway...")
    
    # Build executable
    if build_executable():
        setup_app_for_exe()
        
        print("\n=== Instructions ===")
        print("1. The executable has been created in the 'dist' folder.")
        print("2. A copy has been placed on your Desktop.")
        print("3. You can pin the shortcut to your taskbar by right-clicking it and selecting 'Pin to taskbar'.")
        
        print("\n=== Required Libraries ===")
        print("The following Python libraries are required for development:")
        print("- numpy: For numerical operations")
        print("- pyaudio: For audio recording (may require additional system dependencies)")
        print("- sounddevice: For audio processing")
        print("- soundfile: For audio file handling")
        print("- requests: For API communication")
        print("- pyperclip: For clipboard operations")
        print("- keyboard: For global keyboard shortcuts")
        print("- pillow (PIL): For image processing")
        print("- python-dotenv: For environment variable handling")
        print("- pywin32: For Windows-specific functionality")
        print("- pyautogui: For GUI automation")
        
        print("\nThe executable should include all these dependencies.")
        
        print("\nIf you encounter any issues, please ensure these libraries are installed with:")
        print("pip install numpy pyaudio sounddevice soundfile requests pyperclip keyboard pillow python-dotenv pywin32 pyautogui")
    else:
        print("Failed to build executable.")

if __name__ == "__main__":
    main() 