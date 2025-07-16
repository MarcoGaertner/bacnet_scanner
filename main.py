import sys
import os

# Füge das Projektverzeichnis zum Python-Suchpfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main import BACnetScannerApp

if __name__ == '__main__':
    BACnetScannerApp().run()