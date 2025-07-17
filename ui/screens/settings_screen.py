from ui.screens.base_screen import BaseScreen 
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty

from ui.widgets.dropdown import NestedDropdown
from core.config import ConfigManager
from core.i18n.translator import _
from core.events import event_bus

# KV-Datei laden
Builder.load_file('ui/screens/settings_screen.kv')

class SettingSection(BoxLayout):
    title = StringProperty("")

class SettingsScreen(BaseScreen):
    # Überschriften als StringProperty definieren
    screen_title = StringProperty("")
    section_title = StringProperty("")
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.config_manager = ConfigManager()
        
        # UI nach dem Aufbau des Screens initialisieren
        self.bind(size=self.setup_ui)

        # Überschriften initial setzen
        self.update_translations()
        
        # Events beobachten
        event_bus.bind(on_language_changed=self.on_language_changed)
    
    def update_translations(self):
        """Aktualisiert alle übersetzten Texte"""
        self.screen_title = _("settings.title")
        self.section_title = _("settings.ui.section")
    
    def setup_ui(self, *args):
        # Container leeren und UI-Elemente hinzufügen
        settings_container = self.ids.ui_settings_container
        settings_container.clear_widgets()
        
        # Aktuellen Wert aus der Konfiguration laden
        language = self.config_manager.get_setting("ui", "language")
        theme = self.config_manager.get_setting("ui", "theme")
        units = self.config_manager.get_setting("ui", "units")
        
        # Sprache Dropdown
        language_dropdown = NestedDropdown(
            title=_("settings.language"),
            options=[_("language.german"), _("language.english")],
            current_value=_("language.german") if language == "deutsch" else _("language.english")
        )
        language_dropdown.on_select = lambda value: self.update_language_setting(value)
        
        # Design Dropdown
        theme_dropdown = NestedDropdown(
            title=_("settings.theme"),
            options=[_("theme.light"), _("theme.dark")],
            current_value=_("theme.light") if theme == "hell" else _("theme.dark")
        )
        theme_dropdown.on_select = lambda value: self.update_theme_setting(value)
        
        # Einheitensystem Dropdown
        units_dropdown = NestedDropdown(
            title=_("settings.units"),
            options=[_("units.metric"), _("units.imperial")],
            current_value=_("units.metric") if units == "metrisch" else _("units.imperial")
        )
        units_dropdown.on_select = lambda value: self.update_units_setting(value)
        
        # Widgets zum Container hinzufügen
        settings_container.add_widget(language_dropdown)
        settings_container.add_widget(theme_dropdown)
        settings_container.add_widget(units_dropdown)

    def update_language_setting(self, value):
        """Aktualisiert die Spracheinstellung"""
        language_code = "deutsch" if value == _("language.german") else "englisch"
        self.config_manager.update_setting("ui", "language", language_code)
    
    def update_theme_setting(self, value):
        """Aktualisiert die Designeinstellung"""
        theme_code = "hell" if value == _("theme.light") else "dunkel"
        self.config_manager.update_setting("ui", "theme", theme_code)
    
    def update_units_setting(self, value):
        """Aktualisiert die Einheiteneinstellung"""
        units_code = "metrisch" if value == _("units.metric") else "imperial"
        self.config_manager.update_setting("ui", "units", units_code)
    
    def on_language_changed(self, instance, language_code):
        """Wird aufgerufen, wenn sich die Sprache ändert"""
        self.update_translations()  # Überschriften aktualisieren
        self.setup_ui()  # UI mit neuen Übersetzungen aktualisieren
    
    def reload_language(self):
        """Implementiere die reload_language-Methode der BaseScreen-Klasse"""
        self.update_translations()
        self.setup_ui()
    
    def update_setting(self, key, value):
        """Aktualisiert eine Einstellung und speichert sie"""
        self.config_manager.update_setting("ui", key, value)
        
        # Bei Theme-Änderung sofort die UI aktualisieren
        if key == "theme":
            # Die Aktualisierung erfolgt automatisch über den EventBus
            # Aber wir können auch die eigene UI direkt aktualisieren
            self.reload_theme()