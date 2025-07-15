"""
BACnet Scanner - Haupteinstiegspunkt der Anwendung
"""

import os
import sys

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importiere Factory-Registrierungen
from ui.factory_registers import *
from ui.main import BACnetScannerApp

if __name__ == "__main__":
    app = BACnetScannerApp()
    app.run()