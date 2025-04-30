import socket
import struct
import time
from datetime import datetime

def create_who_is_message(low_limit=None, high_limit=None):
    """Erstellt eine BACnet Who-Is Nachricht mit optionalen ID-Grenzen"""
    if low_limit is None or high_limit is None:
        return bytes.fromhex('810b000801001008')
    else:
        return bytes.fromhex(f'810b000c01001008{low_limit:08x}{high_limit:08x}')

def scan_bacnet(local_ip, bacnet_port):
    """BACnet-Scan mit spezifischen ID-Bereichen"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    devices = {}
    networks = {}  # Hier networks initialisieren
    
    try:
        sock.bind((local_ip, bacnet_port))
        sock.settimeout(0.5)  # Längerer Timeout
        
        # Broadcast-Adresse für Gebäude C
        target = '172.16.13.255'  # Broadcast für das C-Gebäude Subnetz
        
        print(f"[{datetime.now()}] Starting BACnet scan in Building C...")
        
        # Erst einen allgemeinen Who-Is senden
        message = create_who_is_message(None, None)
        print("\nSending general Who-Is")
        
        # Mehrere Versuche mit längeren Wartezeiten
        for attempt in range(5):  # Mehr Versuche
            sock.sendto(message, (target, bacnet_port))
            
            # Längere Wartezeit für Antworten
            start_time = time.time()
            while time.time() - start_time < 2:  # 2 Sekunden Wartezeit
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
            
            time.sleep(0.5)  # Längere Pause zwischen Versuchen
        
        # Ergebnisse ausgeben
        print(f"\n[{datetime.now()}] Scan completed!")
        print(f"Found {len(devices)} devices:")
        
        # Ergebnisse in networks Dictionary organisieren
        for ip, device_id in sorted(devices.items()):
            id_str = f" (Device-ID: {device_id})" if device_id is not None else ""
            print(f"- {ip}{id_str}")
            subnet = '.'.join(ip.split('.')[:3])
            if subnet not in networks:
                networks[subnet] = []
            networks[subnet].append((ip, device_id))
        
        return devices, networks
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error details: {type(e).__name__}")
        return {}, {}
    
    finally:
        sock.close()