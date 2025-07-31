import logging
from .bacnet_client import BACnetClient

class BACnetDiscovery:
    """Klasse für die Erkennung von BACnet-Geräten im Netzwerk"""
    
    def __init__(self, config=None):
        """Initialisiert die Discovery-Klasse"""
        self.logger = logging.getLogger('BACnetDiscovery')
        self.client = BACnetClient(config)
        self.devices = []
    
    def start_scan(self, timeout=10, get_details=True):
        """Startet einen Scan nach BACnet-Geräten"""
        self.logger.info(f"Starte BACnet-Scan (Timeout: {timeout}s)")
        
        # Verbindung zum BACnet-Netzwerk herstellen
        if not self.client.connect():
            self.logger.error("Verbindung fehlgeschlagen, Scan abgebrochen")
            return []
        
        try:
            # Who-Is-Anfrage senden und auf Antworten warten
            discovered_devices = self.client.discover_devices(timeout)
            
            # Ergebnisse sammeln
            self.devices = []
            
            if not discovered_devices:
                self.logger.warning("Keine BACnet-Geräte gefunden")
                return []
            
            self.logger.info(f"Verarbeite {len(discovered_devices)} gefundene Geräte")
            
            # Details für jedes gefundene Gerät abrufen
            for device in discovered_devices:
                try:
                    # Je nach BAC0-Version kann die Struktur unterschiedlich sein
                    if hasattr(device, 'address'):
                        device_address = device.address
                        device_id = device.device_id
                    else:
                        # Alternativ könnte device ein Tuple oder Dict sein
                        device_address = getattr(device, 'address', 
                                             getattr(device, 'bacnet_address', None))
                        device_id = getattr(device, 'device_id', 
                                        getattr(device, 'instance', None))
                    
                    if device_address is None or device_id is None:
                        self.logger.warning(f"Ungültiges Geräteformat: {device}")
                        continue
                        
                    if get_details:
                        # Detaillierte Informationen abrufen
                        device_info = self.client.get_device_properties(device_address, device_id)
                        self.devices.append(device_info)
                    else:
                        # Nur grundlegende Informationen hinzufügen
                        self.devices.append({
                            "name": "Unbekannt",
                            "type": "Unbekannt",
                            "address": device_address,
                            "id": device_id
                        })
                except Exception as e:
                    self.logger.error(f"Fehler bei der Verarbeitung des Geräts: {e}")
            
            self.logger.info(f"Scan abgeschlossen: {len(self.devices)} Geräte gefunden")
            return self.devices
            
        except Exception as e:
            self.logger.error(f"Fehler während des Scans: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
        finally:
            # Verbindung trennen
            self.client.disconnect()
    
    def get_devices(self):
        """Gibt die Liste der gefundenen Geräte zurück"""
        return self.devices
    
    def print_devices(self):
        """Gibt die gefundenen Geräte in der Konsole aus"""
        if not self.devices:
            print("Keine Geräte gefunden")
            return
        
        print("\nGefundene BACnet-Geräte:")
        print("========================")
        for i, device in enumerate(self.devices):
            name = device.get('name', 'Unbekannt')
            device_type = device.get('type', 'Unbekannt')
            address = device.get('address', 'Unbekannt')
            device_id = device.get('id', 'Unbekannt')
            
            print(f"{i+1}. {name}")
            print(f"   Typ:      {device_type}")
            print(f"   Adresse:  {address}")
            print(f"   Geräte-ID: {device_id}")
            print()