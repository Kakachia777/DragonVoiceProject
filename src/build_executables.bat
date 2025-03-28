@echo off
echo Dragon Voice Executable Builder
echo =============================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    exit /b 1
)

:: Install PyInstaller if not already installed
echo Checking for PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)

echo.
echo Creating output directories...
if not exist "output" mkdir output
if not exist "output\DragonVoiceA" mkdir output\DragonVoiceA
if not exist "output\DragonVoiceB" mkdir output\DragonVoiceB

:: Create dragon_gui_minimal_a.py if it doesn't exist
if not exist dragon_gui_minimal_a.py (
    echo Creating dragon_gui_minimal_a.py...
    copy dragon_gui_minimal.py dragon_gui_minimal_a.py
)

:: Create dragon_gui_minimal_b.py if it doesn't exist
if not exist dragon_gui_minimal_b.py (
    echo Creating dragon_gui_minimal_b.py...
    copy dragon_gui_minimal.py dragon_gui_minimal_b.py
    powershell -Command "(Get-Content dragon_gui_minimal_b.py) -replace 'import Dragon_cli2 as dragon_cli', 'import dragon_cli' | Set-Content dragon_gui_minimal_b.py"
)

echo.
echo Building Computer A executable (Dragon_cli2.py)...
echo ---------------------------------------------
python -m PyInstaller --noconfirm --onefile --windowed --icon=dragon_icon.ico --name=DragonVoiceA dragon_gui_minimal_a.py
if %errorlevel% neq 0 (
    echo Error building Computer A executable.
    exit /b 1
)

echo.
echo Building Computer B executable (dragon_cli.py)...
echo ---------------------------------------------
python -m PyInstaller --noconfirm --onefile --windowed --icon=dragon_icon.ico --name=DragonVoiceB dragon_gui_minimal_b.py
if %errorlevel% neq 0 (
    echo Error building Computer B executable.
    exit /b 1
)

echo.
echo Copying files for Computer A...
copy /Y "dist\DragonVoiceA.exe" "output\DragonVoiceA\"
copy /Y "Dragon_cli2.py" "output\DragonVoiceA\"
copy /Y "config.json" "output\DragonVoiceA\"
copy /Y "dragon_icon.ico" "output\DragonVoiceA\"

echo.
echo Copying files for Computer B...
copy /Y "dist\DragonVoiceB.exe" "output\DragonVoiceB\"
copy /Y "dragon_cli.py" "output\DragonVoiceB\"
copy /Y "config copy.json" "output\DragonVoiceB\config.json"
copy /Y "dragon_icon.ico" "output\DragonVoiceB\"

echo.
echo Build completed successfully!
echo Executables are available in:
echo   - output\DragonVoiceA\DragonVoiceA.exe
echo   - output\DragonVoiceB\DragonVoiceB.exe
echo.
echo You can distribute these folders to the target computers.
echo. 