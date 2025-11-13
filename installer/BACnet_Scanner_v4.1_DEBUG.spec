# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\debug\\main_debug.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\z004M8JW\\Documents\\Programmieren\\BACnet-Scanner\\bacnet_scanner\\ui', 'ui'), ('C:\\Users\\z004M8JW\\Documents\\Programmieren\\BACnet-Scanner\\bacnet_scanner\\config', 'config'), ('C:\\Users\\z004M8JW\\Documents\\Programmieren\\BACnet-Scanner\\bacnet_scanner\\core', 'core'), ('C:\\Users\\z004M8JW\\Documents\\Programmieren\\BACnet-Scanner\\bacnet_scanner\\exporter', 'exporter'), ('C:\\Users\\z004M8JW\\Documents\\Programmieren\\BACnet-Scanner\\bacnet_scanner\\assets', 'assets')],
    hiddenimports=['kivy.deps.sdl2', 'kivy.deps.glew', 'kivy.deps.angle', 'kivy_garden', 'kivy_garden.graph', 'bacpypes3', 'bacpypes3.apdu', 'bacpypes3.pdu', 'bacpypes3.primitivedata', 'bacpypes3.constructeddata', 'bacpypes3.basetypes', 'bacpypes3.object', 'bacpypes3.local.device', 'bacpypes3.app', 'bacpypes3.netservice', 'BAC0', 'BAC0.core', 'BAC0.core.devices', 'netifaces', 'asyncio', 'sqlite3', 'aiosqlite', 'pandas', 'numpy', 'openpyxl', 'xlsxwriter', 'reportlab', 'reportlab.pdfgen', 'reportlab.lib', 'lxml', 'lxml.etree', 'svglib', 'PIL', 'PIL.Image', 'PIL._imaging', 'flask', 'werkzeug', 'dateutil', 'dateutil.parser', 'dotenv', 'requests', 'plyer', 'win32api', 'win32gui', 'win32con', 'win32com', 'pywintypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'PyQt5', 'PySide2'],
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
    name='BACnet_Scanner_v4.1_DEBUG',
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
    icon=['C:\\Users\\z004M8JW\\Documents\\Programmieren\\BACnet-Scanner\\bacnet_scanner\\ui\\assets\\icons\\connection_yel-logo.ico'],
)
