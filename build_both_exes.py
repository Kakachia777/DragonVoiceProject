import os
import sys
import subprocess
import shutil
import generate_icon

def build_executables():
    # First generate the icon if it doesn't exist
    icon_path = "dragon_icon.ico"
    if not os.path.exists(icon_path):
        print("Generating icon...")
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

def build_computer_a():
    print("\n=== Building Computer A Executable (Dragon_cli2.py) ===")
    
    # Create spec file for Computer A
    spec_content_a = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dragon_gui_minimal.py'],
    pathex=[],
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
    console=False,
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
    subprocess.run(['pyinstaller', 'dragon_voice_a.spec', '--clean'])
    
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
    
    print(f"Computer A executable successfully created in {comp_a_dir}")

def build_computer_b():
    print("\n=== Building Computer B Executable (dragon_cli.py) ===")
    
    # Create dragon_gui_b.py with import dragon_cli instead of Dragon_cli2
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
    pathex=[],
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
    console=False,
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
    subprocess.run(['pyinstaller', 'dragon_voice_b.spec', '--clean'])
    
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

if __name__ == "__main__":
    build_executables() 