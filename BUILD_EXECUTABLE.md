# Building an Executable

This project includes scripts to build a standalone executable using PyInstaller. The executable will include all dependencies and can be run on Windows machines without requiring Python or the virtual environment.

## Prerequisites

1. Complete the main setup instructions in the README.md
2. Ensure your virtual environment is activated
3. Verify that the models are present in the `models/` folder
4. Ensure `config.yaml` is configured properly

## Building the Executable

### Option 1: Using PowerShell (Recommended)
```powershell
# Make sure you're in the project directory
cd simple-whisper-transcription

# Activate your virtual environment
.\whisper-venv\Scripts\Activate.ps1

# Run the build script
.\build.ps1
```

### Option 2: Using Command Prompt
```cmd
REM Make sure you're in the project directory
cd simple-whisper-transcription

REM Activate your virtual environment
.\whisper-venv\Scripts\activate.bat

REM Run the build script
build.bat
```

### Option 3: Manual Build
```powershell
# Install PyInstaller
pip install -r build-requirements.txt

# Run the build script directly
python build_executable.py
```

## What Gets Built

The build process creates:

1. **WhisperTranscriber.exe** - The main executable
2. **launch_transcriber.bat** - A launcher that keeps the console window open
3. **dist/** folder containing all necessary files

## Running the Executable

After building, you can run the transcriber in several ways:

### Method 1: Direct Execution
Double-click `WhisperTranscriber.exe` in the `dist` folder.

### Method 2: Using the Launcher (Recommended)
Double-click `launch_transcriber.bat` for better user experience. This keeps the console window open and shows a "Press any key to continue" message when the transcription stops.

### Method 3: Command Line
```cmd
cd dist
WhisperTranscriber.exe
```

## Distribution

To distribute the executable to other computers:

1. Copy the entire `dist` folder to the target machine
2. Ensure the following files are included:
   - `WhisperTranscriber.exe`
   - `models/WhisperEncoder.onnx`
   - `models/WhisperDecoder.onnx`
   - `config.yaml`
   - `launch_transcriber.bat` (optional, for better UX)

## Troubleshooting

## Troubleshooting

### Common Issues

**"No output or console messages visible"**
- The executable uses a debug version with enhanced console output
- Make sure you're running `launch_transcriber.bat` instead of the exe directly
- Try running the exe from a command prompt to see any error messages
- Use the `diagnose_executable.bat` script to check for missing files

**"Model files not found"**
- Ensure the `models` folder with the ONNX files is in the same directory as the executable
- Copy the entire models folder from your project root to the dist folder
- Verify both `WhisperEncoder.onnx` and `WhisperDecoder.onnx` are present

**"Config file not found"**
- Ensure `config.yaml` is in the same directory as the executable
- Copy config.yaml from your project root to the dist folder

**"QNN provider failed" or similar ONNX errors****
- The executable automatically falls back to CPU execution if QNN (Snapdragon optimization) fails
- This is normal and the app should still work, just potentially slower
- Look for "✓ Successfully loaded ... with CPU provider" messages

**"Audio device errors"**
- Make sure your microphone is connected and working
- Try running the executable as administrator
- Check Windows audio permissions for the application

**"DLL load failures"**
- The target machine might be missing Visual C++ Redistributables
- Install Microsoft Visual C++ Redistributable for Visual Studio 2019 or later

### Debug Scripts

Use these scripts to diagnose issues:

**`diagnose_executable.bat`** - Comprehensive diagnostic script that:
- Checks if all required files are present
- Lists directory contents
- Runs the executable and captures output
- Provides detailed error information

**`test_python_version.bat`** - Tests the debug Python version to compare with executable:
- Verifies the virtual environment is activated
- Runs the debug version with enhanced output
- Helps identify if the issue is specific to PyInstaller

### Debugging Steps

1. **First, test the Python version**:
   ```cmd
   test_python_version.bat
   ```
   This will show you detailed output and help identify if the issue is with the model loading or PyInstaller.

2. **Run the diagnostic script**:
   ```cmd
   diagnose_executable.bat
   ```
   This will check all files and run the executable with detailed output.

3. **Check the console output** for these key messages:
   - `🚀 Starting Simple Whisper Transcription`
   - `✅ Configuration loaded successfully`
   - `✅ Model files found`
   - `🤖 Loading Whisper model...`
   - `✅ Model loaded successfully!`
   - `✅ Microphone stream initialized...`

4. **If model loading fails**, look for:
   - QNN provider warnings (normal, should fall back to CPU)
   - File path errors
   - ONNX runtime errors

### Build Issues

**"PyInstaller not found"**
- Make sure your virtual environment is activated
- Run `pip install pyinstaller`

**"Module not found during build"**
- Some dependencies might not be detected automatically
- Check the `hiddenimports` list in `build_executable.py` and add missing modules

**"Large executable size"**
- The executable includes all dependencies and can be quite large (100MB+)
- This is normal for ML applications with many dependencies

## Technical Details

The build script:
1. Creates a custom PyInstaller spec file
2. Includes all necessary Python modules and dependencies
3. Bundles the ONNX model files and configuration
4. Creates a single-file executable with embedded dependencies
5. Configures the executable to show a console window for transcription output

The executable will open a command-line interface showing real-time transcription results, just like running the Python script directly.
