from ui.screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.lang import Builder
from ui.utils import get_resource_path
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.clock import Clock
from core.config import ConfigManager
from core.i18n.translator import _
from core.events import event_bus
from ui.styles.colors import ThemeColors
from scanner.storage import DatabaseStorage
from kivy.app import App
import re

# 👉 HintTextInput import mit Fallback auf styles
try:
    from ui.widgets.hint_text_input import HintTextInput
except Exception:
    from ui.styles.hint_text_input import HintTextInput  # Fallback, falls Widget dort liegt

# KV-Datei laden
Builder.load_file('ui/screens/devices_screen.kv')

class IconButton(ButtonBehavior, BoxLayout):
    """Custom Icon Button mit Hover-Effekt"""
    icon_source = StringProperty("")
    
    def __init__(self, icon_source="", **kwargs):
        super(IconButton, self).__init__(**kwargs)
        self.icon_source = icon_source
        self.setup_button()
    
    def setup_button(self):
        """Richtet den Icon-Button ein"""
        self.clear_widgets()
        self.icon_image = Image(
            source=self.icon_source,
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            color=ThemeColors.current["TEXT_COLOR"]
        )
        self.add_widget(self.icon_image)
    
    def on_press(self):
        self.icon_image.color = ThemeColors.current["HIGHLIGHT_COLOR"]
    
    def on_release(self):
        self.icon_image.color = ThemeColors.current["TEXT_COLOR"]

class DeviceRow(ButtonBehavior, BoxLayout):
    """Klickbare Geräte-Zeile"""
    index = NumericProperty(0)
    device_id = NumericProperty(0)
    name = StringProperty("")
    address = StringProperty("")
    description = StringProperty("")
    location = StringProperty("")

