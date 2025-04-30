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
        
        # CSV erstellen
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header schreiben
            writer.writerow(['Subnet', 'IP-Adresse', 'Device-ID', 'Zeitstempel'])
            
            # Daten schreiben
            for subnet in sorted(networks.keys()):
                for ip, device_id in sorted(networks[subnet]):
                    writer.writerow([
                        subnet,
                        ip,
                        device_id if device_id is not None else 'Unbekannt',
                        timestamp
                    ])
        
        return True, f"Daten erfolgreich exportiert nach: {file_path}"
        
    except Exception as e:
        return False, f"Fehler beim Export: {str(e)}"