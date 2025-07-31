import logging
import json
import os
import tempfile
import subprocess
import sys
import re
from pathlib import Path
from scanner.direct_bacnet_scan import scan_for_devices

class BACnetDiscovery:
    """Klasse für die Erkennung von BACnet-Geräten im Netzwerk"""
    
    def __init__(self, config=None):
        """Initialisiert die Discovery-Klasse"""
        self.logger = logging.getLogger('BACnetDiscovery')
        self.config = config or self.load_config()
        self.devices = []
    
    def load_config(self):
        """Lädt die Konfiguration aus der connection_settings.json-Datei"""
        try:
            base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
            config_file = base_dir / "config" / "connection_settings.json"
            
            with open(config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Verbindungstyp und zugehörige Konfiguration extrahieren
            conn_type = settings.get("connection", {}).get("type", "network")
            conn_config = settings.get("connection", {}).get(conn_type, {})
            
            self.logger.info(f"Konfiguration geladen: {conn_type}")
            return {"type": conn_type, **conn_config}
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            return {"type": "network", "ip_address": "0.0.0.0", "udp_port": "47808"}
    
    def start_scan(self, timeout=10, get_details=True):
        """Startet einen Scan nach BACnet-Geräten"""
        self.logger.info(f"Starte BACnet-Scan (Timeout: {timeout}s)")
        
        try:
            # Konfiguration verarbeiten
            ip_address = self.config.get("ip_address", "0.0.0.0")
            
            # Direkt die scan_for_devices-Funktion aufrufen
            self.devices = scan_for_devices(ip_address, timeout=timeout)
            
            self.logger.info(f"Scan abgeschlossen: {len(self.devices)} Geräte gefunden")
            return self.devices
                
        except Exception as e:
            self.logger.error(f"Fehler während des Scans: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def get_devices(self):
        """Gibt die Liste der gefundenen Geräte zurück"""
        return self.devices
    
    def print_devices(self):
        """Gibt die gefundenen Geräte mit detaillierten Informationen aus"""
        if not self.devices:
            print("Keine Geräte gefunden")
            return
        
        print("\nGefundene BACnet-Geräte:")
        print("========================")
        for i, device in enumerate(self.devices):
            # Name - verwende den tatsächlichen Namen oder generiere einen aus der ID
            name = device.get('name', f"Device {device.get('id')}")
            
            # Typ - kombiniere Hersteller und Modell, falls verfügbar
            device_type = "Unknown"
            if 'vendor' in device and 'model' in device:
                device_type = f"{device['vendor']} {device['model']}"
            elif 'model' in device:
                device_type = device['model']
            elif 'vendor' in device:
                device_type = f"{device['vendor']} Device"
            
            address = device.get('address', 'Unbekannt')
            device_id = device.get('id', 'Unbekannt')
            
            print(f"{i+1}. {name}")
            print(f"   Typ:      {device_type}")
            print(f"   Adresse:  {address}")
            print(f"   Geräte-ID: {device_id}")
            
            if 'description' in device and device['description']:
                print(f"   Beschreibung: {device['description']}")
                
            if 'location' in device and device['location']:
                print(f"   Standort:    {device['location']}")
                
            print()