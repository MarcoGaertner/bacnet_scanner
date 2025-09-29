# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\scanner\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('ui', 'ui'), ('config', 'config'), ('core', 'core'), ('exporter', 'exporter'), ('assets', 'assets')],
    hiddenimports=['kivy.deps.sdl2', 'kivy.deps.glew', 'kivy.deps.angle', 'kivy_garden', 'kivy_garden.graph', 'bacpypes3', 'BAC0', 'netifaces', 'asyncio', 'sqlite3', 'aiosqlite', 'pandas', 'numpy', 'openpyxl', 'reportlab', 'lxml', 'svglib', 'PIL', 'PIL.Image', 'flask', 'werkzeug', 'dateutil', 'dotenv', 'requests', 'plyer', 'win32api', 'win32gui', 'win32con'],
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
    name='BACnet_Scanner_v4',
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
    icon=['ui\\assets\\icons\\connection_yel-logo.ico'],
)
