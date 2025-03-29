@echo off
echo ====================================
echo Dragon Voice Assistant Simple Builder
echo ====================================
echo.
echo This script will build the Dragon Voice Assistant executable
echo in a completely fresh directory without depending on any existing files.
echo.
echo The executable will be created in the Dragon_App folder.
echo.

REM Kill any Python processes that might be interfering
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

REM Run the simple build script
echo Running simple build script...
python simple_build.py

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo.
    echo You can find the executable in the Dragon_App folder.
    echo.
    echo Press any key to exit...
) ELSE (
    echo.
    echo Build failed with error code %ERRORLEVEL%
    echo.
    echo Try running this batch file as administrator.
    echo.
    echo Press any key to exit...
)

pause >nul 