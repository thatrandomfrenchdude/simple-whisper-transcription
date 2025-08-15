# -*- mode: python ; coding: utf-8 -*-
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
