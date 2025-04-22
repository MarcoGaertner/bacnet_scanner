import socket
import struct
import time
from datetime import datetime

def get_network_interfaces():
    """Ermittelt alle verfügbaren Netzwerkschnittstellen"""
    interfaces = []
    try:
        # Hostname abrufen
        hostname = socket.gethostname()
        # Alle IP-Adressen des Hosts abrufen
        ip_addresses = socket.getaddrinfo(hostname, None)
        
        # Localhost hinzufügen
        interfaces.append(('127.0.0.1', 'Localhost'))
        # Alle Interfaces hinzufügen
        interfaces.append(('0.0.0.0', 'Alle Interfaces'))
        
        # Weitere IPs hinzufügen
        for ip in ip_addresses:
            if ip[0] == socket.AF_INET:  # Nur IPv4
                addr = ip[4][0]
                if not addr.startswith('127.'):  # Localhost ausschließen
                    interfaces.append((addr, f'Interface {addr}'))
        
    except Exception as e:
        print(f"Fehler beim Ermitteln der Netzwerkschnittstellen: {e}")
    
    return interfaces

def create_who_is_message():
    """Erstellt eine BACnet Who-Is Nachricht"""
    # [Code bleibt gleich wie vorher]
    # ... [vorheriger Code für Who-Is Nachricht] ...

def scan_bacnet(local_ip='0.0.0.0'):
    """BACnet-Scan mit spezifischer lokaler IP"""
    # Socket erstellen
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        # An spezifische lokale IP binden
        sock.bind((local_ip, 0))
        sock.settimeout(5)
        
        # Who-Is Nachricht erstellen und senden
        message = create_who_is_message()
        broadcast_address = '255.255.255.255'
        bacnet_port = 47808
        
        print(f"[{datetime.now()}] Sende Who-Is Broadcast von {local_ip}...")
        sock.sendto(message, (broadcast_address, bacnet_port))
        
        # Auf Antworten warten
        devices = []
        start_time = time.time()
        
        while time.time() - start_time < 5:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"\n[{datetime.now()}] Antwort von {addr[0]}:")
                print(f"Rohdaten: {data.hex()}")
                
                if addr[0] not in devices:
                    devices.append(addr[0])
                
            except socket.timeout:
                continue
        
        print(f"\n[{datetime.now()}] Scan abgeschlossen!")
        print(f"Gefundene Geräte: {len(devices)}")
        for device in devices:
            print(f"- {device}")
            
    except Exception as e:
        print(f"Fehler: {e}")
    
    finally:
        sock.close()

def main():
    # Verfügbare Interfaces anzeigen
    interfaces = get_network_interfaces()
    print("Verfügbare Netzwerkschnittstellen:")
    for i, (ip, desc) in enumerate(interfaces):
        print(f"{i+1}. {desc} ({ip})")
    
    # Benutzerauswahl
    while True:
        try:
            choice = int(input("\nWählen Sie eine Schnittstelle (1-{}): ".format(len(interfaces))))
            if 1 <= choice <= len(interfaces):
                selected_ip = interfaces[choice-1][0]
                break
        except ValueError:
            pass
        print("Ungültige Auswahl. Bitte erneut versuchen.")
    
    # Scan mit gewählter IP durchführen
    print(f"\nStarte Scan mit Interface: {selected_ip}")
    scan_bacnet(selected_ip)

if __name__ == "__main__":
    main()