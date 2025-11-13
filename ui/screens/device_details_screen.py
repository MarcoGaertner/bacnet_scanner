# ui/screens/device_details_screen.py
from kivy.lang import Builder
from ui.utils import get_resource_path
from kivy.properties import DictProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from ui.screens.base_screen import BaseScreen
from scanner.storage import DatabaseStorage


class KVRow(BoxLayout):
    key = StringProperty("")
    value = StringProperty("")


class DeviceDetailsScreen(BaseScreen):
    name = "device_details"
    scan_id = NumericProperty(0)
    device_id = NumericProperty(0)
    device_name = StringProperty("")
    address = StringProperty("")

    details = DictProperty({})  # flache Key/Value-Map für Anzeige

    def load_device(self, scan_id: int, device_id: int):
        self.scan_id = scan_id
        self.device_id = device_id

        storage = DatabaseStorage()
        data = storage.get_scan_details(scan_id) or {}
        device = None
        for d in data.get("devices", []):
            if int(d.get("device_id", -1)) == int(device_id):
                device = d
                break

        if not device:
            self.device_name = f"Device {device_id}"
            self.address = ""
            self.details = {"Fehler": "Gerät nicht gefunden"}
            self._render_details()
            return

        props = device.get("properties") or {}
        self.device_name = props.get("object-name") or props.get("name") or f"Device {device_id}"
        self.address = device.get("address", "")

        # ein paar sinnvolle Felder herausziehen (nur vorhandene)
        kv = {}
        def put(label, key):
            v = props.get(key)
            if v not in (None, "", []):
                kv[label] = str(v)

        put("Beschreibung", "description")
        put("Standort", "location")
        put("Vendor", "vendor-name")
        put("Modell", "model-name")
        put("SW-Version", "application-software-version")

        # Anzahl Objekte, falls verfügbar
        obj_list = props.get("objects") or []
        kv["Anzahl Objekte"] = str(len(obj_list))

        self.details = kv
        self._render_details()

    def on_pre_enter(self, *args):
        self._render_details()

    def on_details(self, *args):
        self._render_details()

    def _render_details(self):
        container = self.ids.get("details_container")
        if not container:
            return
        container.clear_widgets()

        for k, v in self.details.items():
            row = KVRow(key=k, value=v)
            container.add_widget(row)


# NACH den Klassen laden
Builder.load_file('ui/screens/device_details_screen.kv')
