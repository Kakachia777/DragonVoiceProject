@echo off
echo ======================================
echo Dragon Voice Enhanced - EXE Builder
echo ======================================
echo.
echo This script will build the Dragon Voice Enhanced executable
echo with hardcoded coordinates and failsafe disabled.
echo.

REM Kill any Python processes that might be interfering
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

REM Create a clean build directory with random name to avoid conflicts
set BUILD_DIR=temp_build_%random%
echo Creating fresh build directory: %BUILD_DIR%
mkdir %BUILD_DIR%
cd %BUILD_DIR%

REM Copy necessary files
echo Copying necessary files...
copy ..\dragon_voice_enhanced.py .
copy ..\Dragon_cli2.py .
copy ..\config.json .
if exist ..\dragon_icon.ico copy ..\dragon_icon.ico .

REM Create output directory
mkdir ..\DragonVoice 2>nul
mkdir ..\DragonVoice\recordings 2>nul
mkdir ..\DragonVoice\transcripts 2>nul

REM Install PyInstaller if needed
echo Checking for PyInstaller...
python -c "import PyInstaller" 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Installing PyInstaller...
  pip install pyinstaller
  if %ERRORLEVEL% NEQ 0 (
    echo Failed to install PyInstaller
    cd ..
    rd /s /q %BUILD_DIR%
    exit /b 1
  )
)

REM Build the executable
echo Building executable...
python -m PyInstaller --clean --noconfirm --onefile --noconsole ^
  --name=DragonVoice ^
  --add-data "Dragon_cli2.py;." ^
  --add-data "config.json;." ^
  --icon=dragon_icon.ico dragon_voice_enhanced.py

REM Check if build was successful
if not exist dist\DragonVoice.exe (
  echo Error: Build failed!
  cd ..
  rd /s /q %BUILD_DIR%
  exit /b 1
)

REM Copy files to output directory
echo Copying files to output directory...
copy dist\DragonVoice.exe ..\DragonVoice\
copy config.json ..\DragonVoice\
if exist dragon_icon.ico copy dragon_icon.ico ..\DragonVoice\

REM Create README file
echo Creating README file...
echo Dragon Voice Enhanced Application > ..\DragonVoice\README.txt
echo ============================= >> ..\DragonVoice\README.txt
echo. >> ..\DragonVoice\README.txt
echo Features: >> ..\DragonVoice\README.txt
echo - Hardcoded chatbot coordinates >> ..\DragonVoice\README.txt
echo - Custom key press support (Enter, Shift+Enter, etc.) >> ..\DragonVoice\README.txt
echo - Test Coordinates button for verification >> ..\DragonVoice\README.txt
echo. >> ..\DragonVoice\README.txt
echo Instructions: >> ..\DragonVoice\README.txt
echo 1. Double-click DragonVoice.exe to start >> ..\DragonVoice\README.txt
echo 2. Use the Test Coords button to verify coordinates >> ..\DragonVoice\README.txt
echo 3. To pin to taskbar, right-click the icon when app is running >> ..\DragonVoice\README.txt

REM Clean up
cd ..
echo Cleaning up build files...
rd /s /q %BUILD_DIR%

echo.
echo Build completed successfully!
echo Executable is in the DragonVoice folder.
echo.

REM Open the folder
start DragonVoice

echo Press any key to exit...
pause >nul
