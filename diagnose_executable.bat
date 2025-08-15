@echo off
echo ===============================================
echo Whisper Transcriber - Enhanced Diagnostic Test
echo ===============================================
echo.

REM Check if executable exists
if not exist "dist\WhisperTranscriber.exe" (
    echo ERROR: WhisperTranscriber.exe not found in dist folder!
    echo Please run the build script first.
    pause
    exit /b 1
)

echo ✓ Executable found
echo.

REM Check file sizes
echo Executable size:
for %%A in ("dist\WhisperTranscriber.exe") do echo   %%~nA%%~xA: %%~zA bytes

echo.
echo ===============================================
echo Checking Required Files in Dist Folder
echo ===============================================

REM Check if models exist in dist
if not exist "dist\models" (
    echo WARNING: models folder not found in dist!
    echo Copying models folder to dist...
    if exist "models" (
        xcopy "models" "dist\models\" /E /I /Y
        echo ✓ Models copied to dist folder
    ) else (
        echo ERROR: No models folder found in project root!
    )
) else (
    echo ✓ Models folder found in dist
)

REM Check if whisper assets exist in dist
if not exist "dist\whisper" (
    echo INFO: whisper assets folder not found in dist (should be bundled by PyInstaller)
) else (
    echo ✓ Whisper assets folder found in dist
    if exist "dist\whisper\assets" (
        echo ✓ Whisper assets subfolder found
        if exist "dist\whisper\assets\gpt2.tiktoken" (
            echo ✓ gpt2.tiktoken found (tokenizer should work!)
        ) else (
            echo WARNING: gpt2.tiktoken not found
        )
    )
)

if not exist "dist\models\WhisperEncoder.onnx" (
    echo WARNING: WhisperEncoder.onnx not found in dist\models\
    if exist "models\WhisperEncoder.onnx" (
        copy "models\WhisperEncoder.onnx" "dist\models\"
        echo ✓ WhisperEncoder.onnx copied
    )
) else (
    echo ✓ WhisperEncoder.onnx found
    for %%A in ("dist\models\WhisperEncoder.onnx") do echo   Size: %%~zA bytes
)

if not exist "dist\models\WhisperDecoder.onnx" (
    echo WARNING: WhisperDecoder.onnx not found in dist\models\
    if exist "models\WhisperDecoder.onnx" (
        copy "models\WhisperDecoder.onnx" "dist\models\"
        echo ✓ WhisperDecoder.onnx copied
    )
) else (
    echo ✓ WhisperDecoder.onnx found
    for %%A in ("dist\models\WhisperDecoder.onnx") do echo   Size: %%~zA bytes
)

REM Check if config exists in dist
if not exist "dist\config.yaml" (
    echo WARNING: config.yaml not found in dist!
    if exist "config.yaml" (
        copy "config.yaml" "dist\"
        echo ✓ config.yaml copied to dist
    ) else (
        echo ERROR: No config.yaml found in project root!
    )
) else (
    echo ✓ config.yaml found in dist
)

echo.
echo ===============================================
echo Directory Contents
echo ===============================================
echo Project root contents:
dir /b

echo.
echo Dist directory contents:
dir /b dist

if exist "dist\models" (
    echo.
    echo Models directory contents:
    dir /b dist\models
)

echo.
echo ===============================================
echo Running Executable Test
echo ===============================================
echo.
echo This will run the executable for a few seconds to test initialization.
echo Look for these key messages:
echo   🚀 Starting Standalone Whisper Transcription
echo   ✅ Configuration loaded successfully
echo   ✅ Model files found
echo   🤖 Loading Standalone Whisper model...
echo   ✅ Model loaded successfully!
echo   ✅ Microphone stream initialized...
echo.
echo If you see these messages, the executable is working correctly!
echo.
pause

cd dist
timeout /t 2 /nobreak >nul
echo Starting executable test...
WhisperTranscriber.exe
cd ..

echo.
echo ===============================================
echo Diagnostic completed.
echo ===============================================
echo.
echo If you saw the initialization messages above, the executable is working!
echo If there were errors, they should be visible in the output above.
echo.
pause
