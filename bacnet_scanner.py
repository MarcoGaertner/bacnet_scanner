import socket
import struct
import time
from datetime import datetime

def create_who_is_message():
    """Erstellt eine BACnet Who-Is Nachricht"""
    
    # BVLC Header
    bvlc_type = 0x81
    bvlc_function = 0x0B   # Original-Broadcast-NPDU
    bvlc_length = 0x0008   # Gesamtlänge der Nachricht
    
    # NPDU
    npdu_version = 0x01
    npdu_control = 0x00    # Geändert von 0x20 auf 0x00
    
    # APDU
    apdu_type = 0x10       # Unconfirmed-REQ
    service_choice = 0x08   # Who-Is
    
    message = struct.pack('>BBHBB',
        bvlc_type,
        bvlc_function,
        bvlc_length,
        npdu_version,
        npdu_control
    )
    
    message += struct.pack('BB',
        apdu_type,
        service_choice
    )
    
    return message

def scan_bacnet():
    """BACnet-Scan auf spezifischem Interface"""
    local_ip = '10.48.172.120'  # Ihre spezifische IP-Adresse
    bacnet_port = 0xBAC0        # 47808
    
    # Socket erstellen und konfigurieren
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # An die lokale IP und den BACnet-Port binden
        sock.bind((local_ip, bacnet_port))
        sock.settimeout(1)  # Timeout auf 1 Sekunde setzen
        
        # Who-Is Nachricht erstellen
        message = create_who_is_message()
        
        print(f"[{datetime.now()}] Starting BACnet scan from {local_ip}")
        print(f"Sending Who-Is message: {message.hex()}")
        
        # Who-Is mehrmals senden (3 Versuche)
        devices = set()
        for attempt in range(3):
            # Broadcast senden
            sock.sendto(message, ('255.255.255.255', bacnet_port))
            
            # Auf Antworten warten
            start_time = time.time()
            while time.time() - start_time < 2:  # 2 Sekunden pro Versuch
                try:
                    data, addr = sock.recvfrom(1024)
                    if addr[0] not in devices:
                        print(f"\n[{datetime.now()}] Response from {addr[0]}:")
                        print(f"Raw data: {data.hex()}")
                        devices.add(addr[0])
                except socket.timeout:
                    continue
            
            print(f"\nAttempt {attempt + 1} completed")
            
        print(f"\n[{datetime.now()}] Scan completed!")
        print(f"Found {len(devices)} devices:")
        for device in sorted(devices):
            print(f"- {device}")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error details: {type(e).__name__}")
    
    finally:
        sock.close()

if __name__ == "__main__":
    scan_bacnet()