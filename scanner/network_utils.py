import json
import os
import subprocess
import re
from pathlib import Path

def get_network_adapters():
    """Ermittelt alle verfügbaren Netzwerkadapter mit detaillierten Informationen direkt aus ipconfig"""
    adapters = []
    
    try:
        print("Erfasse Netzwerkadapter-Informationen mit ipconfig...")
        
        # Führe ipconfig /all aus und erfasse die Ausgabe
        ipconfig_output = subprocess.check_output('ipconfig /all', shell=True).decode('utf-8', 'ignore')
        
        # Debug-Ausgabe speichern
        base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        debug_dir = base_dir / "config"
        os.makedirs(debug_dir, exist_ok=True)
        
        with open(debug_dir / "ipconfig_raw.txt", 'w', encoding='utf-8') as f:
            f.write(ipconfig_output)
        
        # Adapter-Abschnitte finden
        # Jeder Adapter beginnt mit einer Zeile, die "adapter" enthält und endet vor dem nächsten Adapter
        adapter_pattern = r'((?:Ethernet|Drahtlos-LAN|Mobiler Breitband|Bluetooth)[^:]*Adapter[^:]*:.*?)(?=(?:Ethernet|Drahtlos-LAN|Mobiler Breitband|Bluetooth)[^:]*Adapter|$)'
        adapter_sections = re.findall(adapter_pattern, ipconfig_output, re.DOTALL | re.IGNORECASE)
        
        print(f"Gefundene Adapter-Abschnitte: {len(adapter_sections)}")
        
        # Für jeden Adapter-Abschnitt die Details extrahieren
        for section in adapter_sections:
            # Adaptername extrahieren (zwischen "Adapter" und ":")
            adapter_match = re.search(r'Adapter\s+(.*?):', section, re.IGNORECASE)
            if not adapter_match:
                continue
                
            adapter_name = adapter_match.group(1).strip()
            print(f"Verarbeite Adapter: {adapter_name}")
            
            # Grundgerüst für Adapter-Informationen
            adapter_info = {
                "name": adapter_name,
                "status": "Nicht verbunden",  # Standardwert
                "type": "Unbekannt",
                "mac_address": "",
                "ip_address": "",
                "subnet_mask": "",
                "default_gateway": "",
                "preferred_dns": "",
                "alternate_dns": ""
            }
            
            # Adapter-Typ identifizieren
            if "ethernet" in adapter_name.lower():
                adapter_info["type"] = "Ethernet"
            elif "vmware" in adapter_name.lower():
                adapter_info["type"] = "Virtuell"
            elif any(term in adapter_name.lower() for term in ["wi-fi", "wlan", "drahtlos"]):
                adapter_info["type"] = "WLAN"
            elif "bluetooth" in adapter_name.lower():
                adapter_info["type"] = "Bluetooth"
            elif any(term in adapter_name.lower() for term in ["mobil", "cellular", "broadband"]):
                adapter_info["type"] = "Mobilfunk"
            
            # Verbindungsstatus prüfen
            if "medium getrennt" in section.lower():
                adapter_info["status"] = "Nicht verbunden"
            else:
                # Suche nach einer IP-Adresse, um den Verbindungsstatus zu bestimmen
                ip_match = re.search(r'IPv4-Adresse[\s\.]*:[\s\.]*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', section, re.IGNORECASE)
                if ip_match:
                    adapter_info["status"] = "Verbunden"
                    adapter_info["ip_address"] = ip_match.group(1).strip()
            
            # Physische Adresse (MAC)
            mac_match = re.search(r'Physische Adresse[\s\.]*:[\s\.]*([0-9A-Fa-f-]+)', section, re.IGNORECASE)
            if mac_match:
                adapter_info["mac_address"] = mac_match.group(1).strip()
            
            # Subnetzmaske
            subnet_match = re.search(r'Subnetzmaske[\s\.]*:[\s\.]*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', section, re.IGNORECASE)
            if subnet_match:
                adapter_info["subnet_mask"] = subnet_match.group(1).strip()
            
            # Standardgateway
            gateway_match = re.search(r'Standardgateway[\s\.]*:[\s\.]*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', section, re.IGNORECASE)
            if gateway_match:
                adapter_info["default_gateway"] = gateway_match.group(1).strip()
            
            # DNS-Server
            dns_servers = re.findall(r'DNS-Server[\s\.]*:[\s\.]*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', section, re.IGNORECASE)
            if dns_servers:
                if len(dns_servers) > 0:
                    adapter_info["preferred_dns"] = dns_servers[0].strip()
                if len(dns_servers) > 1:
                    adapter_info["alternate_dns"] = dns_servers[1].strip()
            
            # Adapter zur Liste hinzufügen
            adapters.append(adapter_info)
            print(f"  - Status: {adapter_info['status']}, IP: {adapter_info['ip_address'] or 'Keine'}")
        
    except Exception as e:
        print(f"Fehler bei der ipconfig-Adapter-Erkennung: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback auf Socket-Methode
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            adapters.append({
                "name": "Hauptadapter",
                "status": "Verbunden",
                "type": "Auto-erkannt",
                "mac_address": "",
                "ip_address": local_ip,
                "subnet_mask": "255.255.255.0",  # Annahme
                "default_gateway": "",
                "preferred_dns": "",
                "alternate_dns": ""
            })
            print(f"Socket-Fallback: IP-Adresse {local_ip} erkannt")
        except Exception as socket_error:
            print(f"Socket-Fallback fehlgeschlagen: {socket_error}")
    
    # Lokalen Host hinzufügen, falls noch nicht vorhanden
    loopback_exists = any(adapter["ip_address"] == "127.0.0.1" for adapter in adapters)
    if not loopback_exists:
        adapters.append({
            "name": "localhost",
            "status": "Verbunden",
            "type": "Loopback",
            "mac_address": "",
            "ip_address": "127.0.0.1",
            "subnet_mask": "255.0.0.0",
            "default_gateway": "",
            "preferred_dns": "",
            "alternate_dns": ""
        })
    
    # Wenn keine Adapter gefunden wurden
    if not adapters:
        print("WARNUNG: Keine Adapter gefunden!")
        adapters.append({
            "name": "Unbekannt",
            "status": "Unbekannt",
            "type": "Unbekannt",
            "mac_address": "",
            "ip_address": "",
            "subnet_mask": "",
            "default_gateway": "",
            "preferred_dns": "",
            "alternate_dns": ""
        })
    
    # Verbundene Adapter nach vorne sortieren
    adapters.sort(key=lambda x: 0 if x["status"] == "Verbunden" and x["ip_address"] else 1)
    
    connected_count = sum(1 for adapter in adapters if adapter["status"] == "Verbunden" and adapter["ip_address"])
    print(f"Erfolgreich {len(adapters)} Adapter erkannt, davon {connected_count} verbunden")
    
    return adapters

def save_network_adapters():
    """Speichert die Netzwerkadapter in einer JSON-Datei im Config-Ordner"""
    adapters = get_network_adapters()
    
    # Bestimme den Basisordner (Projektverzeichnis)
    base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    
    # Pfad zur JSON-Datei im config-Ordner
    config_dir = base_dir / "config"
    output_file = config_dir / "network_adapters.json"
    
    # Verzeichnis erstellen, falls es nicht existiert
    os.makedirs(config_dir, exist_ok=True)
    
    # Daten speichern
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(adapters, f, indent=2, ensure_ascii=False)
    
    print(f"Netzwerkadapter in {output_file} gespeichert")
    
    return adapters

def load_network_adapters():
    """Lädt gespeicherte Netzwerkadapter aus der JSON-Datei"""
    # Bestimme den Basisordner (Projektverzeichnis)
    base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    
    # Pfad zur JSON-Datei
    config_dir = base_dir / "config"
    input_file = config_dir / "network_adapters.json"
    
    # Wenn die Datei nicht existiert oder leer ist, erstellen wir sie neu
    if not input_file.exists() or input_file.stat().st_size == 0:
        return save_network_adapters()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            adapters = json.load(f)
        return adapters
    except Exception as e:
        print(f"Fehler beim Laden der Netzwerkadapter: {e}")
        # Bei Fehler neu erstellen
        return save_network_adapters()

def get_adapter_names():
    """Gibt eine Liste der Adapter-Namen zurück"""
    adapters = load_network_adapters()
    return [adapter["name"] for adapter in adapters]

def get_connected_adapter_names():
    """Gibt eine Liste der verbundenen Adapter-Namen zurück"""
    adapters = load_network_adapters()
    return [adapter["name"] for adapter in adapters if adapter["status"] == "Verbunden" and adapter["ip_address"]]

def get_adapter_by_name(name):
    """Gibt die Informationen für einen bestimmten Adapter zurück"""
    adapters = load_network_adapters()
    for adapter in adapters:
        if adapter["name"] == name:
            return adapter
    return None

def refresh_network_adapters():
    """Aktualisiert die Netzwerkadapter-Informationen"""
    print("Aktualisiere Netzwerkadapter-Informationen...")
    return save_network_adapters()

# Wenn das Skript direkt ausgeführt wird
if __name__ == "__main__":
    print("***** Netzwerkadapter-Erkennungstool (ipconfig-Version) *****")
    adapters = save_network_adapters()
    
    print("\nDetailierte Adapter-Informationen:")
    for i, adapter in enumerate(adapters):
        print(f"\n{i+1}. Adapter: {adapter['name']} ({adapter['type']})")
        print(f"   Status:           {adapter['status']}")
        print(f"   MAC-Adresse:      {adapter['mac_address'] or 'Nicht verfügbar'}")
        print(f"   IP-Adresse:       {adapter['ip_address'] or 'Nicht zugewiesen'}")
        print(f"   Subnetzmaske:     {adapter['subnet_mask'] or 'Nicht zugewiesen'}")
        print(f"   Standard-Gateway: {adapter['default_gateway'] or 'Nicht zugewiesen'}")
        print(f"   Bevorzugter DNS:  {adapter['preferred_dns'] or 'Nicht zugewiesen'}")
        print(f"   Alternativer DNS: {adapter['alternate_dns'] or 'Nicht zugewiesen'}")