"""
Hauptmodul für den BACnet-Scanner
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional

from .discovery import DeviceDiscovery
from .storage import DatabaseStorage

async def run_scan(config_path: str = "config/connection_settings.json", scan_mode: str = 'standard') -> Dict[str, Any]:
    """
    Führt einen Scan basierend auf den Einstellungen in der Konfigurationsdatei durch
    
    Args:
        config_path: Pfad zur Konfigurationsdatei
        scan_mode: Scan-Modus ('standard', 'extended', 'full')
    """
    # Discovery-Instanz erstellen
    discovery = DeviceDiscovery(config_path)
    
    # Scan-Modus setzen, falls vorhanden
    discovery.set_scan_mode(scan_mode)
    
    # Geräte entdecken
    result = await discovery.discover_devices()
    
    return result

def list_scans(limit: int = 10):
    """
    Listet die letzten Scans auf
    
    Args:
        limit: Maximale Anzahl anzuzeigender Scans
    """
    storage = DatabaseStorage()
    scans = storage.get_scan_list(limit)
    
    if not scans:
        print("Keine Scan-Ergebnisse gefunden.")
        return
    
    print(f"\nLetzte {len(scans)} Scans:")
    print("-" * 80)
    print(f"{'ID':<5} {'Datum/Zeit':<20} {'Modus':<10} {'Geräte':<7} {'Beschreibung':<30}")
    print("-" * 80)
    
    for scan in scans:
        scan_id = scan['scan_id']
        timestamp = scan['timestamp'][:19].replace('T', ' ')  # ISO-Format kürzen und formatieren
        scan_mode = scan['scan_mode']
        device_count = scan['device_count']
        description = scan['description'][:30]
        
        print(f"{scan_id:<5} {timestamp:<20} {scan_mode:<10} {device_count:<7} {description:<30}")

def show_scan_details(scan_id: int):
    """
    Zeigt die Details eines bestimmten Scans
    
    Args:
        scan_id: ID des Scans
    """
    storage = DatabaseStorage()
    scan = storage.get_scan_details(scan_id)
    
    if not scan:
        print(f"Scan mit ID {scan_id} nicht gefunden.")
        return
    
    print(f"\nDetails für Scan {scan_id}:")
    print(f"Datum/Zeit: {scan['timestamp']}")
    print(f"Scan-Modus: {scan['scan_mode']}")
    print(f"Geräteanzahl: {scan['device_count']}")
    print(f"Beschreibung: {scan['description']}")
    print("\nGefundene Geräte:")
    
    for device in scan['devices']:
        device_id = device['device_id']
        address = device['address']
        properties = device['properties']
        
        print(f"\nGerät {device_id} bei {address}:")
        for prop_name, prop_value in properties.items():
            if prop_name != 'objects':
                print(f"  {prop_name}: {prop_value}")
        
        # Objekte anzeigen, wenn im 'full' Modus gescannt wurde
        if 'objects' in properties:
            objects = properties['objects']
            print(f"\n  Objekte ({len(objects)}):")
            
            # Zeige bis zu 5 Objekte
            for i, obj in enumerate(objects[:5]):
                obj_type = obj.get('type', 'unbekannt')
                obj_instance = obj.get('instance', 'unbekannt')
                obj_name = obj.get('name', 'unbekannt')
                present_value = obj.get('present-value', 'N/A')
                
                print(f"    {i+1}. {obj_type},{obj_instance} - '{obj_name}' = {present_value}")
            
            if len(objects) > 5:
                print(f"    ... und {len(objects) - 5} weitere Objekte")

def search_devices(search_term: str):
    """
    Sucht nach Geräten mit dem angegebenen Suchbegriff
    
    Args:
        search_term: Suchbegriff (Name, Beschreibung, Standort)
    """
    storage = DatabaseStorage()
    results = storage.search_devices(search_term)
    
    if not results:
        print(f"Keine Geräte mit dem Suchbegriff '{search_term}' gefunden.")
        return
    
    print(f"\nGefundene Geräte für '{search_term}':")
    print("-" * 80)
    
    for device in results:
        device_id = device['device_id']
        address = device['address']
        properties = device['properties']
        scan_id = device['scan_id']
        timestamp = device['timestamp'][:19].replace('T', ' ')
        
        name = properties.get('object-name', 'Unbekannt')
        description = properties.get('description', '')
        location = properties.get('location', '')
        
        print(f"Gerät {device_id} bei {address}")
        print(f"  Name: {name}")
        if description:
            print(f"  Beschreibung: {description}")
        if location:
            print(f"  Standort: {location}")
        print(f"  Gefunden in Scan {scan_id} am {timestamp}")
        print("-" * 40)

def main():
    """
    Hauptfunktion, die beim direkten Aufruf des Moduls ausgeführt wird
    """
    # Standardwerte
    scan_mode = 'standard'
    
    # Befehlszeilenargumente verarbeiten
    if len(sys.argv) > 1:
        # Befehle prüfen
        if sys.argv[1] == "list":
            # Liste der letzten Scans anzeigen
            limit = 10
            if len(sys.argv) > 2:
                try:
                    limit = int(sys.argv[2])
                except ValueError:
                    pass
            list_scans(limit)
            return
        
        elif sys.argv[1] == "show" and len(sys.argv) > 2:
            # Details eines bestimmten Scans anzeigen
            try:
                scan_id = int(sys.argv[2])
                show_scan_details(scan_id)
            except ValueError:
                print(f"Ungültige Scan-ID: {sys.argv[2]}")
            return
        
        elif sys.argv[1] == "search" and len(sys.argv) > 2:
            # Nach Geräten suchen
            search_term = sys.argv[2]
            search_devices(search_term)
            return
        
        elif sys.argv[1] == "delete" and len(sys.argv) > 2:
            # Scan löschen
            try:
                scan_id = int(sys.argv[2])
                storage = DatabaseStorage()
                if storage.delete_scan(scan_id):
                    print(f"Scan mit ID {scan_id} wurde gelöscht.")
                else:
                    print(f"Scan mit ID {scan_id} konnte nicht gelöscht werden.")
            except ValueError:
                print(f"Ungültige Scan-ID: {sys.argv[2]}")
            return
        
        elif sys.argv[1] == "help":
            # Hilfe anzeigen
            print("\nVerwendung des BACnet-Scanners:")
            print("  py -m scanner.main [IP Adresse] [Port] [scan_mode]  - Führt einen Scan durch")
            print("  py -m scanner.main list [limit]                    - Zeigt die letzten Scans an")
            print("  py -m scanner.main show [scan_id]                  - Zeigt Details zu einem Scan")
            print("  py -m scanner.main search [term]                   - Sucht nach Geräten")
            print("  py -m scanner.main delete [scan_id]                - Löscht einen Scan")
            print("  py -m scanner.main help                           - Zeigt diese Hilfe an")
            print("\nScan-Modi:")
            print("  standard  - Grundlegende Geräteeigenschaften")
            print("  extended  - Erweiterte Geräteeigenschaften")
            print("  full      - Alle Geräteeigenschaften inkl. Objektliste")
            return
        
        # Wenn keiner der Befehle, dann als Scan-Parameter interpretieren
        ip_address = sys.argv[1]
        port = 47808
        
        # Port prüfen (zweites Argument)
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print(f"Ungültiger Port: {sys.argv[2]}. Verwende Standardport 47808.")
        
        # Scan-Modus prüfen (drittes Argument)
        if len(sys.argv) > 3 and sys.argv[3] in ['standard', 'extended', 'full']:
            scan_mode = sys.argv[3]
        
        # Temporäre Konfiguration erstellen
        config = {
            "connection": {
                "type": "network",
                "network": {
                    "ip_address": ip_address,
                    "udp_port": str(port)
                }
            }
        }
        
        # Temporäre Konfigurationsdatei erstellen
        temp_config_path = "config/temp_connection_settings.json"
        os.makedirs(os.path.dirname(temp_config_path), exist_ok=True)
        
        with open(temp_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Scan mit temporärer Konfiguration ausführen
        result = asyncio.run(run_scan(temp_config_path, scan_mode))
        
        # Temporäre Konfigurationsdatei löschen
        try:
            os.remove(temp_config_path)
        except:
            pass
        
        # Ergebnis ausgeben
        if "error" in result:
            print(f"Fehler: {result['error']}")
        else:
            print(f"\nScan abgeschlossen: {result['device_count']} Geräte gefunden")
            print(f"Scan-Modus: {scan_mode}")
            print(f"Scan-ID: {result.get('scan_id', 'Nicht gespeichert')}")
            print("\nVerwendung:")
            print(f"  py -m scanner.main show {result.get('scan_id', '')}  - Zeigt die Details dieses Scans")
    else:
        # Ohne Argumente - Hilfe anzeigen
        print("\nVerwendung des BACnet-Scanners:")
        print("  py -m scanner.main [IP Adresse] [Port] [scan_mode]  - Führt einen Scan durch")
        print("  py -m scanner.main list [limit]                    - Zeigt die letzten Scans an")
        print("  py -m scanner.main show [scan_id]                  - Zeigt Details zu einem Scan")
        print("  py -m scanner.main search [term]                   - Sucht nach Geräten")
        print("  py -m scanner.main delete [scan_id]                - Löscht einen Scan")
        print("  py -m scanner.main help                           - Zeigt diese Hilfe an")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer unterbrochen.")
    except Exception as e:
        print(f"\nFehler: {e}")
        import traceback
        traceback.print_exc()