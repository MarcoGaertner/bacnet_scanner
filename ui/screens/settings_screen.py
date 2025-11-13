from ui.screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from ui.utils import get_resource_path
from kivy.properties import StringProperty, ObjectProperty
from ui.widgets.dropdown import NestedDropdown
from ui.widgets.expandable_panel import ExpandablePanel
from core.config import ConfigManager
from core.i18n.translator import _
from core.events import event_bus
from kivy.clock import Clock

# KV-Datei laden
Builder.load_file('ui/screens/settings_screen.kv')

class SettingsScreen(BaseScreen):
    """Screen für Anwendungseinstellungen"""
    screen_title = StringProperty("")
    section_title = StringProperty("")
    config_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.config_manager = ConfigManager()
        
        # Übersetzungen aktualisieren
        self.update_translations()
        
        # Event-Listener für Sprachänderungen
        event_bus.bind(on_language_changed=self.on_language_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        
        # UI aufbauen, nachdem das Layout geladen ist
        self.bind(size=self.setup_ui)
    
    def update_translations(self):
        """Aktualisiert alle übersetzten Texte"""
        self.screen_title = _("settings.title")
        self.section_title = _("settings.ui.section")
    
    def setup_ui(self, *args):
        """Erstellt die UI mit den Einstellungen"""
        # Container leeren
        self.ids.settings_container.clear_widgets()
        
        # Aktuellen Wert aus der Konfiguration laden
        language = self.config_manager.get_setting("ui", "language")
        theme = self.config_manager.get_setting("ui", "theme")
        units = self.config_manager.get_setting("ui", "units")
        
        # Sprache Panel
        language_panel = ExpandablePanel(title=_("settings.language"))
        language_dropdown = NestedDropdown(
            title="",  # Kein Titel innerhalb des Panels
            options=[_("language.german"), _("language.english")],
            current_value=_("language.german") if language == "deutsch" else _("language.english")
        )
        language_dropdown.on_select = lambda value: self.update_language_setting(value)
        language_panel.ids.content.add_widget(language_dropdown)
        self.ids.settings_container.add_widget(language_panel)
        
        # Design Panel
        theme_panel = ExpandablePanel(title=_("settings.theme"))
        theme_dropdown = NestedDropdown(
            title="",
            options=[_("theme.light"), _("theme.dark")],
            current_value=_("theme.light") if theme == "hell" else _("theme.dark")
        )
        theme_dropdown.on_select = lambda value: self.update_theme_setting(value)
        theme_panel.ids.content.add_widget(theme_dropdown)
        self.ids.settings_container.add_widget(theme_panel)
        
        # Einheitensystem Panel
        units_panel = ExpandablePanel(title=_("settings.units"))
        units_dropdown = NestedDropdown(
            title="",
            options=[_("units.metric"), _("units.imperial")],
            current_value=_("units.metric") if units == "metrisch" else _("units.imperial")
        )
        units_dropdown.on_select = lambda value: self.update_units_setting(value)
        units_panel.ids.content.add_widget(units_dropdown)
        self.ids.settings_container.add_widget(units_panel)
        
        # Verzögerte Panel-Aktualisierung
        Clock.schedule_once(self._update_panels, 0.2)
    
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
        self.update_translations()
        self.setup_ui()
    
    def reload_language(self):
        """Implementiere die reload_language-Methode der BaseScreen-Klasse"""
        self.update_translations()
        self.setup_ui()
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn sich das Theme ändert"""
        self.reload_theme()
    
    def reload_theme(self):
        """Implementierung der reload_theme-Methode der BaseScreen-Klasse"""
        # Canvas aktualisieren (für Hintergrund)
        self.canvas.ask_update()
        
        # Farben in allen Komponenten aktualisieren
        for child in self.walk():
            if hasattr(child, 'update_colors'):
                child.update_colors()
        
        # UI mit aktualisierten Farben neu aufbauen
        self.setup_ui()

    def _update_panels(self, dt):
        """Aktualisiert die Panel-Zustände"""
        for panel_id in ['language_panel', 'theme_panel', 'units_panel']:
            if hasattr(self.ids, panel_id):
                panel = getattr(self.ids, panel_id)
                # Explizit den aktuellen Zustand neu setzen
                expanded = panel.is_expanded
                panel._update_panel_state(expanded)