from bacnet_scanner import BACnetScanner
from ip_selector import select_ip, get_network_interfaces
from port_selector import select_port, get_common_bacnet_ports
from gui import BACnetScannerGUI
from scan_history import show_previous_scans
import tkinter as tk
import json
import os
from datetime import datetime

def console_mode():
    """Startet den Scanner im Konsolenmodus"""
    print("\nBACnet Scanner - Konsolenmodus")
    print("-" * 30)
    
    # IP-Adresse auswählen
    selected_ip = select_ip()
    if not selected_ip:
        print("Keine IP-Adresse ausgewählt. Beende Programm.")
        return
    
    # Port auswählen
    selected_port = select_port()
    if not selected_port:
        print("Kein Port ausgewählt. Beende Programm.")
        return
    
    # Scanner initialisieren und ausführen
    scanner = BACnetScanner(local_ip=selected_ip, bacnet_port=selected_port)
    
    print("\nStarte BACnet-Scan...")
    devices, networks = scanner.scan()
    
    # Zeige Zusammenfassung
    print("\nScan-Zusammenfassung:")
    print(f"Gefundene Geräte: {len(devices)}")
    print(f"Gefundene Netzwerke: {len(networks)}")
    
    # Frage nach Export
    while True:
        export = input("\nMöchten Sie die Ergebnisse exportieren? (j/n): ").lower()
        if export == 'j':
            # Erstelle Export-Verzeichnis falls nicht vorhanden
            os.makedirs('exports', exist_ok=True)
            
            # Erstelle Dateinamen mit Zeitstempel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exports/bacnet_scan_{timestamp}.json"
            
            # Exportiere Ergebnisse
            try:
                with open(filename, 'w') as f:
                    json.dump({
                        'timestamp': timestamp,
                        'config': {
                            'ip': selected_ip,
                            'port': selected_port
                        },
                        'devices': devices,
                        'networks': networks
                    }, f, indent=4)
                print(f"\nErgebnisse wurden gespeichert in: {filename}")
            except Exception as e:
                print(f"\nFehler beim Exportieren: {e}")
            break
        elif export == 'n':
            break
        else:
            print("Ungültige Eingabe! Bitte 'j' oder 'n' eingeben.")

def gui_mode():
    """Startet den Scanner im GUI-Modus"""
    root = tk.Tk()
    app = BACnetScannerGUI(root)
    root.mainloop()

def main():
    print("BACnet Scanner")
    print("1. Konsolen-Version")
    print("2. GUI-Version")
    print("3. Vorherige Scans anzeigen")
    
    while True:
        choice = input("\nBitte wählen Sie (1/2/3): ")
        if choice == "1":
            console_mode()
            break
        elif choice == "2":
            gui_mode()
            break
        elif choice == "3":
            show_previous_scans()
            # Nach Anzeige zurück zum Hauptmenü
            main()
            break
        else:
            print("Ungültige Eingabe! Bitte 1, 2 oder 3 wählen.")

if __name__ == "__main__":
    main()