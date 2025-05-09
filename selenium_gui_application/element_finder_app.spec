# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the path to the webdriver-manager cache
wdm_cache_paths = []
home_dir = os.path.expanduser("~")
wdm_cache_dir = os.path.join(home_dir, ".wdm")
if os.path.exists(wdm_cache_dir):
    wdm_cache_paths.append((wdm_cache_dir, "wdm"))

# Get the path to the resources directory
resources_path = os.path.join("src", "resources")
styles_path = os.path.join(resources_path, "styles")

# Collect all necessary data files
datas = [
    (os.path.join(styles_path, "dark_theme.css"), os.path.join("resources", "styles"))
]

# Add webdriver-manager cache to datas
datas.extend(wdm_cache_paths)

# Collect hidden imports
hidden_imports = [
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.common.by',
    'selenium.webdriver.common.action_chains',
    'selenium.common.exceptions',
    'webdriver_manager',
    'webdriver_manager.chrome',
    'webdriver_manager.core',
    'PyQt5',
    'PyQt5.QtWidgets',
    'PyQt5.QtCore',
    'PyQt5.QtGui'
]

a = Analysis(
    ['src/gui_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='element_finder_app',
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
    icon=None,  # Add an icon file path here if available
)