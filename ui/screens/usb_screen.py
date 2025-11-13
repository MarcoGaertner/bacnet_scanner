from ui.screens.connection_type_base_screen import ConnectionTypeBaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.lang import Builder
from ui.utils import get_resource_path
from core.i18n.translator import _
from ui.styles.colors import ThemeColors
from ui.widgets.expandable_panel import ExpandablePanel
from ui.widgets.dropdown import NestedDropdown

# KV-Datei laden
Builder.load_file('ui/screens/usb_screen.kv')

class USBScreen(ConnectionTypeBaseScreen):
    """Screen für BACnet USB Verbindungseinstellungen"""
    screen_title = StringProperty("")
    connection_type = "usb"
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen"""
        self.screen_title = _("connection.usb.title")
    
    def create_specific_content(self):
        """Erstellt den spezifischen Inhalt für den USB Verbindungstyp"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Beschreibung
        description = Label(
            text=_("connection.usb.description"),
            color=ThemeColors.current["TEXT_COLOR"],
            font_size=dp(14),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        description.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # USB Gerät Panel
        usb_panel = ExpandablePanel(
            title=_("connection.usb.device"),
            expanded=True,
            size_hint_y=None,
            height=dp(100)
        )
        
        usb_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        usb_dropdown = NestedDropdown(
            title=_("connection.usb.select_device"),
            options=["USB Device 1", "USB Device 2"],
            current_value="USB Device 1"
        )
        
        usb_layout.add_widget(usb_dropdown)
        usb_panel.add_content(usb_layout)
        
        # Füge Widgets zum Content hinzu
        content.add_widget(description)
        content.add_widget(usb_panel)
        
        return content