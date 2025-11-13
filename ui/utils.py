import os
import sys
from pathlib import Path

def get_resource_path(relative_path):
    """
    Gibt den absoluten Pfad zu einer Resource zurück.
    Funktioniert sowohl im Development als auch mit PyInstaller.
    
    Args:
        relative_path (str): Relativer Pfad zur Resource (z.B. 'ui/screens/connection_screen.kv')
    
    Returns:
        str: Absoluter Pfad zur Resource
    """
    if getattr(sys, 'frozen', False):
        # Wenn als .exe ausgeführt (PyInstaller)
        # PyInstaller entpackt alles nach sys._MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # Wenn als Skript ausgeführt
        # Gehe vom ui/ Ordner zum project_root
        base_path = Path(__file__).parent.parent
    
    resource_path = base_path / relative_path
    
    # Debug-Ausgabe (nur wenn als .exe ausgeführt)
    if getattr(sys, 'frozen', False):
        if not resource_path.exists():
            print(f"⚠️ Resource nicht gefunden: {resource_path}")
    
    return str(resource_path)