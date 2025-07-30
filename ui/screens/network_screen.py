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
from ui.widgets.toggle_switch import ToggleSwitch
from kivy.app import App

# KV-Datei laden
Builder.load_file('ui/screens/network_screen.kv')

class NetworkScreen(ConnectionTypeBaseScreen):
    """Screen für BACnet Netzwerk Verbindungseinstellungen"""
    screen_title = StringProperty("")
    connection_type = "network"
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen"""
        self.screen_title = _("connection.network.title")
    
    def create_specific_content(self):
        """Erstellt den spezifischen Inhalt für den Netzwerk Verbindungstyp"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Debug-Funktion für Größenänderungen
        def debug_size(widget, size):
            print(f"DEBUG: {widget.__class__.__name__} Größe geändert: {size}")
            print(f"DEBUG: Content Höhe: {content.height}, minimum_height: {content.minimum_height}")
        
        content.bind(size=lambda instance, size: debug_size(instance, size))
        
        # Überschriften
        step1_label = Label(
            text="1. " + _("connection.network.select_network"),
            color=ThemeColors.current["TEXT_COLOR"],
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        step1_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        step2_label = Label(
            text="2. " + _("connection.network.advanced_settings"),
            color=ThemeColors.current["TEXT_COLOR"],
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        step2_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Netzwerk Panel
        network_panel = ExpandablePanel(
            title=_("connection.network.network"),
            is_expanded=False,  # Standardmäßig eingeklappt
            size_hint_y=None,
            height=dp(40)  # Nur die Höhe des Headers, wird beim Aufklappen angepasst
        )
        
        network_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        # Netzwerkadapter Dropdown
        adapter_dropdown = NestedDropdown(
            title=_("connection.network.adapter"),
            options=["Ethernet", "Wi-Fi", "VPN"],
            current_value="Ethernet"
        )
        
        # IP-Adresse Label
        ip_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        
        ip_label_left = Label(
            text=_("connection.network.ip_address"),
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_x=0.4,
            halign='left',
            valign='middle'
        )
        ip_label_left.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        ip_label_right = Label(
            text="192.168.1.100",
            color=ThemeColors.current["HIGHLIGHT_COLOR"],
            size_hint_x=0.6,
            halign='left',
            valign='middle'
        )
        ip_label_right.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        ip_layout.add_widget(ip_label_left)
        ip_layout.add_widget(ip_label_right)
        
        network_layout.add_widget(adapter_dropdown)
        network_layout.add_widget(ip_layout)
        
        network_panel.add_content(network_layout)
        
        # Netzwerknummer Panel
        network_number_panel = ExpandablePanel(
            title=_("connection.network.network_number"),
            is_expanded=False,
            size_hint_y=None,
            height=dp(40)  # Nur die Höhe des Headers, wird beim Aufklappen angepasst
        )
        
        network_number_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        network_number_input = TextInput(
            hint_text=_("connection.network.network_number_hint"),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        network_number_layout.add_widget(network_number_input)
        network_number_panel.add_content(network_number_layout)
        
        # UDP Port Panel
        udp_port_panel = ExpandablePanel(
            title=_("connection.network.udp_port"),
            is_expanded=False,
            size_hint_y=None,
            height=dp(40)  # Nur die Höhe des Headers, wird beim Aufklappen angepasst
        )
        
        udp_port_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        
        udp_port_dropdown = NestedDropdown(
            title=_("connection.network.port"),
            options=["BAC0 (47808)", "BAC1 (47809)", "BAC2 (47810)", "BAC3 (47811)"],
            current_value="BAC0 (47808)"
        )
        
        udp_port_layout.add_widget(udp_port_dropdown)
        udp_port_panel.add_content(udp_port_layout)
        
        # Foreign Device Panel mit Toggle Switch
        foreign_device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        foreign_device_label = Label(
            text=_("connection.network.foreign_device"),
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_x=0.7,
            halign='left',
            valign='middle'
        )
        foreign_device_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Toggle Switch auskommentiert für Debugging
        # foreign_device_switch = ToggleSwitch(
        #     active=False,
        #     size_hint=(None, None),
        #     size=(dp(50), dp(30)),
        #     pos_hint={'center_y': 0.5}
        # )
        
        foreign_device_layout.add_widget(foreign_device_label)
        # foreign_device_layout.add_widget(foreign_device_switch)
        
        # Foreign Device Panel Inhalt (initial versteckt)
        foreign_device_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(0),
            opacity=0
        )
        
        bbmd_ip_input = TextInput(
            hint_text=_("connection.network.bbmd_ip"),
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        
        bbmd_port_dropdown = NestedDropdown(
            title=_("connection.network.bbmd_port"),
            options=["BAC0 (47808)", "BAC1 (47809)", "BAC2 (47810)", "BAC3 (47811)"],
            current_value="BAC0 (47808)"
        )
        
        bbmd_network_input = TextInput(
            hint_text=_("connection.network.bbmd_network"),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        foreign_device_panel.add_widget(bbmd_ip_input)
        foreign_device_panel.add_widget(bbmd_port_dropdown)
        foreign_device_panel.add_widget(bbmd_network_input)
        
        # Toggle Switch Funktion auskommentiert
        # def on_toggle_switch(instance, value):
        #     if value:
        #         foreign_device_panel.height = dp(150)
        #         foreign_device_panel.opacity = 1
        #     else:
        #         foreign_device_panel.height = dp(0)
        #         foreign_device_panel.opacity = 0
        # 
        # foreign_device_switch.bind(active=on_toggle_switch)
        
        # Füge Widgets zum Content hinzu
        content.add_widget(step1_label)
        content.add_widget(network_panel)
        content.add_widget(step2_label)
        content.add_widget(network_number_panel)
        content.add_widget(udp_port_panel)
        content.add_widget(foreign_device_layout)
        # content.add_widget(foreign_device_panel)  # Auskommentiert für Debugging
        
        return content

    def on_back_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Zurück'-Button geklickt wird"""
        from kivy.app import App
        app = App.get_running_app()
        app.root.ids.screen_manager.current = 'verbindung'

    def on_next_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Weiter'-Button geklickt wird"""
        # Speichere die Konfiguration
        config_data = {
            "adapter": self.adapter_dropdown.current_value,
            "network_number": self.network_number_input.text,
            "udp_port": self.udp_port_dropdown.current_value,
            "foreign_device": self.foreign_device_switch.active,
            "bbmd_ip": self.bbmd_ip_input.text if self.foreign_device_switch.active else "",
            "bbmd_port": self.bbmd_port_dropdown.current_value if self.foreign_device_switch.active else "BAC0 (47808)",
            "bbmd_network": self.bbmd_network_input.text if self.foreign_device_switch.active else ""
        }
        
        # Speichere die Konfiguration
        self.config_manager.save_connection_config("network", config_data)
        
        # Navigiere zum nächsten Screen
        from kivy.app import App
        app = App.get_running_app()
        app.root.ids.screen_manager.current = 'geräte'