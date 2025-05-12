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
        

    def _create_read_property_request(self, device_id: Optional[int], property_id: int) -> bytes:
        """
        Erstellt eine BACnet ReadProperty-Anfrage
        
        Args:
            device_id: Device-ID des Zielgeräts (kann None sein)
            property_id: ID der zu lesenden Property
        """
        try:
            # BVLC Header (BACnet Virtual Link Control)
            bvlc_type = b'\x81'  # BACnet/IP
            bvlc_function = b'\x0a'  # Original-Unicast-NPDU
            bvlc_length = b'\x00\x17'  # Länge des gesamten Pakets
            
            # NPDU Header (Network Protocol Data Unit)
            npdu_version = b'\x01'  # Version 1
            npdu_control = b'\x00'  # Keine zusätzlichen Optionen
            
            # APDU (Application Protocol Data Unit)
            apdu_type = b'\x02'  # Confirmed-REQ
            max_segments = b'\x00'  # Keine Segmentierung
            
            # ReadProperty Service Choice
            service_choice = b'\x0c'  # ReadProperty
            
            # Object Identifier (Device Object)
            object_type = b'\x0c'  # Device Object Type
            if device_id is None:
                object_instance = b'\x00\x00\x00'  # Verwende 0 als Default
            else:
                object_instance = (device_id & 0x3FFFFF).to_bytes(3, 'big')  # Nur die unteren 22 Bits
            object_id = object_type + object_instance
            
            # Property Identifier
            property_tag = b'\x19'  # Property Identifier Tag
            property_value = property_id.to_bytes(1, 'big')
            
            # Paket zusammenbauen
            packet = (
                bvlc_type + bvlc_function + bvlc_length +  # BVLC
                npdu_version + npdu_control +  # NPDU
                apdu_type + max_segments + service_choice +  # APDU
                object_id + property_tag + property_value  # Payload
            )
            
            return packet
            
        except Exception as e:
            print(f"Error creating ReadProperty request: {e}")
            return None

    def _read_property(self, sock: socket.socket, ip: str, device_id: Optional[int], property_id: int) -> Optional[str]:
        """
        Liest eine BACnet-Property von einem Gerät
        
        Args:
            sock: Socket für die Kommunikation
            ip: IP-Adresse des Geräts
            device_id: Device-ID des Geräts (kann None sein)
            property_id: ID der zu lesenden Property
        """
        try:
            # BACnet ReadProperty Request erstellen
            request = self._create_read_property_request(device_id, property_id)
            if request is None:
                return None
            
            # Request senden
            sock.sendto(request, (ip, self.bacnet_port))
            
            # Auf Antwort warten
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    if addr[0] == ip:
                        return self._parse_read_property_response(data, property_id)
                except socket.timeout:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error reading property {property_id} from {ip}: {e}")
            return None

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
            print(f"\nScanning with {len(properties)} enabled properties:")
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
                
                # Erst Who-Is durchführen
                for attempt in range(self.attempts):
                    sock.sendto(message, (self.broadcast_address, self.bacnet_port))
                    self._collect_responses(sock, devices)
                    time.sleep(0.5)
                
                # Dann für jedes gefundene Gerät die zusätzlichen Properties abfragen
                if properties:
                    for ip in list(devices.keys()):
                        device_info = {}
                        device_id = devices[ip]
                        device_info['device_id'] = device_id
                        
                        # Jede aktivierte Property abfragen
                        for prop in properties:
                            if prop.bacnet_id:
                                try:
                                    value = self._read_property(sock, ip, device_id, prop.bacnet_id)
                                    if value is not None:
                                        device_info[prop.name] = value
                                except Exception as e:
                                    print(f"Error reading {prop.name} from {ip}: {e}")
                        
                        devices[ip] = device_info
                
                networks = self._organize_networks(devices)
                self._save_scan_result(devices, networks)
                self._print_results(devices)
                
                return devices, networks
                
            except Exception as e:
                print(f"Error during scan: {e}")
                print(f"Error details: {type(e).__name__}")
                return {}, {}

    def _parse_read_property_response(self, data: bytes, property_id: int) -> Optional[str]:
        """
        Parst die Antwort einer ReadProperty-Anfrage
        
        Args:
            data: Empfangene Daten
            property_id: ID der Property für die Validierung
        """
        try:
            # Minimale Paketgröße prüfen
            if len(data) < 20:
                return None
            
            # APDU Type prüfen (Complex-ACK)
            if data[6] != 0x30:
                return None
            
            # Service Choice prüfen (ReadProperty)
            if data[7] != 0x0c:
                return None
            
            # Property Value suchen
            for i in range(8, len(data)-2):
                # Application Tag für String (0x75) oder Unsigned (0x91) suchen
                if data[i] in [0x75, 0x91]:
                    length = data[i+1]
                    value = data[i+2:i+2+length]
                    
                    if data[i] == 0x75:  # String
                        return value.decode('utf-8', errors='ignore')
                    else:  # Unsigned
                        return str(int.from_bytes(value, 'big'))
            
            return None
            
        except Exception as e:
            print(f"Error parsing ReadProperty response: {e}")
            return None