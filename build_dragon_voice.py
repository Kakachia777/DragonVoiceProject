import os
import sys
import subprocess
import shutil
import platform

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    requirements = [
        "pyinstaller",
        "numpy",
        "pyaudio",
        "sounddevice",
        "soundfile",
        "requests",
        "pyperclip",
        "pillow",
        "pyautogui"
    ]
    
    for package in requirements:
        print(f"Checking/installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
            return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Create spec file content
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['dragon_voice_enhanced.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DragonVoice',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dragon_icon.ico' if os.path.exists('dragon_icon.ico') else None,
)
"""
    
    # Write spec file
    with open("DragonVoice.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller with the spec file
    try:
        subprocess.check_call(["pyinstaller", "DragonVoice.spec", "--clean"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed: {e}")
        return False

def create_shortcuts():
    """Create shortcuts for easy access and pinning"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs("Dragon_App", exist_ok=True)
        
        # Copy executable to output directory
        if os.path.exists("dist/DragonVoice.exe"):
            shutil.copy2("dist/DragonVoice.exe", "Dragon_App/DragonVoice.exe")
            print("Executable copied to Dragon_App folder")
            
            # Copy any necessary files (icon, etc.)
            if os.path.exists("dragon_icon.ico"):
                shutil.copy2("dragon_icon.ico", "Dragon_App/dragon_icon.ico")
            
            # Create Windows shortcut for easier pinning
            if platform.system() == "Windows":
                try:
                    import win32com.client
                    shortcut_path = os.path.abspath("Dragon_App/DragonVoice.lnk")
                    
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.TargetPath = os.path.abspath("Dragon_App/DragonVoice.exe")
                    shortcut.WorkingDirectory = os.path.abspath("Dragon_App")
                    
                    if os.path.exists("Dragon_App/dragon_icon.ico"):
                        shortcut.IconLocation = os.path.abspath("Dragon_App/dragon_icon.ico")
                        
                    shortcut.save()
                    print(f"Shortcut created at: {shortcut_path}")
                    
                    # Create desktop shortcut
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                    desktop_shortcut = os.path.join(desktop_path, "DragonVoice.lnk")
                    shutil.copy2(shortcut_path, desktop_shortcut)
                    print(f"Desktop shortcut created at: {desktop_shortcut}")
                    
                except ImportError:
                    print("Could not create Windows shortcut: win32com module not available")
                    print("Install it with: pip install pywin32")
                except Exception as e:
                    print(f"Error creating shortcut: {e}")
            
            return True
        else:
            print("Executable not found in dist folder")
            return False
    except Exception as e:
        print(f"Error creating shortcuts: {e}")
        return False

def cleanup():
    """Clean up temporary build files"""
    print("Cleaning up build files...")
    try:
        # Remove PyInstaller build artifacts
        if os.path.exists("build"):
            shutil.rmtree("build")
        
        # Remove spec file
        if os.path.exists("DragonVoice.spec"):
            os.remove("DragonVoice.spec")
            
        return True
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False

def main():
    """Main function"""
    print("=== Dragon Voice Assistant Executable Builder ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Install requirements
    install_requirements()
    
    # Build the executable
    if build_executable():
        create_shortcuts()
        
        print("\n=== Build Successful ===")
        print("The executable is ready to use!")
        print("You can pin it to your taskbar by:")
        print("1. Go to the Dragon_App folder and find DragonVoice.lnk")
        print("2. Right-click the shortcut and select 'Pin to taskbar'")
        print("   OR")
        print("1. Double-click the executable")
        print("2. Right-click the icon in your taskbar")
        print("3. Select 'Pin to taskbar'")
        
        # Open the directory
        output_dir = os.path.abspath("Dragon_App")
        if os.path.exists(output_dir):
            print("\nOpening output directory...")
            os.startfile(output_dir)
        
        # Cleanup build files if successful
        cleanup()
        
        return 0
    else:
        print("\n=== Build Failed ===")
        print("Check the error messages above for details.")
        return 1

if __name__ == "__main__":
    main()