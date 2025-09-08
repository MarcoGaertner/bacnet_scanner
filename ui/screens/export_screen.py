# ui/screens/export_screen.py
from typing import List, Dict
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty, StringProperty, DictProperty
from kivy.app import App
from ui.styles import colors

from ui.screens.base_screen import BaseScreen
from scanner.storage import DatabaseStorage
from exporter.device_exporter import build_rows_for_scan, export_csv, export_xlsx

class ExportScreen(BaseScreen):
    name = "export"
    scan_id = NumericProperty(0)

    format = StringProperty("csv")                # "csv" | "xlsx" | "pdf"
    headers = ListProperty([])                    # Liste von export-keys in Reihenfolge
    header_labels = DictProperty({})              # key -> label
    preview_rows = ListProperty([])               # Liste von Dicts (erste N Zeilen)

    def load_for_scan(self, scan_id: int):
        self.scan_id = int(scan_id)
        self.reload_from_settings()

    def reload_from_settings(self):
        storage = DatabaseStorage()
        props = storage.get_export_properties()
        self.headers = [p["key"] for p in props if int(p["enabled"]) == 1]
        self.header_labels = {p["key"]: p["label"] for p in props}
        self._build_preview()

    def _build_preview(self, max_rows: int = 20):
        storage = DatabaseStorage()
        rows = build_rows_for_scan(self.scan_id, self.headers, storage)
        self.preview_rows = rows[:max_rows]
        self._render_preview_grid()

    def _render_preview_grid(self):
        grid = self.ids.get("preview_grid")
        if not grid:
            return
        grid.clear_widgets()
        grid.cols = max(1, len(self.headers))

        # Kopfzeile (Labels)
        for h in self.headers:
            from kivy.uix.label import Label
            grid.add_widget(Label(text=str(self.header_labels.get(h, h)),
                                  bold=True, halign='left', valign='middle',
                                  color=colors.TEXT_COLOR,
                                  text_size=(0, 0)))

        # Zeilen
        from kivy.uix.label import Label
        for row in self.preview_rows:
            for h in self.headers:
                val = row.get(h, "")
                grid.add_widget(Label(text=str(val),
                                      halign='left', valign='middle',
                                      color=colors.TEXT_COLOR,
                                      text_size=(0, 0)))

    # UI-Callbacks (aus KV)
    def set_format_csv(self):  self.format = "csv"
    def set_format_xlsx(self): self.format = "xlsx"
    def set_format_pdf(self):  self.format = "pdf"  # TODO: später implementieren

    def open_settings(self):
        sm = App.get_running_app().root
        try:
            scr = sm.get_screen("export_settings")
        except Exception:
            scr = None
            for s in sm.screens:
                if s.__class__.__name__ in ("ExportSettingsScreen",):
                    scr = s
                    break
        if not scr:
            print("ExportSettingsScreen nicht gefunden")
            return
        scr.load_fields()
        sm.current = scr.name

    def export_now(self):
        storage = DatabaseStorage()
        rows = build_rows_for_scan(self.scan_id, self.headers, storage)
        if not rows:
            print("Keine Daten zu exportieren.")
            return

        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = "exports"
        if self.format == "csv":
            path = f"{base_dir}/scan_{self.scan_id}_{ts}.csv"
            export_csv(path, rows, self.headers, self.header_labels)
            print(f"CSV exportiert: {path}")
        elif self.format == "xlsx":
            path = f"{base_dir}/scan_{self.scan_id}_{ts}.xlsx"
            export_xlsx(path, rows, self.headers, self.header_labels)
            print(f"Excel exportiert: {path}")
        elif self.format == "pdf":
            # TODO: PDF-Unterstützung hinzufügen (ReportLab/WeasyPrint etc.)
            print("PDF-Export ist noch nicht implementiert.")
        else:
            print(f"Unbekanntes Format: {self.format}")

# KV NACH den Klassen laden
Builder.load_file('ui/screens/export_screen.kv')
