import json
import os
import asyncio
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio

from ui.screens.connection_type_base_screen import ConnectionTypeBaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.lang import Builder
from core.i18n.translator import _
from ui.styles.colors import ThemeColors
from ui.widgets.expandable_panel import ExpandablePanel
from ui.widgets.dropdown_scrollbar import ScrollableNestedDropdown
from ui.widgets.toggle_switch import ToggleSwitch
from ui.widgets.hint_text_input import HintTextInput
from kivy.app import App
from kivy.clock import Clock
from scanner.discovery import DeviceDiscovery

# KV-Datei laden
Builder.load_file('ui/screens/network_screen.kv')

class NetworkScreen(ConnectionTypeBaseScreen):
    """Screen für BACnet Netzwerk Verbindungseinstellungen"""
    screen_title = StringProperty("")
    connection_type = "network"
    ip_label = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(NetworkScreen, self).__init__(**kwargs)
        # Lade die Netzwerkadapter beim Initialisieren
        self.network_adapters = self.load_network_adapters()
        # Status Label für Scan-Feedback hinzufügen
        self.status_label = None
        self.scan_button = None
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen"""
        self.screen_title = _("connection.network.title")
    
    def load_network_adapters(self):
        """Lädt die Netzwerkadapter aus der JSON-Datei"""
        try:
            # Pfad zur JSON-Datei im config-Ordner bestimmen
            base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
            config_dir = base_dir / "config"
            adapter_file = config_dir / "network_adapters.json"
            
            # Wenn die Datei existiert, lade sie
            if adapter_file.exists():
                with open(adapter_file, 'r', encoding='utf-8') as f:
                    adapters = json.load(f)
                print(f"INFO: {len(adapters)} Netzwerkadapter geladen")
                return adapters
            else:
                print(f"WARNUNG: Netzwerkadapter-Datei nicht gefunden: {adapter_file}")
                return []
        except Exception as e:
            print(f"FEHLER: Konnte Netzwerkadapter nicht laden: {e}")
            return []

    def _load_bacnet_ports(self):
        """Lädt BACnet-Port-Optionen aus der Konfigurationsdatei."""
        try:
            current_dir = os.path.dirname(__file__)
            project_root = os.path.join(current_dir, '..', '..')
            config_path = os.path.join(project_root, 'config', 'bacnet_ports.json')
            config_path = os.path.abspath(config_path)

            with open(config_path, 'r') as f:
                ports_data = json.load(f)
            
            return [item['display_text'] for item in ports_data]
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"FEHLER: Konnte bacnet_ports.json nicht laden oder verarbeiten: {e}")
            return ["BAC0 (47808)", "BAC1 (47809)", "BAC2 (47810)", "BAC3 (47811)"]
    
    def create_specific_content(self):
        """Erstellt den spezifischen Inhalt für den Netzwerk Verbindungstyp"""
        print("DEBUG: 1. Starte create_specific_content")
        
        # Hauptcontainer für den gesamten Inhalt
        main_container = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        main_container.bind(minimum_height=main_container.setter('height'))
        print("DEBUG: 2. main_container erstellt")
        
        # Überschriften
        step1_label = Label(text="1. " + _("connection.network.select_network"), color=ThemeColors.current["TEXT_COLOR"], font_size=dp(16), size_hint_y=None, height=dp(30), halign='left', valign='middle')
        step1_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        print("DEBUG: 3. step1_label erstellt")
        
        step2_label = Label(text="2. " + _("connection.network.advanced_settings"), color=ThemeColors.current["TEXT_COLOR"], font_size=dp(16), size_hint_y=None, height=dp(30), halign='left', valign='middle')
        step2_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        print("DEBUG: 4. step2_label erstellt")
        
        # Netzwerk Panel
        network_panel = ExpandablePanel(title=_("connection.network.network"), is_expanded=False, size_hint_y=None)
        network_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)], size_hint_y=None)
        network_layout.bind(minimum_height=network_layout.setter('height'))
        
        # Adapter-Optionen aus der geladenen JSON-Datei extrahieren
        adapter_options = [adapter["name"] for adapter in self.network_adapters] if self.network_adapters else ["Ethernet"]
        
        # Wenn keine Adapter gefunden wurden, Standard-Optionen verwenden
        if not adapter_options:
            adapter_options = ["Ethernet", "Wi-Fi", "VPN"]
            
        # Dropdown für Netzwerkadapter
        self.adapter_dropdown = ScrollableNestedDropdown(
            title=_("connection.network.adapter"), 
            options=adapter_options, 
            current_value=adapter_options[0] if adapter_options else "", 
            size_hint_y=None, 
            height=dp(50)
        )
        
        # Event-Handler für die Auswahl eines Adapters
        def on_adapter_selected(value):
            print(f"DEBUG: Adapter '{value}' ausgewählt")
            # IP-Adresse des ausgewählten Adapters aktualisieren
            self.update_ip_address(value)
        
        self.adapter_dropdown.on_select = on_adapter_selected
        
        # Layout für IP-Adresse
        ip_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        ip_label_left = Label(
            text=_("connection.network.ip_address"), 
            color=ThemeColors.current["TEXT_COLOR"], 
            size_hint_x=0.4, 
            halign='left', 
            valign='middle'
        )
        ip_label_left.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Label für die IP-Adresse (wird dynamisch aktualisiert)
        self.ip_label = Label(
            text="", 
            color=ThemeColors.current["HIGHLIGHT_COLOR"], 
            size_hint_x=0.6, 
            halign='left', 
            valign='middle'
        )
        self.ip_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        ip_layout.add_widget(ip_label_left)
        ip_layout.add_widget(self.ip_label)
        
        network_layout.add_widget(self.adapter_dropdown)
        network_layout.add_widget(ip_layout)
        network_panel.add_content(network_layout)
        print("DEBUG: 5. network_panel erstellt")

        # Initiale IP-Adresse setzen
        Clock.schedule_once(lambda dt: self.update_ip_address(self.adapter_dropdown.current_value), 0.1)
        
        # Netzwerknummer Panel
        network_number_panel = ExpandablePanel(title=_("connection.network.network_number"), is_expanded=False, size_hint_y=None)
        network_number_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)], size_hint_y=None)
        network_number_layout.bind(minimum_height=network_number_layout.setter('height'))
        
        # HintTextInput statt TextInput verwenden
        self.network_number_input = HintTextInput(
            hint_text=_("connection.network.network_number_hint"), 
            multiline=False, 
            input_filter='int', 
            size_hint_y=None, 
            height=dp(40)
        )
        
        network_number_layout.add_widget(self.network_number_input)
        network_number_panel.add_content(network_number_layout)
        print("DEBUG: 6. network_number_panel erstellt")

        # UDP Port Panel
        udp_port_panel = ExpandablePanel(title=_("connection.network.udp_port"), is_expanded=False, size_hint_y=None)
        udp_port_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)], size_hint_y=None)
        udp_port_layout.bind(minimum_height=udp_port_layout.setter('height'))
        
        udp_port_options = self._load_bacnet_ports()
        
        self.udp_port_dropdown = ScrollableNestedDropdown(title=_("connection.network.port"), options=udp_port_options, current_value=udp_port_options[0] if udp_port_options else "", size_hint_y=None, height=dp(50))
        
        udp_port_layout.add_widget(self.udp_port_dropdown)
        udp_port_panel.add_content(udp_port_layout)
        print("DEBUG: 7. udp_port_panel erstellt")

        # Foreign Device Panel mit Toggle Switch
        foreign_device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[0, 0, dp(10), 0])
        foreign_device_label = Label(text=_("connection.network.foreign_device"), color=ThemeColors.current["TEXT_COLOR"], size_hint_x=0.855, halign='left', valign='middle')
        foreign_device_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        switch_container = BoxLayout(size_hint_x=0.145, padding=[0, 0, 0, 0])
        self.foreign_device_switch = ToggleSwitch(active=False, size_hint=(None, None), size=(dp(50), dp(30)), pos_hint={'center_y': 0.5, 'center_x': 0.5})
        switch_container.add_widget(self.foreign_device_switch)
        foreign_device_layout.add_widget(foreign_device_label)
        foreign_device_layout.add_widget(switch_container)
        print("DEBUG: 8. foreign_device_layout erstellt")

        # Foreign Device Panel Inhalt
        self.foreign_device_panel = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(0), opacity=0, padding=[dp(10), 0, dp(10), dp(10)])
        self.foreign_device_panel.bind(minimum_height=self.foreign_device_panel.setter('height'))
        
        # HintTextInput statt TextInput verwenden
        self.bbmd_ip_input = HintTextInput(
            hint_text=_("connection.network.bbmd_ip"), 
            multiline=False, 
            size_hint_y=None, 
            height=dp(40)
        )
        
        bbmd_port_options = self._load_bacnet_ports() # Auch hier die Ports laden
        self.bbmd_port_dropdown = ScrollableNestedDropdown(title=_("connection.network.bbmd_port"), options=bbmd_port_options, current_value=bbmd_port_options[0] if bbmd_port_options else "", size_hint_y=None, height=dp(50))
        
        # HintTextInput statt TextInput verwenden
        self.bbmd_network_input = HintTextInput(
            hint_text=_("connection.network.bbmd_network"), 
            multiline=False, 
            input_filter='int', 
            size_hint_y=None, 
            height=dp(40)
        )
        
        self.foreign_device_panel.add_widget(self.bbmd_ip_input)
        self.foreign_device_panel.add_widget(self.bbmd_port_dropdown)
        self.foreign_device_panel.add_widget(self.bbmd_network_input)
        print("DEBUG: 9. foreign_device_panel Inhalt erstellt")

        # Toggle Switch Funktion
        def on_toggle_switch(instance, value):
            print(f"DEBUG: Toggle Switch geändert auf {value}")
            if value:
                total_height = sum(c.height for c in self.foreign_device_panel.children) + self.foreign_device_panel.spacing * (len(self.foreign_device_panel.children) - 1) + self.foreign_device_panel.padding[1] + self.foreign_device_panel.padding[3]
                self.foreign_device_panel.height = total_height
                self.foreign_device_panel.opacity = 1
            else:
                self.foreign_device_panel.height = dp(0)
                self.foreign_device_panel.opacity = 0
            Clock.schedule_once(lambda dt: update_container_height(), 0.1)

        def update_container_height():
            print("DEBUG: update_container_height wird aufgerufen")
            total_height = sum(c.height for c in main_container.children) + main_container.spacing * (len(main_container.children) - 1)
            main_container.height = total_height
            print(f"DEBUG: Hauptcontainer Höhe aktualisiert: {main_container.height}")

        self.foreign_device_switch.bind(active=on_toggle_switch)
        print("DEBUG: 10. Toggle Switch Funktion gebunden")

        # Status Label für Scan-Feedback hinzufügen
        self.status_label = Label(
            text="", 
            color=ThemeColors.current["TEXT_COLOR"], 
            size_hint_y=None, 
            height=dp(30), 
            halign='center', 
            valign='middle'
        )
        self.status_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        # Füge Widgets zum Hauptcontainer hinzu
        main_container.add_widget(step1_label)
        main_container.add_widget(network_panel)
        main_container.add_widget(step2_label)
        main_container.add_widget(network_number_panel)
        main_container.add_widget(udp_port_panel)
        main_container.add_widget(foreign_device_layout)
        main_container.add_widget(self.foreign_device_panel)
        main_container.add_widget(self.status_label)  # Status Label hinzufügen
        print("DEBUG: 11. Alle Widgets zum main_container hinzugefügt")

        # Event-Handler für Panel-Änderungen
        def on_panel_expanded(panel, is_expanded):
            print(f"DEBUG: Panel '{panel.title}' expanded: {is_expanded}")
            Clock.schedule_once(lambda dt: update_container_height(), 0.2)
        
        network_panel.bind(is_expanded=on_panel_expanded)
        network_number_panel.bind(is_expanded=on_panel_expanded)
        udp_port_panel.bind(is_expanded=on_panel_expanded)
        print("DEBUG: 12. Panel-Handler gebunden")

        # Initiale Höhe setzen
        Clock.schedule_once(lambda dt: update_container_height(), 0.1)
        print("DEBUG: 13. create_specific_content abgeschlossen")
        return main_container
    
    def update_ip_address(self, adapter_name):
        """Aktualisiert die angezeigte IP-Adresse basierend auf dem ausgewählten Adapter"""
        if not hasattr(self, 'ip_label') or not self.ip_label:
            print("DEBUG: IP-Label noch nicht initialisiert")
            return
            
        ip_address = "Nicht verfügbar"
        
        # Adapter in der Liste suchen
        for adapter in self.network_adapters:
            if adapter["name"] == adapter_name:
                # IP-Adresse aus dem Adapter-Dictionary lesen
                ip_address = adapter.get("ip_address") or "Nicht verfügbar"
                status = adapter.get("status", "")
                
                # Zusätzliche Informationen für Debug-Zwecke ausgeben
                print(f"DEBUG: Adapter '{adapter_name}' gefunden")
                print(f"       Status: {status}")
                print(f"       IP-Adresse: {ip_address}")
                break
        
        # IP-Adresse im Label anzeigen
        self.ip_label.text = ip_address
        print(f"DEBUG: IP-Adresse aktualisiert: {ip_address}")

    def on_back_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Zurück'-Button geklickt wird"""
        app = App.get_running_app()
        app.root.ids.screen_manager.current = 'verbindung'

    def save_connection_config(self, connection_type, config_data):
        """Speichert die Verbindungskonfiguration für einen bestimmten Typ"""
        if hasattr(self, 'config_manager') and self.config_manager:
            self.config_manager.update_setting("connection", "type", connection_type)
            
            for key, value in config_data.items():
                if connection_type not in self.config_manager.settings["connection"]:
                    self.config_manager.settings["connection"][connection_type] = {}
                self.config_manager.settings["connection"][connection_type][key] = value
            
            self.config_manager.save_settings()

    def on_next_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Weiter'-Button geklickt wird"""
        print("DEBUG: Next Button geklickt - starte Scan")
        
        # Button deaktivieren während des Scans
        if hasattr(self, 'scan_button') and self.scan_button:
            self.scan_button.disabled = True
        
        # Status anzeigen
        if self.status_label:
            self.status_label.text = _("connection.network.preparing_scan")  # "Preparing scan..."
        
        try:
            # Aktuelle IP-Adresse des ausgewählten Adapters abrufen
            ip_address = self.ip_label.text if hasattr(self, 'ip_label') else ""
            
            config_data = {
                "adapter": self.adapter_dropdown.current_value if hasattr(self, 'adapter_dropdown') else "Ethernet",
                "ip_address": ip_address,
                "network_number": self.network_number_input.text if hasattr(self, 'network_number_input') else "",
                "udp_port": self.udp_port_dropdown.current_value if hasattr(self, 'udp_port_dropdown') else "BAC0 (47808)",
                "foreign_device": self.foreign_device_switch.active if hasattr(self, 'foreign_device_switch') else False,
                "bbmd_ip": self.bbmd_ip_input.text if hasattr(self, 'bbmd_ip_input') and self.foreign_device_switch.active else "",
                "bbmd_port": self.bbmd_port_dropdown.current_value if hasattr(self, 'bbmd_port_dropdown') and self.foreign_device_switch.active else "BAC0 (47808)",
                "bbmd_network": self.bbmd_network_input.text if hasattr(self, 'bbmd_network_input') and self.foreign_device_switch.active else ""
            }
            
            # Konfiguration speichern falls config_manager verfügbar ist
            if hasattr(self, 'config_manager') and self.config_manager:
                self.config_manager.save_connection_config("network", config_data)
                print(f"DEBUG: Netzwerkkonfiguration gespeichert: {config_data}")
            
            # Scan in separatem Thread starten
            def run_scan_in_thread():
                # Neue Event Loop für diesen Thread erstellen
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Asynchronen Scan ausführen
                    loop.run_until_complete(self._start_scan_async())
                finally:
                    loop.close()
            
            # Thread starten
            scan_thread = threading.Thread(target=run_scan_in_thread, daemon=True)
            scan_thread.start()
            
        except Exception as e:
            print(f"ERROR: Fehler beim Starten des Scans: {e}")
            if self.status_label:
                self.status_label.text = f"Fehler: {e}"
            # Button wieder aktivieren bei Fehler
            if hasattr(self, 'scan_button') and self.scan_button:
                self.scan_button.disabled = False

    def load_scan_results_to_devices_screen(self, scan_id):
        """Lädt die Scan-Ergebnisse in den Devices Screen"""
        def do_load_scan(dt):
            try:
                app = App.get_running_app()
                screen_manager = app.root.ids.screen_manager
                
                # Devices Screen finden
                devices_screen = None
                try:
                    devices_screen = screen_manager.get_screen('geräte')
                except:
                    # Fallback: Screen über Klassenname suchen
                    for screen in screen_manager.screens:
                        if screen.__class__.__name__ == 'DevicesScreen':
                            devices_screen = screen
                            break
                
                if devices_screen and hasattr(devices_screen, 'load_scan'):
                    print(f"DEBUG: Lade Scan-Ergebnisse für Scan-ID {scan_id} in DevicesScreen")
                    devices_screen.load_scan(scan_id)
                    print("DEBUG: Scan-Ergebnisse erfolgreich geladen")
                else:
                    print("ERROR: DevicesScreen nicht gefunden oder load_scan Methode fehlt")
                    
            except Exception as e:
                print(f"ERROR: Fehler beim Laden der Scan-Ergebnisse: {e}")
                import traceback
                traceback.print_exc()
        
        # Im Hauptthread ausführen
        Clock.schedule_once(do_load_scan, 0)

    async def _start_scan_async(self):
        """Asynchrone Methode zum Starten des Scans"""
        def update_status(text):
            # UI-Updates müssen im Hauptthread erfolgen
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text) if self.status_label else None, 0)
        
        def enable_button():
            # Button im Hauptthread wieder aktivieren
            Clock.schedule_once(lambda dt: setattr(self.scan_button, 'disabled', False) if hasattr(self, 'scan_button') and self.scan_button else None, 0)
        
        def navigate_to_devices_with_results(scan_id):
            # Navigation und Laden der Ergebnisse im Hauptthread
            def do_navigate_and_load(dt):
                try:
                    app = App.get_running_app()
                    app.root.ids.screen_manager.current = 'geräte'
                    print("DEBUG: Navigation zu 'geräte' erfolgreich")
                    
                    # Scan-Ergebnisse laden (mit kleiner Verzögerung für Navigation)
                    Clock.schedule_once(lambda dt2: self.load_scan_results_to_devices_screen(scan_id), 0.1)
                    
                except Exception as e:
                    print(f"ERROR: Fehler bei Navigation und Laden: {e}")
            
            Clock.schedule_once(do_navigate_and_load, 0)
        
        update_status(_("connection.network.scanning_in_progress"))  # "Scanning in progress..."
        
        try:
            # Save current config to connection_settings.json
            ip_address = self.ip_label.text if hasattr(self, 'ip_label') else ""
            udp_port_str = self.udp_port_dropdown.current_value if hasattr(self, 'udp_port_dropdown') else "BAC0 (47808)"
            
            # Extract port number from string like "BAC0 (47808)"
            udp_port = 47808
            if "(" in udp_port_str and ")" in udp_port_str:
                try:
                    udp_port = int(udp_port_str.split("(")[1].split(")")[0])
                except ValueError:
                    pass  # Keep default 47808
            else:
                try:
                    udp_port = int(udp_port_str)
                except ValueError:
                    pass  # Keep default 47808

            config_data = {
                "adapter": self.adapter_dropdown.current_value if hasattr(self, 'adapter_dropdown') else "Ethernet",
                "ip_address": ip_address,
                "network_number": self.network_number_input.text if hasattr(self, 'network_number_input') else "",
                "udp_port": str(udp_port),  # Ensure it's stored as string or int, consistent with usage
                "foreign_device": self.foreign_device_switch.active if hasattr(self, 'foreign_device_switch') else False,
                "bbmd_ip": self.bbmd_ip_input.text if hasattr(self, 'bbmd_ip_input') and self.foreign_device_switch.active else "",
                "bbmd_port": self.bbmd_port_dropdown.current_value if hasattr(self, 'bbmd_port_dropdown') and self.foreign_device_switch.active else "BAC0 (47808)",
                "bbmd_network": self.bbmd_network_input.text if hasattr(self, 'bbmd_network_input') and self.foreign_device_switch.active else ""
            }
            
            # Get the path to connection_settings.json
            base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
            config_file_path = base_dir / "config" / "connection_settings.json"
            
            # Ensure config directory exists
            os.makedirs(config_file_path.parent, exist_ok=True)

            # Save the config to the file
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump({"connection": {"type": "network", "network": config_data}}, f, indent=2)
            print(f"DEBUG: Netzwerkkonfiguration für Scan gespeichert in: {config_file_path}")

            # Initialize DeviceDiscovery with the saved config path
            discovery = DeviceDiscovery(config_path=str(config_file_path))
            
            # Set scan mode to 'full' for UI initiated scans
            discovery.set_scan_mode('full')
            
            # Perform the scan
            scan_result = await discovery.discover_devices()
            
            if "error" in scan_result:
                update_status(_("connection.network.scan_error") + f": {scan_result['error']}")  # "Scan Error"
                print(f"ERROR: Scan failed: {scan_result['error']}")
            else:
                device_count = scan_result.get('device_count', 0)
                scan_id = scan_result.get('scan_id')  # Scan-ID aus dem Ergebnis extrahieren
                
                update_status(_("connection.network.scan_complete") + f": {device_count} " + _("connection.network.devices_found"))  # "Scan Complete"
                print(f"DEBUG: Scan completed: {device_count} devices found. Scan-ID: {scan_id}")
                
                if scan_id:
                    # Navigation mit Scan-Ergebnissen
                    navigate_to_devices_with_results(scan_id)
                else:
                    print("WARNING: Keine Scan-ID im Ergebnis gefunden")
                    # Fallback: Normale Navigation ohne Ergebnisse
                    def do_navigate(dt):
                        app = App.get_running_app()
                        app.root.ids.screen_manager.current = 'geräte'
                    Clock.schedule_once(do_navigate, 0)
                
        except Exception as e:
            update_status(_("connection.network.scan_exception") + f": {e}")  # "Scan Exception"
            print(f"ERROR: Exception during scan: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Button wieder aktivieren
            enable_button()
            
            # Clear status label after a short delay if there was an error
            def clear_error_status(dt):
                if self.status_label and (self.status_label.text.startswith(_("connection.network.scan_error")) or self.status_label.text.startswith(_("connection.network.scan_exception"))):
                    self.status_label.text = ''
            
            Clock.schedule_once(clear_error_status, 5)  # Clear error message after 5 seconds