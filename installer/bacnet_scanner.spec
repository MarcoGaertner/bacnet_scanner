# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['scanner/main.py'],  # Ihr Hauptskript
    pathex=['.'],
    binaries=[],
    datas=[
        ('ui', 'ui'),  # UI-Dateien einschließen
        ('config', 'config'),  # Konfigurationsdateien
        ('assets', 'assets'),  # Assets/Icons
        ('core', 'core'),  # Core-Module
        ('exporter', 'exporter'),  # Export-Module
    ],
    hiddenimports=[
        'kivy.deps.sdl2',
        'kivy.deps.glew',
        'kivy.deps.gstreamer',
        'bacpypes',
        'asyncio',
        'sqlite3',
        'pandas',
        'openpyxl',
        'reportlab',
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
    name='BACnet_Scanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Für GUI-Anwendung
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ui/assets/icons/connection_yel-logo.ico'  # Ihr App-Icon
)