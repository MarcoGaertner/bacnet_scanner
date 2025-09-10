import os
import json
from pathlib import Path
from core.events import event_bus
from ui.styles.colors import ThemeManager

class ConfigManager:
    def __init__(self, config_dir="config"):
        # Konfigurationspfade
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.config_dir = self.base_dir / config_dir
        self.ui_config_file = self.config_dir / "ui_settings.json"
        self.user_config_file = self.config_dir / "user_settings.json"
        self.connection_config_file = self.config_dir / "connection_settings.json"
        self.export_config_file = self.config_dir / "export_settings.json"
        
        # Standardeinstellungen
        self.default_settings = {
            "ui": {
                "language": "deutsch",
                "theme": "hell",
                "units": "metrisch"
            },
            "user": {
                "first_name": "",
                "last_name": "",
                "phone": "",
                "email": "",
                "company": ""
            },
            "connection": {
                "type": "network",
                "device_ap": {
                    "device_address": ""
                },
                "network": {
                    "adapter": "Ethernet",
                    "network_number": "",
                    "udp_port": "BAC0 (47808)",
                    "foreign_device": False,
                    "bbmd_ip": "",
                    "bbmd_port": "BAC0 (47808)",
                    "bbmd_network": ""
                },
                "mstp": {
                    "com_port": "COM1",
                    "baud_rate": "38400",
                    "mac_address": "0"
                },
                "usb": {
                    "device": ""
                },
                "secure": {
                    "server_url": "",
                    "certificate": "Kein Zertifikat (Anonym)"
                }
            },
            "export": {
                "properties": [
                    {"key": "object-name", "label": "Objektname", "enabled": 1, "order": 10},
                    {"key": "local-date", "label": "lokales Datum", "enabled": 1, "order": 20},
                    {"key": "model-name", "label": "Gerätemodell", "enabled": 1, "order": 30},
                    {"key": "firmware-revision", "label": "Firmwareversion", "enabled": 1, "order": 40},
                    {"key": "address_port", "label": "Adresse + Port", "enabled": 1, "order": 50},
                    {"key": "device_id", "label": "Geräteinstanznr.", "enabled": 1, "order": 60},
                    {"key": "application-software-version", "label": "SW Version Applikation", "enabled": 1, "order": 70},
                    {"key": "description", "label": "Beschreibung", "enabled": 1, "order": 80},
                    {"key": "local-date", "label": "lokales Datum", "enabled": 0, "order": 90},
                    {"key": "local-time", "label": "lokale Zeit", "enabled": 0, "order": 100},
                    {"key": "ipv4", "label": "IPv4", "enabled": 1, "order": 110},
                    {"key": "subnet_mask", "label": "Subnetzmaske", "enabled": 1, "order": 120},
                    {"key": "router", "label": "Router", "enabled": 0, "order": 130},
                    {"key": "udp_port", "label": "Udp port", "enabled": 1, "order": 140},
                    # Weitere Felder...
                    {"key": "device-type", "label": "Gerätetyp", "enabled": 0, "order": 200},
                    {"key": "serial-number", "label": "Seriennummer", "enabled": 0, "order": 210},
                    {"key": "network-number", "label": "Netzwerknummer", "enabled": 0, "order": 220},
                    {"key": "model-info", "label": "Modellinfo", "enabled": 0, "order": 230},
                    {"key": "operational-url", "label": "Betriebsurl", "enabled": 0, "order": 240},
                    {"key": "mac-address", "label": "Mac Adresse", "enabled": 0, "order": 250},
                    {"key": "instance", "label": "Instanz", "enabled": 0, "order": 260},
                    {"key": "standort", "label": "Standort", "enabled": 0, "order": 270},
                    {"key": "firmware_revision_serial_number", "label": "firmware revisioseriennummer", "enabled": 0, "order": 280},
                    {"key": "betriebs_url_dup", "label": "Betriebs url", "enabled": 0, "order": 290}
                ]
            }
        }
        
        # Konfigurationsordner erstellen, falls nicht vorhanden
        if not self.config_dir.exists():
            os.makedirs(self.config_dir)
        
        # Konfiguration laden oder Standardeinstellungen verwenden
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Lädt die Einstellungen aus der Konfigurationsdatei"""
        settings = self.default_settings.copy()
        
        # UI-Einstellungen laden
        if self.ui_config_file.exists():
            try:
                with open(self.ui_config_file, 'r', encoding='utf-8') as f:
                    ui_settings = json.load(f)
                    settings.update(ui_settings)
            except Exception as e:
                print(f"Fehler beim Laden der UI-Konfiguration: {e}")
        
        # Benutzereinstellungen laden
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    if "user" in user_settings:
                        settings["user"] = user_settings["user"]
            except Exception as e:
                print(f"Fehler beim Laden der Benutzer-Konfiguration: {e}")
        
        # Verbindungseinstellungen laden
        if self.connection_config_file.exists():
            try:
                with open(self.connection_config_file, 'r', encoding='utf-8') as f:
                    connection_settings = json.load(f)
                    if "connection" in connection_settings:
                        settings["connection"] = connection_settings["connection"]
            except Exception as e:
                print(f"Fehler beim Laden der Verbindungs-Konfiguration: {e}")
    
        # Export-Einstellungen laden
        if self.export_config_file.exists():
            try:
                with open(self.export_config_file, 'r', encoding='utf-8') as f:
                    export_settings = json.load(f)
                    if "export" in export_settings:
                        settings["export"] = export_settings["export"]
            except Exception as e:
                print(f"Fehler beim Laden der Export-Konfiguration: {e}")
        
        return settings
    
    def save_settings(self, settings=None):
        """Speichert die Einstellungen in den entsprechenden Konfigurationsdateien"""
        if settings is None:
            settings = self.settings
        
        # UI-Einstellungen speichern
        try:
            ui_settings = {"ui": settings.get("ui", {})}
            with open(self.ui_config_file, 'w', encoding='utf-8') as f:
                json.dump(ui_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der UI-Konfiguration: {e}")
            return False
        
        # Benutzereinstellungen speichern
        try:
            user_settings = {"user": settings.get("user", {})}
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(user_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Benutzer-Konfiguration: {e}")
            return False
        
        # Verbindungseinstellungen speichern
        try:
            connection_settings = {"connection": settings.get("connection", {})}
            with open(self.connection_config_file, 'w', encoding='utf-8') as f:
                json.dump(connection_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Verbindungs-Konfiguration: {e}")
            return False
        
        # Export-Einstellungen speichern
        try:
            export_settings = {"export": settings.get("export", {})}
            with open(self.export_config_file, 'w', encoding='utf-8') as f:
                json.dump(export_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Export-Konfiguration: {e}")
            return False
        
        return True
    
    def get_setting(self, section, key=None, sub_key=None):
        """Gibt eine spezifische Einstellung zurück"""
        try:
            if key is None:
                return self.settings.get(section, {})
            elif sub_key is None:
                return self.settings[section][key]
            else:
                return self.settings[section][key][sub_key]
        except KeyError:
            if key is None:
                return self.default_settings.get(section, {})
            elif sub_key is None:
                return self.default_settings.get(section, {}).get(key)
            else:
                return self.default_settings.get(section, {}).get(key, {}).get(sub_key)
    
    def update_setting(self, section, key, value, sub_key=None):
        """Aktualisiert eine spezifische Einstellung"""
        if section not in self.settings:
            self.settings[section] = {}
        
        # Alte Werte für Event-Vergleich speichern
        if sub_key is None:
            old_value = self.get_setting(section, key)
            self.settings[section][key] = value
        else:
            if key not in self.settings[section]:
                self.settings[section][key] = {}
            old_value = self.get_setting(section, key, sub_key)
            self.settings[section][key][sub_key] = value
        
        self.save_settings()
        
        # Events für bestimmte Einstellungen auslösen
        if section == "ui":
            if key == "theme" and old_value != value:
                ThemeManager.set_theme(value)
                event_bus.dispatch('on_theme_changed', value)
            elif key == "language" and old_value != value:
                # Sprache aktualisieren
                from core.i18n.translator import Translator
                Translator().set_language(value)
        elif section == "connection" and key == "type" and old_value != value:
            event_bus.dispatch('on_connection_type_changed', value)
    
    def get_connection_config(self):
        """Gibt die aktuelle Verbindungskonfiguration zurück"""
        connection_type = self.get_setting("connection", "type")
        config = {
            "type": connection_type,
            **self.get_setting("connection", connection_type)
        }
        return config
    
    def save_connection_config(self, connection_type, config_data):
        """Speichert die Verbindungskonfiguration für einen bestimmten Typ"""
        # Aktualisiere den Verbindungstyp
        self.update_setting("connection", "type", connection_type)
        
        # Aktualisiere die Konfigurationsdaten
        for key, value in config_data.items():
            self.update_setting("connection", connection_type, value, key)

    def get_export_properties(self):
        """Gibt die Export-Properties zurück"""
        return self.get_setting("export", "properties") or []
    

    def set_export_properties(self, properties):
        """Setzt die Export-Properties"""
        self.update_setting("export", "properties", properties)


    def get_enabled_export_keys(self):
        """Gibt die aktivierten Export-Keys zurück"""
        properties = self.get_export_properties()
        return [prop["key"] for prop in properties if int(prop.get("enabled", 0)) == 1]