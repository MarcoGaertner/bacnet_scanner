# ui/screens/export_screen.py
from typing import List, Dict
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty, StringProperty, DictProperty
from kivy.app import App
from ui.styles import colors
import os

from ui.screens.base_screen import BaseScreen
from scanner.storage import DatabaseStorage
from exporter.common import build_rows_for_scan
from exporter.csv_exporter import export_csv
from exporter.xlsx_exporter import export_xlsx
from exporter.pdf_exporter import export_pdf
from core.config import ConfigManager



class ExportScreen(BaseScreen):
    name = "export"
    scan_id = NumericProperty(0)

    format = StringProperty("csv")                # "csv" | "xlsx" | "pdf"
    headers = ListProperty([])                    # Liste von export-keys in Reihenfolge
    header_labels = DictProperty({})              # key -> label
    preview_rows = ListProperty([])               # Liste von Dicts (erste N Zeilen)

    # ---------- Lifecycle ----------
    def on_pre_enter(self, *args):
        # Falls der Screen ohne load_for_scan() geöffnet wurde:
        self._ensure_scan_and_headers()
        self._build_preview()

    # ---------- Öffentliche API (vom DevicesScreen aufgerufen) ----------
    def load_for_scan(self, scan_id: int):
        self.scan_id = int(scan_id or 0)
        self.reload_from_settings()  # lädt headers + baut Vorschau

    # ---------- Debug ----------
    def _debug_dump(self, where: str, rows_len: int | None = None):
        msg = f"[ExportScreen DEBUG] {where}: scan_id={self.scan_id}, " \
              f"headers={self.headers[:6]}... (n={len(self.headers)})"
        if rows_len is not None:
            msg += f", rows={rows_len}"
        print(msg)

    # ---------- Intern: Scan/Headers sicherstellen ----------
    def _ensure_scan_and_headers(self):
        # 1) scan_id sichern
        if not int(self.scan_id or 0):
            sm = self.manager
            if sm:
                dev = None
                # versuche offiziellen Namen (z.B. 'geräte')
                try:
                    dev = sm.get_screen("geräte")
                except Exception:
                    # Fallback: per Klassenname suchen
                    for sc in sm.screens:
                        if sc.__class__.__name__ == "DevicesScreen":
                            dev = sc
                            break
                if dev and int(getattr(dev, "scan_id", 0)):
                    self.scan_id = int(dev.scan_id)

        # 2) headers laden, falls leer
        if not self.headers:
            storage = DatabaseStorage()
            try:
                props = storage.get_export_properties()
            except Exception as e:
                print(f"[ExportScreen DEBUG] get_export_properties() fehlgeschlagen: {e}")
                props = []
            self.headers = [p["key"] for p in props if int(p.get("enabled", 0)) == 1]
            self.header_labels = {p["key"]: p.get("label", p["key"]) for p in props}

        # 3) Fallback-Header, falls immer noch leer (nie blockieren!)
        if not self.headers:
            self.headers = ["object-name", "device_id", "address_port"]
            self.header_labels.update({
                "object-name": "Name",
                "device_id": "Geräteinstanznr.",
                "address_port": "Adresse + Port",
            })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = ConfigManager()


    # ---------- Daten laden und Vorschau rendern ----------
    def reload_from_settings(self):
        """Lädt headers aus Config und baut Vorschau neu."""
        props = self.config_manager.get_export_properties()
        enabled_props = [p for p in props if int(p.get("enabled", 0)) == 1]
        enabled_props.sort(key=lambda x: int(x.get("order", 999)))
        
        self.headers = [p["key"] for p in enabled_props]
        self.header_labels = {p["key"]: p["label"] for p in enabled_props}
        
        self._debug_dump("reload_from_settings")
        self._build_preview()

    def _build_preview(self, max_rows: int = 20):
        self._ensure_scan_and_headers()

        # Debug: wie viele Geräte hat der Scan überhaupt?
        try:
            storage = DatabaseStorage()
            scan = storage.get_scan_details(int(self.scan_id)) or {}
            dev_count = len(scan.get("devices", []) or [])
            print(f"[ExportScreen DEBUG] _build_preview: devices_in_scan={dev_count}")
        except Exception as e:
            print(f"[ExportScreen DEBUG] get_scan_details() Fehler: {e}")

        storage = DatabaseStorage()
        rows = build_rows_for_scan(int(self.scan_id), self.headers, storage)
        self._debug_dump("_build_preview", rows_len=len(rows))
        self.preview_rows = rows[:max_rows]
        self._render_preview_grid()

    def _render_preview_grid(self):
        grid = self.ids.get("preview_grid")
        if not grid:
            print("[ExportScreen DEBUG] preview_grid nicht gefunden.")
            return
        grid.clear_widgets()
        grid.cols = max(1, len(self.headers))

        from kivy.uix.label import Label
        # Kopfzeile
        for h in self.headers:
            grid.add_widget(Label(
                text=str(self.header_labels.get(h, h)),
                bold=True, halign='left', valign='middle',
                color=colors.TEXT_COLOR, text_size=(0, 0)
            ))
        # Zeilen
        for row in self.preview_rows:
            for h in self.headers:
                val = row.get(h, "")
                grid.add_widget(Label(
                    text=str(val),
                    halign='left', valign='middle',
                    color=colors.TEXT_COLOR, text_size=(0, 0)
                ))

    # ---------- UI-Callbacks (aus KV) ----------
    def set_format_csv(self):  self.format = "csv"
    def set_format_xlsx(self): self.format = "xlsx"
    def set_format_pdf(self):  self.format = "pdf"  # TODO: später implementieren

    def open_settings(self):
        sm = self.manager
        if not sm:
            print("Kein ScreenManager gefunden.")
            return
        try:
            scr = sm.get_screen("export_settings")
        except Exception:
            scr = None
            for s in sm.screens:
                if s.__class__.__name__ == "ExportSettingsScreen":
                    scr = s
                    break
        if not scr:
            print("ExportSettingsScreen nicht gefunden")
            return
        scr.load_fields()
        sm.current = scr.name

    # ---------- SPEICHERN UNTER… ----------
    def export_now(self):
        """Öffnet den nativen 'Speichern unter…' Dialog (plyer).
        Prüft vorab, ob Daten vorhanden sind. Hängt fehlende Extension an
        und merkt sich den letzten Ordner."""
        self._ensure_scan_and_headers()

        storage = DatabaseStorage()
        probe_rows = build_rows_for_scan(int(self.scan_id), self.headers, storage)
        self._debug_dump("export_now (probe)", rows_len=len(probe_rows))
        if not probe_rows:
            # Zusätzlicher Hinweis, WIESO keine rows:
            try:
                scan = storage.get_scan_details(int(self.scan_id)) or {}
                dev_count = len(scan.get("devices", []) or [])
                print(f"[ExportScreen DEBUG] export_now: Keine Rows. devices_in_scan={dev_count}")
            except Exception:
                pass
            print("Keine Daten zu exportieren (Probe vor Dialog). Prüfe scan_id/DB-Inhalt.")
            return

        ext = self._ext_for_format()             # ".csv" / ".xlsx" / ".pdf"
        suggested = self._suggest_filename()     # z.B. "scan_12_20250908_153012.csv"
        start_dir = self._get_last_dir()

        try:
            from plyer import filechooser
            preferred_path = os.path.join(start_dir, suggested)
            selection = None
            try:
                selection = filechooser.save_file(
                    title="Speichern unter…",
                    path=preferred_path,
                    filters=[("Dateien", f"*{ext}")]
                )
            except Exception:
                selection = filechooser.save_file(
                    title="Speichern unter…",
                    path=start_dir,
                    filters=[("Dateien", f"*{ext}")]
                )

            if not selection:
                print("[ExportScreen DEBUG] export_now: Nutzer hat abgebrochen.")
                return

            chosen = selection if isinstance(selection, str) else selection[0]

            # Falls Ordner zurückkam → Namensvorschlag anhängen
            if os.path.isdir(chosen):
                chosen = os.path.join(chosen, suggested)

            # Extension erzwingen
            if not chosen.lower().endswith(ext):
                chosen += ext

            # Ordner merken
            self._save_last_dir(os.path.dirname(chosen) or ".")

            # Export durchführen (mit bereits vorbereiteten rows)
            return self._do_export_to(chosen, rows=probe_rows)

        except Exception as e:
            print(f"Speichern fehlgeschlagen (plyer). Grund: {e}")
            return

    # ---------- Hilfsfunktionen ----------
    def _ext_for_format(self) -> str:
        return ".csv" if self.format == "csv" else ".xlsx" if self.format == "xlsx" else ".pdf"

    def _suggest_filename(self) -> str:
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"scan_{self.scan_id}_{ts}{self._ext_for_format()}"

    def _get_last_dir(self) -> str:
        """Merkt den letzten Export-Ordner schlicht in einer Textdatei unter ./data/."""
        try:
            os.makedirs("data", exist_ok=True)
            path = "data/last_export_dir.txt"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    d = f.read().strip()
                    if d and os.path.isdir(d):
                        return d
        except Exception:
            pass
        # Fallback
        try:
            app = App.get_running_app()
            if hasattr(app, "user_data_dir") and os.path.isdir(app.user_data_dir):
                return app.user_data_dir
        except Exception:
            pass
        return os.getcwd()

    def _save_last_dir(self, d: str):
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/last_export_dir.txt", "w", encoding="utf-8") as f:
                f.write(d)
        except Exception:
            pass

    def _do_export_to(self, target_path: str, rows: List[Dict] | None = None):
        storage = DatabaseStorage()
        rows = rows if rows is not None else build_rows_for_scan(int(self.scan_id), self.headers, storage)
        self._debug_dump("_do_export_to", rows_len=len(rows))

        if not rows:
            print("Keine Daten zu exportieren.")
            return

        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)

        if self.format == "csv":
            export_csv(target_path, rows, self.headers, self.header_labels)
        elif self.format == "xlsx":
            export_xlsx(target_path, rows, self.headers, self.header_labels)
        elif self.format == "pdf":
            from exporter.pdf_exporter import export_pdf
            export_pdf(
                target_path,
                rows,
                self.headers,
                self.header_labels,
                title=f"Geräteliste – Scan {self.scan_id}",
                landscape_mode=True,
                logo_path="assets/siemens_logo.svg",   # Pfad anpassen, falls abweichend
                user_info=None,                        # optional: direkt dict übergeben
                user_settings_path="config/user_settings.json"  # oder weglassen -> Auto-Suche
            )


# KV NACH den Klassen laden
Builder.load_file('ui/screens/export_screen.kv')
