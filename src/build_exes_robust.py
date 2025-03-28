import os
import sys
import subprocess
import shutil
import traceback

def ensure_dependencies():
    """Ensure all dependencies are installed"""
    print("Checking dependencies...")
    try:
        # Check if PyInstaller is installed
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                      check=True, capture_output=True)
        print("PyInstaller already installed.")
    except subprocess.CalledProcessError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Check if generate_icon module exists
    if not os.path.exists("generate_icon.py"):
        print("Error: generate_icon.py not found")
        sys.exit(1)
    
    # Check for dragon_gui_minimal.py
    if not os.path.exists("dragon_gui_minimal.py"):
        print("Error: dragon_gui_minimal.py not found")
        sys.exit(1)
    
    # Check for main Python files
    if not os.path.exists("dragon_cli.py"):
        print("Error: dragon_cli.py not found")
        sys.exit(1)
    
    if not os.path.exists("Dragon_cli2.py"):
        print("Error: Dragon_cli2.py not found")
        sys.exit(1)
    
    # Check for config files
    if not os.path.exists("config.json"):
        print("Error: config.json not found")
        sys.exit(1)
    
    if not os.path.exists("config copy.json"):
        print("Error: 'config copy.json' not found")
        sys.exit(1)

def build_executables():
    """Build executables for both computer A and B"""
    try:
        print("\n=== Starting Build Process ===")
        
        # First generate the icon if it doesn't exist
        icon_path = "dragon_icon.ico"
        if not os.path.exists(icon_path):
            print("Generating icon...")
            import generate_icon
            generate_icon.create_dragon_icon(icon_path)
        
        # Create output directories
        if not os.path.exists("output"):
            os.makedirs("output")
        
        # Computer A - Using Dragon_cli2.py with config.json
        build_computer_a()
        
        # Computer B - Using dragon_cli.py with config copy.json
        build_computer_b()
        
        print("\nBuild complete! The executables are located in the output folder.")
        print("Computer A: output/DragonVoiceA/DragonVoiceA.exe (using Dragon_cli2.py and config.json)")
        print("Computer B: output/DragonVoiceB/DragonVoiceB.exe (using dragon_cli.py and config copy.json)")
    except Exception as e:
        print(f"Error during build process: {e}")
        traceback.print_exc()
        sys.exit(1)

def build_computer_a():
    """Build executable for Computer A (Dragon_cli2.py)"""
    print("\n=== Building Computer A Executable (Dragon_cli2.py) ===")
    
    try:
        # Create dragon_gui_minimal_a.py with explicit import
        with open("dragon_gui_minimal.py", "r") as f:
            content = f.read()
        
        # Make sure we're importing Dragon_cli2 correctly
        modified_content = content.replace("import Dragon_cli2 as dragon_cli", "import Dragon_cli2 as dragon_cli")
        
        with open("dragon_gui_minimal_a.py", "w") as f:
            f.write(modified_content)
        
        # Create spec file for Computer A
        spec_content_a = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dragon_gui_minimal_a.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[('config.json', '.'), ('dragon_icon.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DragonVoiceA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dragon_icon.ico'
)
"""
        
        # Write the spec file
        with open('dragon_voice_a.spec', 'w') as f:
            f.write(spec_content_a)
        
        # Build the executable
        print("Building Computer A executable...")
        subprocess.run([sys.executable, '-m', 'PyInstaller', 'dragon_voice_a.spec', '--clean'], check=True)
        
        # Create final output directory for Computer A
        comp_a_dir = "output/DragonVoiceA"
        if os.path.exists(comp_a_dir):
            shutil.rmtree(comp_a_dir)
        os.makedirs(comp_a_dir)
        
        # Copy the executable to the output directory
        shutil.copy("dist/DragonVoiceA.exe", f"{comp_a_dir}/DragonVoiceA.exe")
        
        # Copy Dragon_cli2.py to the output directory (for reference)
        shutil.copy("Dragon_cli2.py", f"{comp_a_dir}/Dragon_cli2.py")
        
        # Copy config.json to the output directory
        shutil.copy("config.json", f"{comp_a_dir}/config.json")
        
        # Copy dragon_icon.ico to the output directory
        shutil.copy("dragon_icon.ico", f"{comp_a_dir}/dragon_icon.ico")
        
        # Clean up the temporary file
        if os.path.exists("dragon_gui_minimal_a.py"):
            os.remove("dragon_gui_minimal_a.py")
        
        print(f"Computer A executable successfully created in {comp_a_dir}")
    except Exception as e:
        print(f"Error building Computer A executable: {e}")
        traceback.print_exc()
        raise

def build_computer_b():
    """Build executable for Computer B (dragon_cli.py)"""
    print("\n=== Building Computer B Executable (dragon_cli.py) ===")
    
    try:
        # Create dragon_gui_minimal_b.py with modified import
        with open("dragon_gui_minimal.py", "r") as f:
            content = f.read()
        
        modified_content = content.replace("import Dragon_cli2 as dragon_cli", "import dragon_cli")
        
        with open("dragon_gui_minimal_b.py", "w") as f:
            f.write(modified_content)
        
        # Create spec file for Computer B
        spec_content_b = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dragon_gui_minimal_b.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[('config copy.json', 'config.json'), ('dragon_icon.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DragonVoiceB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dragon_icon.ico'
)
"""
        
        # Write the spec file
        with open('dragon_voice_b.spec', 'w') as f:
            f.write(spec_content_b)
        
        # Build the executable
        print("Building Computer B executable...")
        subprocess.run([sys.executable, '-m', 'PyInstaller', 'dragon_voice_b.spec', '--clean'], check=True)
        
        # Create final output directory for Computer B
        comp_b_dir = "output/DragonVoiceB"
        if os.path.exists(comp_b_dir):
            shutil.rmtree(comp_b_dir)
        os.makedirs(comp_b_dir)
        
        # Copy the executable to the output directory
        shutil.copy("dist/DragonVoiceB.exe", f"{comp_b_dir}/DragonVoiceB.exe")
        
        # Copy dragon_cli.py to the output directory (for reference)
        shutil.copy("dragon_cli.py", f"{comp_b_dir}/dragon_cli.py")
        
        # Copy config copy.json to the output directory as config.json
        shutil.copy("config copy.json", f"{comp_b_dir}/config.json")
        
        # Copy dragon_icon.ico to the output directory
        shutil.copy("dragon_icon.ico", f"{comp_b_dir}/dragon_icon.ico")
        
        # Clean up the temporary file
        if os.path.exists("dragon_gui_minimal_b.py"):
            os.remove("dragon_gui_minimal_b.py")
        
        print(f"Computer B executable successfully created in {comp_b_dir}")
    except Exception as e:
        print(f"Error building Computer B executable: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        ensure_dependencies()
        build_executables()
    except Exception as e:
        print(f"Build failed: {e}")
        traceback.print_exc()
        sys.exit(1) 