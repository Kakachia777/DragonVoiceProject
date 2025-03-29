@echo off
echo ====================================
echo Dragon Voice Assistant Builder
echo ====================================
echo.

REM Kill any Python processes that might be interfering
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 1 /nobreak >nul

REM Clear any existing build artifacts
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del DragonVoice.spec 2>nul

REM Create output folders
mkdir Dragon_App 2>nul
mkdir Dragon_App\recordings 2>nul
mkdir Dragon_App\transcripts 2>nul
mkdir Dragon_App\logs 2>nul

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller

REM Create a very simple spec file
echo # -*- mode: python -*- > DragonVoice.spec
echo block_cipher = None >> DragonVoice.spec
echo a = Analysis(['dragon_voice_enhanced.py'], pathex=['.'], binaries=[], datas=[('Dragon_cli2.py', '.'), ('config.json', '.')], hiddenimports=[], hookspath=[], runtime_hooks=[], excludes=[], win_no_prefer_redirects=False, win_private_assemblies=False, cipher=block_cipher) >> DragonVoice.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> DragonVoice.spec
echo exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [], name='DragonVoice', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False) >> DragonVoice.spec

REM Build using the spec file
echo Building executable...
pyinstaller --clean DragonVoice.spec

REM Copy files to output folder
echo Copying files to Dragon_App folder...
copy dist\DragonVoice.exe Dragon_App\ 2>nul
copy config.json Dragon_App\ 2>nul
if exist dragon_icon.ico copy dragon_icon.ico Dragon_App\ 2>nul

REM Create a basic readme
echo Dragon Voice Assistant > Dragon_App\README.txt
echo ==================== >> Dragon_App\README.txt
echo. >> Dragon_App\README.txt
echo To pin to taskbar: >> Dragon_App\README.txt
echo 1. Right-click on DragonVoice.exe >> Dragon_App\README.txt
echo 2. Select "Create shortcut" >> Dragon_App\README.txt
echo 3. Right-click on the shortcut and select "Pin to taskbar" >> Dragon_App\README.txt

REM Open the folder
IF EXIST Dragon_App\DragonVoice.exe (
    echo.
    echo Build successful! The executable is in the Dragon_App folder.
    start "" "Dragon_App"
) ELSE (
    echo.
    echo Build may have failed. Check for errors above.
    echo Try running this batch file as administrator.
)

echo.
echo Press any key to exit...
pause >nul 