import BAC0
import logging
import json
import os
import re
import time
from pathlib import Path

class BACnetClient:
    """Klasse für die BACnet-Kommunikation"""
    
    def __init__(self, config=None):
        """Initialisiert den BACnet-Client"""
        self.logger = logging.getLogger('BACnetClient')
        self.bacnet = None
        self.config = config or self.load_config()
    
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
    
    def connect(self):
        """Stellt eine Verbindung zum BACnet-Netzwerk her"""
        try:
            # Konfiguration parsen
            conn_type = self.config.get("type", "network")
            
            if conn_type == "network":
                # Netzwerk-Verbindung
                ip_address = self.config.get("ip_address", "0.0.0.0")
                
                # Port aus dem Formatstring extrahieren (z.B. "BAC0 (47808)" -> 47808)
                port_str = self.config.get("udp_port", "BAC0 (47808)")
                port = 47808  # Standardport
                if "(" in port_str and ")" in port_str:
                    port_match = re.search(r'\((\d+)\)', port_str)
                    if port_match:
                        port = int(port_match.group(1))
                
                # Foreign Device Registrierung
                foreign_device = self.config.get("foreign_device", False)
                foreign_device_settings = {}
                
                if foreign_device:
                    bbmd_ip = self.config.get("bbmd_ip", "")
                    
                    # BBMD Port extrahieren
                    bbmd_port_str = self.config.get("bbmd_port", "BAC0 (47808)")
                    bbmd_port = 47808
                    if "(" in bbmd_port_str and ")" in bbmd_port_str:
                        port_match = re.search(r'\((\d+)\)', bbmd_port_str)
                        if port_match:
                            bbmd_port = int(port_match.group(1))
                    
                    foreign_device_settings = {
                        "register": True,
                        "bbmd_address": bbmd_ip,
                        "bbmd_port": bbmd_port
                    }
                
                # BACnet-Client erstellen
                self.logger.info(f"Verbinde mit BACnet-Netzwerk über {ip_address}:{port}")
                
                try:
                    # Verwende die synchrone Version von BAC0.connect
                    self.bacnet = BAC0.connect(
                        ip=ip_address,
                        port=port,
                        **foreign_device_settings
                    )
                    return True
                except TypeError:
                    # Fallback für neuere BAC0-Versionen
                    self.logger.info("Verwende alternativen Verbindungsaufbau für neuere BAC0-Version")
                    self.bacnet = BAC0.lite(
                        ip=ip_address,
                        port=port,
                        **foreign_device_settings
                    )
                    return True
                
            elif conn_type == "device_ap":
                # Direkte Verbindung zu einem Gerät über Access Point
                device_address = self.config.get("device_address", "")
                
                if not device_address:
                    self.logger.error("Keine Geräteadresse für Geräte-AP-Verbindung angegeben")
                    return False
                
                self.logger.info(f"Verbinde mit BACnet-Gerät über AP: {device_address}")
                try:
                    # Synchrone Version
                    self.bacnet = BAC0.connect(ip=device_address)
                except TypeError:
                    # Fallback für neuere BAC0-Versionen
                    self.bacnet = BAC0.lite(ip=device_address)
                return True
                
            else:
                self.logger.error(f"Nicht unterstützter Verbindungstyp: {conn_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verbindungsaufbau: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def disconnect(self):
        """Trennt die Verbindung zum BACnet-Netzwerk"""
        if self.bacnet:
            try:
                self.bacnet.disconnect()
                self.logger.info("BACnet-Verbindung getrennt")
            except Exception as e:
                self.logger.error(f"Fehler beim Trennen der Verbindung: {e}")
    
    def discover_devices(self, timeout=5):
        """Entdeckt BACnet-Geräte im Netzwerk"""
        if not self.bacnet:
            self.logger.error("Keine BACnet-Verbindung vorhanden")
            return []
        
        try:
            self.logger.info(f"Suche nach BACnet-Geräten (Timeout: {timeout}s)")
            
            # Who-Is-Anfrage senden
            # Verwende die richtige Methode je nach BAC0-Version
            if hasattr(self.bacnet, 'whois'):
                self.bacnet.whois()
            else:
                self.bacnet.who_is()
            
            # Warten auf Antworten
            self.logger.info(f"Warte {timeout} Sekunden auf Antworten...")
            time.sleep(timeout)
            
            # Ergebnisse aus dem BAC0-Client abrufen
            devices = getattr(self.bacnet, 'devices', [])
            
            self.logger.info(f"Gefunden: {len(devices)} Geräte")
            return devices
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Gerätesuche: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def get_device_properties(self, device_address, device_id):
        """Ruft Eigenschaften eines BACnet-Geräts ab"""
        try:
            # Remote-Gerät erstellen
            if hasattr(self.bacnet, 'device'):
                # Ältere BAC0-Version
                remote_device = self.bacnet.device(device_address, device_id)
            else:
                # Neuere BAC0-Version mit direktem Gerätezugriff
                remote_device = self.bacnet.get_device(device_address, device_id)
            
            # Versuche verschiedene Wege, die Eigenschaften zu erhalten
            device_name = None
            device_type = None
            
            try:
                # Versuche zunächst direkten Eigenschaftszugriff
                if hasattr(remote_device, 'objectName'):
                    device_name = remote_device.objectName
                if hasattr(remote_device, 'modelName'):
                    device_type = remote_device.modelName
                    
                # Wenn nicht erfolgreich, versuche read_property
                if device_name is None and hasattr(remote_device, 'read_property'):
                    device_name = remote_device.read_property('objectName')
                if device_type is None and hasattr(remote_device, 'read_property'):
                    device_type = remote_device.read_property('modelName')
            except:
                # Im Fehlerfall verwenden wir Standard-Informationen
                self.logger.warning(f"Konnte Geräteeigenschaften nicht vollständig lesen für {device_address}")
            
            # Fallback, falls keine Informationen abgerufen werden konnten
            if device_name is None:
                device_name = f"Gerät {device_id}"
            if device_type is None:
                device_type = "Unbekannt"
                
            return {
                "name": device_name,
                "type": device_type,
                "address": device_address,
                "id": device_id
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Geräteeigenschaften: {e}")
            return {
                "name": f"Gerät {device_id}",
                "type": "Unbekannt",
                "address": device_address,
                "id": device_id
            }