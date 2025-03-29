"""
Dragon Voice Assistant Executable Builder
This script builds the DragonVoice.exe executable with all necessary dependencies
and creates a pinnable shortcut for Windows taskbar.
"""

import os
import sys
import subprocess
import shutil
import time
import traceback
from pathlib import Path

def install_requirements():
    """Install necessary requirements for the build"""
    print("Checking and installing requirements...")
    requirements = [
        "pyinstaller",
        "pillow",
        "pyperclip",
        "pyautogui",
        "numpy",
        "sounddevice",
        "scipy",
        "soundfile",
        "requests"
    ]
    
    for req in requirements:
        try:
            __import__(req)
            print(f"√ {req} is already installed")
        except ImportError:
            print(f"Installing {req}...")
            subprocess.run([sys.executable, "-m", "pip", "install", req], check=True)
            print(f"√ {req} installed successfully")

def clean_build_directories():
    """Clean existing build and dist directories with better error handling"""
    print("Cleaning build directories...")
    
    directories_to_clean = ['build', 'dist', '__pycache__']
    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"Attempting to remove {directory}/")
            try:
                shutil.rmtree(directory)
                print(f"Successfully removed {directory}/")
            except PermissionError as e:
                print(f"Warning: Permission error removing {directory}/: {e}")
                print(f"Will attempt to continue anyway.")
            except Exception as e:
                print(f"Warning: Error removing {directory}/: {e}")
                print(f"Will attempt to continue anyway.")
    
    # Remove any .spec files
    try:
        for spec_file in Path(".").glob("*.spec"):
            try:
                print(f"Removing {spec_file}")
                os.remove(spec_file)
            except Exception as e:
                print(f"Warning: Could not remove {spec_file}: {e}")
    except Exception as e:
        print(f"Warning: Error while searching for spec files: {e}")

def ensure_output_directories():
    """Ensure output directories exist"""
    print("Setting up output directories...")
    
    # Main output directory
    if not os.path.exists("output"):
        os.makedirs("output")
    
    # Dragon Voice directory
    if not os.path.exists("output/DragonVoice"):
        os.makedirs("output/DragonVoice")
    else:
        # Clean the directory but keep it
        for file in os.listdir("output/DragonVoice"):
            file_path = os.path.join("output/DragonVoice", file)
            if os.path.isfile(file_path):
                os.remove(file_path)

