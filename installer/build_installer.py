import os
import subprocess
import sys
import shutil
from pathlib import Path
import re
import pkg_resources
from packaging import version

class BACnetScannerBuilder:
    def __init__(self, app_version=None, debug_mode=False):
        self.installer_dir = Path(__file__).parent
        self.project_root = self.installer_dir.parent
        self.output_dir = self.installer_dir / "output"
        self.dist_dir = self.output_dir / "dist"
        self.build_dir = self.output_dir / "build"
        self.debug_mode = debug_mode
        
        # Versionsinformationen
        self.app_version = app_version or self._get_version_from_user()
        self.app_name = f"BACnet_Scanner_v{self.app_version}"
        if self.debug_mode:
            self.exe_name = f"{self.app_name}_DEBUG.exe"
        else:
            self.exe_name = f"{self.app_name}.exe"
        self.installer_name = f"{self.app_name}_Installer.exe"
        self.spec_name = f"bacnet_scanner_v{self.app_version}.spec"
        
        # Prüfe ob wir in einer venv sind
        self.in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        print(f"🏗️ Installer-Verzeichnis: {self.installer_dir}")
        print(f"🏠 Projekt-Root: {self.project_root}")
        print(f"📦 Version: {self.app_version}")
        print(f"📝 App-Name: {self.app_name}")
        print(f"🐛 Debug-Modus: {'✅ Aktiv' if self.debug_mode else '❌ Inaktiv'}")
        print(f"🐍 Virtuelle Umgebung: {'✅ Aktiv' if self.in_venv else '❌ Nicht aktiv'}")
        print(f"📤 Output-Verzeichnis: {self.output_dir}")

    def _get_version_from_user(self):
        """Fragt den Benutzer nach der Versionsnummer"""
        print("\n" + "=" * 60)
        print("📋 Versionsinformation erforderlich")
        print("=" * 60)
        
        # Versuche Version aus vorhandenen Dateien zu ermitteln
        suggested_version = self._detect_current_version()
        
        if suggested_version:
            print(f"\n💡 Erkannte Version: {suggested_version}")
        
        while True:
            if suggested_version:
                version_input = input(f"\n🔢 Bitte Versionsnummer eingeben (z.B. 4.0, 4.1.2) [{suggested_version}]: ").strip()
                if not version_input:
                    version_input = suggested_version
            else:
                version_input = input(f"\n🔢 Bitte Versionsnummer eingeben (z.B. 4.0, 4.1.2): ").strip()
            
            # Validiere Versionsnummer
            if self._validate_version(version_input):
                print(f"✅ Version bestätigt: {version_input}")
                return version_input
            else:
                print("❌ Ungültige Versionsnummer! Bitte Format wie '4.0' oder '4.1.2' verwenden.")

    def _get_debug_mode_from_user(self):
        """Fragt den Benutzer nach dem Debug-Modus"""
        print("\n" + "=" * 60)
        print("🐛 Debug-Modus Konfiguration")
        print("=" * 60)
        print("\n💡 Debug-Modus zeigt Console-Fenster mit Fehlermeldungen")
        print("   Empfohlen für: Entwicklung und Fehlersuche")
        print("   Release-Modus: Keine Console, nur GUI-Fenster\n")
        
        while True:
            choice = input("Debug-Modus aktivieren? (j/N): ").strip().lower()
            if choice in ['j', 'ja', 'y', 'yes']:
                print("✅ Debug-Modus aktiviert")
                return True
            elif choice in ['n', 'nein', 'no', '']:
                print("✅ Release-Modus aktiviert")
                return False
            else:
                print("❌ Ungültige Eingabe! Bitte 'j' oder 'n' eingeben.")

    def _detect_current_version(self):
        """Versucht die aktuelle Version aus vorhandenen Dateien zu ermitteln"""
        # Suche nach vorhandenen .spec Dateien im installer-Verzeichnis
        spec_files = list(self.installer_dir.glob("bacnet_scanner_v*.spec"))
        if spec_files:
            match = re.search(r'v([\d.]+)\.spec', spec_files[0].name)
            if match:
                return match.group(1)
        
        # Suche nach vorhandenen Executables
        if self.output_dir.exists() and self.dist_dir.exists():
            exe_files = list(self.dist_dir.glob("BACnet_Scanner_v*.exe"))
            if exe_files:
                match = re.search(r'v([\d.]+)', exe_files[0].name)
                if match:
                    return match.group(1)
        
        # Fallback: Standard-Version
        return "4.0"

    def _validate_version(self, version_string):
        """Validiert das Versionsformat"""
        pattern = r'^\d+(\.\d+)*$'
        return bool(re.match(pattern, version_string))

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

    def verify_project_structure(self):
        """Prüft ob alle benötigten Dateien vorhanden sind"""
        print("\n🔍 Prüfe Projektstruktur...")
        
        required_files = [
            "scanner/main.py",
            "ui/main.py",
            "ui/bacnet_scanner.kv",
            "core/config.py",
            "core/events.py",
        ]
        
        required_dirs = [
            "ui/screens",
            "ui/widgets",
            "ui/styles",
            "config",
            "exporter",
        ]
        
        missing = []
        
        for file in required_files:
            file_path = self.project_root / file
            if not file_path.exists():
                missing.append(f"Datei: {file}")
            else:
                print(f"   ✅ {file}")
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing.append(f"Verzeichnis: {dir_name}")
            else:
                print(f"   ✅ {dir_name}/")
        
        if missing:
            print("\n❌ Fehlende Dateien/Verzeichnisse:")
            for item in missing:
                print(f"   - {item}")
            return False
        
        print("✅ Alle benötigten Dateien vorhanden")
        return True

    def cleanup(self):
        """Bereinigt vorherige Builds"""
        print("\n🧹 Bereinige vorherige Builds...")
        
        # Entferne alte Build-Artefakte
        cleanup_items = [
            self.output_dir,
            self.project_root / "build",
            self.project_root / "dist",
        ]
        
        # Entferne alte .spec Dateien im installer-Verzeichnis
        for spec_file in self.installer_dir.glob("bacnet_scanner_v*.spec"):
            cleanup_items.append(spec_file)
        
        for item in cleanup_items:
            if item.exists():
                if item.is_file():
                    item.unlink()
                    print(f"   🗑️ {item.name} entfernt")
                else:
                    shutil.rmtree(item)
                    print(f"   🗑️ {item.name}/ entfernt")
        
        # Erstelle Output-Verzeichnisse
        self.output_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True, parents=True)
        self.build_dir.mkdir(exist_ok=True, parents=True)
        print("   ✅ Output-Verzeichnisse erstellt")

    def check_dependencies(self):
        """Prüft erforderliche Python-Abhängigkeiten"""
        print("\n📋 Prüfe Python-Abhängigkeiten...")
        
        if not self.in_venv:
            print("⚠️ WARNUNG: Keine virtuelle Umgebung aktiv!")
            print("   Empfehlung: Aktiviere die venv mit '.venv\\Scripts\\activate'")
        
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
                        print(f"   ✅ {package_name} {installed_version}")
                    else:
                        missing_packages.append(package_spec)
                        print(f"   ❌ {package_name} {installed_version} (benötigt: {operator}{required_version})")
                else:
                    available_packages.append(package_spec)
                    print(f"   ✅ {package_name} {installed_version or 'unbekannt'}")
                    
            except ImportError:
                missing_packages.append(package_spec)
                print(f"   ❌ {package_name} (nicht installiert)")
        
        if missing_packages:
            print(f"\n⚠️ Fehlende oder inkompatible Pakete ({len(missing_packages)}):")
            for pkg in missing_packages:
                print(f"   - {pkg}")
            
            print(f"\n💡 Installiere/aktualisiere Pakete mit:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
        
        print(f"\n✅ Alle Abhängigkeiten verfügbar ({len(available_packages)} Pakete)")
        return True

    def build_executable(self):
        """Erstellt die ausführbare Datei"""
        print("\n🔧 Erstelle Executable mit PyInstaller...")
        
        # Wechsle ins Projekt-Root für PyInstaller
        original_cwd = os.getcwd()
        os.chdir(self.project_root)
        print(f"📂 Arbeitsverzeichnis: {self.project_root}")
        
        try:
            # Prüfe ob Entry Point existiert
            entry_point = Path("scanner/main.py")
            if not entry_point.exists():
                print(f"❌ Entry Point nicht gefunden: {entry_point.absolute()}")
                return False
            
            print(f"✅ Entry Point: {entry_point}")
            
            # Prüfe ob .spec Datei existiert (im installer-Verzeichnis!)
            spec_file = self.installer_dir / self.spec_name
            
            if spec_file.exists():
                print(f"✅ Verwende .spec Datei: {spec_file.name}")
                cmd = [
                    sys.executable, '-m', 'PyInstaller',
                    '--clean',
                    '--noconfirm',
                    f'--distpath={self.dist_dir.absolute()}',
                    f'--workpath={self.build_dir.absolute()}',
                    str(spec_file)
                ]
            else:
                print("⚠️ Keine .spec Datei gefunden, erstelle Build-Kommando...")
                cmd = self._build_manual_command()
            
            print(f"\n🐍 Python: {sys.executable}")
            print(f"🔧 Starte PyInstaller...\n")
            
            # PyInstaller ausführen
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Zeige wichtige Ausgaben
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if any(keyword in line for keyword in ['WARNING', 'ERROR', 'INFO: Building', 'INFO: Writing']):
                        print(f"   {line}")
            
            print("\n✅ Executable erfolgreich erstellt!")
            
            # Prüfe Ergebnis
            exe_path = self.dist_dir / self.exe_name
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 Executable: {exe_path.name}")
                print(f"📏 Größe: {size_mb:.1f} MB")
                print(f"📂 Pfad: {exe_path}")
                return True
            else:
                print(f"❌ Executable nicht gefunden: {self.exe_name}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ PyInstaller Fehler: {e}")
            if e.stdout:
                print(f"\n--- STDOUT ---")
                print(e.stdout)
            if e.stderr:
                print(f"\n--- STDERR ---")
                print(e.stderr)
            return False
        except Exception as e:
            print(f"\n❌ Unerwarteter Fehler: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            os.chdir(original_cwd)

    def _build_manual_command(self):
        """Erstellt PyInstaller-Kommando ohne .spec Datei"""
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--console' if self.debug_mode else '--windowed',
            f'--name={self.app_name}{"_DEBUG" if self.debug_mode else ""}',
            '--clean',
            '--noconfirm',
            f'--distpath={self.dist_dir.absolute()}',
            f'--workpath={self.build_dir.absolute()}',
            f'--specpath={self.installer_dir.absolute()}',
            
            # Datenverzeichnisse mit ABSOLUTEN Pfaden
            f'--add-data={self.project_root / "ui"};ui',
            f'--add-data={self.project_root / "config"};config',
            f'--add-data={self.project_root / "core"};core',
            f'--add-data={self.project_root / "exporter"};exporter',
        ]
        
        # Assets hinzufügen falls vorhanden
        assets_dir = self.project_root / "assets"
        if assets_dir.exists():
            cmd.append(f'--add-data={assets_dir};assets')
            print("   📁 Assets hinzugefügt")
        
        # Icon hinzufügen
        icon_path = self.project_root / "ui/assets/icons/connection_yel-logo.ico"
        if icon_path.exists():
            cmd.append(f'--icon={icon_path}')
            print(f"   🎨 Icon: {icon_path.name}")
        
        # Hidden imports
        hidden_imports = [
            'kivy.deps.sdl2', 'kivy.deps.glew', 'kivy.deps.angle',
            'kivy_garden', 'kivy_garden.graph',
            'bacpypes3', 'bacpypes3.apdu', 'bacpypes3.pdu',
            'bacpypes3.primitivedata', 'bacpypes3.constructeddata',
            'bacpypes3.basetypes', 'bacpypes3.object',
            'bacpypes3.local.device', 'bacpypes3.app', 'bacpypes3.netservice',
            'BAC0', 'BAC0.core', 'BAC0.core.devices', 'netifaces',
            'asyncio', 'sqlite3', 'aiosqlite',
            'pandas', 'numpy', 'openpyxl', 'xlsxwriter',
            'reportlab', 'reportlab.pdfgen', 'reportlab.lib',
            'lxml', 'lxml.etree', 'svglib',
            'PIL', 'PIL.Image', 'PIL._imaging',
            'flask', 'werkzeug',
            'dateutil', 'dateutil.parser', 'dotenv', 'requests', 'plyer',
            'win32api', 'win32gui', 'win32con', 'win32com', 'pywintypes',
        ]
        
        for imp in hidden_imports:
            cmd.append(f'--hidden-import={imp}')
        
        # Excludes
        excludes = ['matplotlib', 'tkinter', 'PyQt5', 'PySide2']
        for exc in excludes:
            cmd.append(f'--exclude-module={exc}')
        
        # Entry Point - UNTERSCHIEDLICH je nach Debug-Modus!
        if self.debug_mode:
            entry_point = 'debug/main_debug.py'
            print(f"   🐛 Debug Entry Point: {entry_point}")
        else:
            entry_point = 'scanner/main.py'
        
        cmd.append(entry_point)
        
        return cmd

    def check_nsis(self):
        """Prüft ob NSIS verfügbar ist"""
        print("\n🔍 Prüfe NSIS-Installation...")
        try:
            result = subprocess.run(['makensis', '/VERSION'], 
                                  capture_output=True, text=True, check=True)
            nsis_version = result.stdout.strip()
            print(f"   ✅ NSIS gefunden: v{nsis_version}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ❌ NSIS nicht gefunden!")
            print("   💡 Installiere NSIS von: https://nsis.sourceforge.io/")
            print("   📝 NSIS wird für die Installer-Erstellung benötigt")
            return False

    def build_installer(self):
        """Erstellt den NSIS-Installer"""
        if self.debug_mode:
            print("\n⚠️ Installer-Erstellung im Debug-Modus übersprungen")
            return True
        
        print("\n📦 Erstelle NSIS-Installer...")
        
        if not self.check_nsis():
            return False
        
        nsi_file = self.installer_dir / "installer.nsi"
        if not nsi_file.exists():
            print(f"❌ {nsi_file} nicht gefunden!")
            return False
        
        # Prüfe ob Executable existiert
        exe_path = self.dist_dir / self.exe_name
        if not exe_path.exists():
            print(f"❌ Executable nicht gefunden: {exe_path}")
            return False
        
        # Erstelle temporäre NSI-Datei
        temp_nsi = self._create_temp_nsi(nsi_file)
        
        original_cwd = os.getcwd()
        os.chdir(self.installer_dir)
        
        try:
            cmd = ['makensis', '/V3', temp_nsi.name]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('['):
                        print(f"   {line}")
            
            print("\n✅ Installer erfolgreich erstellt!")
            
            installer_path = self.installer_dir / self.installer_name
            if installer_path.exists():
                size_mb = installer_path.stat().st_size / 1024 / 1024
                print(f"📁 Installer: {installer_path.name}")
                print(f"📏 Größe: {size_mb:.1f} MB")
                
                final_installer = self.output_dir / self.installer_name
                shutil.move(str(installer_path), str(final_installer))
                print(f"📦 Finaler Installer: {final_installer}")
                return True
            else:
                print(f"❌ Installer nicht gefunden: {self.installer_name}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ NSIS Fehler: {e}")
            if e.stdout:
                print(f"\n--- STDOUT ---")
                print(e.stdout)
            if e.stderr:
                print(f"\n--- STDERR ---")
                print(e.stderr)
            return False
        except Exception as e:
            print(f"\n❌ Unerwarteter Fehler: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if temp_nsi.exists():
                temp_nsi.unlink()
            os.chdir(original_cwd)

    def _create_temp_nsi(self, original_nsi):
        """Erstellt temporäre NSI-Datei mit angepassten Pfaden"""
        temp_nsi = self.installer_dir / f"installer_v{self.app_version}_temp.nsi"
        
        with open(original_nsi, 'r', encoding='utf-8') as f:
            content = f.read()
        
        replacements = {
            'BACnet_Scanner_v4.exe': self.exe_name,
            'BACnet_Scanner_v4_Installer.exe': self.installer_name,
            'BACnet Scanner v4': f'BACnet Scanner v{self.app_version}',
            'VERSIONMAJOR 4': f'VERSIONMAJOR {self.app_version.split(".")[0]}',
            'VERSIONMINOR 0': f'VERSIONMINOR {self.app_version.split(".")[1] if len(self.app_version.split(".")) > 1 else "0"}',
            'VERSIONBUILD 0': f'VERSIONBUILD {self.app_version.split(".")[2] if len(self.app_version.split(".")) > 2 else "0"}',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(temp_nsi, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return temp_nsi

    def show_results(self):
        """Zeigt die Build-Ergebnisse an"""
        print("\n" + "=" * 60)
        print("🎉 Build-Prozess abgeschlossen!")
        print("=" * 60)
        print("\n📁 Ergebnisse:")
        
        exe_path = self.dist_dir / self.exe_name
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print(f"\n   ✅ Executable:")
            print(f"      📄 Name: {exe_path.name}")
            print(f"      📏 Größe: {size_mb:.1f} MB")
            print(f"      📂 Pfad: {exe_path}")
        
        installer_path = self.output_dir / self.installer_name
        if installer_path.exists():
            size_mb = installer_path.stat().st_size / 1024 / 1024
            print(f"\n   ✅ Installer:")
            print(f"      📄 Name: {installer_path.name}")
            print(f"      📏 Größe: {size_mb:.1f} MB")
            print(f"      📂 Pfad: {installer_path}")
        
        print(f"\n📂 Output-Verzeichnis: {self.output_dir.absolute()}")
        print("\n💡 Nächste Schritte:")
        if exe_path.exists():
            print(f"   1. Teste die .exe: {exe_path}")
        if installer_path.exists():
            print(f"   2. Teste den Installer: {installer_path}")
        print("=" * 60)

    def build_all(self):
        """Führt den kompletten Build-Prozess aus"""
        print("=" * 60)
        print(f"🚀 BACnet Scanner v{self.app_version} - Installer Build")
        print("=" * 60)
        
        if not self.verify_project_structure():
            print("\n❌ Build abgebrochen: Projektstruktur unvollständig")
            return False
        
        if not self.check_dependencies():
            print("\n❌ Build abgebrochen: Abhängigkeiten fehlen")
            return False
        
        self.cleanup()
        
        if not self.build_executable():
            print("\n❌ Build abgebrochen: Executable-Erstellung fehlgeschlagen")
            return False
        
        if not self.build_installer():
            print("\n⚠️ Installer-Erstellung fehlgeschlagen")
            print("   Aber Executable ist verfügbar!")
        
        self.show_results()
        return True

def main():
    """Hauptfunktion"""
    try:
        # Parse Kommandozeilenargumente
        app_version = None
        debug_mode = False
        
        for arg in sys.argv[1:]:
            if arg in ['--debug', '-d']:
                debug_mode = True
            elif not arg.startswith('-'):
                app_version = arg
        
        builder = BACnetScannerBuilder(app_version=app_version, debug_mode=debug_mode)
        
        # Frage nach Debug-Modus wenn nicht per Kommandozeile gesetzt
        if not any(arg in sys.argv for arg in ['--debug', '-d']):
            builder.debug_mode = builder._get_debug_mode_from_user()
            # Update exe_name basierend auf Debug-Modus
            if builder.debug_mode:
                builder.exe_name = f"{builder.app_name}_DEBUG.exe"
            else:
                builder.exe_name = f"{builder.app_name}.exe"
        
        success = builder.build_all()
        
        if success:
            print("\n✅ Build erfolgreich abgeschlossen!")
            sys.exit(0)
        else:
            print("\n❌ Build fehlgeschlagen!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Build durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()