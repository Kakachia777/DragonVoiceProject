@echo off
echo ====================================
echo Dragon Voice Assistant Builder
echo ====================================
echo.

REM Kill any Python processes that might be interfering
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

REM Install PyInstaller if needed
pip install pyinstaller

REM Create needed directories
mkdir Dragon_App 2>nul
mkdir Dragon_App\recordings 2>nul
mkdir Dragon_App\transcripts 2>nul
mkdir Dragon_App\logs 2>nul

REM Build the executable
echo Building executable...
pyinstaller --onefile --noconsole --clean --name=DragonVoice ^
  --add-data "Dragon_cli2.py;." ^
  --add-data "config.json;." ^
  dragon_voice_enhanced.py

REM Copy files to output folder
echo Copying files to Dragon_App folder...
copy dist\DragonVoice.exe Dragon_App\
copy config.json Dragon_App\
if exist dragon_icon.ico copy dragon_icon.ico Dragon_App\

echo.
echo Build completed!
echo You can find the executable in the Dragon_App folder.
echo.
echo To pin to taskbar:
echo 1. Right-click on DragonVoice.exe in the Dragon_App folder
echo 2. Select "Create shortcut"
echo 3. Right-click on the shortcut and select "Pin to taskbar"
echo.

start "" "Dragon_App"

echo Press any key to exit...
pause >nul 