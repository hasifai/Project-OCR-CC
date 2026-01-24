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

echo Building OCR Translator.exe...
pyinstaller --onefile --noconsole --name "OCR Translator" main.py

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Output: dist\OCR Translator.exe
echo.
pause
