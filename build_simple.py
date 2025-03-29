import os
import sys
import subprocess
import shutil
import time

def build_executables():
    print("Starting build process...")
    
    # Make sure output directory exists
    if not os.path.exists("output"):
        os.makedirs("output")
    
    if not os.path.exists("output/DragonVoiceA"):
        os.makedirs("output/DragonVoiceA")
    
    if not os.path.exists("output/DragonVoiceB"):
        os.makedirs("output/DragonVoiceB")
    
    # Build Computer A (Dragon_cli2.py)
    print("\nBuilding Computer A executable...")
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--icon=dragon_icon.ico",
            "--name=DragonVoiceA",
            "dragon_gui_minimal_a.py"
        ], check=True)
        
        # Copy necessary files
        print("Copying files for Computer A...")
        shutil.copy("dist/DragonVoiceA.exe", "output/DragonVoiceA/")
        shutil.copy("Dragon_cli2.py", "output/DragonVoiceA/")
        shutil.copy("config.json", "output/DragonVoiceA/")
        shutil.copy("dragon_icon.ico", "output/DragonVoiceA/")
        print("Computer A build complete!")
    except Exception as e:
        print(f"Error building Computer A: {e}")
    
    # Build Computer B (dragon_cli.py)
    print("\nBuilding Computer B executable...")
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--icon=dragon_icon.ico",
            "--name=DragonVoiceB",
            "dragon_gui_minimal_b.py"
        ], check=True)
        
        # Copy necessary files
        print("Copying files for Computer B...")
        shutil.copy("dist/DragonVoiceB.exe", "output/DragonVoiceB/")
        shutil.copy("dragon_cli.py", "output/DragonVoiceB/")
        shutil.copy("config copy.json", "output/DragonVoiceB/config.json")
        shutil.copy("dragon_icon.ico", "output/DragonVoiceB/")
        print("Computer B build complete!")
    except Exception as e:
        print(f"Error building Computer B: {e}")
    
    print("\nBuild process complete!")
    print("Executables can be found in the output directory:")
    print("  - Computer A: output/DragonVoiceA/DragonVoiceA.exe")
    print("  - Computer B: output/DragonVoiceB/DragonVoiceB.exe")

if __name__ == "__main__":
    # First ensure we have the PyInstaller package
    try:
        import PyInstaller
        print(f"PyInstaller version {PyInstaller.__version__} is installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    build_executables() 