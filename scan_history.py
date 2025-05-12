# scan_history.py
import os
from bacnet_scanner import BACnetScanner

def show_previous_scans():
    """Zeigt vorherige Scans an"""
    scan_dir = 'scan_results'
    if not os.path.exists(scan_dir):
        print("\nKeine vorherigen Scans gefunden.")
        return
    
    scans = [f for f in os.listdir(scan_dir) if f.endswith('.json')]
    if not scans:
        print("\nKeine vorherigen Scans gefunden.")
        return
    
    print("\nVorherige Scans:")
    for i, scan in enumerate(sorted(scans, reverse=True)):
        print(f"{i+1}. {scan}")
    
    while True:
        choice = input("\nWählen Sie einen Scan zum Anzeigen (0 zum Abbrechen): ")
        if choice == "0":
            break
        try:
            index = int(choice) - 1
            if 0 <= index < len(scans):
                scan_file = os.path.join(scan_dir, scans[index])
                scan_data = BACnetScanner.load_scan_result(scan_file)
                
                print("\nScan Details:")
                print(f"Zeitpunkt: {scan_data['timestamp']}")
                print(f"IP-Adresse: {scan_data['config']['local_ip']}")
                print(f"Port: {scan_data['config']['bacnet_port']}")
                print(f"Gefundene Geräte: {len(scan_data['devices'])}")
                print("\nGefundene Geräte:")
                for ip, device_id in scan_data['devices'].items():
                    id_str = f" (Device-ID: {device_id})" if device_id else ""
                    print(f"- {ip}{id_str}")
                break
            else:
                print("Ungültige Auswahl!")
        except ValueError:
            print("Ungültige Eingabe!")