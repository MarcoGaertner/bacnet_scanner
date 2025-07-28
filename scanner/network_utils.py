import socket
import json
import os

def get_network_adapters():
    """Ermittelt alle verfügbaren Netzwerkadapter mit ihren IP-Adressen"""
    adapters = []
    
    try:
        # Windows-spezifischer Code (für andere Betriebssysteme anpassen)
        import subprocess
        import re
        
        # Befehl zum Auflisten aller Netzwerkadapter
        output = subprocess.check_output('ipconfig /all', shell=True).decode('utf-8', 'ignore')
        
        # Adapter-Informationen extrahieren
        sections = re.split(r'\n\n+', output)
        for section in sections:
            if 'adapter' in section.lower():
                adapter_name = re.search(r'adapter (.*?):', section, re.IGNORECASE)
                if adapter_name:
                    name = adapter_name.group(1).strip()
                    # IP-Adresse suchen
                    ip_match = re.search(r'IPv4 Address[.\s]*: ([0-9.]+)', section)
                    if ip_match:
                        ip = ip_match.group(1)
                        adapters.append({
                            "name": name,
                            "ip": ip
                        })
        
        # Wenn kein Adapter gefunden wurde, füge lokalen Host hinzu
        if not adapters:
            adapters.append({
                "name": "localhost",
                "ip": "127.0.0.1"
            })
    except Exception as e:
        print(f"Fehler bei der Adapter-Erkennung: {e}")
        # Fallback: Lokalen Host hinzufügen
        adapters.append({
            "name": "localhost",
            "ip": "127.0.0.1"
        })
    
    return adapters

def save_network_adapters():
    """Speichert die Netzwerkadapter in einer JSON-Datei"""
    adapters = get_network_adapters()
    
    # Pfad zur JSON-Datei
    output_file = os.path.join('scanner', 'network_adapters.json')
    
    # Verzeichnis erstellen, falls es nicht existiert
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Daten speichern
    with open(output_file, 'w') as f:
        json.dump(adapters, f, indent=2)
    
    print(f"Netzwerkadapter in {output_file} gespeichert")
    return adapters

if __name__ == "__main__":
    save_network_adapters()