def build_dragon_voice():
    """Build the executable for Dragon Voice"""
    print("\n=== Building Dragon Voice Assistant (DragonVoice.exe) ===")
    start_time = time.time()
    
    try:
        # Copy assets to current directory if not already there
        if os.path.exists("assets"):
            if not os.path.exists("dragon_icon.ico") and os.path.exists("assets/dragon_icon.ico"):
                shutil.copy("assets/dragon_icon.ico", ".")
                print("Copied icon from assets folder")
        
        # Create necessary directories
        os.makedirs("dist", exist_ok=True)
        os.makedirs("dist/DragonVoice", exist_ok=True)
        os.makedirs("recordings", exist_ok=True)
        os.makedirs("transcripts", exist_ok=True)

        # Create the PyInstaller command with options to avoid permission issues
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",  # Clean PyInstaller cache before building
            "--name=DragonVoice",
            "--onefile",
            "--noconsole",  # Use --noconsole for windowed mode
            "--icon=dragon_icon.ico",
            "--add-data=dragon_icon.ico;.",
            "--add-data=config.json;.",
            "--add-binary=Dragon_cli2.py;.",  # Include the backend script directly
            "--distpath=output/DragonVoice",  # Output directly to final location
            "--workpath=build_temp",  # Use a different build directory
            "--specpath=build_temp",  # Put spec file in build_temp
            "dragon_gui_enhanced_a.py"  # Use enhanced GUI
        ]
        
        # Run the command
        print("Running PyInstaller...")
        print(f"Command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Ensure output directory exists
        os.makedirs("output/DragonVoice", exist_ok=True)
        
        # Copy necessary directories and files
        print("Copying additional files to output directory...")
        
        # Create required directories
        os.makedirs("output/DragonVoice/recordings", exist_ok=True)
        os.makedirs("output/DragonVoice/transcripts", exist_ok=True)
        print("Created recordings and transcripts directories")
        
        # Copy necessary files if they're not already there
        required_files = [
            "dragon_icon.ico",
            "config.json",
        ]
        
        for file in required_files:
            dest_file = os.path.join("output/DragonVoice", file)
            # Only copy if the file exists and the destination doesn't
            if os.path.exists(file) and not os.path.exists(dest_file):
                try:
                    shutil.copy(file, "output/DragonVoice/")
                    print(f"Copied {file}")
                except Exception as e:
                    print(f"Warning: Could not copy {file}: {e}")
            elif not os.path.exists(file):
                print(f"Warning: {file} not found, skipping")
        
        # Create README file
        with open("output/DragonVoice/README.txt", "w") as f:
            f.write("Dragon Voice Assistant\n")
            f.write("=======================\n\n")
            f.write("QUICK START:\n")
            f.write("1. Double-click DragonVoice.exe to start the application\n")
            f.write("2. Hold the SPACE key to record your voice (release to process)\n")
            f.write("3. Your message will be sent to all configured chatbots\n\n")
            f.write("PINNING TO TASKBAR:\n")
            f.write("1. Start the application by double-clicking DragonVoice.exe\n")
            f.write("2. Right-click on the application icon in the taskbar\n")
            f.write("3. Select 'Pin to taskbar'\n")
            f.write("4. Now you can launch directly from your taskbar anytime!\n\n")
            f.write("KEYBOARD SHORTCUTS:\n")
            f.write("- SPACE: Press and hold to record, release to process\n")
            f.write("- F10: Quick Mode (record and send automatically)\n")
            f.write("- F11: Retry Failed\n")
            f.write("- F12: Settings\n\n")
            f.write("TROUBLESHOOTING:\n")
            f.write("- Make sure all files remain in the same folder\n")
            f.write("- If it won't start, try running as administrator\n")
            f.write("- Check that your microphone is connected\n")
        
        # Create Windows-compatible shortcut
        create_windows_shortcut()
        
        # Report success
        end_time = time.time()
        print(f"Build completed in {end_time - start_time:.2f} seconds")
        print(f"Executable created at: output/DragonVoice/DragonVoice.exe")
        
        return True
    except Exception as e:
        print(f"Error building Dragon Voice: {e}")
        traceback.print_exc()
        return False

def create_windows_shortcut():
    """Create a Windows shortcut that can be pinned to taskbar"""
    try:
        # Get the absolute path to the executable
        exe_path = os.path.abspath("output/DragonVoice/DragonVoice.exe")
        shortcut_path = os.path.abspath("output/DragonVoice/DragonVoice.lnk")
        
        # Get the directory containing the executable
        working_dir = os.path.dirname(exe_path)
        
        # PowerShell script to create shortcut with all required properties
        ps_script = f"""
try {{
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
    $Shortcut.TargetPath = "{exe_path}"
    $Shortcut.WorkingDirectory = "{working_dir}"
    $Shortcut.IconLocation = "{exe_path},0"
    $Shortcut.Description = "Dragon Voice Assistant"
    $Shortcut.WindowStyle = 1
    $Shortcut.Save()
    
    # Add registry compatibility info to make pinning more reliable
    if (Test-Path "{shortcut_path}") {{
        $bytes = [System.IO.File]::ReadAllBytes("{shortcut_path}")
        $bytes[0x15] = $bytes[0x15] -bor 0x20 #set bit 5
        [System.IO.File]::WriteAllBytes("{shortcut_path}", $bytes)
        Write-Host "Shortcut created and optimized for pinning successfully"
    }} else {{
        Write-Host "Warning: Shortcut file not found after creation"
    }}
}} catch {{
    Write-Host "Error creating shortcut: $_"
}}
        """
        
        # Write the PowerShell script to a temporary file
        with open("create_shortcut.ps1", "w") as f:
            f.write(ps_script)
        
        # Execute the PowerShell script
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "create_shortcut.ps1"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Clean up
        try:
            os.remove("create_shortcut.ps1")
        except:
            print("Note: Couldn't remove temporary PowerShell script file")
        
        print(f"Created pinnable shortcut: {shortcut_path}")
        
        # Also create a desktop shortcut for easier access
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            desktop_shortcut = os.path.join(desktop_path, "DragonVoice.lnk")
            
            desktop_script = f"""
try {{
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{desktop_shortcut}")
    $Shortcut.TargetPath = "{exe_path}"
    $Shortcut.WorkingDirectory = "{working_dir}"
    $Shortcut.IconLocation = "{exe_path},0"
    $Shortcut.Description = "Dragon Voice Assistant"
    $Shortcut.WindowStyle = 1
    $Shortcut.Save()
    Write-Host "Desktop shortcut created successfully"
}} catch {{
    Write-Host "Error creating desktop shortcut: $_"
}}
            """
            
            with open("create_desktop_shortcut.ps1", "w") as f:
                f.write(desktop_script)
            
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "create_desktop_shortcut.ps1"],
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Clean up
            try:
                os.remove("create_desktop_shortcut.ps1")
            except:
                pass
                
            print(f"Created desktop shortcut at: {desktop_shortcut}")
        except Exception as e:
            print(f"Note: Could not create desktop shortcut: {e}")
        
        return True
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False

def create_run_batch_file():
    """Create a simple batch file to run the executable"""
    try:
        batch_path = "output/DragonVoice/Run_DragonVoice.bat"
        with open(batch_path, "w") as f:
            f.write('@echo off\n')
            f.write('echo Starting Dragon Voice Assistant...\n')
            f.write('start "" "%~dp0DragonVoice.exe"\n')
        
        print(f"Created batch file: {batch_path}")
        return True
    except Exception as e:
        print(f"Error creating batch file: {e}")
        return False

def main():
    """Main build function"""
    print("=== Dragon Voice Executable Builder ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Install requirements
    install_requirements()
    
    # Clean build directories
    clean_build_directories()
    
    # Create output directories
    ensure_output_directories()
    
    # Build the executable
    if build_dragon_voice():
        # Create batch file for easy running
        create_run_batch_file()
        
        print("\n=== Build Successful ===")
        print("The executable is located at output/DragonVoice/DragonVoice.exe")
        print("You can pin it to your taskbar by:")
        print("1. Double-clicking the executable")
        print("2. Right-clicking the icon in your taskbar")
        print("3. Selecting 'Pin to taskbar'")
        return 0
    else:
        print("\n=== Build Failed ===")
        print("Check the error messages above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 