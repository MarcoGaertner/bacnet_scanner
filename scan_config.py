# scan_config.py
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum, auto
import json
import os
from pathlib import Path

class PropertyCategory(Enum):
    """Kategorien für BACnet-Eigenschaften"""
    BASIC = "Grundlegende Identifikation"
    NETWORK = "Netzwerkinformationen"
    SYSTEM = "Systemspezifische Informationen"
    OPERATIONAL = "Betriebsdaten"
    SECURITY = "Sicherheitsinformationen"

@dataclass
class BACnetProperty:
    """Repräsentiert eine BACnet-Eigenschaft"""
    name: str
    category: PropertyCategory
    enabled: bool = False
    bacnet_id: int = None  # BACnet Property ID
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "enabled": self.enabled,
            "bacnet_id": self.bacnet_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BACnetProperty':
        data['category'] = PropertyCategory(data['category'])
        return cls(**data)

@dataclass
class ScanConfig:
    """Konfiguration für den BACnet-Scan"""
    ip_address: str
    port: int
    timeout: int = 2
    attempts: int = 5
    properties: Dict[str, BACnetProperty] = field(default_factory=lambda: {
        # Grundlegende Identifikation
        "device_id": BACnetProperty("Device ID", PropertyCategory.BASIC, True, 75),
        "vendor_id": BACnetProperty("Vendor ID", PropertyCategory.BASIC, True, 120),
        "object_name": BACnetProperty("Object Name", PropertyCategory.BASIC, False, 77),
        "location": BACnetProperty("Location", PropertyCategory.BASIC, False, 58),
        "description": BACnetProperty("Description", PropertyCategory.BASIC, False, 28),
        "app_version": BACnetProperty("Application Software Version", PropertyCategory.BASIC, False, 12),
        "firmware": BACnetProperty("Firmware Version", PropertyCategory.BASIC, False, 0),
        "model_name": BACnetProperty("Model Name", PropertyCategory.BASIC, False, 70),
        
        # Netzwerkinformationen
        "protocol_version": BACnetProperty("Protocol Version", PropertyCategory.NETWORK, False, 98),
        "protocol_services": BACnetProperty("Protocol Services Supported", PropertyCategory.NETWORK, False, 97),
        "protocol_types": BACnetProperty("Protocol Object Types Supported", PropertyCategory.NETWORK, False, 96),
        "segmentation": BACnetProperty("Segmentation Supported", PropertyCategory.NETWORK, False, 107),
        "max_apdu": BACnetProperty("Max APDU Length", PropertyCategory.NETWORK, False, 62),
        
        # Systemspezifische Informationen
        "system_status": BACnetProperty("System Status", PropertyCategory.SYSTEM, False, 112),
        "local_time": BACnetProperty("Local Time", PropertyCategory.SYSTEM, False, 57),
        "local_date": BACnetProperty("Local Date", PropertyCategory.SYSTEM, False, 56),
        "utc_offset": BACnetProperty("UTC Offset", PropertyCategory.SYSTEM, False, 119),
        
        # Betriebsdaten
        "restart_reason": BACnetProperty("Last Restart Reason", PropertyCategory.OPERATIONAL, False, 196),
        "database_revision": BACnetProperty("Database Revision", PropertyCategory.OPERATIONAL, False, 155),
        
        # Sicherheitsinformationen
        "auth_policy": BACnetProperty("Active Authentication Policy", PropertyCategory.SECURITY, False, 154),
        "security_timeout": BACnetProperty("Security PDU Timeout", PropertyCategory.SECURITY, False, 0)
    })
    
    def get_enabled_properties(self) -> List[BACnetProperty]:
        """Gibt eine Liste aller aktivierten Eigenschaften zurück"""
        return [prop for prop in self.properties.values() if prop.enabled]
    
    def get_properties_by_category(self, category: PropertyCategory) -> List[BACnetProperty]:
        """Gibt alle Eigenschaften einer bestimmten Kategorie zurück"""
        return [prop for prop in self.properties.values() if prop.category == category]
    
    def to_dict(self) -> Dict:
        """Konvertiert die Konfiguration in ein Dictionary"""
        return {
            "ip_address": self.ip_address,
            "port": self.port,
            "timeout": self.timeout,
            "attempts": self.attempts,
            "properties": {
                name: prop.to_dict() 
                for name, prop in self.properties.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScanConfig':
        """Erstellt eine Konfiguration aus einem Dictionary"""
        properties = {
            name: BACnetProperty.from_dict(prop_data)
            for name, prop_data in data.get('properties', {}).items()
        }
        data['properties'] = properties
        return cls(**data)
    
    def update_property_settings(self, settings: Dict[str, bool]):
        """Aktualisiert die Aktivierung der Eigenschaften"""
        print("Aktualisiere Property-Einstellungen:")
        print("Eingehende Einstellungen:", settings)
        for name, enabled in settings.items():
            if name in self.properties:
                print(f"Setze {name} auf {enabled}")
                self.properties[name].enabled = enabled
        print("Aktualisierte Properties:", {name: prop.enabled for name, prop in self.properties.items()})

CONFIG_FILE = "config/scan_config.json"

def save_scan_config(config: ScanConfig):
    """Speichert die Scan-Konfiguration in einer JSON-Datei"""
    try:
        # Erstelle Konfigurations-Verzeichnis falls nicht vorhanden
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # Konvertiere Konfiguration in Dictionary
        config_dict = config.to_dict()
        
        # Speichere als JSON
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_dict, f, indent=4)
            
        print(f"Konfiguration gespeichert in: {CONFIG_FILE}")
        return True
        
    except Exception as e:
        print(f"Fehler beim Speichern der Konfiguration: {e}")
        return False

def load_scan_config() -> ScanConfig:
    """Lädt die Scan-Konfiguration aus der JSON-Datei"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            return ScanConfig.from_dict(data)
        else:
            # Erstelle Standard-Konfiguration wenn keine Datei existiert
            config = ScanConfig(
                ip_address="",  # Leer, wird später gesetzt
                port=47808     # Standard BACnet-Port
            )
            save_scan_config(config)  # Speichere Standard-Konfiguration
            return config
            
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        # Erstelle Standard-Konfiguration im Fehlerfall
        return ScanConfig(
            ip_address="",
            port=47808
        )