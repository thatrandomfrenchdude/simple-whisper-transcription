@echo off
echo ===============================================
echo Simple Whisper Transcription - Builder
echo ===============================================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ERROR: Virtual environment not detected!
    echo Please activate your virtual environment first:
    echo   .\whisper-venv\Scripts\Activate.ps1
    echo.
    pause
    exit /b 1
)

echo Virtual environment detected: %VIRTUAL_ENV%
echo.

echo Installing build dependencies...
pip install -r build-requirements.txt

echo.
echo Running build script...
python build_executable.py

echo.
echo Build process completed.
pause
