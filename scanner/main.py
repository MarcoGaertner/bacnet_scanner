import logging
import argparse
import sys
import os
from pathlib import Path

# Füge das Hauptverzeichnis zum Python-Suchpfad hinzu
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent))

from scanner.discovery import BACnetDiscovery

def configure_logging():
    """Konfiguriert das Logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def main():
    """Hauptfunktion für den BACnet-Scanner"""
    configure_logging()
    logger = logging.getLogger('BACnetScanner')
    
    parser = argparse.ArgumentParser(description='BACnet Netzwerk-Scanner')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout für die Gerätesuche in Sekunden')
    parser.add_argument('--no-details', action='store_true', help='Keine detaillierten Informationen abrufen')
    
    args = parser.parse_args()
    
    logger.info("BACnet Scanner wird gestartet...")
    
    # Discovery-Klasse initialisieren und Scan starten
    discovery = BACnetDiscovery()
    logger.info("Starte Netzwerk-Scan...")
    
    discovery.start_scan(timeout=args.timeout, get_details=not args.no_details)
    
    # Ergebnisse ausgeben
    discovery.print_devices()
    
    logger.info("BACnet Scanner beendet.")

if __name__ == "__main__":
    main()