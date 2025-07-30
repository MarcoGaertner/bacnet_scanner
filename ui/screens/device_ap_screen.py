from ui.screens.connection_type_base_screen import ConnectionTypeBaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.lang import Builder
from core.i18n.translator import _
from ui.styles.colors import ThemeColors
from ui.widgets.expandable_panel import ExpandablePanel

# KV-Datei laden
Builder.load_file('ui/screens/device_ap_screen.kv')

class DeviceAPScreen(ConnectionTypeBaseScreen):
    """Screen für BACnet Device AP Verbindungseinstellungen"""
    screen_title = StringProperty("")
    connection_type = "device_ap"
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen"""
        self.screen_title = _("connection.device_ap.title")
    
    def create_specific_content(self):
        """Erstellt den spezifischen Inhalt für den Device AP Verbindungstyp"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Beschreibung
        description = Label(
            text=_("connection.device_ap.description"),
            color=ThemeColors.current["TEXT_COLOR"],
            font_size=dp(14),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        description.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Geräteadresse Panel
        device_panel = ExpandablePanel(
            title=_("connection.device_ap.device_address"),
            expanded=True,
            size_hint_y=None,
            height=dp(120)
        )
        
        device_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        device_input = TextInput(
            hint_text=_("connection.device_ap.device_address_hint"),
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        
        device_layout.add_widget(device_input)
        device_panel.add_content(device_layout)
        
        # Füge Widgets zum Content hinzu
        content.add_widget(description)
        content.add_widget(device_panel)
        
        return content