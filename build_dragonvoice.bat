@echo off
echo ===================================
echo Dragon Voice Assistant Builder
echo ===================================
echo.

REM Set console title
title Dragon Voice Assistant Builder

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found! Please install Python 3.8 or higher.
    echo Visit https://www.python.org/downloads/ to download and install Python.
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Python version:
python --version
echo.

REM Run the build script
echo Starting build process...
echo.
python build_dragon_voice.py

REM Check if build was successful
if %ERRORLEVEL% neq 0 (
    echo.
    echo Build failed! Check the errors above.
    pause
    exit /b 1
)

echo.
echo Build process completed!
echo You can now pin DragonVoice.exe to your taskbar.
echo.
pause 