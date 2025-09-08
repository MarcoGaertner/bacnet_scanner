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
                
                # Debug-Ausgabe für Properties
                print(f"DEBUG: Gerät {device_id} Properties: {list(props.keys())}")
                
                # Verschiedene Möglichkeiten für den Gerätenamen prüfen
                device_name = None
                
                # 1. Versuche "object-name"
                if "object-name" in props:
                    device_name = props["object-name"]
                    print(f"DEBUG: Gefunden object-name: '{device_name}'")
                
                # 2. Fallback auf "name"
                elif "name" in props:
                    device_name = props["name"]
                    print(f"DEBUG: Gefunden name: '{device_name}'")
                
                # 3. Fallback auf Standard-Name
                if not device_name or device_name.strip() == "":
                    device_name = f"Device {device_id}"
                    print(f"DEBUG: Verwende Standard-Name: '{device_name}'")
                
                items.append({
                    "device_id": device_id,
                    "name": device_name,
                    "address": address,
                })
                
                print(f"DEBUG: Hinzugefügtes Gerät - ID: {device_id}, Name: '{device_name}', Adresse: '{address}'")
        
        self.devices = items
        print(f"DEBUG: Scan-Ergebnisse erfolgreich geladen: {len(items)} Geräte")
        self._render_device_rows()

    def on_pre_enter(self, *args):
        # falls jemand direkt auf den Screen navigiert hat
        self._render_device_rows()

    def on_devices(self, *args):
        self._render_device_rows()

    def _render_device_rows(self):
        container = self.ids.get("device_list_container")
        if not container:
            print("DEBUG: device_list_container nicht gefunden!")
            return
        
        print(f"DEBUG: Rendere {len(self.devices)} Geräte-Zeilen")
        container.clear_widgets()
        
        for i, dev in enumerate(self.devices):
            print(f"DEBUG: Erstelle Zeile für Gerät {i}: {dev}")
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


    def open_export_screen(self, *_):
        # 1) Nimm den ScreenManager des aktuellen Screens
        sm = self.manager
        if not sm:
            print("Kein ScreenManager gefunden.")
            return

        # 2) ExportScreen besorgen (erst Name 'export', dann Fallback Klassenname)
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

        # 3) Kontext setzen + navigieren
        screen.load_for_scan(int(self.scan_id))
        sm.current = screen.name

# NACH den Klassen laden
Builder.load_file('ui/screens/devices_screen.kv')