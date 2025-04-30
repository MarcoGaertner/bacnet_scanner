def get_common_bacnet_ports():
    """Liefert häufig verwendete BACnet Ports"""
    return [
        (0xBAC0, "47808 (0xBAC0) - Standard BACnet/IP Port"),
        (0xBAC1, "47809 (0xBAC1) - Alternativer BACnet Port"),
        (47808, "47808 - BACnet/IP dezimal"),
        (47809, "47809 - Alternativer Port dezimal")
    ]

def select_port():
    """Lässt den Benutzer einen Port auswählen"""
    print("\nBACnet Port-Auswahl")
    print("-" * 50)
    
    print("\nWie möchten Sie den Port auswählen?")
    print("1. Aus häufig verwendeten Ports wählen")
    print("2. Port manuell eingeben")
    
    while True:
        choice = input("\nBitte wählen Sie (1/2): ")
        if choice in ['1', '2']:
            break
        print("Ungültige Eingabe! Bitte 1 oder 2 wählen.")
    
    if choice == '1':
        return select_from_common_ports()
    else:
        return manual_port_input()

def select_from_common_ports():
    """Lässt den Benutzer aus häufig verwendeten Ports wählen"""
    ports = get_common_bacnet_ports()
    print("\nVerfügbare BACnet Ports:")
    for i, (port, desc) in enumerate(ports):
        print(f"{i+1}. {desc}")
    
    while True:
        try:
            idx = int(input("\nBitte wählen Sie einen Port (1-{}): ".format(len(ports))))
            if 1 <= idx <= len(ports):
                return ports[idx-1][0]
        except ValueError:
            pass
        print("Ungültige Auswahl! Bitte erneut versuchen.")

def manual_port_input():
    """Lässt den Benutzer einen Port manuell eingeben"""
    while True:
        try:
            port = input("\nBitte geben Sie den Port ein (1-65535): ")
            port_num = int(port)
            if 1 <= port_num <= 65535:
                return port_num
        except ValueError:
            pass
        print("Ungültiger Port! Bitte geben Sie eine Zahl zwischen 1 und 65535 ein.")

def validate_port(port):
    """Überprüft, ob der Port gültig ist"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (TypeError, ValueError):
        return False