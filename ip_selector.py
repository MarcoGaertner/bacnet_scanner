import socket

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

def select_ip():
    """Lässt den Benutzer eine IP-Adresse auswählen"""
    print("BACnet Scanner - IP-Auswahl")
    print("-" * 50)
    
    print("\nWie möchten Sie die IP-Adresse auswählen?")
    print("1. Verfügbare Netzwerkinterfaces anzeigen")
    print("2. IP-Adresse manuell eingeben")
    
    while True:
        choice = input("\nBitte wählen Sie (1/2): ")
        if choice in ['1', '2']:
            break
        print("Ungültige Eingabe! Bitte 1 oder 2 wählen.")
    
    if choice == '1':
        return select_from_interfaces()
    else:
        return manual_ip_input()

def select_from_interfaces():
    """Lässt den Benutzer aus verfügbaren Interfaces wählen"""
    interfaces = get_network_interfaces()
    print("\nVerfügbare Netzwerkschnittstellen:")
    for i, (ip, desc) in enumerate(interfaces):
        print(f"{i+1}. {desc} ({ip})")
    
    while True:
        try:
            idx = int(input("\nBitte wählen Sie eine Schnittstelle (1-{}): ".format(len(interfaces))))
            if 1 <= idx <= len(interfaces):
                return interfaces[idx-1][0]
        except ValueError:
            pass
        print("Ungültige Auswahl! Bitte erneut versuchen.")

def manual_ip_input():
    """Lässt den Benutzer eine IP-Adresse manuell eingeben"""
    while True:
        ip = input("\nBitte geben Sie die IP-Adresse ein: ")
        if validate_ip(ip):
            return ip
        print("Ungültige IP-Adresse! Bitte erneut versuchen.")

def validate_ip(ip):
    """Überprüft, ob die IP-Adresse gültig ist"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        return all(0 <= int(part) <= 255 for part in parts)
    except (AttributeError, TypeError, ValueError):
        return False