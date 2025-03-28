@echo off
echo ===== Dragon Voice Assistant Executable Builder =====
echo.
echo This script will build DragonVoice.exe with a modern
echo graphical interface and full functionality.
echo.
echo Features:
echo - Modern card-based interface
echo - Complete access to all voice transcription features
echo - Real-time audio level meter
echo - Detailed logging
echo - Profile management for different chatbot layouts
echo - Enhanced settings dialog
echo - Mouse Without Borders support for cross-computer control
echo.
echo Please wait while the build process completes...
echo.

python build_pyinstaller.py

echo.
echo ===== Build process completed =====
echo.
echo If the build was successful, you can find the executable at:
echo - output\DragonVoice\DragonVoice.exe
echo.
echo A desktop shortcut has been created that can be pinned to your taskbar:
echo - Desktop\DragonVoice.lnk
echo.
echo To pin to taskbar:
echo 1. Right-click the shortcut file
echo 2. Select "Pin to taskbar" from the context menu
echo.
echo To use with Mouse Without Borders:
echo 1. Install Mouse Without Borders on all computers
echo 2. Run Dragon Voice Assistant on your main computer
echo 3. Use the Calibrate function to set up chatbot positions
echo 4. For best results, increase the delay settings in Settings
echo.
echo A ZIP file for distribution is available at:
echo - output\DragonVoice.zip
echo.
echo Press any key to exit...
pause > nul 