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
        
        # PyInstaller-Kommando mit expliziten Modulpfaden
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name=BACnet_Scanner_v4',
            '--clean',
            f'--distpath={self.dist_dir.absolute()}',
            f'--workpath={self.build_dir.absolute()}',
            f'--specpath={self.project_root.absolute()}',
            
            # Datenverzeichnisse (relativ zum project_root)
            '--add-data=ui;ui',
            '--add-data=config;config',
            '--add-data=core;core',
            '--add-data=exporter;exporter',
            '--add-data=scanner;scanner',  # ← WICHTIG: scanner-Verzeichnis hinzufügen
            
            # Python-Pfad für Imports
            f'--paths={self.project_root.absolute()}',  # ← WICHTIG: Projekt-Root als Python-Pfad
            
            # Explizite Modul-Imports (alle Ihre Module)
            '--hidden-import=ui',
            '--hidden-import=ui.main',
            '--hidden-import=ui.widgets',
            '--hidden-import=ui.widgets.screen_manager',
            '--hidden-import=config',
            '--hidden-import=core',
            '--hidden-import=exporter',
            '--hidden-import=scanner',
            
            # Kivy Dependencies
            '--hidden-import=kivy.deps.sdl2',
            '--hidden-import=kivy.deps.glew',
            '--hidden-import=kivy.deps.angle',
            '--hidden-import=kivy_garden',
            '--hidden-import=kivy_garden.graph',
            
            # BACnet Libraries
            '--hidden-import=bacpypes3',
            '--hidden-import=BAC0',
            '--hidden-import=netifaces',
            
            # Standard Libraries
            '--hidden-import=asyncio',
            '--hidden-import=sqlite3',
            '--hidden-import=aiosqlite',
            
            # Data Processing
            '--hidden-import=pandas',
            '--hidden-import=numpy',
            
            # Export Functions
            '--hidden-import=openpyxl',
            '--hidden-import=reportlab',
            '--hidden-import=lxml',
            '--hidden-import=svglib',
            
            # Image Processing
            '--hidden-import=PIL',
            '--hidden-import=PIL.Image',
            
            # Web Framework
            '--hidden-import=flask',
            '--hidden-import=werkzeug',
            
            # Utilities
            '--hidden-import=dateutil',
            '--hidden-import=dotenv',
            '--hidden-import=requests',
            '--hidden-import=plyer',
            
            # Windows-specific
            '--hidden-import=win32api',
            '--hidden-import=win32gui',
            '--hidden-import=win32con',
            
            # Entry Point
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
                    cmd.insert(-1, f'--icon={icon_path}')
                else:
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