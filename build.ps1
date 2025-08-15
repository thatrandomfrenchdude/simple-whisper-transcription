# Simple Whisper Transcription - Builder (PowerShell)
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Simple Whisper Transcription - Builder" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "ERROR: Virtual environment not detected!" -ForegroundColor Red
    Write-Host "Please activate your virtual environment first:" -ForegroundColor Yellow
    Write-Host "  .\whisper-venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

Write-Host "Installing build dependencies..." -ForegroundColor Yellow
pip install -r build-requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install build dependencies!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Running build script..." -ForegroundColor Yellow
python build_executable.py

Write-Host ""
Write-Host "Build process completed." -ForegroundColor Green
Read-Host "Press Enter to exit"
