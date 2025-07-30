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
from ui.widgets.dropdown import NestedDropdown

# KV-Datei laden
Builder.load_file('ui/screens/secure_connect_screen.kv')

class SecureConnectScreen(ConnectionTypeBaseScreen):
    """Screen für BACnet Secure Connect Verbindungseinstellungen"""
    screen_title = StringProperty("")
    connection_type = "secure"
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen"""
        self.screen_title = _("connection.secure.title")
    
    def create_specific_content(self):
        """Erstellt den spezifischen Inhalt für den Secure Connect Verbindungstyp"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Beschreibung
        description = Label(
            text=_("connection.secure.description"),
            color=ThemeColors.current["TEXT_COLOR"],
            font_size=dp(14),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        description.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Server URL Panel
        server_panel = ExpandablePanel(
            title=_("connection.secure.server_url"),
            expanded=True,
            size_hint_y=None,
            height=dp(100)
        )
        
        server_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        server_input = TextInput(
            hint_text=_("connection.secure.server_url_hint"),
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        
        server_layout.add_widget(server_input)
        server_panel.add_content(server_layout)
        
        # Zertifikat Panel
        cert_panel = ExpandablePanel(
            title=_("connection.secure.certificate"),
            expanded=True,
            size_hint_y=None,
            height=dp(100)
        )
        
        cert_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        cert_dropdown = NestedDropdown(
            title=_("connection.secure.select_certificate"),
            options=[_("connection.secure.no_certificate"), "Certificate 1", "Certificate 2"],
            current_value=_("connection.secure.no_certificate")
        )
        
        cert_layout.add_widget(cert_dropdown)
        cert_panel.add_content(cert_layout)
        
        # Füge Widgets zum Content hinzu
        content.add_widget(description)
        content.add_widget(server_panel)
        content.add_widget(cert_panel)
        
        return content