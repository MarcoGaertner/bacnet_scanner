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
from typing import Callable, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner.bacnet_client import BACnetClient
from scanner.network_utils import get_adapter_by_name  # Verwenden der vorhandenen Funktion
from scanner.storage import DatabaseStorage

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
        self.on_progress: Optional[Callable[[float, str], None]] = None
        
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
        

    def _progress(self, pct: float, msg: str):
        try:
            if self.on_progress:
                self.on_progress(float(pct), str(msg))
        except Exception:
            pass
    
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
    
    def _load_user_info(self) -> Dict[str, Any]:
        """Lädt die Benutzerinformationen aus der user_settings.json"""
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
                print(f"DEBUG: User-Info geladen: {user_info}")
        except Exception as e:
            print(f"WARNING: Konnte User-Info nicht laden: {e}")
            user_info = {}
        
        return user_info
    
    async def _discover_network_devices(self) -> Dict[str, Any]:
        """
        Entdeckt BACnet/IP-Geräte im Netzwerk
        """
        self._progress(0.02, "Lade Konfiguration …")
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
        


        self._progress(0.05, "Initialisiere BACnet Client …")
        # BACnet-Client initialisieren
        init_success = await self.bacnet_client.initialize(ip_address, udp_port)
        
        if not init_success:
            return {"error": "BACnet-Client konnte nicht initialisiert werden"}
        
        self.bacnet_client.on_progress = self.on_progress

        try:
            # Scan durchführen
            scan_result = await self.bacnet_client.scan_network()
            
            self._progress(0.97, "Speichere Scan-Ergebnis …")

            # Verbindungsinfo für die Datenbank vorbereiten
            connection_info = {
                "type": "network",
                "ip_address": ip_address,
                "port": udp_port,
                "adapter": adapter_name
            }
            
            # User-Infos laden
            user_info = self._load_user_info()
            
            # Scan-Ergebnis in der Datenbank speichern
            scan_id = self.storage.save_scan_result(
                scan_result, 
                description=f"BACnet/IP-Scan auf {ip_address}:{udp_port}", 
                connection_info=connection_info,
                user_info=user_info  # Jetzt korrekt übergeben
            )
            
            # Prüfen, ob das Speichern erfolgreich war
            if scan_id == -1:
                print("ERROR: Scan konnte nicht in der Datenbank gespeichert werden")
                return {"error": "Scan konnte nicht gespeichert werden"}
            
            # Alte Scans löschen, wenn mehr als 100 vorhanden sind
            deleted_count = self.storage.delete_old_scans(100)
            if deleted_count > 0:
                print(f"INFO: {deleted_count} alte Scans gelöscht")
            
            # Scan-ID zum Ergebnis hinzufügen
            scan_result["scan_id"] = scan_id
            
            print(f"SUCCESS: Scan erfolgreich gespeichert mit ID: {scan_id}")

            self._progress(1.0, "Scan abgeschlossen")
            return scan_result
        
        except Exception as e:
            print(f"Fehler beim Scannen des Netzwerks: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
            
        finally:
            # BACnet-Client schließen
            self.bacnet_client.close()
    
    def set_scan_mode(self, mode: str):
        """Setzt den Scan-Modus für den BACnet-Client"""
        self.bacnet_client.set_scan_mode(mode)