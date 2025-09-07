from ui.screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from core.config import ConfigManager
from core.i18n.translator import _
from core.events import event_bus
from ui.styles.colors import ThemeColors
from ui.widgets.hint_text_input import HintTextInput
from ui.widgets.expandable_panel import ExpandablePanel

# KV-Datei laden
Builder.load_file('ui/screens/account_screen.kv')

class AccountScreen(BaseScreen):
    """Screen für Kontoeinstellungen"""
    screen_title = StringProperty("")
    config_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(AccountScreen, self).__init__(**kwargs)
        self.config_manager = ConfigManager()
        
        # Übersetzungen aktualisieren
        self.update_translations()
        
        # Event-Listener
        event_bus.bind(on_language_changed=self.on_language_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        
        # UI aufbauen, nachdem das Layout geladen ist
        self.bind(size=self.setup_ui)
    
    def update_translations(self):
        """Aktualisiert alle übersetzten Texte"""
        self.screen_title = _("account.title")
    
    def setup_ui(self, *args):
        """Erstellt die UI mit den Eingabefeldern"""
        # Name Dropdown mit zwei Feldern
        name_container = self.ids.name_dropdown.ids.content
        name_container.clear_widgets()
        
        first_name_input = HintTextInput(
            hint_text=_("account.first_name"),
            text=self.config_manager.get_setting("user", "first_name") or ""
        )
        first_name_input.bind(text=lambda instance, value: self.save_setting("first_name", value))
        
        last_name_input = HintTextInput(
            hint_text=_("account.last_name"),
            text=self.config_manager.get_setting("user", "last_name") or ""
        )
        last_name_input.bind(text=lambda instance, value: self.save_setting("last_name", value))
        
        name_container.add_widget(first_name_input)
        name_container.add_widget(last_name_input)
        
        # Phone Dropdown
        phone_container = self.ids.phone_dropdown.ids.content
        phone_container.clear_widgets()
        
        phone_input = HintTextInput(
            hint_text=_("account.phone_number"),
            text=self.config_manager.get_setting("user", "phone") or ""
        )
        phone_input.bind(text=lambda instance, value: self.save_setting("phone", value))
        
        phone_container.add_widget(phone_input)
        
        # Email Dropdown
        email_container = self.ids.email_dropdown.ids.content
        email_container.clear_widgets()
        
        email_input = HintTextInput(
            hint_text=_("account.email_address"),
            text=self.config_manager.get_setting("user", "email") or ""
        )
        email_input.bind(text=lambda instance, value: self.save_setting("email", value))
        
        email_container.add_widget(email_input)
        
        # Company Dropdown
        company_container = self.ids.company_dropdown.ids.content
        company_container.clear_widgets()
        
        company_input = HintTextInput(
            hint_text=_("account.company_name"),
            text=self.config_manager.get_setting("user", "company") or ""
        )
        company_input.bind(text=lambda instance, value: self.save_setting("company", value))
        
        company_container.add_widget(company_input)
    
    def save_setting(self, key, value):
        """Speichert eine Benutzereinstellung"""
        # Bei leerem Eingabefeld auf Leerstring setzen (nicht None)
        self.config_manager.update_setting("user", key, value or "")
    
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
        
        # UI mit aktualisierten Farben neu aufbauen
        self.setup_ui()