# Live Transcription with AI Hub Whisper

Streaming transcription application built with [Whisper Base En](https://aihub.qualcomm.com/compute/models/whisper_base_en?domain=Audio) from [Qualcomm AI Hub](https://aihub.qualcomm.com/).

### Table of Contents
[1. Purpose](#purpose)<br>
[2. Code Organization](#code-organization)<br>
[3. Implementation](#implementation)<br>
[4. Setup](#setup)<br>
[5. Usage](#usage)<br>
[6. Building an Executable](#building-an-executable)<br>
[7. Contributing](#contributing)<br>
[8. Code of Conduct](#code-of-conduct)<br>

### Purpose
This is an extensible base app for custom language transcription workflows using Whisper. Base performance is acceptable and can be improved.

### Code Organization
This project provides two main implementations:

**AI Hub Version (Original)**
- `src/LiveTranscriber.py` - Main transcriber using Qualcomm AI Hub
- `src/model.py` - ONNX model wrapper with QNN optimization
- Requires AI Hub dependencies

**Standalone Version (No AI Hub)**
- `src/LiveTranscriber_standalone.py` - Standalone transcriber without AI Hub
- `src/standalone_model.py` - Independent ONNX model wrapper
- `src/standalone_whisper.py` - Custom Whisper implementation
- No AI Hub dependencies required

Both versions use the same ONNX model files and configuration but have different dependency requirements.

### Implementation
This app was built for the Snapdragon X Elite but designed to be platform agnostic. Performance may vary on other hardware.

- Machine: Dell Latitude 7455
- Chip: Snapdragon X Elite
- OS: Windows 11
- Memory: 32 GB
- Python Version: 3.11.9 (x86)

### Setup
1. Download & Extract [FFMPeg for Windows](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip).
    1. Extract the zip to `C:\Program Files`
    2. Rename `ffmpeg-master-latest-win64-gpl` to `ffmpeg`
    3. Add `C:\Program Files\ffmpeg\bin` to your $PATH
        1. Click the Windows button and search "Edit environment variables"
        2. Click "Edit environment variables for your account"
        3. In User variables, choose `Path` and click edit
        4. Click new to make an entry with `C:\Program Files\ffmpeg\bin`
        5. Click OK to save
        6. In a new PowerShell, run ffmpeg to verify installation
2. Open a PowerShell instance and clone the repo
    ```
    git clone https://github.com/thatrandomfrenchdude/simple-whisper-transcription.git
    ```
3. Create and activate your virtual environment with reqs
    ```
    # 1. navigate to the cloned directory
    cd simple-whisper-transcription

    # 2. create the python virtual environment
    python -m venv whisper-venv

    # 3. activate the virtual environment
    ./whisper-venv/Scripts/Activate.ps1     # windows

    # 4. install the requirements
    pip install -r requirements.txt
    ```
4. Download the model from AI Hub*
    1. Create a directory called `models` at the project root
    2. From the project root, run `python -m qai_hub_models.models.whisper_base_en.export --target-runtime onnx`
    3. Copy the model files from `build` to `models`
    
    *NOTE: There is a bug in some versions of AI Hub that may cause the model not to work. If you encounter any issues, try downloading these preconverted models from [this google drive](https://drive.google.com/drive/folders/14RzasqSFfgO4Wtbw_tZ1Qs3Y22F8lymY?usp=sharing) and **skip straight to step 5**.
5. Create your `config.yaml` file with the following variables
    ```
    # audio settings
    "sample_rate": 16000          # Audio sample rate in Hz
    "chunk_duration": 4           # Duration of each audio chunk in seconds
    "channels": 1                 # Number of audio channels (1 for mono)

    # processing settings
    "max_workers": 4              # Number of parallel transcription workers
    "silence_threshold": 0.001    # Threshold for silence detection
    "queue_timeout": 1.0          # Timeout for audio queue operations

    # model paths
    "encoder_path": "models/WhisperEncoder.onnx"
    "decoder_path": "models/WhisperDecoder.onnx"
    ```

### Usage

#### AI Hub Version (Original)
With the virtual environment active, run the original AI Hub version:
```
python src\LiveTranscriber.py 
```

#### Standalone Version (No AI Hub)
With the virtual environment active, run the standalone version:
```
python src\LiveTranscriber_standalone.py 
```

Both versions provide the same functionality but use different model loading approaches. The standalone version is more portable and doesn't require AI Hub dependencies.

### Building an Executable
To create a standalone executable that can run without Python installed:

1. **With your virtual environment activated**, run the build script:
   ```powershell
   # PowerShell (recommended)
   .\build.ps1
   
   # Or Command Prompt
   build.bat
   
   # Or manually
   python build_executable.py
   ```

2. **Find your executable** in the `dist` folder:
   - `WhisperTranscriber.exe` - The main executable
   - `launch_transcriber.bat` - Launcher that keeps console open

3. **Copy the config file, mel_filters.npz, and models folder** to the `dist` folder:
   - `config.yaml`
   - `mel_filters.npz`
   - `models/` (entire folder)

4. **Run the executable**:
   - Double-click `WhisperTranscriber.exe` for direct execution
   - Double-click `launch_transcriber.bat` for better user experience (recommended)

5. **For distribution**: Copy the entire `dist` folder to other computers. The executable includes all dependencies and will show transcription in a command-line interface.

For detailed build instructions and troubleshooting, see [BUILD_EXECUTABLE.md](BUILD_EXECUTABLE.md).

### Contributing
Contributions to extend the functionality are welcome and encouraged. Please review the [contribution guide](CONTRIBUTING.md) prior to submitting a pull request. 

Please do your best to maintain the "base template" spirit of the app so that it remains a blank canvas for developers looking to build a custom local chat app.

### Code of Conduct
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/). Read more about it in the [code of conduct](CODE_OF_CONDUCT.md) file.