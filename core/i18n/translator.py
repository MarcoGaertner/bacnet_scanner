from core.events import event_bus
from core.config import ConfigManager

class Translator:
    """Verwaltet Übersetzungen für die App"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialisiert den Übersetzer"""
        self.config_manager = ConfigManager()
        self.translations = {}
        self.current_language = None
        
        # Unterstützte Sprachen
        self.supported_languages = ['deutsch', 'englisch']
        
        # Sprache laden
        self.set_language(self.config_manager.get_setting("ui", "language"))
    
    def set_language(self, language_code):
        """Setzt die aktuelle Sprache"""
        if language_code not in self.supported_languages:
            language_code = 'deutsch'  # Standardsprache
        
        # Lade das Sprachmodul dynamisch
        if language_code == 'deutsch':
            from core.i18n.languages.de import translations
            self.translations = translations
        elif language_code == 'englisch':
            from core.i18n.languages.en import translations
            self.translations = translations
        
        self.current_language = language_code
        
        # Event für UI-Updates auslösen
        event_bus.dispatch('on_language_changed', language_code)
        return True
    
    def get(self, key, default=None):
        """Gibt eine Übersetzung für den Schlüssel zurück"""
        if default is None:
            default = key
        result = self.translations.get(key, default)
        print(f"Übersetzung für '{key}' -> '{result}'")
        return result

# Globaler Übersetzer für einfachen Zugriff
def _(key, default=None):
    """Kurzform für Übersetzungen"""
    return Translator().get(key, default)