#!/usr/bin/env python3
"""
Setup script for Bravo Sensor Viewer
For creating executable builds with PyInstaller or cx_Freeze
"""

from setuptools import setup, find_packages
import sys
import os

# Import version information
sys.path.insert(0, os.path.dirname(__file__))
from version import __version__, __build_date__, __author__, __description__

# Read requirements
def read_requirements():
    try:
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return ['PyQt5', 'matplotlib', 'numpy']

setup(
    name="bravo-sensor-viewer",
    version=__version__,
    description=__description__,
    author=__author__,
    python_requires=">=3.7",
    install_requires=read_requirements(),
    py_modules=['bravo_sensor_viewer', 'bravo_device_test', 'simple_sensor_test', 'version'],
    entry_points={
        'console_scripts': [
            'bravo-sensor-viewer=bravo_sensor_viewer:main',
            'bravo-device-test=bravo_device_test:main',
            'simple-sensor-test=simple_sensor_test:test_continuous_readings',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-repo/bravo-sensor-viewer/issues",
        "Source": "https://github.com/your-repo/bravo-sensor-viewer",
    },
)

# PyInstaller spec template for executable creation
PYINSTALLER_SPEC = f"""
# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Bravo Sensor Viewer v{__version__}

block_cipher = None

a = Analysis(
    ['bravo_sensor_viewer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('version.py', '.'),
        ('Vibration_test_scripts/passwords_enc_mecha.ini.template', 'Vibration_test_scripts/'),
    ],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BravoSensorViewer_v{__version__}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version_info={{
        'version': '{__version__}',
        'description': '{__description__}',
        'company': '{__author__}',
        'product': 'Bravo Sensor Viewer',
        'copyright': 'Copyright (c) 2025 {__author__}',
    }},
)
"""

if __name__ == "__main__":
    print(f"Setup for Bravo Sensor Viewer v{__version__}")
    print(f"Build date: {__build_date__}")
    print(f"To create executable with PyInstaller, save the spec template above to 'bravo_sensor_viewer.spec'")