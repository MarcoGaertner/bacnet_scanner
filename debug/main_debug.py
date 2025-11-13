import sys
import os
from pathlib import Path
from datetime import datetime

# Log-Datei erstellen
log_file = Path.home() / "bacnet_scanner_debug.log"

def log(message):
    """Schreibt in Log-Datei und Console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    
    # In Datei schreiben
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)
    
    # Auch in Console ausgeben
    print(log_message.strip())

try:
    log("=" * 60)
    log("BACnet Scanner Start (DEBUG MODE)")
    log("=" * 60)
    log(f"Python Version: {sys.version}")
    log(f"Executable: {sys.executable}")
    log(f"Frozen: {getattr(sys, 'frozen', False)}")
    
    # Füge das Projektverzeichnis zum Python-Suchpfad hinzu
    if getattr(sys, 'frozen', False):
        # Wenn als .exe ausgeführt (PyInstaller)
        application_path = sys._MEIPASS
        log(f"Running as EXE, MEIPASS: {application_path}")
        project_root = Path(application_path)
    else:
        # Wenn als Skript ausgeführt (aus debug/ Ordner)
        # debug/main_debug.py -> gehe 1 Ebene hoch zum project_root
        application_path = os.path.dirname(os.path.abspath(__file__))
        project_root = Path(application_path).parent
        log(f"Running as Script, Path: {application_path}")
        log(f"Project Root: {project_root}")
    
    # Füge project_root zum sys.path hinzu
    sys.path.insert(0, str(project_root))
    if getattr(sys, 'frozen', False):
        sys.path.insert(0, application_path)
    
    log(f"sys.path[0]: {sys.path[0]}")
    log(f"sys.path[1]: {sys.path[1] if len(sys.path) > 1 else 'N/A'}")
    
    # Liste verfügbare Dateien im Bundle
    if getattr(sys, 'frozen', False):
        log("\nDateien im Bundle:")
        for root, dirs, files in os.walk(application_path):
            level = root.replace(application_path, '').count(os.sep)
            indent = ' ' * 2 * level
            log(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # Nur erste 10 Dateien
                log(f"{subindent}{file}")
            if len(files) > 10:
                log(f"{subindent}... und {len(files) - 10} weitere")
    
    log("\nImportiere Module...")
    
    # Versuche Imports einzeln
    try:
        log("  - Importiere ui.widgets.screen_manager...")
        from ui.widgets.screen_manager import AppScreenManager
        log("    ✅ Erfolgreich")
    except Exception as e:
        log(f"    ❌ Fehler: {e}")
        import traceback
        log(traceback.format_exc())
        raise
    
    try:
        log("  - Importiere ui.main...")
        from ui.main import BACnetScannerApp
        log("    ✅ Erfolgreich")
    except Exception as e:
        log(f"    ❌ Fehler: {e}")
        import traceback
        log(traceback.format_exc())
        raise
    
    log("\nStarte Anwendung...")
    app = BACnetScannerApp()
    log("App-Instanz erstellt")
    
    app.run()
    log("App beendet")

except Exception as e:
    log(f"\n❌ KRITISCHER FEHLER:")
    log(f"Typ: {type(e).__name__}")
    log(f"Nachricht: {str(e)}")
    
    import traceback
    log("\nTraceback:")
    log(traceback.format_exc())
    
    # Warte auf Eingabe, damit Console nicht schließt
    input("\nDrücke Enter zum Beenden...")
    sys.exit(1)

finally:
    log(f"\nLog gespeichert in: {log_file}")