@echo off
echo ========================================
echo   OCR Translator - Build Script
echo ========================================
echo.

:: Check if pyinstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo Building launcher.exe...
pyinstaller --onefile --noconsole --name "OCR Translator" launcher.py

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Output files in 'dist' folder:
echo   - OCR Translator.exe (the launcher)
echo.
echo To distribute, copy these files together:
echo   - dist/OCR Translator.exe
echo   - main.py
echo.
pause
