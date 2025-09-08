# ui/screens/devices_screen.py
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import App

from ui.screens.base_screen import BaseScreen
from scanner.storage import DatabaseStorage


class DeviceRow(ButtonBehavior, BoxLayout):  # klickbar
    index = NumericProperty(0)
    device_id = NumericProperty(0)
    name = StringProperty("")
    address = StringProperty("")


class DevicesScreen(BaseScreen):
    name = "devices"  # ScreenManager-Name
    scan_id = NumericProperty(0)
    devices = ListProperty([])  # [{device_id, name, address}]

    def load_scan(self, scan_id: int):
        """Vom FilesScreen aufgerufen."""
        self.scan_id = scan_id
        storage = DatabaseStorage()
        data = storage.get_scan_details(scan_id)
        items = []
        if data and data.get("devices"):
            for d in data["devices"]:
                props = (d.get("properties") or {})
                device_name = props.get("object-name") or props.get("name") or f"Device {d.get('device_id')}"
                items.append({
                    "device_id": d.get("device_id", 0),
                    "name": device_name,
                    "address": d.get("address", ""),
                })
        self.devices = items
        self._render_device_rows()

    def on_pre_enter(self, *args):
        # falls jemand direkt auf den Screen navigiert hat
        self._render_device_rows()

    def on_devices(self, *args):
        self._render_device_rows()

    def _render_device_rows(self):
        container = self.ids.get("device_list_container")
        if not container:
            return
        container.clear_widgets()
        for i, dev in enumerate(self.devices):
            row = DeviceRow(
                index=i,
                device_id=dev["device_id"],
                name=dev["name"],
                address=dev.get("address", ""),
            )
            row.bind(on_release=lambda inst, did=dev["device_id"]: self.open_device_details(did))
            container.add_widget(row)

    def open_device_details(self, device_id: int, *_):
            sm = self.manager
            if not sm:
                print("Kein ScreenManager gefunden.")
                return

            details = None
            # 1) versuche offiziellen Namen
            try:
                details = sm.get_screen("device_details")
            except Exception:
                pass
            # 2) Fallback per Klassenname
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


# NACH den Klassen laden
Builder.load_file('ui/screens/devices_screen.kv')
