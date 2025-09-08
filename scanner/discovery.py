"""
Geräte-Discovery-Schnittstelle für verschiedene Verbindungstypen
"""

import os
import json
import time
import sys
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .bacnet_client import BACnetClient
from scanner.network_utils import get_adapter_by_name  # Verwenden der vorhandenen Funktion
from .storage import DatabaseStorage

class DeviceDiscovery:
    """
    Klasse zur Geräteentdeckung mit verschiedenen Verbindungsmethoden
    """
    
    def __init__(self, config_path: str = "config/connection_settings.json"):
        """Initialisiert die Geräteentdeckung mit der angegebenen Konfiguration"""
        self.config_path = config_path
        self.config = {}
        
        # Client-Instanzen für verschiedene Verbindungstypen
        self.bacnet_client = BACnetClient()
        
        # Speicher für Scan-Ergebnisse initialisieren
        self.storage = DatabaseStorage()
        
    def load_config(self) -> Dict[str, Any]:
        """Lädt die Konfiguration aus der connection_settings.json"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            return self.config
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {e}")
            return {}
    
    async def discover_devices(self) -> Dict[str, Any]:
        """
        Entdeckt Geräte basierend auf der aktuellen Konfiguration
        """
        # Konfiguration laden
        self.load_config()
        
        if not self.config:
            return {"error": "Keine Konfiguration gefunden"}
        
        connection_type = self.config.get("connection", {}).get("type")
        
        if connection_type == "network":
            return await self._discover_network_devices()
        elif connection_type == "mstp":
            # Hier könnte in Zukunft die MS/TP-Discovery implementiert werden
            return {"error": "MS/TP-Discovery noch nicht implementiert"}
        elif connection_type == "device_ap":
            # Hier könnte in Zukunft die Device AP-Discovery implementiert werden
            return {"error": "Device AP-Discovery noch nicht implementiert"}
        elif connection_type == "usb":
            # Hier könnte in Zukunft die USB-Discovery implementiert werden
            return {"error": "USB-Discovery noch nicht implementiert"}
        else:
            return {"error": f"Unbekannter Verbindungstyp: {connection_type}"}
    
    async def _discover_network_devices(self) -> Dict[str, Any]:
        """
        Entdeckt BACnet/IP-Geräte im Netzwerk
        """
        network_config = self.config.get("connection", {}).get("network", {})
        
        # Adapter-Name aus Konfiguration holen
        adapter_name = network_config.get("adapter", "")
        
        # IP-Adresse aus Adapter-Info oder direkt aus Konfiguration holen
        ip_address = network_config.get("ip_address", "")
        if not ip_address and adapter_name:
            # Adapter-Information abrufen
            adapter_info = get_adapter_by_name(adapter_name)
            if adapter_info and adapter_info.get("ip_address"):
                ip_address = adapter_info.get("ip_address")
        
        if not ip_address:
            return {"error": "Keine gültige IP-Adresse gefunden"}
        
        # UDP-Port aus Konfiguration holen
        udp_port_str = network_config.get("udp_port", "BAC0 (47808)")
        
        # UDP-Port-String parsen
        if "(" in udp_port_str and ")" in udp_port_str:
            udp_port = int(udp_port_str.split("(")[1].split(")")[0])
        else:
            try:
                udp_port = int(udp_port_str)
            except ValueError:
                udp_port = 47808  # Standard BACnet-Port
        
        # BACnet-Client initialisieren
        init_success = await self.bacnet_client.initialize(ip_address, udp_port)
        
        if not init_success:
            return {"error": "BACnet-Client konnte nicht initialisiert werden"}
        
        try:
            # Scan durchführen
            scan_result = await self.bacnet_client.scan_network()
            
            # Verbindungsinfo für die Datenbank vorbereiten
            connection_info = {
                "type": "network",
                "ip_address": ip_address,
                "port": udp_port,
                "adapter": adapter_name
            }
            
            # --- User-Infos laden (aus config/user_settings.json) ---
            user_info = {}
            try:
                base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent  # Projektwurzel
                user_settings_path = base_dir / "config" / "user_settings.json"
                if user_settings_path.exists():
                    with open(user_settings_path, "r", encoding="utf-8") as f:
                        raw = json.load(f) or {}
                    # Erwartete Struktur: {"user": {"first_name": "...", "last_name": "...", "email": "...", "company": "..."}}
                    u = raw.get("user", raw)
                    user_info = {
                        "first_name": u.get("first_name", ""),
                        "last_name":  u.get("last_name", ""),
                        "email":      u.get("email", ""),
                        "company":    u.get("company", ""),
                    }
            except Exception as _e:
                # still write scan without user_info
                user_info = {}
            
            # Scan-Ergebnis in der Datenbank speichern
            scan_id = self.storage.save_scan_result(
                scan_result, 
                description=f"BACnet/IP-Scan auf {ip_address}:{udp_port}", 
                connection_info=connection_info,
                user_info=user_info
            )
            
            # Alte Scans löschen, wenn mehr als 100 vorhanden sind
            self.storage.delete_old_scans(100)
            
            # Scan-ID zum Ergebnis hinzufügen
            scan_result["scan_id"] = scan_id
            
            return scan_result
        
        except Exception as e:
            print(f"Fehler beim Scannen des Netzwerks: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
            
        finally:
            # BACnet-Client schließen
            self.bacnet_client.close()
    
    def _save_scan_result(self, scan_result: Dict[str, Any], description: str = ""):
        """Speichert das Scan-Ergebnis mit dem neuen Speichermechanismus"""
        try:
            scan_id = self.storage.save_scan_result(scan_result, description)
            print(f"Scan-Ergebnis gespeichert mit ID: {scan_id}")
            
            # Alte Scan-Ergebnisse löschen, wenn mehr als 100 vorhanden sind
            deleted_count = self.storage.delete_old_scans(100)
            if deleted_count > 0:
                print(f"{deleted_count} alte Scan-Ergebnisse gelöscht.")
                
            return scan_id
        except Exception as e:
            print(f"Fehler beim Speichern des Scan-Ergebnisses: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        
    def _cleanup_old_scans(self):
        """
        Löscht alte Scan-Ergebnisse, wenn mehr als 100 vorhanden sind
        """
        try:
            # Alle Scan-Dateien auflisten
            scan_files = sorted([
                os.path.join(self.scan_results_dir, f)
                for f in os.listdir(self.scan_results_dir)
                if f.startswith("scan_") and f.endswith(".json")
            ])
            
            # Überprüfen, ob mehr als 100 Scan-Dateien vorhanden sind
            while len(scan_files) > 100:
                # Älteste Datei löschen
                oldest_file = scan_files.pop(0)
                os.remove(oldest_file)
                print(f"Alte Scan-Datei gelöscht: {oldest_file}")
        except Exception as e:
            print(f"Fehler beim Aufräumen alter Scan-Ergebnisse: {e}")

    def set_scan_mode(self, mode: str):
        """Setzt den Scan-Modus für den BACnet-Client"""
        self.bacnet_client.set_scan_mode(mode)