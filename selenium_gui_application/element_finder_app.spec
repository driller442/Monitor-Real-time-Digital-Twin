# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Projects\\selenium_gui_application\\src\\gui_app.py'],
    pathex=['C:\\Projects\\selenium_gui_application\\src'],
    binaries=[('C:\\Users\\aiaio\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms/qwindows.dll', 'platforms')],
    datas=[('C:\\Projects\\selenium_gui_application\\src\\resources\\styles\\dark_theme.css', 'resources\\styles')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='element_finder_app',
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
