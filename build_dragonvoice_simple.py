"""
Simple Dragon Voice Assistant Build Script
This script builds a standalone executable for Dragon Voice Assistant.
"""

import os
import sys
import subprocess
import shutil
import time
import traceback
from pathlib import Path
import tempfile

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
        "soundfile",
        "requests",
        "python-dotenv",
        "keyboard",
        "colorama"
    ]
    
    # Try to install pywin32 on Windows
    if os.name == 'nt':
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=False)
            print("Installed pywin32")
        except:
            print("Note: Could not install pywin32, but continuing anyway")
    
    for req in requirements:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", req], check=False)
            print(f"Installed {req}")
        except:
            print(f"Warning: Could not install {req}, but continuing anyway")

def prepare_directories():
    """Create necessary directories"""
    directories = ["recordings", "transcripts", "logs", "Dragon_App"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def clean_build_directories():
    """Clean up any existing build directories that might cause issues"""
    print("Cleaning up any existing build directories...")
    paths_to_clean = ["build", "dist", "__pycache__"]
    
    for path in paths_to_clean:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
                print(f"Removed {path}")
        except Exception as e:
            print(f"Warning: Could not remove {path}: {e}")
            print("Continuing anyway...")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n=== Building Dragon Voice Assistant Executable ===")
    
    # Clean existing build directories to avoid conflicts
    clean_build_directories()
    
    # Create a temporary working directory outside of OneDrive to avoid permission issues
    temp_dir = tempfile.mkdtemp(prefix="dragonvoice_build_")
    print(f"Using temporary build directory: {temp_dir}")
    
    try:
        # Copy necessary files to the temp directory
        files_to_copy = ["dragon_voice_enhanced.py", "Dragon_cli2.py", "config.json"]
        if os.path.exists("dragon_icon.ico"):
            files_to_copy.append("dragon_icon.ico")
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, os.path.join(temp_dir, file))
                print(f"Copied {file} to build directory")
            else:
                print(f"Warning: {file} not found, skipping")
        
        # Change to the temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Create the pyinstaller command
        command = [
            sys.executable, "-m", "PyInstaller",
            "--name=DragonVoice",
            "--onefile",
            "--noconsole",
            "--clean",
            "--noconfirm"  # Skip confirmation prompts
        ]
        
        # Add icon if it exists
        if os.path.exists("dragon_icon.ico"):
            command.extend(["--icon=dragon_icon.ico"])
        
        # Add data files with correct separator based on OS
        sep = ";" if os.name == "nt" else ":"
        data_files = [
            f"Dragon_cli2.py{sep}.",
            f"config.json{sep}.",
        ]
        
        if os.path.exists("dragon_icon.ico"):
            data_files.append(f"dragon_icon.ico{sep}.")
        
        for data_file in data_files:
            command.extend(["--add-data", data_file])
        
        # Add the main script file
        command.append("dragon_voice_enhanced.py")
        
        # Run the PyInstaller command
        try:
            print("Running PyInstaller with command:")
            print(" ".join(command))
            subprocess.run(command, check=True)
            
            # Copy the executable back to the original directory
            if os.path.exists("dist/DragonVoice.exe"):
                # Create dist directory in original location if it doesn't exist
                os.makedirs(os.path.join(original_dir, "dist"), exist_ok=True)
                
                # Copy the executable
                shutil.copy2(
                    "dist/DragonVoice.exe", 
                    os.path.join(original_dir, "dist", "DragonVoice.exe")
                )
                print("Copied executable back to original directory")
                
                # Return to original directory
                os.chdir(original_dir)
                return True
            else:
                print("Error: Executable not found in dist folder")
                os.chdir(original_dir)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"Error running PyInstaller: {e}")
            os.chdir(original_dir)
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()
            os.chdir(original_dir)
            return False
    
    finally:
        # Make sure we're back in the original directory
        if os.getcwd() != original_dir:
            os.chdir(original_dir)
        
        # Clean up the temp directory, but don't fail if it can't be removed
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Cleaned up temporary build directory")
        except Exception as e:
            print(f"Warning: Could not clean up temporary directory {temp_dir}: {e}")
            print("You may want to delete it manually later")

