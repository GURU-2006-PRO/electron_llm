# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

# Collect all binaries from key packages
pandas_binaries = collect_dynamic_libs('pandas')
numpy_binaries = collect_dynamic_libs('numpy')

a = Analysis(
    ['api_server.py'],
    pathex=[],
    binaries=pandas_binaries + numpy_binaries,
    datas=[
        ('data', 'data'),
        ('.env', '.'),
        ('*.py', '.'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'flask',
        'flask_cors',
        'google.generativeai',
        'openai',
        'dotenv',
        'sqlite3',
        'json',
        'time',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='api_server',
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
)
