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
        
        # Standardeinstellungen
        self.default_settings = {
            "ui": {
                "language": "deutsch",
                "theme": "hell",
                "units": "metrisch"
            },
            "user": {  # NEU
                "first_name": "",
                "last_name": "",
                "phone": "",
                "email": "",
                "company": ""
            }
        }
        
        # Konfigurationsordner erstellen, falls nicht vorhanden
        if not self.config_dir.exists():
            os.makedirs(self.config_dir)
        
        # Konfiguration laden oder Standardeinstellungen verwenden
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Lädt die Einstellungen aus der Konfigurationsdatei"""
        if not self.ui_config_file.exists():
            # Konfigurationsdatei erstellen mit Standardeinstellungen
            self.save_settings(self.default_settings)
            return self.default_settings
        
        try:
            with open(self.ui_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {e}")
            return self.default_settings
    
    def save_settings(self, settings=None):
        """Speichert die Einstellungen in der Konfigurationsdatei"""
        if settings is None:
            settings = self.settings
        
        try:
            with open(self.ui_config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def get_setting(self, section, key):
        """Gibt eine spezifische Einstellung zurück"""
        try:
            return self.settings[section][key]
        except KeyError:
            return self.default_settings.get(section, {}).get(key)


    def update_setting(self, section, key, value):
        """Aktualisiert eine spezifische Einstellung"""
        if section not in self.settings:
            self.settings[section] = {}
        
        # Alte Werte für Event-Vergleich speichern
        old_value = self.get_setting(section, key)
        
        self.settings[section][key] = value
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