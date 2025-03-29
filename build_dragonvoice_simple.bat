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

REM Create a clean build environment to avoid permission issues
echo Creating clean build environment...
set BUILD_DIR=fresh_build_%random%

REM Create directory
mkdir %BUILD_DIR%
cd %BUILD_DIR%

REM Copy necessary files
echo Copying necessary files to build directory...
copy ..\dragon_voice_enhanced.py .
copy ..\Dragon_cli2.py .
copy ..\config.json .
if exist ..\dragon_icon.ico copy ..\dragon_icon.ico .

REM Create simple script to avoid complex command line issues
echo import os > build_script.py
echo import sys >> build_script.py
echo import subprocess >> build_script.py
echo import shutil >> build_script.py
echo. >> build_script.py
echo # Create output dirs >> build_script.py
echo os.makedirs("../Dragon_App", exist_ok=True) >> build_script.py
echo os.makedirs("../Dragon_App/recordings", exist_ok=True) >> build_script.py
echo os.makedirs("../Dragon_App/transcripts", exist_ok=True) >> build_script.py
echo. >> build_script.py
echo # Build the executable >> build_script.py
echo print("Running PyInstaller...") >> build_script.py
echo cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--clean"] >> build_script.py
echo cmd.extend(["--name=DragonVoice"]) >> build_script.py
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
echo print("Running command:", " ".join(cmd)) >> build_script.py
echo result = subprocess.run(cmd, check=False) >> build_script.py
echo if result.returncode != 0: >> build_script.py
echo     print("Error: PyInstaller failed with code", result.returncode) >> build_script.py
echo     sys.exit(result.returncode) >> build_script.py
echo. >> build_script.py
echo # Copy files to output directory >> build_script.py
echo if os.path.exists("dist/DragonVoice.exe"): >> build_script.py
echo     print("Copying executable to Dragon_App folder...") >> build_script.py
echo     shutil.copy2("dist/DragonVoice.exe", "../Dragon_App/DragonVoice.exe") >> build_script.py
echo     print("Copying config file...") >> build_script.py
echo     shutil.copy2("config.json", "../Dragon_App/config.json") >> build_script.py
echo     if os.path.exists("dragon_icon.ico"): >> build_script.py
echo         print("Copying icon...") >> build_script.py
echo         shutil.copy2("dragon_icon.ico", "../Dragon_App/dragon_icon.ico") >> build_script.py
echo     print("Creating readme...") >> build_script.py
echo     with open("../Dragon_App/README.txt", "w") as f: >> build_script.py
echo         f.write("Dragon Voice Assistant\\n") >> build_script.py
echo         f.write("====================\\n\\n") >> build_script.py
echo         f.write("1. Double-click DragonVoice.exe to start\\n") >> build_script.py
echo         f.write("2. Use the Test Coords button to verify your coordinates work\\n") >> build_script.py
echo         f.write("3. To pin to taskbar, right-click on the taskbar icon while running\\n") >> build_script.py
echo     print("Build completed successfully!") >> build_script.py
echo else: >> build_script.py
echo     print("Error: Executable not found after build") >> build_script.py
echo     sys.exit(1) >> build_script.py

REM Run the build script
echo Running build script...
python build_script.py

REM Return to original directory
cd ..

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo.
    echo You can find the executable in the Dragon_App folder.
    echo.
    echo Opening Dragon_App folder...
    start "" "Dragon_App"
) ELSE (
    echo.
    echo Build failed with error code %ERRORLEVEL%
    echo.
    echo Try running this batch file as administrator.
    echo.
)

REM Clean up build directory
echo Cleaning up temporary build files...
rd /s /q %BUILD_DIR% 2>nul

echo Press any key to exit...
pause >nul 