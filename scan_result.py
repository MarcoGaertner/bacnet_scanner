from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
import json
import os

@dataclass
class ScanResult:
    """Speichert die Ergebnisse eines BACnet-Scans"""
    devices: Dict
    networks: Dict
    scan_time: datetime
    config: 'ScanConfig'
    
    def to_dict(self) -> Dict:
        """Konvertiert das Ergebnis in ein Dictionary"""
        return {
            "devices": self.devices,
            "networks": self.networks,
            "scan_time": self.scan_time.isoformat(),
            "config": self.config.to_dict()
        }
    
    def save_to_json(self, filename: Optional[str] = None) -> str:
        """Speichert das Ergebnis als JSON-Datei"""
        if filename is None:
            # Erstelle Standarddateinamen mit Zeitstempel
            timestamp = self.scan_time.strftime("%Y%m%d_%H%M%S")
            filename = f"bacnet_scan_{timestamp}.json"
        
        # Stelle sicher, dass der Ordner existiert
        os.makedirs("scan_results", exist_ok=True)
        filepath = os.path.join("scan_results", filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
        
        return filepath
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'ScanResult':
        """Lädt ein Ergebnis aus einer JSON-Datei"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Konvertiere Zeitstempel zurück zu datetime
        data['scan_time'] = datetime.fromisoformat(data['scan_time'])
        # Konvertiere Konfiguration zurück zu ScanConfig
        data['config'] = ScanConfig.from_dict(data['config'])
        
        return cls(**data)