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
Builder.load_file('ui/screens/mstp_screen.kv')

class MSTPScreen(ConnectionTypeBaseScreen):
    """Screen für BACnet MS/TP Verbindungseinstellungen"""
    screen_title = StringProperty("")
    connection_type = "mstp"
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen"""
        self.screen_title = _("connection.mstp.title")
    
    def create_specific_content(self):
        """Erstellt den spezifischen Inhalt für den MS/TP Verbindungstyp"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Beschreibung
        description = Label(
            text=_("connection.mstp.description"),
            color=ThemeColors.current["TEXT_COLOR"],
            font_size=dp(14),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        description.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # COM Port Panel
        com_panel = ExpandablePanel(
            title=_("connection.mstp.com_port"),
            expanded=True,
            size_hint_y=None,
            height=dp(100)
        )
        
        com_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        com_dropdown = NestedDropdown(
            title=_("connection.mstp.port"),
            options=["COM1", "COM2", "COM3", "COM4"],
            current_value="COM1"
        )
        
        com_layout.add_widget(com_dropdown)
        com_panel.add_content(com_layout)
        
        # Baudrate Panel
        baud_panel = ExpandablePanel(
            title=_("connection.mstp.baud_rate"),
            expanded=True,
            size_hint_y=None,
            height=dp(100)
        )
        
        baud_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        baud_dropdown = NestedDropdown(
            title=_("connection.mstp.baud_rate"),
            options=["9600", "19200", "38400", "57600", "76800", "115200"],
            current_value="38400"
        )
        
        baud_layout.add_widget(baud_dropdown)
        baud_panel.add_content(baud_layout)
        
        # MAC Adresse Panel
        mac_panel = ExpandablePanel(
            title=_("connection.mstp.mac_address"),
            expanded=True,
            size_hint_y=None,
            height=dp(100)
        )
        
        mac_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        mac_input = TextInput(
            hint_text=_("connection.mstp.mac_address_hint"),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        mac_layout.add_widget(mac_input)
        mac_panel.add_content(mac_layout)
        
        # Füge Widgets zum Content hinzu
        content.add_widget(description)
        content.add_widget(com_panel)
        content.add_widget(baud_panel)
        content.add_widget(mac_panel)
        
        return content