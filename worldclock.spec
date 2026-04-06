# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for World Clock
# Run:  pyinstaller worldclock.spec --noconfirm
# Or:   build.bat  (on Windows)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtXml',
        'PySide6.QtNetwork',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Trim unused large stdlib modules to keep exe smaller
    excludes=[
        'tkinter', 'unittest', 'email', 'html',
        'http', 'urllib', 'xmlrpc', 'pydoc',
        'doctest', 'difflib', 'ftplib', 'imaplib',
        'mailbox', 'msilib', 'optparse', 'pickle',
    ],
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
    name='WorldClock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # compress with UPX if available (smaller file)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # uncomment if you add an icon file
)
