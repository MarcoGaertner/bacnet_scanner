import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_executable():
    """Erstellt die ausführbare Datei für BACnet Scanner"""
    
    print("🔧 Starte Build-Prozess für BACnet Scanner...")
    
    # Cleanup vorheriger Builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # PyInstaller Kommando
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=BACnet_Scanner_v4',
        '--icon=ui/assets/icons/connection_yel-logo.ico',
        '--add-data=ui;ui',
        '--add-data=config;config',
        '--add-data=assets;assets',
        '--add-data=core;core',
        '--add-data=exporter;exporter',
        '--hidden-import=kivy.deps.sdl2',
        '--hidden-import=kivy.deps.glew',
        '--hidden-import=bacpypes',
        '--hidden-import=asyncio',
        '--hidden-import=sqlite3',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=reportlab',
        'scanner/main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable erfolgreich erstellt!")
        print(f"📁 Ausgabe: {os.path.abspath('dist/BACnet_Scanner_v4.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Erstellen der Executable: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    build_executable()