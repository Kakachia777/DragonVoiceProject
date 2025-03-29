import os
import sys
import subprocess
import generate_icon

def build_executable():
    # First generate the icon if it doesn't exist
    icon_path = "dragon_icon.ico"
    if not os.path.exists(icon_path):
        print("Generating icon...")
        generate_icon.create_dragon_icon(icon_path)
    
    # Ensure config.json is copied to the executable folder
    additional_data = [
        ('config copy.json', '.', 'DATA'),
    ]
    
    # Create a spec file with all our options
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dragon_gui_minimal.py'],
    pathex=[],
    binaries=[],
    datas=[('config copy.json', '.'), ('dragon_icon.ico', '.')],
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
    icon='{icon_path}'
)
"""
    
    # Write the spec file
    with open('dragon_voice.spec', 'w') as f:
        f.write(spec_content)
    
    # Build the executable
    print("Building executable...")
    subprocess.run(['pyinstaller', 'dragon_voice.spec', '--clean'])
    
    print("\nBuild complete! The executable is located in the dist folder.")
    print("You can find it at: dist/DragonVoice.exe")

if __name__ == "__main__":
    build_executable() 