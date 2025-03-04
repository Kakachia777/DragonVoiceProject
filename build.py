#!/usr/bin/env python3
"""
DragonVoiceProject - Build Script

This script creates a distributable package of the Dragon Voice Project.

Usage:
    python build.py [--version VERSION]

Options:
    --version VERSION   Version number for the release (default: current date)

Requirements:
    - Python 3.6+
"""

import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Build Script")
    
    parser.add_argument("--version", type=str,
                        default=datetime.now().strftime("%Y.%m.%d"),
                        help="Version number for this release")
    
    return parser.parse_args()


def create_build_directory(version):
    """
    Create a clean build directory.
    
    Args:
        version: Version number string
        
    Returns:
        Path to the build directory
    """
    # Create build directory name
    build_dir = f"DragonVoiceProject-{version}"
    
    # Get absolute path to the build directory
    build_path = os.path.abspath(build_dir)
    
    # Remove existing build directory if it exists
    if os.path.exists(build_path):
        print(f"Removing existing build directory: {build_path}")
        shutil.rmtree(build_path)
    
    # Create the build directory
    print(f"Creating build directory: {build_path}")
    os.makedirs(build_path)
    
    return build_path


def copy_source_files(build_path):
    """
    Copy source files to the build directory.
    
    Args:
        build_path: Path to the build directory
    """
    # Create source directory in the build directory
    src_dir = os.path.join(build_path, "src")
    os.makedirs(src_dir)
    
    # Copy Python source files
    source_files = [
        "dragon_monitor.py",
        "quick_test.py",
        "setup.py",
        "config.json"
    ]
    
    for file in source_files:
        src_file = os.path.join("src", file)
        if os.path.exists(src_file):
            print(f"Copying {src_file} to {src_dir}")
            shutil.copy2(src_file, src_dir)
        else:
            print(f"Warning: Source file not found: {src_file}")
    
    # Create docs directory in the build directory
    docs_dir = os.path.join(build_path, "docs")
    os.makedirs(docs_dir)
    
    # Copy documentation files
    doc_files = [
        "user_guide.md",
        "quick_reference.md"
    ]
    
    for file in doc_files:
        doc_file = os.path.join("docs", file)
        if os.path.exists(doc_file):
            print(f"Copying {doc_file} to {docs_dir}")
            shutil.copy2(doc_file, docs_dir)
        else:
            print(f"Warning: Documentation file not found: {doc_file}")
    
    # Copy README and requirements files
    for file in ["README.md", "requirements.txt"]:
        if os.path.exists(file):
            print(f"Copying {file} to {build_path}")
            shutil.copy2(file, build_path)
        else:
            print(f"Warning: File not found: {file}")


def create_windows_batch_file(build_path):
    """
    Create a Windows batch file to run the application.
    
    Args:
        build_path: Path to the build directory
    """
    batch_content = """@echo off
echo Starting Dragon Voice Project...
cd /d "%~dp0src"
python dragon_monitor.py
pause
"""
    
    batch_path = os.path.join(build_path, "start_dragon_voice.bat")
    
    print(f"Creating Windows batch file: {batch_path}")
    with open(batch_path, 'w') as f:
        f.write(batch_content)


def create_windows_installer(build_path, version):
    """
    Create a Windows installer using NSIS if available.
    
    Args:
        build_path: Path to the build directory
        version: Version number string
        
    Returns:
        True if installer was created, False otherwise
    """
    try:
        # Check if makensis is available
        subprocess.run(["makensis", "-VERSION"], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE,
                       check=True)
        
        # Create NSIS script
        nsis_script = f"""
; DragonVoiceProject Installer
!include "MUI2.nsh"

; General settings
Name "Dragon Voice Project"
OutFile "DragonVoiceProject-{version}-setup.exe"
InstallDir "$PROGRAMFILES\\DragonVoiceProject"
InstallDirRegKey HKCU "Software\\DragonVoiceProject" ""

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Install sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy files
    File /r "{build_path}\\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\Dragon Voice Project"
    CreateShortcut "$SMPROGRAMS\\Dragon Voice Project\\Dragon Voice Project.lnk" "$INSTDIR\\start_dragon_voice.bat"
    CreateShortcut "$SMPROGRAMS\\Dragon Voice Project\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    ; Write registry keys
    WriteRegStr HKCU "Software\\DragonVoiceProject" "" $INSTDIR
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\DragonVoiceProject" "DisplayName" "Dragon Voice Project"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\DragonVoiceProject" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\DragonVoiceProject" "DisplayVersion" "{version}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\DragonVoiceProject" "Publisher" "DragonVoiceProject"
SectionEnd

; Uninstall section
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    RMDir /r "$SMPROGRAMS\\Dragon Voice Project"
    
    ; Remove registry keys
    DeleteRegKey HKCU "Software\\DragonVoiceProject"
    DeleteRegKey HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\DragonVoiceProject"
SectionEnd
"""
        
        # Write NSIS script to file
        nsis_path = "installer.nsi"
        with open(nsis_path, 'w') as f:
            f.write(nsis_script)
        
        # Run NSIS to create installer
        print("Creating Windows installer...")
        subprocess.run(["makensis", nsis_path], check=True)
        
        # Clean up NSIS script
        os.remove(nsis_path)
        
        print(f"Windows installer created: DragonVoiceProject-{version}-setup.exe")
        return True
    
    except (subprocess.SubprocessError, FileNotFoundError):
        print("NSIS not found, skipping installer creation.")
        return False


def create_zip_archive(build_path, version):
    """
    Create a ZIP archive of the build directory.
    
    Args:
        build_path: Path to the build directory
        version: Version number string
    """
    # Create ZIP archive
    zip_filename = f"DragonVoiceProject-{version}.zip"
    print(f"Creating ZIP archive: {zip_filename}")
    
    # Change to parent directory of build directory to get proper paths in ZIP file
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(build_path))
    
    try:
        # Create ZIP archive with relative paths
        shutil.make_archive(
            os.path.join(original_dir, f"DragonVoiceProject-{version}"),
            'zip',
            '.',
            os.path.basename(build_path)
        )
    finally:
        # Change back to original directory
        os.chdir(original_dir)
    
    print(f"ZIP archive created: {zip_filename}")


def update_version_file(build_path, version):
    """
    Create a version file in the build directory.
    
    Args:
        build_path: Path to the build directory
        version: Version number string
    """
    version_file = os.path.join(build_path, "version.txt")
    
    print(f"Creating version file: {version_file}")
    with open(version_file, 'w') as f:
        f.write(f"Dragon Voice Project v{version}\n")
        f.write(f"Build date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def main():
    """Main function."""
    print("=" * 60)
    print("DragonVoiceProject - Build Script")
    print("=" * 60)
    
    # Parse command line arguments
    args = parse_arguments()
    version = args.version
    
    print(f"Building version: {version}")
    
    # Create build directory
    build_path = create_build_directory(version)
    
    # Copy source files
    copy_source_files(build_path)
    
    # Create Windows batch file
    create_windows_batch_file(build_path)
    
    # Update version file
    update_version_file(build_path, version)
    
    # Create Windows installer (if NSIS is available)
    installer_created = create_windows_installer(build_path, version)
    
    # Create ZIP archive
    create_zip_archive(build_path, version)
    
    # Print build summary
    print("\n" + "=" * 60)
    print("Build Summary:")
    print(f"- Version: {version}")
    print(f"- Build directory: {build_path}")
    print(f"- ZIP archive: DragonVoiceProject-{version}.zip")
    if installer_created:
        print(f"- Windows installer: DragonVoiceProject-{version}-setup.exe")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nBuild process cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 