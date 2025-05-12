import socket
import struct
import time
from datetime import datetime
from typing import Tuple, Dict, Optional
import json
import os

class BACnetScanner:
    def __init__(self, local_ip: str, bacnet_port: int = 47808):
        self.local_ip = local_ip
        self.bacnet_port = bacnet_port
        self.timeout = 0.5
        self.attempts = 5
        self.broadcast_address = '172.16.13.255'  # Konfigurierbar machen
        self.scan_result = None

    @staticmethod
    def create_who_is_message(low_limit: Optional[int] = None, high_limit: Optional[int] = None) -> bytes:
        """Erstellt eine BACnet Who-Is Nachricht"""
        if low_limit is None or high_limit is None:
            return bytes.fromhex('810b000801001008')
        return bytes.fromhex(f'810b000c01001008{low_limit:08x}{high_limit:08x}')

    def scan(self, properties=None) -> Tuple[Dict, Dict]:
        """
        Führt den BACnet-Scan durch
        
        Args:
            properties: Liste von BACnetProperty-Objekten, die abgefragt werden sollen
        """
        devices = {}
        networks = {}
        
        # Debug-Ausgabe der Properties
        if properties:
            print(f"Scanning with {len(properties)} enabled properties:")
            for prop in properties:
                print(f"- {prop.name} (ID: {prop.bacnet_id})")
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                sock.bind((self.local_ip, self.bacnet_port))
                sock.settimeout(self.timeout)
                
                print(f"[{datetime.now()}] Starting BACnet scan...")
                message = self.create_who_is_message()
                
                for attempt in range(self.attempts):
                    sock.sendto(message, (self.broadcast_address, self.bacnet_port))
                    self._collect_responses(sock, devices)
                    time.sleep(0.5)
                
                networks = self._organize_networks(devices)
                self._save_scan_result(devices, networks)
                self._print_results(devices)
                
                return devices, networks
                
            except Exception as e:
                print(f"Error during scan: {e}")
                print(f"Error details: {type(e).__name__}")
                return {}, {}

    def _collect_responses(self, sock: socket.socket, devices: Dict):
        """Sammelt die Antworten der BACnet-Geräte"""
        start_time = time.time()
        while time.time() - start_time < 2:
            try:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                
                if ip not in devices:
                    print(f"\n[{datetime.now()}] New device {ip}:")
                    print(f"Raw data: {data.hex()}")
                    devices[ip] = self._extract_device_id(data)
                    
            except socket.timeout:
                continue

    @staticmethod
    def _extract_device_id(data: bytes) -> Optional[int]:
        """Extrahiert die Device-ID aus den empfangenen Daten"""
        try:
            if len(data) >= 20:
                for i in range(len(data)-4):
                    if data[i:i+2] == b'\xc4\x02':
                        return struct.unpack('>I', data[i+2:i+6])[0]
        except:
            pass
        return None

    @staticmethod
    def _organize_networks(devices: Dict) -> Dict:
        """Organisiert die gefundenen Geräte nach Netzwerken"""
        networks = {}
        for ip, device_id in devices.items():
            subnet = '.'.join(ip.split('.')[:3])
            if subnet not in networks:
                networks[subnet] = []
            networks[subnet].append((ip, device_id))
        return networks

    def _save_scan_result(self, devices: Dict, networks: Dict):
        """Speichert das Scan-Ergebnis als JSON"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'local_ip': self.local_ip,
                'bacnet_port': self.bacnet_port,
                'broadcast_address': self.broadcast_address
            },
            'devices': devices,
            'networks': {net: devices for net, devices in networks.items()}
        }
        
        # Erstelle Verzeichnis falls nicht vorhanden
        os.makedirs('scan_results', exist_ok=True)
        
        # Speichere mit Zeitstempel
        filename = f"scan_results/bacnet_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=4)
        
        self.scan_result = result
        print(f"\nScan results saved to {filename}")

    def _print_results(self, devices: Dict):
        """Gibt die Scan-Ergebnisse aus"""
        print(f"\n[{datetime.now()}] Scan completed!")
        print(f"Found {len(devices)} devices:")
        for ip, device_id in sorted(devices.items()):
            id_str = f" (Device-ID: {device_id})" if device_id is not None else ""
            print(f"- {ip}{id_str}")

    @classmethod
    def load_scan_result(cls, filename: str) -> Dict:
        """Lädt ein gespeichertes Scan-Ergebnis"""
        with open(filename, 'r') as f:
            return json.load(f)