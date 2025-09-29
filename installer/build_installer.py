import os
import subprocess
import sys
import shutil
from pathlib import Path
import re
import pkg_resources
from packaging import version

class BACnetScannerBuilder:
    def __init__(self):
        self.installer_dir = Path(__file__).parent
        self.project_root = self.installer_dir.parent
        self.output_dir = self.installer_dir / "output"
        self.dist_dir = self.output_dir / "dist"
        self.build_dir = self.output_dir / "build"
        
        # Prüfe ob wir in einer venv sind
        self.in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        print(f"🏗️ Installer-Verzeichnis: {self.installer_dir}")
        print(f"🏠 Projekt-Root: {self.project_root}")
        print(f"🐍 Virtuelle Umgebung: {'✅ Aktiv' if self.in_venv else '❌ Nicht aktiv'}")
        print(f"📤 Output-Verzeichnis: {self.output_dir}")

    def get_import_name(self, package_name):
        """Konvertiert Paketnamen zu Import-Namen"""
        import_mapping = {
            'pyinstaller': 'PyInstaller',
            'pywin32': 'win32api',
            'kivy-deps.angle': 'kivy_deps.angle',
            'kivy-deps.glew': 'kivy_deps.glew', 
            'kivy-deps.sdl2': 'kivy_deps.sdl2',
            'Kivy-Garden': 'kivy_garden',
            'kivy-garden.graph': 'kivy_garden.graph',
            'python-dateutil': 'dateutil',
            'python-dotenv': 'dotenv',
            'pillow': 'PIL',
            'pywin32-ctypes': 'win32ctypes',
            'bacpypes3': 'bacpypes3',
            'BAC0': 'BAC0',
            'Flask': 'flask',
            'Werkzeug': 'werkzeug'
        }
        
        return import_mapping.get(package_name, package_name.lower())

    def parse_version_spec(self, package_spec):
        """Parst Paket-Spezifikation und extrahiert Name und Versionsbedingung"""
        match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!]+)(.+)$', package_spec.strip())
        
        if match:
            package_name = match.group(1)
            operator = match.group(2)
            required_version = match.group(3)
            return package_name, operator, required_version
        else:
            return package_spec.strip(), None, None

    def check_version_compatibility(self, installed_version, operator, required_version):
        """Prüft ob installierte Version die Anforderung erfüllt"""
        if operator is None:
            return True
        
        try:
            installed = version.parse(installed_version)
            required = version.parse(required_version)
            
            if operator == '>=':
                return installed >= required
            elif operator == '==':
                return installed == required
            elif operator == '<=':
                return installed <= required
            elif operator == '>':
                return installed > required
            elif operator == '<':
                return installed < required
            elif operator == '!=':
                return installed != required
            else:
                return True
        except Exception:
            return True

    def get_installed_version(self, package_name):
        """Ermittelt die installierte Version eines Pakets"""
        try:
            return pkg_resources.get_distribution(package_name).version
        except pkg_resources.DistributionNotFound:
            return None

    def parse_requirements(self, requirements_file):
        """Parst requirements.txt und entfernt Kommentare"""
        requirements = []
        
        if not requirements_file.exists():
            return [
                'pyinstaller>=6.0.0', 'kivy>=2.0.0', 'bacpypes3>=0.0.100', 
                'BAC0>=2025.0.0', 'pandas>=2.0.0', 'openpyxl>=3.0.0', 
                'reportlab>=4.0.0', 'pillow>=10.0.0', 'requests>=2.30.0'
            ]
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                if line:
                    requirements.append(line)
        
        return requirements

    def cleanup(self):
        """Bereinigt vorherige Builds"""
        print("🧹 Bereinige vorherige Builds...")
        
        for folder in [self.output_dir]:
            if folder.exists():
                shutil.rmtree(folder)
                print(f"   🗑️ {folder.name} entfernt")
        
        self.output_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)

    def check_dependencies(self):
        """Prüft erforderliche Python-Abhängigkeiten"""
        print("📋 Prüfe Python-Abhängigkeiten...")
        
        if not self.in_venv:
            print("⚠️ WARNUNG: Keine virtuelle Umgebung aktiv!")
        
        requirements_file = self.installer_dir / "requirements.txt"
        required_packages = self.parse_requirements(requirements_file)
        
        missing_packages = []
        available_packages = []
        
        for package_spec in required_packages:
            package_name, operator, required_version = self.parse_version_spec(package_spec)
            import_name = self.get_import_name(package_name)
            
            try:
                if import_name == 'sqlite3':
                    import sqlite3
                    installed_version = "3.x"
                else:
                    __import__(import_name)
                    installed_version = self.get_installed_version(package_name)
                
                if operator and required_version and installed_version:
                    if self.check_version_compatibility(installed_version, operator, required_version):
                        available_packages.append(package_spec)
                        print(f"   ✅ {package_spec} (installiert: {installed_version})")
                    else:
                        missing_packages.append(package_spec)
                        print(f"   ❌ {package_spec} (installiert: {installed_version}, benötigt: {operator}{required_version})")
                else:
                    available_packages.append(package_spec)
                    print(f"   ✅ {package_spec} (installiert: {installed_version or 'unbekannt'})")
                    
            except ImportError:
                missing_packages.append(package_spec)
                print(f"   ❌ {package_spec} (nicht installiert)")
        
        if missing_packages:
            print(f"\n⚠️ Fehlende oder inkompatible Pakete ({len(missing_packages)}):")
            for pkg in missing_packages:
                print(f"   - {pkg}")
            
            print(f"\n💡 Installiere/aktualisiere Pakete:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
        
        print(f"✅ Alle Abhängigkeiten verfügbar ({len(available_packages)} Pakete)")
        return True

    def build_executable(self):
        """Erstellt die ausführbare Datei"""
        print("🔧 Erstelle Executable mit PyInstaller...")
        
        # Wechsle ins Projekt-Root für PyInstaller
        original_cwd = os.getcwd()
        os.chdir(self.project_root)
        print(f"📂 Arbeitsverzeichnis gewechselt zu: {self.project_root}")
        
        try:
            # Prüfe ob Entry Point existiert
            entry_point = Path("scanner/main.py")
            if not entry_point.exists():
                print(f"❌ Entry Point nicht gefunden: {entry_point.absolute()}")
                return False
            
            print(f"✅ Entry Point gefunden: {entry_point.absolute()}")
            
            # PyInstaller-Kommando (jetzt mit korrekten relativen Pfaden)
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--windowed',
                '--name=BACnet_Scanner_v4',
                '--clean',
                f'--distpath={self.dist_dir.absolute()}',
                f'--workpath={self.build_dir.absolute()}',
                f'--specpath={self.project_root.absolute()}',  # ← HIER IST DIE ÄNDERUNG
                
                # Datenverzeichnisse (relativ zum project_root)
                '--add-data=ui;ui',
                '--add-data=config;config',
                '--add-data=core;core',
                '--add-data=exporter;exporter',
                
                # Hidden Imports
                '--hidden-import=kivy.deps.sdl2',
                '--hidden-import=kivy.deps.glew',
                '--hidden-import=kivy.deps.angle',
                '--hidden-import=kivy_garden',
                '--hidden-import=kivy_garden.graph',
                '--hidden-import=bacpypes3',
                '--hidden-import=BAC0',
                '--hidden-import=netifaces',
                '--hidden-import=asyncio',
                '--hidden-import=sqlite3',
                '--hidden-import=aiosqlite',
                '--hidden-import=pandas',
                '--hidden-import=numpy',
                '--hidden-import=openpyxl',
                '--hidden-import=reportlab',
                '--hidden-import=lxml',
                '--hidden-import=svglib',
                '--hidden-import=PIL',
                '--hidden-import=PIL.Image',
                '--hidden-import=flask',
                '--hidden-import=werkzeug',
                '--hidden-import=dateutil',
                '--hidden-import=dotenv',
                '--hidden-import=requests',
                '--hidden-import=plyer',
                '--hidden-import=win32api',
                '--hidden-import=win32gui',
                '--hidden-import=win32con',
                
                # Entry Point (relativ zum project_root)
                'scanner/main.py'
            ]
            
            # Assets hinzufügen falls vorhanden
            if Path("assets").exists():
                cmd.insert(-1, '--add-data=assets;assets')
                print("   📁 Assets hinzugefügt")
            
            # Icon hinzufügen
            icon_paths = [
                Path("ui/assets/icons/connection_yel-logo.ico"),
                self.installer_dir / "assets" / "installer_icon.ico"
            ]
            
            for icon_path in icon_paths:
                if icon_path.exists():
                    if icon_path.is_absolute():
                        # Für absolute Pfade (installer assets)
                        cmd.insert(-1, f'--icon={icon_path}')
                    else:
                        # Für relative Pfade (project assets)
                        cmd.insert(-1, f'--icon={icon_path}')
                    print(f"   🎨 Icon: {icon_path}")
                    break
            
            print(f"🐍 Python: {sys.executable}")
            print(f"🔧 Starte PyInstaller...")
            
            # PyInstaller ausführen
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Executable erfolgreich erstellt!")
            
            # Prüfe Ergebnis
            exe_path = self.dist_dir / "BACnet_Scanner_v4.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 Executable: {exe_path}")
                print(f"📏 Größe: {size_mb:.1f} MB")
                return True
            else:
                print("❌ Executable nicht gefunden!")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller Fehler: {e}")
            if e.stdout:
                print(f"Stdout: {e.stdout}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")
            return False
        finally:
            # Arbeitsverzeichnis zurücksetzen
            os.chdir(original_cwd)
            print(f"📂 Arbeitsverzeichnis zurückgesetzt zu: {original_cwd}")


    def check_nsis(self):
        """Prüft ob NSIS verfügbar ist"""
        print("🔍 Prüfe NSIS-Installation...")
        try:
            result = subprocess.run(['makensis', '/VERSION'], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"   ✅ NSIS gefunden: {version}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ❌ NSIS nicht gefunden!")
            print("   💡 Installiere NSIS von: https://nsis.sourceforge.io/")
            return False

    def build_installer(self):
        """Erstellt den NSIS-Installer"""
        print("📦 Erstelle NSIS-Installer...")
        
        if not self.check_nsis():
            return False
        
        nsi_file = self.installer_dir / "installer.nsi"
        if not nsi_file.exists():
            print(f"❌ {nsi_file} nicht gefunden!")
            return False
        
        original_cwd = os.getcwd()
        os.chdir(self.installer_dir)
        
        try:
            cmd = ['makensis', 'installer.nsi']
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Installer erfolgreich erstellt!")
            
            installer_path = self.installer_dir / "BACnet_Scanner_v4_Installer.exe"
            if installer_path.exists():
                size_mb = installer_path.stat().st_size / 1024 / 1024
                print(f"📁 Installer: {installer_path}")
                print(f"📏 Größe: {size_mb:.1f} MB")
                
                final_installer = self.output_dir / "BACnet_Scanner_v4_Installer.exe"
                shutil.move(str(installer_path), str(final_installer))
                print(f"📦 Finaler Installer: {final_installer}")
                return True
            else:
                print("❌ Installer nicht gefunden!")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ NSIS Fehler: {e}")
            if e.stdout:
                print(f"Stdout: {e.stdout}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")
            return False
        finally:
            os.chdir(original_cwd)

    def show_results(self):
        """Zeigt die Build-Ergebnisse an"""
        print("\n🎉 Build-Prozess abgeschlossen!")
        print("📁 Ergebnisse im installer/output/ Verzeichnis:")
        
        exe_path = self.dist_dir / "BACnet_Scanner_v4.exe"
        if exe_path.exists():
            print(f"   ✅ Executable: {exe_path.relative_to(self.installer_dir)}")
        
        installer_path = self.output_dir / "BACnet_Scanner_v4_Installer.exe"
        if installer_path.exists():
            print(f"   ✅ Installer: {installer_path.relative_to(self.installer_dir)}")
        
        print(f"\n📂 Vollständiger Pfad: {self.output_dir.absolute()}")

    def build_all(self):
        """Führt den kompletten Build-Prozess aus"""
        print("🚀 BACnet Scanner v4 - Installer Build")
        print("=" * 60)
        
        if not self.check_dependencies():
            return False
        
        self.cleanup()
        
        if not self.build_executable():
            return False
        
        if not self.build_installer():
            print("⚠️ Installer-Erstellung fehlgeschlagen, aber Executable verfügbar")
        
        self.show_results()
        return True

def main():
    builder = BACnetScannerBuilder()
    success = builder.build_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()