@echo off
echo ====================================
echo Dragon Voice Assistant Simple Builder
echo ====================================
echo.
echo This script will build Dragon Voice Enhanced into a standalone executable.
echo.

REM Kill any Python processes that might be interfering
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

REM Create a simple one-file PyInstaller script
echo import os > build_script.py
echo import sys >> build_script.py
echo import subprocess >> build_script.py
echo import shutil >> build_script.py
echo. >> build_script.py
echo # Install PyInstaller if needed >> build_script.py
echo subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=False) >> build_script.py
echo. >> build_script.py
echo # Create necessary directories >> build_script.py
echo os.makedirs("Dragon_App", exist_ok=True) >> build_script.py
echo os.makedirs("Dragon_App/recordings", exist_ok=True) >> build_script.py
echo os.makedirs("Dragon_App/transcripts", exist_ok=True) >> build_script.py
echo os.makedirs("Dragon_App/logs", exist_ok=True) >> build_script.py
echo. >> build_script.py
echo # Build the executable >> build_script.py
echo cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--clean", "--name=DragonVoice"] >> build_script.py
echo. >> build_script.py
echo # Add data files >> build_script.py
echo cmd.extend(["--add-data", "Dragon_cli2.py;."]) >> build_script.py
echo cmd.extend(["--add-data", "config.json;."]) >> build_script.py
echo. >> build_script.py
echo if os.path.exists("dragon_icon.ico"): >> build_script.py
echo     cmd.extend(["--icon=dragon_icon.ico"]) >> build_script.py
echo     cmd.extend(["--add-data", "dragon_icon.ico;."]) >> build_script.py
echo. >> build_script.py
echo # Add main script >> build_script.py
echo cmd.append("dragon_voice_enhanced.py") >> build_script.py
echo. >> build_script.py
echo # Run PyInstaller >> build_script.py
echo print("Running PyInstaller...") >> build_script.py
echo subprocess.run(cmd, check=True) >> build_script.py
echo. >> build_script.py
echo # Copy files to output directory >> build_script.py
echo if os.path.exists("dist/DragonVoice.exe"): >> build_script.py
echo     print("Copying files to Dragon_App folder...") >> build_script.py
echo     shutil.copy2("dist/DragonVoice.exe", "Dragon_App/DragonVoice.exe") >> build_script.py
echo     if os.path.exists("config.json"): >> build_script.py
echo         shutil.copy2("config.json", "Dragon_App/config.json") >> build_script.py
echo     if os.path.exists("dragon_icon.ico"): >> build_script.py
echo         shutil.copy2("dragon_icon.ico", "Dragon_App/dragon_icon.ico") >> build_script.py
echo     print("Build completed successfully!") >> build_script.py
echo else: >> build_script.py
echo     print("Error: Build failed - executable not found") >> build_script.py
echo     sys.exit(1) >> build_script.py

REM Run the build script
echo Running build script...
echo.
python build_script.py

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo.
    echo You can find the executable in the Dragon_App folder.
    echo.
    echo To pin to taskbar:
    echo 1. Right-click on DragonVoice.exe in the Dragon_App folder
    echo 2. Select "Create shortcut"
    echo 3. Right-click on the shortcut and select "Pin to taskbar"
    echo.
    start "" "Dragon_App"
) ELSE (
    echo.
    echo Build failed with error code %ERRORLEVEL%
    echo.
    echo Try running this batch file as administrator.
    echo.
)

REM Clean up
if exist build_script.py del build_script.py

echo Press any key to exit...
pause >nul 