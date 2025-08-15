"""
PyInstaller build script for Simple Whisper Transcription
This script compiles the LiveTranscriber_standalone.py (standalone version) into a standalone executable.
The standalone version is used because it has fewer dependencies and is more portable.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")

def create_spec_file():
    """Create a custom .spec file for PyInstaller with all necessary configurations."""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH)

# Get whisper assets dynamically
import whisper
whisper_assets_dir = os.path.join(os.path.dirname(whisper.__file__), 'assets')

a = Analysis(
    ['src/LiveTranscriber_standalone.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('models/*.onnx', 'models'),
        ('src/standalone_whisper.py', 'src'),
        ('src/standalone_model.py', 'src'),
        ('mel_filters.npz', '.'),
        (whisper_assets_dir + '/*', 'whisper/assets'),
    ],
    hiddenimports=[
        'numpy',
        'sounddevice',
        'yaml',
        'queue',
        'threading',
        'concurrent.futures',
        'onnxruntime',
        '_sounddevice',
        'cffi',
        'coloredlogs',
        'humanfriendly',
        'backoff',
        'requests',
        'certifi',
        'urllib3',
        'charset_normalizer',
        'idna',
        'packaging',
        'ruamel.yaml',
        'ruamel.yaml.clib',
        'torch',
        'tqdm',
        'regex',
        'tiktoken',
        'traceback',
        'sys',
        'os',
        'standalone_whisper',
        'standalone_model',
        'samplerate',
        'scipy',
        'scipy.special',
        'whisper',
        'whisper.decoding',
        'whisper.tokenizer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WhisperTranscriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('WhisperTranscriber.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created WhisperTranscriber.spec file.")

def check_requirements():
    """Check if all required files exist."""
    required_files = [
        'config.yaml',
        'src/LiveTranscriber_standalone.py',
        'src/standalone_whisper.py',
        'src/standalone_model.py',
        'models/WhisperEncoder.onnx',
        'models/WhisperDecoder.onnx'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("ERROR: Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nPlease ensure all required files are present before building.")
        return False
    
    print("All required files found.")
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    try:
        # Clean previous builds
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        print("Building executable...")
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            'WhisperTranscriber.spec'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Build completed successfully!")
            print(f"Executable created at: {os.path.abspath('dist/WhisperTranscriber.exe')}")
            return True
        else:
            print("Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"Error during build: {e}")
        return False

def create_launcher_script():
    """Create a comprehensive launcher script that shows loading progress."""
    launcher_content = '''@echo off
title Whisper Transcription Launcher
color 0A
echo ===============================================
echo       Whisper Transcription Launcher
echo ===============================================
echo.
echo Starting Whisper Transcription...
echo.
echo NOTE: Model loading can take 15-30 seconds on first run.
echo       Please be patient while the system initializes.
echo.
echo You should see these messages in order:
echo   [*] Starting Standalone Whisper Transcription
echo   [OK] Configuration loaded successfully
echo   [OK] Model files found
echo   [*] Loading Standalone Whisper model...
echo   [OK] Model loaded successfully!
echo   [OK] Microphone stream initialized...
echo.
echo Once initialized, speak into your microphone and you'll see:
echo   [TRANSCRIPT] [your speech here]
echo.
echo Press Ctrl+C to stop transcription at any time.
echo.
echo ===============================================
echo Launching executable...
echo ===============================================
echo.

REM Change to the directory where the executable is located
cd /d "%~dp0"

REM Check if required files exist
if not exist "WhisperTranscriber.exe" (
    echo ERROR: WhisperTranscriber.exe not found!
    echo Make sure you're running this from the dist folder.
    pause
    exit /b 1
)

if not exist "config.yaml" (
    echo ERROR: config.yaml not found!
    echo Please copy config.yaml to this folder.
    pause
    exit /b 1
)

if not exist "models" (
    echo ERROR: models folder not found!
    echo Please copy the models folder to this folder.
    pause
    exit /b 1
)

REM Run the executable
WhisperTranscriber.exe

echo.
echo ===============================================
echo Transcription session ended.
echo ===============================================
echo.
pause
'''
    
    if os.path.exists('dist'):
        with open('dist/launch_transcriber.bat', 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        print("Created enhanced launch_transcriber.bat in dist folder.")
    else:
        print("Warning: dist folder not found. Launcher will be created after build.")

def main():
    """Main build function."""
    print("=" * 60)
    print("Simple Whisper Transcription - Executable Builder")
    print("=" * 60)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        create_launcher_script()
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print("Your executable is ready:")
        print(f"  Location: {os.path.abspath('dist/WhisperTranscriber.exe')}")
        print(f"  Launcher: {os.path.abspath('dist/launch_transcriber.bat')}")
        print("\nTo run the transcriber:")
        print("  1. Double-click WhisperTranscriber.exe, or")
        print("  2. Double-click launch_transcriber.bat (keeps console open)")
        print("\nNote: Make sure the models folder and config.yaml are in the same")
        print("      directory as the executable when distributing.")
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
