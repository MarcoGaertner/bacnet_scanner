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
from kivy.clock import Clock

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
        # Hauptcontainer für den gesamten Inhalt
        main_container = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        main_container.bind(minimum_height=main_container.setter('height'))
        
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
            is_expanded=False,
            size_hint_y=None
        )
        
        network_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)], size_hint_y=None)
        network_layout.bind(minimum_height=network_layout.setter('height'))
        
        # Netzwerkadapter Dropdown
        self.adapter_dropdown = NestedDropdown(
            title=_("connection.network.adapter"),
            options=["Ethernet", "Wi-Fi", "VPN"],
            current_value="Ethernet",
            size_hint_y=None,
            height=dp(50)
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
        
        network_layout.add_widget(self.adapter_dropdown)
        network_layout.add_widget(ip_layout)
        
        network_panel.add_content(network_layout)
        
        # Netzwerknummer Panel
        network_number_panel = ExpandablePanel(
            title=_("connection.network.network_number"),
            is_expanded=False,
            size_hint_y=None
        )
        
        network_number_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)], size_hint_y=None)
        network_number_layout.bind(minimum_height=network_number_layout.setter('height'))
        
        self.network_number_input = TextInput(
            hint_text=_("connection.network.network_number_hint"),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        network_number_layout.add_widget(self.network_number_input)
        network_number_panel.add_content(network_number_layout)
        
        # UDP Port Panel
        udp_port_panel = ExpandablePanel(
            title=_("connection.network.udp_port"),
            is_expanded=False,
            size_hint_y=None
        )
        
        udp_port_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)], size_hint_y=None)
        udp_port_layout.bind(minimum_height=udp_port_layout.setter('height'))
        
        self.udp_port_dropdown = NestedDropdown(
            title=_("connection.network.port"),
            options=["BAC0 (47808)", "BAC1 (47809)", "BAC2 (47810)", "BAC3 (47811)"],
            current_value="BAC0 (47808)",
            size_hint_y=None,
            height=dp(50)
        )
        
        udp_port_layout.add_widget(self.udp_port_dropdown)
        udp_port_panel.add_content(udp_port_layout)
        
        # Foreign Device Panel mit Toggle Switch
        foreign_device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[0, 0, dp(10), 0])
        
        foreign_device_label = Label(
            text=_("connection.network.foreign_device"),
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_x=0.855,
            halign='left',
            valign='middle'
        )
        foreign_device_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Container für den Toggle Switch, um sicherzustellen, dass er vollständig sichtbar ist
        switch_container = BoxLayout(size_hint_x=0.145, padding=[0, 0, 0, 0])
        
        # Toggle Switch
        self.foreign_device_switch = ToggleSwitch(
            active=False,
            size_hint=(None, None),
            size=(dp(50), dp(30)),
            pos_hint={'center_y': 0.5, 'center_x': 0.5}  # Zentriert im Container
        )
        
        switch_container.add_widget(self.foreign_device_switch)
        foreign_device_layout.add_widget(foreign_device_label)
        foreign_device_layout.add_widget(switch_container)
        
        # Foreign Device Panel Inhalt
        self.foreign_device_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(0),
            opacity=0,
            padding=[dp(10), 0, dp(10), dp(10)]  # Padding hinzufügen, um Rand einzuhalten
        )
        self.foreign_device_panel.bind(minimum_height=self.foreign_device_panel.setter('height'))
        
        self.bbmd_ip_input = TextInput(
            hint_text=_("connection.network.bbmd_ip"),
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        
        self.bbmd_port_dropdown = NestedDropdown(
            title=_("connection.network.bbmd_port"),
            options=["BAC0 (47808)", "BAC1 (47809)", "BAC2 (47810)", "BAC3 (47811)"],
            current_value="BAC0 (47808)",
            size_hint_y=None,
            height=dp(50)
        )
        
        self.bbmd_network_input = TextInput(
            hint_text=_("connection.network.bbmd_network"),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        self.foreign_device_panel.add_widget(self.bbmd_ip_input)
        self.foreign_device_panel.add_widget(self.bbmd_port_dropdown)
        self.foreign_device_panel.add_widget(self.bbmd_network_input)
        
        # Toggle Switch Funktion
        def on_toggle_switch(instance, value):
            if value:
                # Berechne die Höhe basierend auf den Kindern
                total_height = sum(c.height for c in self.foreign_device_panel.children)
                total_height += self.foreign_device_panel.spacing * (len(self.foreign_device_panel.children) - 1)
                total_height += self.foreign_device_panel.padding[1] + self.foreign_device_panel.padding[3]  # Oberes und unteres Padding
                
                self.foreign_device_panel.height = total_height
                self.foreign_device_panel.opacity = 1
            else:
                self.foreign_device_panel.height = dp(0)
                self.foreign_device_panel.opacity = 0
            
            # Wichtig: Aktualisiere die Größe des Hauptcontainers
            Clock.schedule_once(lambda dt: update_container_height(), 0.1)
        
        def update_container_height():
            # Berechne die Gesamthöhe des Containers
            total_height = 0
            for child in main_container.children:
                total_height += child.height
            total_height += main_container.spacing * (len(main_container.children) - 1)
            
            # Setze die Höhe des Containers
            main_container.height = total_height
            
            # Debug-Ausgabe
            print(f"DEBUG: Hauptcontainer Höhe aktualisiert: {main_container.height}")
            print(f"DEBUG: Foreign Device Panel Höhe: {self.foreign_device_panel.height}")
        
        self.foreign_device_switch.bind(active=on_toggle_switch)
        
        # Füge Widgets zum Hauptcontainer hinzu
        main_container.add_widget(step1_label)
        main_container.add_widget(network_panel)
        main_container.add_widget(step2_label)
        main_container.add_widget(network_number_panel)
        main_container.add_widget(udp_port_panel)
        main_container.add_widget(foreign_device_layout)
        main_container.add_widget(self.foreign_device_panel)
        
        # Aktualisiere die Höhe des Hauptcontainers
        Clock.schedule_once(lambda dt: update_container_height(), 0.1)
        
        # Füge Event-Handler für Panel-Änderungen hinzu
        def on_panel_expanded(panel, is_expanded):
            # Aktualisiere die Höhe des Hauptcontainers
            Clock.schedule_once(lambda dt: update_container_height(), 0.2)
        
        network_panel.bind(is_expanded=on_panel_expanded)
        network_number_panel.bind(is_expanded=on_panel_expanded)
        udp_port_panel.bind(is_expanded=on_panel_expanded)
        
        return main_container


    def on_back_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Zurück'-Button geklickt wird"""
        from kivy.app import App
        app = App.get_running_app()
        app.root.ids.screen_manager.current = 'verbindung'

    def on_next_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Weiter'-Button geklickt wird"""
        # Speichere die Konfiguration
        try:
            config_data = {
                "adapter": self.adapter_dropdown.current_value if hasattr(self, 'adapter_dropdown') else "Ethernet",
                "network_number": self.network_number_input.text if hasattr(self, 'network_number_input') else "",
                "udp_port": self.udp_port_dropdown.current_value if hasattr(self, 'udp_port_dropdown') else "BAC0 (47808)",
                "foreign_device": self.foreign_device_switch.active if hasattr(self, 'foreign_device_switch') else False,
                "bbmd_ip": self.bbmd_ip_input.text if hasattr(self, 'bbmd_ip_input') and hasattr(self, 'foreign_device_switch') and self.foreign_device_switch.active else "",
                "bbmd_port": self.bbmd_port_dropdown.current_value if hasattr(self, 'bbmd_port_dropdown') and hasattr(self, 'foreign_device_switch') and self.foreign_device_switch.active else "BAC0 (47808)",
                "bbmd_network": self.bbmd_network_input.text if hasattr(self, 'bbmd_network_input') and hasattr(self, 'foreign_device_switch') and self.foreign_device_switch.active else ""
            }
            
            # Speichere die Konfiguration
            self.config_manager.save_connection_config("network", config_data)
            
            print(f"DEBUG: Netzwerkkonfiguration gespeichert: {config_data}")
        except Exception as e:
            print(f"ERROR: Fehler beim Speichern der Netzwerkkonfiguration: {e}")
        
        # Navigiere zum nächsten Screen
        from kivy.app import App
        app = App.get_running_app()
        app.root.ids.screen_manager.current = 'geräte'


    def save_connection_config(self, connection_type, config_data):
        """Speichert die Verbindungskonfiguration für einen bestimmten Typ"""
        # Aktualisiere den Verbindungstyp
        self.update_setting("connection", "type", connection_type)
        
        # Aktualisiere die Konfigurationsdaten
        for key, value in config_data.items():
            if connection_type not in self.settings["connection"]:
                self.settings["connection"][connection_type] = {}
            self.settings["connection"][connection_type][key] = value
        
        # Speichere die Einstellungen
        self.save_settings()