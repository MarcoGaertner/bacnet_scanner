from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ScanConfig:
    """Konfiguration für den BACnet-Scan"""
    ip_address: str
    port: int
    device_properties: List[str] = field(default_factory=lambda: [
        "device_id",
        "vendor_id",
        "network"
    ])
    timeout: int = 2
    attempts: int = 5
    
    def to_dict(self) -> Dict:
        """Konvertiert die Konfiguration in ein Dictionary"""
        return {
            "ip_address": self.ip_address,
            "port": self.port,
            "device_properties": self.device_properties,
            "timeout": self.timeout,
            "attempts": self.attempts
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScanConfig':
        """Erstellt eine Konfiguration aus einem Dictionary"""
        return cls(**data)