def create_shortcuts():
    """Create shortcuts for the application"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs("Dragon_App", exist_ok=True)
        
        # Copy executable to output directory
        if os.path.exists("dist/DragonVoice.exe"):
            shutil.copy2("dist/DragonVoice.exe", "Dragon_App/DragonVoice.exe")
            print("Executable copied to Dragon_App folder")
            
            # Copy necessary files
            if os.path.exists("dragon_icon.ico"):
                shutil.copy2("dragon_icon.ico", "Dragon_App/dragon_icon.ico")
            
            if os.path.exists("config.json"):
                shutil.copy2("config.json", "Dragon_App/config.json")
            
            # Create necessary directories
            os.makedirs("Dragon_App/recordings", exist_ok=True)
            os.makedirs("Dragon_App/transcripts", exist_ok=True)
            os.makedirs("Dragon_App/logs", exist_ok=True)
            
            # Create README file
            with open("Dragon_App/README.txt", "w") as f:
                f.write("Dragon Voice Assistant\n")
                f.write("====================\n\n")
                f.write("QUICK START:\n")
                f.write("1. Double-click DragonVoice.exe to start the application\n")
                f.write("2. Hold the SPACE key to record your voice (release to process)\n")
                f.write("3. Your message will be sent to all configured chatbots\n\n")
                f.write("PINNING TO TASKBAR:\n")
                f.write("1. Right-click on DragonVoice.exe and select 'Create shortcut'\n")
                f.write("2. Right-click on the shortcut and select 'Pin to taskbar'\n")
                f.write("   OR\n")
                f.write("1. Run the application\n")
                f.write("2. Right-click on its icon in the taskbar\n")
                f.write("3. Select 'Pin to taskbar'\n\n")
                f.write("KEYBOARD SHORTCUTS:\n")
                f.write("- SPACE: Press and hold to record, release to process\n")
                f.write("- F10: Quick Mode (record and send automatically)\n")
                f.write("- F11: Retry Failed\n")
                f.write("- F12: Settings\n\n")
                f.write("NOTE: For best results, run the application as administrator.\n")
            
            # Try to create Windows shortcuts with alternative methods since we had permission issues
            if os.name == 'nt':
                try:
                    # Method 1: Use PowerShell to create shortcuts
                    print("Creating shortcuts with PowerShell...")
                    
                    # Create PowerShell script content
                    ps_cmd = f'''
                    $WshShell = New-Object -comObject WScript.Shell
                    $Shortcut = $WshShell.CreateShortcut("{os.path.abspath('Dragon_App/DragonVoice.lnk')}")
                    $Shortcut.TargetPath = "{os.path.abspath('Dragon_App/DragonVoice.exe')}"
                    $Shortcut.WorkingDirectory = "{os.path.abspath('Dragon_App')}"
                    $Shortcut.Description = "Dragon Voice Assistant"
                    $Shortcut.Save()
                    
                    # Create desktop shortcut only if not on OneDrive Desktop
                    $DesktopPath = [Environment]::GetFolderPath("Desktop")
                    if (-not ($DesktopPath -like "*OneDrive*")) {{
                        $DesktopShortcut = $WshShell.CreateShortcut("$DesktopPath\\DragonVoice.lnk")
                        $DesktopShortcut.TargetPath = "{os.path.abspath('Dragon_App/DragonVoice.exe')}"
                        $DesktopShortcut.WorkingDirectory = "{os.path.abspath('Dragon_App')}"
                        $DesktopShortcut.Description = "Dragon Voice Assistant"
                        $DesktopShortcut.Save()
                    }}
                    '''
                    
                    # Write to a temporary file
                    with open("create_shortcut.ps1", "w") as f:
                        f.write(ps_cmd)
                    
                    # Execute PowerShell script
                    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "create_shortcut.ps1"], check=False)
                    
                    # Clean up
                    if os.path.exists("create_shortcut.ps1"):
                        os.remove("create_shortcut.ps1")
                    
                    print("Created shortcuts successfully")
                    
                except Exception as e:
                    print(f"Warning: Could not create shortcuts with PowerShell: {e}")
                    print("Trying alternative method...")
                    
                    try:
                        # Method 2: Create a .bat file to make a shortcut
                        bat_cmd = f'''@echo off
                        echo Creating shortcuts...
                        echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
                        echo sLinkFile = "{os.path.abspath('Dragon_App/DragonVoice.lnk')}" >> CreateShortcut.vbs
                        echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
                        echo oLink.TargetPath = "{os.path.abspath('Dragon_App/DragonVoice.exe')}" >> CreateShortcut.vbs
                        echo oLink.WorkingDirectory = "{os.path.abspath('Dragon_App')}" >> CreateShortcut.vbs
                        echo oLink.Description = "Dragon Voice Assistant" >> CreateShortcut.vbs
                        echo oLink.Save >> CreateShortcut.vbs
                        cscript CreateShortcut.vbs
                        del CreateShortcut.vbs
                        '''
                        
                        with open("create_shortcut.bat", "w") as f:
                            f.write(bat_cmd)
                        
                        subprocess.run(["create_shortcut.bat"], check=False, shell=True)
                        
                        # Clean up
                        if os.path.exists("create_shortcut.bat"):
                            os.remove("create_shortcut.bat")
                        
                        print("Created shortcuts with alternative method")
                    except Exception as e:
                        print(f"Warning: Alternative shortcut creation also failed: {e}")
                        print("You'll need to create shortcuts manually")
            
            return True
        else:
            print("Warning: Executable not found in dist folder")
            return False
    except Exception as e:
        print(f"Error creating shortcuts: {e}")
        return False

def main():
    """Main function for building the executable"""
    print("=== Dragon Voice Assistant Executable Builder ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Operating system: {os.name}")
    print()
    
    # Install requirements
    install_requirements()
    
    # Prepare directories
    prepare_directories()
    
    # Build the executable
    if build_executable():
        print("\n✅ Executable built successfully!")
        
        # Create shortcuts
        create_shortcuts()
        
        print("\n=== Build Successful ===")
        print("The executable is ready to use!")
        print("You can find it in the Dragon_App folder: Dragon_App/DragonVoice.exe")
        print("You can pin it to your taskbar by:")
        print("1. Double-clicking the executable")
        print("2. Right-clicking the icon in your taskbar")
        print("3. Selecting 'Pin to taskbar'")
        
        # Open the directory
        output_dir = os.path.abspath("Dragon_App")
        if os.path.exists(output_dir):
            print("\nOpening output directory...")
            try:
                if os.name == 'nt':
                    os.startfile(output_dir)
                else:
                    subprocess.run(['xdg-open', output_dir], check=False)
            except:
                print(f"Could not open directory, but it's located at: {output_dir}")
        
        return 0
    else:
        print("\n❌ Build Failed")
        print("Check the error messages above for details.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unhandled error: {e}")
        traceback.print_exc()
        print("\nBuild process failed. Please try again or contact support.")
        sys.exit(1) 