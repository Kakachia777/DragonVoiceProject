@echo off
echo Starting Dragon Voice Assistant Build Process...
echo.

REM Kill any python processes that might be locking files
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

REM Wait a moment to ensure processes are terminated
timeout /t 1 /nobreak >nul

REM Try to clean problematic directories manually
if exist build_temp (
    echo Removing build_temp directory...
    rd /s /q build_temp 2>nul
)

if exist build (
    echo Removing build directory...
    rd /s /q build 2>nul
)

echo Running build script...
python build_dragonvoice_exe.py

echo.
if %ERRORLEVEL% == 0 (
    echo Build completed successfully!
    echo.
    echo The executable is located at output\DragonVoice\DragonVoice.exe
    echo.
    echo Press any key to open the output folder...
    pause > nul
    start explorer.exe "%~dp0output\DragonVoice"
) else (
    echo Build failed with error code %ERRORLEVEL%
    echo Please check the output above for errors.
    echo.
    echo You may need to run this script as administrator or close any applications
    echo that might be locking files in the build directory.
    echo.
    pause
) 