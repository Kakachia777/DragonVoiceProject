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
        "scipy"
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
    """Clean existing build and dist directories"""
    print("Cleaning build directories...")
    
    directories_to_clean = ['build', 'dist', '__pycache__']
    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"Removing {directory}/")
            shutil.rmtree(directory)
    
    # Remove any .spec files
    for spec_file in Path(".").glob("*.spec"):
        print(f"Removing {spec_file}")
        os.remove(spec_file)

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
        # Create the PyInstaller command
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name=DragonVoice",
            "--onefile",
            "--noconsole",  # Use --noconsole for windowed mode
            "--icon=dragon_icon.ico",
            "--add-data=dragon_icon.ico;.",
            "--add-data=config.json;.",
            "--distpath=dist/DragonVoice",
            "dragon_gui_enhanced_a.py"  # Use enhanced GUI
        ]
        
        # Run the command
        print("Running PyInstaller...")
        print(f"Command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Copy necessary files to output directory
        print("Copying files to output directory...")
        
        # Copy executable
        shutil.copy("dist/DragonVoice/DragonVoice.exe", "output/DragonVoice/")
        
        # Copy necessary Python files
        shutil.copy("Dragon_cli2.py", "output/DragonVoice/")
        shutil.copy("dragon_gui_enhanced_a.py", "output/DragonVoice/")
        
        # Copy configuration
        shutil.copy("config.json", "output/DragonVoice/")
        
        # Copy icon
        shutil.copy("dragon_icon.ico", "output/DragonVoice/")
        
        # Create README file
        with open("output/DragonVoice/README.txt", "w") as f:
            f.write("Dragon Voice Assistant\n")
            f.write("=======================\n\n")
            f.write("QUICK START:\n")
            f.write("1. Double-click DragonVoice.exe to start the application\n")
            f.write("2. Click 'Record' to start recording your voice\n")
            f.write("3. Your message will be sent to all connected chatbots\n\n")
            f.write("USING WITH MOUSE WITHOUT BORDERS:\n")
            f.write("1. Install Mouse Without Borders on all computers\n")
            f.write("2. Run Dragon Voice Assistant on your main computer\n")
            f.write("3. Calibrate chatbot positions by clicking 'Calibrate'\n")
            f.write("4. Follow the prompts to click on each chatbot input field\n")
            f.write("5. For reliable cross-computer interaction, increase delays in Settings\n\n")
            f.write("PINNING TO TASKBAR:\n")
            f.write("1. Start the application by double-clicking DragonVoice.exe\n")
            f.write("2. Right-click on the application icon in the taskbar\n")
            f.write("3. Select 'Pin to taskbar'\n")
            f.write("4. Now you can launch directly from your taskbar anytime!\n\n")
            f.write("KEYBOARD SHORTCUTS:\n")
            f.write("- F9: Record\n")
            f.write("- F10: Quick Mode\n")
            f.write("- F11: Retry Failed\n")
            f.write("- F12: Settings\n\n")
            f.write("TROUBLESHOOTING:\n")
            f.write("- Make sure all files remain in the same folder\n")
            f.write("- If it won't start, try running as administrator\n")
            f.write("- Check that your microphone is connected\n")
        
        # Create shortcut file for Windows
        write_shortcut_file("output/DragonVoice/DragonVoice.exe.lnk", "DragonVoice")
        
        # Report success
        end_time = time.time()
        print(f"Build completed in {end_time - start_time:.2f} seconds")
        print(f"Executable created at: output/DragonVoice/DragonVoice.exe")
        
        return True
    except Exception as e:
        print(f"Error building Dragon Voice: {e}")
        traceback.print_exc()
        return False

def write_shortcut_file(path, app_name):
    """Create a Windows shortcut file using PowerShell that can be pinned to taskbar"""
    try:
        # Get the absolute path to the executable
        exe_path = os.path.abspath(path.replace('.lnk', ''))
        # Get the directory containing the executable
        working_dir = os.path.dirname(exe_path)
        
        # PowerShell script to create shortcut with all required properties
        ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{path}")
$Shortcut.TargetPath = "{exe_path}"
$Shortcut.WorkingDirectory = "{working_dir}"
$Shortcut.IconLocation = "{exe_path},0"
$Shortcut.Description = "Dragon Voice Assistant"
$Shortcut.WindowStyle = 1
$Shortcut.Hotkey = ""
# Add registry compatibility info to make pinning more reliable
$bytes = [System.IO.File]::ReadAllBytes("{path}")
$bytes[0x15] = $bytes[0x15] -bor 0x20 #set bit 5
[System.IO.File]::WriteAllBytes("{path}", $bytes)
# Make Explorer refresh icons
(New-Object -ComObject Shell.Application).Windows() | Out-Null
$Shortcut.Save()
        """
        
        # Write the PowerShell script to a temporary file
        with open("create_shortcut.ps1", "w") as f:
            f.write(ps_script)
        
        # Execute the PowerShell script
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "create_shortcut.ps1"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Clean up
        os.remove("create_shortcut.ps1")
        
        print(f"Created shortcut: {path}")
        print(f"✓ Shortcut is optimized for Windows taskbar pinning")
        return True
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False

def write_admin_shortcut_file(path, target_exe, app_name):
    """Create a Windows shortcut file with admin privileges using PowerShell"""
    try:
        # Get the directory containing the executable
        working_dir = os.path.dirname(target_exe)
        
        # PowerShell script to create admin shortcut
        ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{path}")
$Shortcut.TargetPath = "{target_exe}"
$Shortcut.WorkingDirectory = "{working_dir}"
$Shortcut.IconLocation = "{target_exe},0"
$Shortcut.Description = "Dragon Voice Assistant (Administrator mode)"
$Shortcut.WindowStyle = 1
$Shortcut.Hotkey = ""

# Create the shortcut first
$Shortcut.Save()

# Now add admin privileges with COM object
$bytes = [System.IO.File]::ReadAllBytes("{path}")
$bytes[0x15] = $bytes[0x15] -bor 0x20 #set bit 5 for compatibility
[System.IO.File]::WriteAllBytes("{path}", $bytes)

# Add administrator execution level
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace((Split-Path "{path}"))
$objFile = $objFolder.ParseName((Split-Path -Leaf "{path}"))
$objFile.InvokeVerb("runas")

# Make Explorer refresh icons
(New-Object -ComObject Shell.Application).Windows() | Out-Null
        """
        
        # Write the PowerShell script to a temporary file
        with open("create_admin_shortcut.ps1", "w") as f:
            f.write(ps_script)
        
        # Execute the PowerShell script
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "create_admin_shortcut.ps1"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Clean up
        os.remove("create_admin_shortcut.ps1")
        
        print(f"Created admin shortcut: {path}")
        print(f"✓ Admin shortcut can be used if regular shortcut doesn't work")
        return True
    except Exception as e:
        print(f"Error creating admin shortcut: {e}")
        return False

def create_desktop_shortcuts():
    """Create desktop shortcuts for the application with admin rights option"""
    print("\n=== Creating desktop shortcuts ===")
    
    try:
        # Get desktop path
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        # Create desktop shortcut
        shortcut_path = os.path.join(desktop_path, "DragonVoice.lnk")
        exe_path = os.path.abspath("output/DragonVoice/DragonVoice.exe")
        if os.path.exists(exe_path):
            print(f"Creating desktop shortcut for DragonVoice...")
            write_shortcut_file(shortcut_path, "DragonVoice")
            
            # Create admin shortcut
            admin_shortcut_path = os.path.join(desktop_path, "DragonVoice (Admin).lnk")
            write_admin_shortcut_file(admin_shortcut_path, exe_path, "DragonVoice")
        
        print("Desktop shortcuts created successfully. You can now pin them to the taskbar.")
        return True
    
    except Exception as e:
        print(f"Error creating desktop shortcuts: {e}")
        traceback.print_exc()
        return False

def create_zip_file():
    """Create zip file for easy distribution"""
    print("\n=== Creating distribution zip file ===")
    
    try:
        import zipfile
        
        # Create zip for Dragon Voice
        zip_path = "output/DragonVoice.zip"
        print(f"Creating {zip_path}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("output/DragonVoice"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, "output")
                    zipf.write(file_path, arcname)
        
        print("Zip file created successfully:")
        print(f"- {zip_path}")
        return True
    except Exception as e:
        print(f"Error creating zip file: {e}")
        traceback.print_exc()
        return False

def create_pinning_guide():
    """Create a simple HTML guide for pinning the application to the taskbar"""
    print("Creating taskbar pinning guide...")
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>How to Pin Dragon Voice Assistant to Taskbar</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #0078d4;
            text-align: center;
        }
        .step {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        .step h2 {
            margin-top: 0;
            color: #0078d4;
        }
        img {
            max-width: 100%;
            border: 1px solid #ddd;
            margin: 10px 0;
        }
        .note {
            background-color: #fff8dc;
            padding: 10px;
            border-left: 4px solid #ffeb3b;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <h1>How to Pin Dragon Voice Assistant to Taskbar</h1>
    
    <div class="step">
        <h2>Step 1: Run the Application</h2>
        <p>Double-click on the Dragon Voice Assistant executable file to start the application.</p>
    </div>
    
    <div class="step">
        <h2>Step 2: Find the Icon in Taskbar</h2>
        <p>When the application is running, you'll see its icon in the Windows taskbar at the bottom of the screen.</p>
    </div>
    
    <div class="step">
        <h2>Step 3: Right-click on the Icon</h2>
        <p>Right-click on the Dragon Voice Assistant icon in the taskbar to open the context menu.</p>
    </div>
    
    <div class="step">
        <h2>Step 4: Select "Pin to taskbar"</h2>
        <p>Click on the "Pin to taskbar" option in the menu that appears.</p>
    </div>
    
    <div class="step">
        <h2>Step 5: Done!</h2>
        <p>The Dragon Voice Assistant is now permanently pinned to your taskbar for easy access.</p>
        <p>You can click on the pinned icon anytime to start the application, even when it's not running.</p>
    </div>
    
    <div class="note">
        <strong>Note:</strong> If you have trouble starting the application, try the following:
        <ul>
            <li>Use the "(Admin)" shortcut if available</li>
            <li>Make sure all files stay together in the same folder</li>
            <li>Check that your microphone is properly connected</li>
        </ul>
    </div>
</body>
</html>
"""
    # Write the HTML file
    with open("How_to_Pin_to_Taskbar.html", "w") as f:
        f.write(html_content)
    
    print("✓ Created How_to_Pin_to_Taskbar.html")
    return True

def main():
    """Main build process"""
    print("=== Dragon Voice Executable Builder ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    try:
        # Check for necessary files
        required_files = [
            "dragon_gui_enhanced_a.py",
            "Dragon_cli2.py",
            "config.json",
            "dragon_icon.ico"
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        if missing_files:
            print("Error: Missing required files:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        # Install requirements
        install_requirements()
        
        # Clean build directories
        clean_build_directories()
        
        # Ensure output directories
        ensure_output_directories()
        
        # Create taskbar pinning guide
        create_pinning_guide()
        
        # Build Dragon Voice
        success = build_dragon_voice()
        
        # Create zip file if build succeeded
        if success:
            # Copy the taskbar pinning guide to output folder
            if os.path.exists("How_to_Pin_to_Taskbar.html"):
                shutil.copy("How_to_Pin_to_Taskbar.html", "output/DragonVoice/")
                print("✓ Copied taskbar pinning guide to output folder")
            
            # Copy the user guide to output folder
            if os.path.exists("USER_GUIDE.md"):
                shutil.copy("USER_GUIDE.md", "output/DragonVoice/")
                print("✓ Copied user guide to output folder")
            
            create_zip_file()
            # Create desktop shortcuts
            create_desktop_shortcuts()
        
        # Final summary
        print("\n=== Build Summary ===")
        print(f"Dragon Voice: {'Success' if success else 'Failed'}")
        
        if success:
            print("\nExecutable is ready for distribution in the output folder:")
            print("- output/DragonVoice/DragonVoice.exe")
            print("\nShortcut file created for easy pinning to taskbar:")
            print("- output/DragonVoice/DragonVoice.exe.lnk")
            print("\nDesktop shortcuts (can be pinned to taskbar):")
            print(f"- {os.path.join(os.path.expanduser('~'), 'Desktop', 'DragonVoice.lnk')}")
            print(f"- {os.path.join(os.path.expanduser('~'), 'Desktop', 'DragonVoice (Admin).lnk')} - Use if standard version doesn't work")
            print("\nDocumentation:")
            print("- output/DragonVoice/How_to_Pin_to_Taskbar.html")
            print("- output/DragonVoice/USER_GUIDE.md")
            print("\nZip file for distribution:")
            print("- output/DragonVoice.zip")
            return True
        else:
            print("\nBuild failed. Please check the errors above.")
            return False
    
    except Exception as e:
        print(f"Error in build process: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 