# ui/screens/files_screen.py
from functools import partial
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior  # <- wichtig

from ui.screens.base_screen import BaseScreen
from scanner.storage import DatabaseStorage


class ScanRow(ButtonBehavior, BoxLayout):  # <- ButtonBehavior dazu
    index = NumericProperty(0)
    date = StringProperty("")
    time = StringProperty("")
    user_display = StringProperty("")
    scan_id = NumericProperty(0)


class FilesScreen(BaseScreen):
    scans = ListProperty([])  # [{date,time,user_display,scan_id,...}]

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        Clock.schedule_once(lambda dt: self.refresh_scans(), 0)

    def refresh_scans(self):
        storage = DatabaseStorage()
        rows = storage.get_scan_list(limit=200) or []

        normalized = []
        for r in rows:
            ts = (r.get("timestamp") or "").strip()
            ui = r.get("user_info") or {}
            first = (ui.get("first_name") or "").strip()
            last  = (ui.get("last_name") or "").strip()
            email = (ui.get("email") or "").strip()
            name = (f"{first} {last}".strip()) or email or "—"

            normalized.append({
                "scan_id": r.get("scan_id"),
                "timestamp": ts,
                "date": ts[:10] if len(ts) >= 10 else ts,   # YYYY-MM-DD
                "time": ts[11:19] if len(ts) >= 19 else "",  # HH:MM:SS
                "user_display": name,
            })

        self.scans = normalized
        self._render_scan_rows()

    def on_scans(self, instance, value):
        self._render_scan_rows()

    def _render_scan_rows(self):
        container = self.ids.get('list_container', None)
        if not container:
            return
        container.clear_widgets()

        for i, s in enumerate(self.scans):
            row = ScanRow(
                index=i,
                date=s.get("date", ""),
                time=s.get("time", ""),
                user_display=s.get("user_display", ""),
                scan_id=int(s.get("scan_id", 0)),
            )
            # Klick-Handler
            row.bind(on_release=partial(self.goto_devices_screen, s.get("scan_id", 0)))
            container.add_widget(row)

    # --- Navigation ---
    def goto_devices_screen(self, scan_id: int, *_):
        sm = self.manager
        if not sm:
            print("Kein ScreenManager gefunden.")
            return
        # versuche, den DevicesScreen zu bekommen
        screen = None
        try:
            screen = sm.get_screen("devices")
        except Exception:
            for sc in sm.screens:
                if sc.__class__.__name__ in ("DevicesScreen",):
                    screen = sc
                    break
        if not screen:
            print("DevicesScreen nicht im ScreenManager.")
            return

        # Daten laden & anzeigen
        screen.load_scan(int(scan_id))
        sm.current = screen.name


# KV NACH den Klassen laden
Builder.load_file('ui/screens/files_screen.kv')
