import socket
import struct
import time
from datetime import datetime

def create_who_is_message(low_limit=None, high_limit=None):
    """Erstellt eine BACnet Who-Is Nachricht mit optionalen ID-Grenzen"""
    if low_limit is None or high_limit is None:
        return bytes.fromhex('810b000801001008')
    else:
        # Who-Is mit ID-Bereich
        return bytes.fromhex(f'810b000c01001008{low_limit:08x}{high_limit:08x}')

def scan_bacnet():
    """BACnet-Scan mit spezifischen ID-Bereichen"""
    local_ip = '10.48.172.120'
    bacnet_port = 0xBAC0
    
    # Socket erstellen und konfigurieren
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    devices = {}
    
    try:
        sock.bind((local_ip, bacnet_port))
        sock.settimeout(0.1)
        
        # Spezifische ID-Bereiche für verschiedene Gerätetypen
        id_ranges = [
            (None, None),          # Standard Who-Is
            (1000000, 1000999),    # PXM-Geräte
            (2159000, 2159999),    # HVSH-Geräte
            (3146000, 3146999),    # Automationsstationen
            (4000000, 4199999),    # Weitere mögliche Bereiche
            (5000, 5999)           # Edge Router und andere
        ]
        
        print(f"[{datetime.now()}] Starting BACnet scan...")
        
        for low, high in id_ranges:
            message = create_who_is_message(low, high)
            range_str = "standard Who-Is" if low is None else f"ID range {low}-{high}"
            print(f"\nScanning {range_str}")
            
            # Mehrere Versuche pro Bereich
            for attempt in range(3):
                # An verschiedene Broadcast-Adressen senden
                for subnet in ['168', '174', '171']:
                    target = f'10.48.{subnet}.255'
                    sock.sendto(message, (target, bacnet_port))
                
                # Auf Antworten warten
                start_time = time.time()
                while time.time() - start_time < 1:
                    try:
                        data, addr = sock.recvfrom(1024)
                        ip = addr[0]
                        
                        if ip not in devices:
                            print(f"\n[{datetime.now()}] New device {ip}:")
                            print(f"Raw data: {data.hex()}")
                            devices[ip] = None
                            
                            try:
                                if len(data) >= 20:
                                    for i in range(len(data)-4):
                                        if data[i:i+2] == b'\xc4\x02':
                                            device_id = struct.unpack('>I', data[i+2:i+6])[0]
                                            devices[ip] = device_id
                                            print(f"Detected Device-ID: {device_id}")
                                            break
                            except:
                                pass
                    
                    except socket.timeout:
                        continue
                
                time.sleep(0.1)
        
        # Ergebnisse ausgeben
        print(f"\n[{datetime.now()}] Scan completed!")
        print(f"Found {len(devices)} devices:")
        
        networks = {}
        for ip, device_id in sorted(devices.items()):
            subnet = '.'.join(ip.split('.')[:3])
            if subnet not in networks:
                networks[subnet] = []
            networks[subnet].append((ip, device_id))
        
        for subnet in sorted(networks.keys()):
            print(f"\nSubnet {subnet}:")
            for ip, device_id in sorted(networks[subnet]):
                id_str = f" (Device-ID: {device_id})" if device_id is not None else ""
                print(f"- {ip}{id_str}")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error details: {type(e).__name__}")
    
    finally:
        sock.close()

if __name__ == "__main__":
    scan_bacnet()