class DevicesScreen(BaseScreen):
    """Screen für die Anzeige der gescannten BACnet-Geräte"""
    name = "devices"
    screen_title = StringProperty("")
    scan_id = NumericProperty(0)
    devices = ListProperty([])           # Alle Geräte
    filtered_devices = ListProperty([])  # Gefilterte Geräte
    search_query = StringProperty("")
    config_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(DevicesScreen, self).__init__(**kwargs)
        self.config_manager = ConfigManager()
        
        # Events registrieren
        event_bus.bind(on_language_changed=self.on_language_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        
        # UI
        self.update_translations()
        Clock.schedule_once(self.setup_ui, 0)
    
    def update_translations(self):
        self.screen_title = _("devices.title")
    
    def setup_ui(self, *args):
        """Richtet die UI ein"""
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(20), dp(20), dp(20)], spacing=dp(20))
        
        # Scrollview für den Inhalt
        scroll_view = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Header Layout
        header_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Titel
        title_label = Label(
            text=self.screen_title,
            font_size=dp(24),
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Scan-ID
        scan_info_label = Label(
            text=f"Scan #{self.scan_id}" if self.scan_id else "",
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_y=None,
            height=dp(24) if self.scan_id else dp(0),
            halign='left',
            valign='middle',
            opacity=0.75
        )
        scan_info_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Suchfeld-Zeile
        search_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        search_label = Label(
            text=_("devices.search"),
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_x=None,
            width=dp(80),
            halign='left',
            valign='middle'
        )
        search_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # 👉 NEU: HintTextInput statt TextInput
        self.search_input = HintTextInput(
            hint_text=_("devices.search_hint"),
            size_hint_y=None,
            height=dp(40),
            multiline=False
            # keine foreground/background hier setzen – das macht das Widget selbst
        )
        # falls deine HintTextInput-Version unsichtbare Selektion kann – nur setzen, wenn vorhanden
        if hasattr(self.search_input, "hide_selection_visuals"):
            self.search_input.hide_selection_visuals = True

        self.search_input.bind(text=self.on_search_text_changed)
        
        # Clear Button (Icon oder Fallback-Button)
        clear_button_container = BoxLayout(size_hint_x=None, width=dp(40), size_hint_y=None, height=dp(40))
        self.clear_button = IconButton(icon_source='ui/assets/icons/clear.ico', size_hint=(1, 1))
        if not self._icon_exists('ui/assets/icons/clear.ico'):
            self.clear_button = Button(
                text="✕",
                size_hint=(1, 1),
                background_normal='',
                background_color=ThemeColors.current["CARD_BACKGROUND"],
                color=ThemeColors.current["TEXT_COLOR"],
                font_size=dp(16)
            )
        self.clear_button.bind(on_release=self.clear_search)
        clear_button_container.add_widget(self.clear_button)
        
        search_layout.add_widget(search_label)
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(clear_button_container)
        
        # Ergebnis-Info
        self.result_info_label = Label(
            text="",
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle',
            opacity=0.75,
            font_size=dp(12)
        )
        self.result_info_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Header zusammenfügen
        header_layout.add_widget(title_label)
        if self.scan_id:
            header_layout.add_widget(scan_info_label)
        header_layout.add_widget(search_layout)
        header_layout.add_widget(self.result_info_label)
        
        # Geräte-Container
        self.device_container = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.device_container.bind(minimum_height=self.device_container.setter('height'))
        
        # Geräte rendern
        self._update_filtered_devices()
        self._render_device_rows()
        
        # Export-Button
        export_button = Button(
            text=_("devices.export"),
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=ThemeColors.current["HIGHLIGHT_COLOR"],
            color=(1, 1, 1, 1)
        )
        export_button.bind(on_release=self.open_export_screen)
        
        # Layout aufbauen
        content_layout.add_widget(header_layout)
        content_layout.add_widget(self.device_container)
        content_layout.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))  # Spacer
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(export_button)
        
        self.clear_widgets()
        self.add_widget(main_layout)
        
        Clock.schedule_once(self._initialize_clear_button_state, 0.1)
    
    def _initialize_clear_button_state(self, *args):
        if hasattr(self, 'clear_button') and hasattr(self, 'search_input'):
            current_text = (self.search_input.text or "").strip()
            self.clear_button.opacity = 1.0 if current_text else 0.3
            print(f"DEBUG: Clear-Button initialisiert - Text: '{current_text}', Opacity: {self.clear_button.opacity}")
    
    def _icon_exists(self, path):
        import os
        return os.path.exists(path)
    
    def on_search_text_changed(self, instance, text):
        self.search_query = (text or "").lower().strip()
        self._update_filtered_devices()
        self._render_device_rows()
        self._update_result_info()
        if hasattr(self, 'clear_button'):
            self.clear_button.opacity = 1.0 if (text or "").strip() else 0.3
    
    def clear_search(self, *args):
        if hasattr(self, 'search_input'):
            self.search_input.text = ""
    
    def _update_filtered_devices(self):
        if not self.search_query:
            self.filtered_devices = self.devices[:]
            return
        filtered = [d for d in self.devices if self._device_matches_search(d, self.search_query)]
        self.filtered_devices = filtered
    
    def _device_matches_search(self, device, query):
        if not query:
            return True
        searchable_fields = [
            device.get("name", ""),
            str(device.get("device_id", "")),
            device.get("address", ""),
            device.get("description", ""),
            device.get("location", ""),
            device.get("vendor_name", ""),
            device.get("model_name", ""),
            device.get("application_software_version", ""),
            device.get("firmware_revision", ""),
            device.get("object_name", ""),
        ]
        props = device.get("properties", {})
        if props:
            for key, value in props.items():
                if isinstance(value, (str, int, float)):
                    searchable_fields.append(str(value))
        search_text = " ".join(searchable_fields).lower()
        return all(term in search_text for term in query.split())
    
    def _update_result_info(self):
        if not hasattr(self, 'result_info_label'):
            return
        total_devices = len(self.devices)
        filtered_devices = len(self.filtered_devices)
        if self.search_query:
            if filtered_devices == 0:
                self.result_info_label.text = _("devices.no_results")
            elif filtered_devices == 1:
                self.result_info_label.text = _("devices.one_result").format(total=total_devices)
            else:
                self.result_info_label.text = _("devices.multiple_results").format(
                    count=filtered_devices, total=total_devices
                )
        else:
            if total_devices == 0:
                self.result_info_label.text = _("devices.no_devices")
            elif total_devices == 1:
                self.result_info_label.text = _("devices.one_device")
            else:
                self.result_info_label.text = _("devices.multiple_devices").format(count=total_devices)
    
    def load_scan(self, scan_id: int):
        print(f"DEBUG: Lade Scan-Ergebnisse für Scan-ID {scan_id} in DevicesScreen")
        self.scan_id = scan_id
        storage = DatabaseStorage()
        data = storage.get_scan_details(scan_id)
        
        print(f"DEBUG: Scan-Daten erhalten: {data is not None}")
        if data:
            print(f"DEBUG: Anzahl Geräte in Scan: {len(data.get('devices', []))}")
        
        items = []
        if data and data.get("devices"):
            for d in data["devices"]:
                device_id = d.get("device_id", 0)
                address = d.get("address", "")
                props = d.get("properties") or {}
                print(f"DEBUG: Gerät {device_id} Properties: {list(props.keys())}")
                
                device_name = None
                if "object-name" in props:
                    device_name = props["object-name"]
                    print(f"DEBUG: Gefunden object-name: '{device_name}'")
                elif "name" in props:
                    device_name = props["name"]
                    print(f"DEBUG: Gefunden name: '{device_name}'")
                if not device_name or device_name.strip() == "":
                    device_name = f"Device {device_id}"
                    print(f"DEBUG: Verwende Standard-Name: '{device_name}'")
                
                device_info = {
                    "device_id": device_id,
                    "name": device_name,
                    "address": address,
                    "description": props.get("description", ""),
                    "location": props.get("location", ""),
                    "vendor_name": props.get("vendor-name", ""),
                    "model_name": props.get("model-name", ""),
                    "application_software_version": props.get("application-software-version", ""),
                    "firmware_revision": props.get("firmware-revision", ""),
                    "object_name": props.get("object-name", ""),
                    "properties": props
                }
                items.append(device_info)
                print(f"DEBUG: Hinzugefügtes Gerät - ID: {device_id}, Name: '{device_name}', Adresse: '{address}'")
        
        self.devices = items
        print(f"DEBUG: Scan-Ergebnisse erfolgreich geladen: {len(items)} Geräte")
        self.setup_ui()
    
    def _render_device_rows(self):
        if not hasattr(self, 'device_container') or not self.device_container:
            return
        devices_to_show = self.filtered_devices
        print(f"DEBUG: Rendere {len(devices_to_show)} Geräte-Zeilen")
        self.device_container.clear_widgets()
        
        for i, dev in enumerate(devices_to_show):
            print(f"DEBUG: Erstelle Zeile für Gerät {i}: {dev}")
            description = dev.get("description", "")
            location = dev.get("location", "")
            row = DeviceRow(
                index=i,
                device_id=dev["device_id"],
                name=dev["name"],
                address=dev.get("address", ""),
                description=description,
                location=location,
                size_hint_y=None,
                height=dp(48)
            )
            row.bind(on_release=lambda inst, did=dev["device_id"]: self.open_device_details(did))
            self.device_container.add_widget(row)
    
    def open_device_details(self, device_id: int, *_):
        sm = self.manager
        if not sm:
            print("Kein ScreenManager gefunden.")
            return
        details = None
        try:
            details = sm.get_screen("device_details")
        except Exception:
            pass
        if not details:
            for sc in sm.screens:
                if sc.__class__.__name__ == "DeviceDetailsScreen":
                    details = sc
                    break
        if not details:
            print("DeviceDetailsScreen nicht im ScreenManager gefunden.")
            return
        details.load_device(self.scan_id, int(device_id))
        sm.current = details.name

    def open_export_screen(self, *_):
        sm = self.manager
        if not sm:
            print("Kein ScreenManager gefunden.")
            return
        try:
            screen = sm.get_screen("export")
        except Exception:
            screen = None
            for sc in sm.screens:
                if sc.__class__.__name__ == "ExportScreen":
                    screen = sc
                    break
        if not screen:
            print("ExportScreen nicht im ScreenManager gefunden.")
            return
        screen.load_for_scan(int(self.scan_id))
        sm.current = screen.name
    
    def on_language_changed(self, instance, language_code):
        self.update_translations()
        self.setup_ui()
    
    def on_theme_changed(self, instance, theme_name):
        self.setup_ui()
    
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        if hasattr(self, 'device_container'):
            self._update_filtered_devices()
            self._render_device_rows()
            self._update_result_info()
        if hasattr(self, 'clear_button') and hasattr(self, 'search_input'):
            current_text = (self.search_input.text or "").strip()
            self.clear_button.opacity = 1.0 if current_text else 0.3
