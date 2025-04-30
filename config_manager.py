import json
import os

CONFIG_FILE = 'scanner_config.json'

def save_config(ip, port, **additional_settings):
    """Speichert die Konfiguration in einer JSON-Datei"""
    try:
        # Lade existierende Konfiguration, falls vorhanden
        config = load_config()
        
        # Aktualisiere nur die Werte, die tatsächlich übergeben wurden
        config['last_ip'] = ip
        config['last_port'] = port
        
        # Aktualisiere nur die zusätzlichen Einstellungen, die einen Wert haben
        if additional_settings:
            for key, value in additional_settings.items():
                if value is not None:  # Nur speichern wenn ein Wert vorhanden ist
                    config[key] = value
        
        # Speichere aktualisierte Konfiguration
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
            
        print(f"Konfiguration gespeichert: {config}")
        
    except Exception as e:
        print(f"Fehler beim Speichern der Konfiguration: {e}")
        print(f"Zusätzliche Einstellungen: {additional_settings}")

def load_config():
    """Lädt die Konfiguration aus der JSON-Datei"""
    default_config = {
        'last_ip': None,
        'last_port': None,
        'window_size': None,
        'window_position': None,
        'last_export_path': None,
        'scan_timeout': 2,
        'scan_attempts': 5
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                print(f"Geladene Konfiguration: {loaded_config}")
                
                # Behalte nur gültige Werte
                for key, value in loaded_config.items():
                    if value is not None:
                        default_config[key] = value
                
                return default_config
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
    
    return default_config