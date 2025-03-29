"""
Simple Dragon Voice Assistant Build Script
This script creates a standalone executable without requiring cleanup of existing directories.
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

def build_executable():
    """Build the executable using PyInstaller with a fresh directory structure"""
    print("\n=== Building Dragon Voice Assistant (DragonVoice.exe) ===")
    start_time = time.time()
    
    # Use a timestamp to create unique build directories
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    build_dir = f"build_{timestamp}"
    output_dir = "Dragon_App"
    
    try:
        # Create fresh build and output directories
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy assets if needed
        if os.path.exists("assets") and os.path.exists("assets/dragon_icon.ico"):
            shutil.copy("assets/dragon_icon.ico", build_dir)
            print(f"Copied icon to {build_dir}")
            
        # Copy necessary files to build directory
        required_files = [
            "dragon_gui_enhanced_a.py",
            "Dragon_cli2.py",
            "config.json",
            "dragon_icon.ico"
        ]
        
        for file in required_files:
            if os.path.exists(file):
                shutil.copy(file, build_dir)
                print(f"Copied {file} to build directory")
            else:
                print(f"Warning: {file} not found, executable may not work properly")
        
        # Create necessary subdirectories in build directory
        os.makedirs(os.path.join(build_dir, "recordings"), exist_ok=True)
        os.makedirs(os.path.join(build_dir, "transcripts"), exist_ok=True)
        
        # Change to build directory to run PyInstaller
        original_dir = os.getcwd()
        os.chdir(build_dir)
        
        # PyInstaller command
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name=DragonVoice",
            "--onefile",
            "--noconsole",
            "--icon=dragon_icon.ico",
            "--add-data=dragon_icon.ico;.",
            "--add-data=config.json;.",
            "--add-data=Dragon_cli2.py;.",
            "--add-data=recordings;recordings",
            "--add-data=transcripts;transcripts",
            "dragon_gui_enhanced_a.py"
        ]
        
        # Run PyInstaller
        print(f"Running PyInstaller in {build_dir}...")
        subprocess.run(cmd, check=True)
        
        # Copy the executable to the output directory
        print(f"Copying executable to {output_dir}...")
        shutil.copy(os.path.join("dist", "DragonVoice.exe"), os.path.join(original_dir, output_dir))
        
        # Return to original directory
        os.chdir(original_dir)
        
        # Create necessary directories in output
        os.makedirs(os.path.join(output_dir, "recordings"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "transcripts"), exist_ok=True)
        
        # Copy config file to output
        if os.path.exists("config.json"):
            shutil.copy("config.json", os.path.join(output_dir, "config.json"))
        
        # Create README file
        with open(os.path.join(output_dir, "README.txt"), "w") as f:
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
        
        # Create desktop shortcut
        create_shortcuts(os.path.join(original_dir, output_dir, "DragonVoice.exe"))
        
        # Report success
        end_time = time.time()
        print(f"\n✅ Build completed successfully in {end_time - start_time:.2f} seconds!")
        print(f"Executable created at: {output_dir}/DragonVoice.exe")
        
        return True
    except Exception as e:
        print(f"❌ Error building DragonVoice: {e}")
        traceback.print_exc()
        return False

def create_shortcuts(exe_path):
    """Create shortcuts for easy access"""
    exe_path = os.path.abspath(exe_path)
    working_dir = os.path.dirname(exe_path)
    
    try:
        # Create shortcut in app folder
        app_shortcut = os.path.join(working_dir, "DragonVoice.lnk")
        create_single_shortcut(exe_path, app_shortcut)
        
        # Create desktop shortcut
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        desktop_shortcut = os.path.join(desktop_path, "DragonVoice.lnk")
        create_single_shortcut(exe_path, desktop_shortcut)
        print(f"Created desktop shortcut at: {desktop_shortcut}")
        
        return True
    except Exception as e:
        print(f"Warning: Could not create shortcuts: {e}")
        return False

def create_single_shortcut(target_path, shortcut_path):
    """Create a single Windows shortcut"""
    working_dir = os.path.dirname(target_path)
    
    ps_script = f"""
try {{
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
    $Shortcut.TargetPath = "{target_path}"
    $Shortcut.WorkingDirectory = "{working_dir}"
    $Shortcut.IconLocation = "{target_path},0"
    $Shortcut.Description = "Dragon Voice Assistant"
    $Shortcut.WindowStyle = 1
    $Shortcut.Save()
    
    # Make shortcut pinnable (if it exists)
    if (Test-Path "{shortcut_path}") {{
        $bytes = [System.IO.File]::ReadAllBytes("{shortcut_path}")
        $bytes[0x15] = $bytes[0x15] -bor 0x20  # Set bit 5
        [System.IO.File]::WriteAllBytes("{shortcut_path}", $bytes)
        Write-Host "Created shortcut: {shortcut_path}"
    }}
}} catch {{
    Write-Host "Error creating shortcut: $_"
}}
"""
    
    # Write script to file
    script_path = "create_shortcut_temp.ps1"
    with open(script_path, "w") as f:
        f.write(ps_script)
    
    # Run PowerShell script
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], 
                  check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Remove temporary script
    try:
        os.remove(script_path)
    except:
        pass

def main():
    """Main function"""
    print("=== Dragon Voice Assistant Simple Builder ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Install requirements
    install_requirements()
    
    # Build the executable
    if build_executable():
        print("\n=== Build Successful ===")
        print("The executable is ready to use!")
        print("You can pin it to your taskbar by:")
        print("1. Double-clicking the executable")
        print("2. Right-clicking the icon in your taskbar")
        print("3. Selecting 'Pin to taskbar'")
        
        # Open the directory
        output_dir = os.path.abspath("Dragon_App")
        if os.path.exists(output_dir):
            print("\nOpening output directory...")
            os.startfile(output_dir)
        
        return 0
    else:
        print("\n=== Build Failed ===")
        print("Check the error messages above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 