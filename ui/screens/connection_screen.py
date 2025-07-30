from ui.screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.metrics import dp
from core.config import ConfigManager
from core.i18n.translator import _
from core.events import event_bus
from ui.styles.colors import ThemeColors
from ui.widgets.expandable_panel import ExpandablePanel
from ui.widgets.radio_button import RadioButtonGroup, SimpleRadioButton
from ui.widgets.toggle_switch import ToggleSwitch
from kivy.clock import Clock
import json
import os

# KV-Datei laden
Builder.load_file('ui/screens/connection_screen.kv')

class ConnectionScreen(BaseScreen):
    """Screen für BACnet-Verbindungseinstellungen"""
    screen_title = StringProperty("BACnet Connection")
    connection_type = StringProperty("network")
    config_manager = ObjectProperty(None)
    
    _radio_button_group_widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ConnectionScreen, self).__init__(**kwargs)
        self.config_manager = ConfigManager()

        self.update_translations()
        event_bus.bind(on_language_changed=self.on_language_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)

        # setup_ui nach dem vollständigen Laden und der Größenanpassung des Screens planen
        Clock.schedule_once(lambda dt: self.setup_ui(), 0)

        self.connection_type = self.config_manager.get_setting("connection", "type") or "network"

    def update_translations(self):
        self.screen_title = _("connection.title")

    def setup_ui(self, *args):
        print(f"DEBUG: ConnectionScreen.setup_ui called. Current size: {self.size}, pos: {self.pos}")
        if hasattr(self.ids, 'connection_type_screen') and self.ids.connection_type_screen.opacity == 1:
            self._setup_connection_type_ui()
        else:
            self._setup_connection_settings_ui()
        # Schedule a debug tree print after a short delay to allow layout to settle
        Clock.schedule_once(lambda dt: self._debug_widget_tree(), 0.5)

    def _setup_connection_type_ui(self):
        """Richtet die UI für die Verbindungstyp-Auswahl ein"""
        print("DEBUG: Setting up connection type UI using RadioButtonGroup")

        if hasattr(self.ids, 'connection_options'):
            options_container = self.ids.connection_options
            print(f"DEBUG: options_container initial state - pos: {options_container.pos}, size: {options_container.size}, size_hint_y: {options_container.size_hint_y}, height: {options_container.height}")
            options_container.clear_widgets()

            options = [
                _("connection.type.device_ap"),
                _("connection.type.network"),
                _("connection.type.mstp"),
                _("connection.type.usb"),
                _("connection.type.secure")
            ]
            selected_option_translated = self._get_translated_connection_type()
            print(f"DEBUG: Options: {options}, Selected: {selected_option_translated}")

            self._radio_button_group_widget = RadioButtonGroup(
                options=options,
                selected=selected_option_translated,
                group_name="connection_type_group",
                on_selection_changed=self._on_connection_type_changed
            )
            options_container.add_widget(self._radio_button_group_widget)
            print(f"DEBUG: RadioButtonGroup added to options_container. options_container children: {options_container.children}")

            # Hinzugefügte Zeilen: Erzwingen einer Layout-Aktualisierung
            # This is often not strictly necessary if size_hint_y is None and height is minimum_height,
            # but it helps in debugging to see immediate effects.
            options_container.do_layout()
            print(f"DEBUG: options_container.do_layout() called.")
            options_container.canvas.ask_update()
            print(f"DEBUG: options_container.canvas.ask_update() called.")
            print(f"DEBUG: options_container after do_layout - pos: {options_container.pos}, size: {options_container.size}, height: {options_container.height}")

    def _setup_connection_settings_ui(self):
        """Richtet die UI für die Verbindungseinstellungen ein"""
        if self.connection_type == "network":
            self._setup_network_settings_ui()

    def _setup_network_settings_ui(self):
        """Richtet die UI für Netzwerk-Verbindungseinstellungen ein"""
        from ui.widgets.dropdown import NestedDropdown

        if hasattr(self.ids, 'network_panel'):
            network_panel = self.ids.network_panel.ids.content
            network_panel.clear_widgets()

            adapter_dropdown = NestedDropdown(
                title=_("connection.network.adapter"),
                options=["Ethernet", "Wi-Fi", "VPN"],
                current_value="Ethernet"
            )
            network_panel.add_widget(adapter_dropdown)

    def _get_translated_connection_type(self):
        """Gibt den übersetzten Verbindungstyp zurück"""
        type_mapping = {
            "device_ap": _("connection.type.device_ap"),
            "network": _("connection.type.network"),
            "mstp": _("connection.type.mstp"),
            "usb": _("connection.type.usb"),
            "secure": _("connection.type.secure")
        }
        return type_mapping.get(self.connection_type, _("connection.type.network"))

    def _get_connection_type_from_translated(self, translated_type):
        """Gibt den internen Verbindungstyp für einen übersetzten Typ zurück"""
        type_mapping = {
            _("connection.type.device_ap"): "device_ap",
            _("connection.type.network"): "network",
            _("connection.type.mstp"): "mstp",
            _("connection.type.usb"): "usb",
            _("connection.type.secure"): "secure"
        }
        return type_mapping.get(translated_type, "network")

    def _on_connection_type_changed(self, value):
        """Wird aufgerufen, wenn der Verbindungstyp geändert wird"""
        internal_type = self._get_connection_type_from_translated(value)
        self.connection_type = internal_type
        self.config_manager.update_setting("connection", "type", internal_type)
        if self._radio_button_group_widget:
            self._radio_button_group_widget.selected = value

    def on_next_button_clicked(self):
        """Wird aufgerufen, wenn der 'Weiter'-Button geklickt wird"""
        if hasattr(self.ids, 'connection_type_screen') and self.ids.connection_type_screen.opacity == 1:
            self.ids.connection_type_screen.opacity = 0
            self.ids.connection_settings_screen.opacity = 1
            self._setup_connection_settings_ui()
        else:
            app = self.get_root_window().children[0]
            app.root.ids.screen_manager.current = 'geräte'

    def on_language_changed(self, instance, language_code):
        self.update_translations()
        if self._radio_button_group_widget:
            options = [
                _("connection.type.device_ap"),
                _("connection.type.network"),
                _("connection.type.mstp"),
                _("connection.type.usb"),
                _("connection.type.secure")
            ]
            self._radio_button_group_widget.options = options
            self._radio_button_group_widget.selected = self._get_translated_connection_type()
        self.setup_ui()

    def reload_language(self):
        self.update_translations()
        self.setup_ui()

    def on_theme_changed(self, instance, theme_name):
        self.reload_theme()

    def reload_theme(self):
        self.canvas.ask_update()
        self.setup_ui()

    def _debug_widget_tree(self, widget=None, level=0):
        """Rekursives Debugging des Widget-Baums (für Debug-Zwecke)"""
        if widget is None:
            widget = self
            print("\n--- DEBUG: Widget Tree Analysis ---")
        
        indent = "  " * level
        
        # Limit depth for readability, but ensure key widgets are fully detailed
        if level > 5 and not isinstance(widget, (RadioButtonGroup, SimpleRadioButton)):
            # Only print basic info for deeper levels if not a target widget
            print(f"{indent}Widget: {widget.__class__.__name__} (id: {widget.id if hasattr(widget, 'id') else 'None'}) ... (too deep)")
            return

        widget_info = (
            f"Widget: {widget.__class__.__name__} (id: {widget.id if hasattr(widget, 'id') else 'None'}) "
            f"pos: {widget.pos}, size: {widget.size}, "
            f"size_hint: {widget.size_hint}, pos_hint: {widget.pos_hint}, "
            f"opacity: {widget.opacity:.2f}, visible: {widget.opacity > 0}"
        )
        print(f"{indent}{widget_info}")

        if hasattr(widget, 'children') and widget.children:
            # Iterate through children in reverse order as Kivy adds them to the beginning of the list
            for child in reversed(widget.children):
                self._debug_widget_tree(child, level + 1)
        
        if level == 0:
            print("--- END Widget Tree Analysis ---\n")