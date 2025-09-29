import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Führt ein Kommando aus und gibt Feedback"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} erfolgreich!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei {description}:")
        print(f"   {e.stderr}")
        return False

def main():
    print("🚀 BACnet Scanner v4 - Vollständiger Build-Prozess")
    print("=" * 60)
    
    # 1. Abhängigkeiten prüfen
    print("📋 Prüfe Abhängigkeiten...")
    required_packages = ['pyinstaller', 'kivy', 'bacpypes', 'pandas', 'openpyxl', 'reportlab']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} fehlt - installiere mit: pip install {package}")
            return False
    
    # 2. Cleanup
    print("\n🧹 Cleanup alter Builds...")
    for folder in ['dist', 'build']:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
            print(f"   🗑️ {folder} entfernt")
    
    # 3. Executable erstellen
    print("\n🔧 Erstelle Executable...")
    pyinstaller_cmd = [
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
        'scanner/main.py'
    ]
    
    if not run_command(' '.join(pyinstaller_cmd), "PyInstaller Build"):
        return False
    
    # 4. Installer erstellen (falls NSIS verfügbar)
    print("\n📦 Erstelle Installer...")
    if os.path.exists('installer.nsi'):
        nsis_cmd = 'makensis installer.nsi'
        if not run_command(nsis_cmd, "NSIS Installer"):
            print("⚠️ NSIS Installer konnte nicht erstellt werden (NSIS installiert?)")
    else:
        print("⚠️ installer.nsi nicht gefunden - überspringe Installer-Erstellung")
    
    # 5. Ergebnisse anzeigen
    print("\n🎉 Build-Prozess abgeschlossen!")
    print("📁 Ergebnisse:")
    
    exe_path = Path('dist/BACnet_Scanner_v4.exe')
    if exe_path.exists():
        print(f"   ✅ Executable: {exe_path.absolute()}")
        print(f"   📏 Größe: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    installer_path = Path('BACnet_Scanner_v4_Installer.exe')
    if installer_path.exists():
        print(f"   ✅ Installer: {installer_path.absolute()}")
        print(f"   📏 Größe: {installer_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)