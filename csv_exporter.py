import csv
import os
from datetime import datetime
from tkinter import filedialog

def export_to_csv(devices, networks):
    """Exportiert die gefundenen Geräte in eine CSV-Datei"""
    try:
        # Aktuelles Datum und Zeit für den Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"bacnet_devices_{timestamp}.csv"
        
        # Dialog zum Speichern der Datei
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Speichern als CSV"
        )
        
        if not file_path:  # Wenn der Benutzer abbricht
            return False, "Export abgebrochen"
        
        # CSV erstellen mit erweiterter Formatierung
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            
            # Header mit Formatierung
            writer.writerow(['BACnet Geräteliste'])
            writer.writerow(['Erstellt am:', datetime.now().strftime("%Y-%m-%d")])
            writer.writerow(['Uhrzeit:', datetime.now().strftime("%H:%M:%S")])
            writer.writerow([])  # Leerzeile
            
            # Spaltenüberschriften
            writer.writerow(['Subnet', 'IP-Adresse', 'Device-ID', 'Zeitstempel'])
            
            # Daten nach Subnet sortiert
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_devices = 0
            
            for subnet in sorted(networks.keys()):
                devices_in_subnet = networks[subnet]
                total_devices += len(devices_in_subnet)
                
                for ip, device_id in sorted(devices_in_subnet):
                    writer.writerow([
                        subnet,
                        ip,
                        device_id if device_id is not None else 'Unbekannt',
                        current_time
                    ])
            
            # Zusammenfassung am Ende
            writer.writerow([])
            writer.writerow(['Gesamtanzahl gefundener Geräte:', total_devices])
            writer.writerow(['Scan durchgeführt von:', os.getenv('USERNAME', 'Unbekannt')])
        
        return True, f"Daten erfolgreich exportiert nach: {file_path}"
        
    except Exception as e:
        return False, f"Fehler beim Export: {str(e)}"